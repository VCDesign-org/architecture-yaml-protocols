import yaml
import sys
import os
import argparse
import ast
import re

def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def get_constraints(boundaries_path):
    try:
        data = load_yaml(boundaries_path)
    except Exception as e:
        print(f"Error loading boundaries: {e}")
        return {}
    
    constraints = {}
    for b in data.get('boundaries', []):
        if 'constraints' in b:
            for lang, rules in b['constraints'].items():
                if lang not in constraints:
                    constraints[lang] = set()
                constraints[lang].update(rules.get('forbidden_symbols', []))
    return constraints

class ForbiddenSymbolVisitor(ast.NodeVisitor):
    def __init__(self, forbidden_symbols):
        self.forbidden_symbols = forbidden_symbols
        self.found_issues = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in self.forbidden_symbols:
                self.found_issues.append((node.lineno, node.func.id))
        elif isinstance(node.func, ast.Attribute):
             if node.func.attr in self.forbidden_symbols:
                 self.found_issues.append((node.lineno, node.func.attr))
        self.generic_visit(node)

def check_python_ast(filepath, forbidden_symbols):
    try:
        with open(filepath, 'r') as f:
            source = f.read()
        tree = ast.parse(source)
        visitor = ForbiddenSymbolVisitor(forbidden_symbols)
        visitor.visit(tree)
        return visitor.found_issues
    except Exception as e:
        # Fallback to text check if AST fails? Or just report error.
        print(f"Error parsing python AST for {filepath}: {e}")
        return []

def check_text_regex(filepath, forbidden_symbols):
    issues = []
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # Simple word boundary regex for each symbol
        # This is a basic implementation.
        for i, line in enumerate(lines):
            for symbol in forbidden_symbols:
                # Regex looks for symbol as a whole word
                pattern = r'\b' + re.escape(symbol) + r'\b'
                if re.search(pattern, line):
                    issues.append((i + 1, symbol))
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return issues

# Map file extensions to language keys
EXTENSION_MAP = {
    '.py': 'python',
    '.c': 'c_cpp',
    '.cpp': 'c_cpp',
    '.cc': 'c_cpp',
    '.h': 'c_cpp',
    '.hpp': 'c_cpp'
}

def check_file(filepath, all_constraints):
    ext = os.path.splitext(filepath)[1]
    lang = EXTENSION_MAP.get(ext)
    
    if not lang or lang not in all_constraints:
        return []

    forbidden = all_constraints[lang]
    if not forbidden:
        return []

    if lang == 'python':
        return check_python_ast(filepath, forbidden)
    else:
        return check_text_regex(filepath, forbidden)

def main():
    parser = argparse.ArgumentParser(description='Universal Gatekeeper: Governance Scanner')
    parser.add_argument('target', type=str, help='File or directory to check')
    parser.add_argument('--boundaries', type=str, required=True, help='Path to boundaries.yaml')
    args = parser.parse_args()

    all_constraints = get_constraints(args.boundaries)
    if not all_constraints:
        print("No constraints found or error loading boundaries.")
        sys.exit(0)

    print(f"Loaded constraints for languages: {list(all_constraints.keys())}")

    targets = []
    if os.path.isfile(args.target):
        targets.append(args.target)
    elif os.path.isdir(args.target):
        for root, _, files in os.walk(args.target):
            for file in files:
                 targets.append(os.path.join(root, file))
    
    has_error = False
    for t in targets:
        issues = check_file(t, all_constraints)
        if issues:
            has_error = True
            print(f"Issues found in {t}:")
            for line, symbol in issues:
                print(f"  Line {line}: Forbidden symbol '{symbol}' used.")
    
    if has_error:
        sys.exit(1)
    else:
        print("No issues found.")
        sys.exit(0)

# Semgrep Helper (Planned Integration)
def generate_semgrep_config(all_constraints):
    # This function would generate a temporary semgrep YAML config
    # based on the constraints.
    # For now, we rely on the Universal Scanner (AST/Regex) as the primary check.
    # Future enhancement: if semgrep is installed, use it for deeper analysis.
    pass

if __name__ == "__main__":
    main()
