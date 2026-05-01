import ast


def count_loc(source_code):
    lines = source_code.splitlines()
    count = 0

    for line in lines:
        stripped = line.strip()

        if stripped != "" and not stripped.startswith("#"):
            count += 1

    return count


def count_function_loc(function_node):
    if hasattr(function_node, "end_lineno") and function_node.end_lineno is not None:
        return function_node.end_lineno - function_node.lineno + 1

    return 0


def count_commented_out_blocks(source_code):
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
    complexity = 1

    for inner_node in ast.walk(function_node):
        if isinstance(inner_node, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.BoolOp)):
            complexity += 1

    return complexity

def calculate_vulnerability_density(red_flag_count, loc):
    if loc > 0:
        return (red_flag_count / loc) * 1000
    else:
        return 0
    

def calculate_tdi(complexity_score, vulnerability_density):
    return (complexity_score * 0.5) + (vulnerability_density * 0.5)


def detect_ast_red_flags_in_node(root_node):
    red_flags = []

    for node in ast.walk(root_node):
        # Hardcoded credentials/secrets
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name = target.id.lower()
                    secret_words = ["password", "secret", "token", "api_key", "apikey"]

                    for word in secret_words:
                        if word in name:
                            if isinstance(node.value, ast.Constant):
                                if isinstance(node.value.value, (str, int)):
                                    red_flags.append(f"Possible hardcoded secret: {target.id}")
                            break

        # Weak crypto
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id == "hashlib" and node.func.attr in ["md5", "sha1"]:
                    red_flags.append(f"Weak cryptographic algorithm used: {node.func.attr}")

        # SQL injection pattern
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "execute":
                if node.args:
                    first_arg = node.args[0]
                    if isinstance(first_arg, ast.BinOp) and isinstance(first_arg.op, ast.Add):
                        red_flags.append("Possible SQL injection pattern: concatenated query in execute()")

    return red_flags


def detect_ast_red_flags(tree):
    return detect_ast_red_flags_in_node(tree)


def detect_function_red_flags(function_node):
    return detect_ast_red_flags_in_node(function_node)


def classify_tdi(tdi):
    if tdi >= 50:
        return "High"
    elif tdi >= 20:
        return "Medium"
    else:
        return "Low"


def scan_code(source_code):
    tree = ast.parse(source_code)

    function_results = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function_complexity = calculate_complexity(node)

            function_loc = count_function_loc(node)

            function_red_flags = detect_function_red_flags(node)
            function_red_flags_count = len(function_red_flags)

            function_vulnerability_density = calculate_vulnerability_density(
                function_red_flags_count,
                function_loc
            )

            function_tdi = calculate_tdi(
                function_complexity,
                function_vulnerability_density
            )

            function_results.append({
                "function": node.name,
                "loc": function_loc,
                "complexity": function_complexity,
                "red_flag_count": function_red_flags_count,
                "red_flags": function_red_flags,
                "vulnerability_density": round(function_vulnerability_density, 2),
                "tdi": round(function_tdi, 2),
                "risk": classify_tdi(function_tdi)
            })

    loc = count_loc(source_code)

    if loc == 0:
        file_complexity = 0
    else:
        file_complexity = calculate_complexity(tree)

    ast_red_flags = detect_ast_red_flags(tree)
    comment_block_flags = count_commented_out_blocks(source_code)

    red_flags = list(ast_red_flags)

    for _ in range(comment_block_flags):
        red_flags.append("Commented-out code block detected")

    red_flag_count = len(red_flags)

    vulnerability_density = calculate_vulnerability_density(red_flag_count, loc)

    tdi = calculate_tdi(file_complexity, vulnerability_density)

    return {
        "functions": function_results,
        "loc": loc,
        "red_flag_count": red_flag_count,
        "red_flags": red_flags,
        "vulnerability_density": round(vulnerability_density, 2),
        "file_complexity": file_complexity,
        "tdi": round(tdi, 2),
        "risk": classify_tdi(tdi)
    }