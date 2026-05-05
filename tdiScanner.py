import ast

HIGH_RISK_THRESHOLD = 50


def count_loc(source_code):
    """Count effective lines of code, excluding blank lines and comments."""
    lines = source_code.splitlines()
    count = 0
    for line in lines:
        stripped = line.strip()
        if stripped != "" and not stripped.startswith("#"):
            count += 1
    return count


def count_function_loc(function_node):
    """Return line span of a function node."""
    if hasattr(function_node, "end_lineno") and function_node.end_lineno is not None:
        return function_node.end_lineno - function_node.lineno + 1
    return 0


def count_commented_out_blocks(source_code):
    """
    Detect blocks of 3+ consecutive comment lines as a code smell.
    These are flagged as technical debt indicators.
    """
    lines = source_code.splitlines()
    count = 0
    consecutive_comments = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            consecutive_comments += 1
        else:
            if consecutive_comments >= 3:
                count += 1
            consecutive_comments = 0
    if consecutive_comments >= 3:
        count += 1
    return count


def calculate_complexity(function_node):
    """
    Approximate Cyclomatic Complexity using the decision-point method.
    M = number_of_decision_points + 1

    This is equivalent to M = E - N + 2P for a single connected function
    (as described in Appendix B of the brief). Decision points counted are:
    if, for, while, except handlers, and boolean operators (and/or).

    Assumption: each BoolOp (and/or) is treated as one additional path,
    consistent with standard McCabe complexity extensions.
    """
    complexity = 1
    for node in ast.walk(function_node):
        if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.BoolOp)):
            complexity += 1
    return complexity


def calculate_vulnerability_density(red_flag_count, loc):
    """
    Vulnerability Density = (red flags / LOC) * 1000
    Expressed as red flags per 1,000 lines of code (Section 3.2).
    """
    if loc > 0:
        return (red_flag_count / loc) * 1000
    return 0


def calculate_tdi(complexity_score, vulnerability_density):
    """
    Technical Debt Index as defined in Section 3:
    TDI = (Complexity_Score * 0.5) + (Vulnerability_Density * 0.5)
    """
    return (complexity_score * 0.5) + (vulnerability_density * 0.5)


def classify_tdi(tdi):
    """
    Risk classification per Section 3.3:
    TDI >= 50 → High (Extremely Complex / High Risk)
    TDI >= 20 → Medium
    TDI <  20 → Low
    """
    if tdi >= HIGH_RISK_THRESHOLD:
        return "High"
    elif tdi >= 20:
        return "Medium"
    return "Low"


def detect_ast_red_flags_in_node(root_node):
    """
    Detect security red flags by walking the AST.

    Covers all five categories referenced in Section 3.2:
    1. Hardcoded credentials / secrets
    2. Weak or deprecated cryptographic functions (md5, sha1)
    3. SQL injection patterns (string concatenation in execute())
    4. Unsafe input handling (eval, exec)
    5. Insecure configuration values (DEBUG=True, SSL verify disabled)
    """
    red_flags = []

    for node in ast.walk(root_node):

        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name = target.id.lower()
                    secret_words = ["password", "secret", "token", "api_key", "apikey", "passwd", "private_key"]
                    for word in secret_words:
                        if word in name and isinstance(node.value, ast.Constant):
                            if isinstance(node.value.value, (str, int)):
                                red_flags.append(
                                    f"Hardcoded secret detected: '{target.id}' assigned a literal value"
                                )
                            break

        if isinstance(node, ast.Call):
            func = node.func

            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                if func.value.id == "hashlib" and func.attr in ("md5", "sha1"):
                    red_flags.append(
                        f"Weak cryptographic algorithm: hashlib.{func.attr}() is deprecated for security use"
                    )

            if isinstance(func, ast.Attribute) and func.attr == "execute":
                if node.args:
                    first_arg = node.args[0]
                    if isinstance(first_arg, ast.BinOp) and isinstance(first_arg.op, ast.Add):
                        red_flags.append(
                            "SQL injection risk: string concatenation used in execute() — use parameterised queries"
                        )

            if isinstance(func, ast.Name) and func.id in ("eval", "exec"):
                red_flags.append(
                    f"Unsafe input handling: {func.id}() executes arbitrary code and must not accept user input"
                )

        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name = target.id.lower()
                    if name == "debug" and isinstance(node.value, ast.Constant):
                        if node.value.value is True:
                            red_flags.append(
                                "Insecure configuration: DEBUG=True should never be set in production"
                            )
                if isinstance(target, ast.Attribute) and target.attr == "verify":
                    if isinstance(node.value, ast.Constant) and node.value.value is False:
                        red_flags.append(
                            "Insecure configuration: SSL verification disabled (verify=False)"
                        )

    return red_flags


def detect_ast_red_flags(tree):
    return detect_ast_red_flags_in_node(tree)


def detect_function_red_flags(function_node):
    return detect_ast_red_flags_in_node(function_node)


def _collect_top_level_functions(tree):
    """
    Collect only top-level functions, avoiding double-counting nested ones.
    Nested functions are analysed as part of their parent's complexity.
    """
    top_level = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            top_level.append(node)
    direct = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Module):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    direct.append(child)
    return direct if direct else top_level


def scan_code(source_code):
    """
    Main scanning entry point. Returns per-function metrics and file-level aggregates.

    Per-function data includes:
    - loc: lines of code
    - complexity: Cyclomatic Complexity score
    - vulnerability_density: red flags per 1,000 LoC
    - tdi: Technical Debt Index
    - risk: Low / Medium / High classification
    - critical: True if TDI >= HIGH_RISK_THRESHOLD (50)

    File-level data includes aggregate versions of the above plus all red flags.
    """
    tree = ast.parse(source_code)

    function_results = []
    top_level_functions = _collect_top_level_functions(tree)

    for node in top_level_functions:
        fn_complexity = calculate_complexity(node)
        fn_loc = count_function_loc(node)
        fn_red_flags = detect_function_red_flags(node)
        fn_red_flag_count = len(fn_red_flags)
        fn_vuln_density = calculate_vulnerability_density(fn_red_flag_count, fn_loc)
        fn_tdi = calculate_tdi(fn_complexity, fn_vuln_density)
        fn_risk = classify_tdi(fn_tdi)

        function_results.append({
            "function": node.name,
            "loc": fn_loc,
            "complexity": fn_complexity,
            "red_flag_count": fn_red_flag_count,
            "red_flags": fn_red_flags,
            "vulnerability_density": round(fn_vuln_density, 2),
            "tdi": round(fn_tdi, 2),
            "risk": fn_risk,
            "critical": fn_tdi >= HIGH_RISK_THRESHOLD,
        })

    loc = count_loc(source_code)
    file_complexity = calculate_complexity(tree) if loc > 0 else 0

    ast_red_flags = detect_ast_red_flags(tree)
    comment_block_count = count_commented_out_blocks(source_code)
    red_flags = list(ast_red_flags) + ["Commented-out code block detected"] * comment_block_count

    red_flag_count = len(red_flags)
    vuln_density = calculate_vulnerability_density(red_flag_count, loc)
    tdi = calculate_tdi(file_complexity, vuln_density)
    risk = classify_tdi(tdi)

    return {
        "functions": function_results,
        "loc": loc,
        "file_complexity": file_complexity,
        "red_flag_count": red_flag_count,
        "red_flags": red_flags,
        "vulnerability_density": round(vuln_density, 2),
        "tdi": round(tdi, 2),
        "risk": risk,
        "critical": tdi >= HIGH_RISK_THRESHOLD,
    }