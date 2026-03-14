import ast

def get_risk_label(complexity):
    if complexity <= 5:
        return "Low"
    elif complexity <= 10:
        return "Moderate"
    elif complexity <= 20:
        return "High"
    else:
        return "Critical"
    
def calculate_complexity(source_code):
    tree = ast.parse(source_code)
    
    results = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            
            complexity = 1
            
            for inner_node in ast.walk(node):
                if isinstance(inner_node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                    complexity += 1
            
            results.append({
                "function": node.name,
                "complexity": complexity
            })
    
    return results

filename = "complexityScanner.py"

with open(filename, "r") as f:
    source_code = f.read()

results = calculate_complexity(source_code)

for r in results:
    label = get_risk_label(r['complexity'])
    print(f"Function: {r['function']}, Complexity: {r['complexity']}, Risk: {label}")