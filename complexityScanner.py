import ast

def calculate_complexity(source_code):
    tree = ast.parse(source_code)

    complexity = 1

    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
            complexity += 1

    return complexity

filename = "complexityScanner.py"

with open(filename, "r") as f:
    source_code = f.read()

result = calculate_complexity(source_code)
print("Cyclomatic Complexity:", result)