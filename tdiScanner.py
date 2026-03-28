import ast


def count_loc(source_code):
    lines = source_code.splitlines()
    count = 0

    for line in lines:
        stripped = line.strip()

        if stripped != "" and not stripped.startswith("#"):
            count += 1

    return count


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


def calculate_function_complexity(function_node):
    complexity = 1

    for inner_node in ast.walk(function_node):
        if isinstance(inner_node, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.BoolOp)):
            complexity += 1

    return complexity


def detect_ast_red_flags(tree):
    red_flags = []

    for node in ast.walk(tree):
        # Hardcoded credentials/secretsdf
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

        # SQL injection pattern: string concatenation inside execute(...)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "execute":
                if node.args:
                    first_arg = node.args[0]
                    if isinstance(first_arg, ast.BinOp) and isinstance(first_arg.op, ast.Add):
                        red_flags.append("Possible SQL injection pattern: concatenated query in execute()")

    return red_flags


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
            complexity = calculate_function_complexity(node)
            function_results.append({
                "function": node.name,
                "complexity": complexity
            })

    loc = count_loc(source_code)

    ast_red_flags = detect_ast_red_flags(tree)
    comment_block_flags = count_commented_out_blocks(source_code)

    red_flags = list(ast_red_flags)

    for _ in range(comment_block_flags):
        red_flags.append("Commented-out code block detected")

    red_flag_count = len(red_flags)

    if function_results:
        total_complexity = 0
        
        for fn in function_results:
            total_complexity += fn["complexity"]
            
            avg_complexity = total_complexity / len(function_results)
            
    else:
        avg_complexity = 0

    if loc > 0:
        vulnerability_density = (red_flag_count / loc) * 1000
    else:
        vulnerability_density = 0

    tdi = (avg_complexity * 0.5) + (vulnerability_density * 0.5)

    return {
        "functions": function_results,
        "loc": loc,
        "red_flag_count": red_flag_count,
        "red_flags": red_flags,
        "vulnerability_density": round(vulnerability_density, 2),
        "avg_complexity": round(avg_complexity, 2),
        "tdi": round(tdi, 2),
        "risk": classify_tdi(tdi)
    }