import ast

code = """
def grade(score):
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    else:
        return "F"
"""

tree = ast.parse(code)

complexity = 1

for node in ast.walk(tree):
    if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
        complexity += 1

print("Cyclomatic Complexity:", complexity)