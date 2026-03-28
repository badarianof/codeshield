import ast

def get_risk_label(complexity):
    if complexity <= 20:
        return "Low"
    elif complexity < 50:
        return "Medium"
    else:
        return "High"


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
                "complexity": complexity,
                "risk": get_risk_label(complexity)
            })
            
    return results
