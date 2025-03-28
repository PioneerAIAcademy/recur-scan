import ast
import sys


def extract_functions(file_path: str) -> list[str]:
    with open(file_path) as f:
        content = f.read()

    tree = ast.parse(content)
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]


def extract_tested_functions(file_path: str, prefix: str = "test_") -> list[str]:
    with open(file_path) as f:
        content = f.read()

    tree = ast.parse(content)
    test_funcs = [
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name.startswith(prefix)
    ]

    # Extract function names being tested from the test function names
    tested_funcs = set()
    for func in test_funcs:
        if func.startswith(prefix):
            tested_funcs.add(func[len(prefix) :])

    # Also look for direct usage of functions in the test file
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and "features" in node.module:
            for name in node.names:
                imports.append(name.name)

    return imports


# Extract all feature functions and test functions
feature_funcs = extract_functions("src/recur_scan/features.py")
tested_funcs = extract_tested_functions("tests/test_features.py")

# Filter out helper functions (those starting with underscore)
public_feature_funcs = [f for f in feature_funcs if not f.startswith("_")]

# Check for untested functions
untested = [f for f in public_feature_funcs if f not in tested_funcs and f != "get_features"]

if untested:
    print("Error: The following functions in features.py don't have corresponding tests:")
    for func in untested:
        print(f"  - {func}")
    sys.exit(1)
else:
    print("All public functions in features.py have corresponding tests!")
    sys.exit(0)
