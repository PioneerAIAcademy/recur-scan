import ast
import os
import sys
from pathlib import Path

untested_funcs = [
    "get_features",
    "get_new_features",
    "read_labeled_transactions",
    "read_test_transactions",
    "read_unlabeled_transactions",
    "group_transactions",
    "write_transactions",
]


def extract_functions(file_path: str) -> list[str]:
    with open(file_path) as f:
        content = f.read()

    tree = ast.parse(content)
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]


def extract_tested_functions(file_path: str, prefix: str = "test_") -> list[str]:
    if not os.path.exists(file_path):
        return []

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
        if isinstance(node, ast.ImportFrom) and node.module and "recur_scan" in node.module:
            for name in node.names:
                imports.append(name.name)

    return list(tested_funcs) + imports


def check_file_coverage(source_file: str, test_file: str) -> list[str]:
    # Extract all functions and test functions
    source_funcs = extract_functions(source_file)
    tested_funcs = extract_tested_functions(test_file)

    # Filter out helper functions (those starting with underscore)
    public_source_funcs = [f for f in source_funcs if not f.startswith("_") and f not in untested_funcs]

    # Check for untested functions
    untested = [f for f in public_source_funcs if f not in tested_funcs]

    return untested


def main() -> None:
    src_dir = Path("src/recur_scan")
    test_dir = Path("tests")

    all_untested = {}

    # Process each Python file in src/recur_scan
    for src_file in src_dir.glob("**/*.py"):
        # Skip __init__.py files
        if src_file.name == "__init__.py":
            continue

        # Determine the corresponding test file path
        relative_path = src_file.relative_to(src_dir)
        test_file = test_dir / f"test_{relative_path}"

        # Check coverage for this file
        untested = check_file_coverage(str(src_file), str(test_file))

        if untested:
            all_untested[str(src_file)] = untested

    # Report results
    if all_untested:
        print("Error: The following functions don't have corresponding tests:")
        for file_path, funcs in all_untested.items():
            print(f"\nIn {file_path}:")
            for func in funcs:
                print(f"  - {func}")
        sys.exit(1)
    else:
        print("All public functions in src/recur_scan have corresponding tests!")
        sys.exit(0)


if __name__ == "__main__":
    main()
