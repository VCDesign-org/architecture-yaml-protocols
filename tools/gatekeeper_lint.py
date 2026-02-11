import yaml
import sys
import os
import argparse
import ast
import re
import subprocess
import tempfile
import json
import shutil

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

# --- AST / Regex (Fallback & Legacy) ---

class ForbiddenSymbolVisitor(ast.NodeVisitor):
    def __init__(self, forbidden_symbols):
        self.forbidden_symbols = forbidden_symbols
        self.found_issues = []

    def visit_Call(self, node):
        # Check function calls: print(), requests.get()
        if isinstance(node.func, ast.Name):
            if node.func.id in self.forbidden_symbols:
                self.found_issues.append((node.lineno, node.func.id))
        elif isinstance(node.func, ast.Attribute):
             # For attr calls like requests.get, we check the attribute name 'get'
             # OR the full 'requests.get' if checking that way?
             # Current logic checks 'attr'.
             # Semgrep is better for 'requests.get'.
             if node.func.attr in self.forbidden_symbols:
                 self.found_issues.append((node.lineno, node.func.attr))
             
             # Also check full name if possible? 
             # AST full name reconstruction is complex, relying on simple match for now.
             
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
        print(f"Error parsing python AST for {filepath}: {e}")
        return []

def check_text_regex(filepath, forbidden_symbols):
    issues = []
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            for symbol in forbidden_symbols:
                pattern = r'\b' + re.escape(symbol) + r'\b'
                if re.search(pattern, line):
                    issues.append((i + 1, symbol))
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return issues

# --- Semgrep Integration ---

def generate_semgrep_config(constraints):
    """
    Generates a Semgrep YAML config structure from constraints.
    Returns the config dict.
    """
    rules = []
    
    # Python Rules
    if 'python' in constraints:
        for symbol in constraints['python']:
            # Create a rule for each forbidden symbol
            # Heuristic: if symbol has a dot, use it as is (e.g. requests.get)
            # If no dot, it might be a function call or pattern.
            
            rule_id = f"forbidden-python-{symbol.replace('.', '-')}"
            pattern = f"{symbol}(...)"
            
            rules.append({
                'id': rule_id,
                'patterns': [{'pattern': pattern}],
                'message': f"Forbidden symbol '{symbol}' detected.",
                'languages': ['python'],
                'severity': 'ERROR'
            })

    # C/C++ Rules
    if 'c_cpp' in constraints:
        for symbol in constraints['c_cpp']:
            rule_id = f"forbidden-cpp-{symbol}"
            pattern = f"{symbol}(...)"
            
            rules.append({
                'id': rule_id,
                'patterns': [{'pattern': pattern}],
                'message': f"Forbidden symbol '{symbol}' detected.",
                'languages': ['c', 'cpp'],
                'severity': 'ERROR'
            })
            
    return {'rules': rules}

def run_semgrep(filepath, config_dict):
    """
    Runs semgrep on the filepath using the provided config dict.
    Returns list of (line, symbol) tuples.
    """
    # Check if semgrep is installed
    if not shutil.which('semgrep'):
        return None 

    issues = []
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_config:
        yaml.dump(config_dict, tmp_config)
        config_path = tmp_config.name
        
    try:
        # Run semgrep with JSON output
        cmd = ['semgrep', '--config', config_path, '--json', filepath]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0 and result.returncode != 1: 
             # semgrep exit code 0=ok, 1=findings (depending on version, strictness)
             # actually usually 0 even with findings unless --error
             # We parse JSON anyway.
             pass
             
        try:
            output = json.loads(result.stdout)
            results = output.get('results', [])
            for res in results:
                line = res['start']['line']
                msg = res['extra']['message']
                # Extract symbol from message or ID? 
                # Message is "Forbidden symbol 'X' detected."
                match = re.search(r"Forbidden symbol '(.*)' detected", msg)
                symbol = match.group(1) if match else "unknown"
                issues.append((line, symbol))
                
        except json.JSONDecodeError:
            print(f"Failed to parse semgrep output for {filepath}")

    except Exception as e:
        print(f"Error running semgrep: {e}")
        
    finally:
        os.remove(config_path)
        
    return issues

# --- Main Driver ---

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

    # Try Semgrep first
    semgrep_config = generate_semgrep_config(all_constraints)
    semgrep_issues = run_semgrep(filepath, semgrep_config)
    
    if semgrep_issues is not None:
        return semgrep_issues
    
    # Fallback
    forbidden = all_constraints[lang]
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
        sys.exit(0)

    # Check for target existence
    if not os.path.exists(args.target):
        print(f"Target not found: {args.target}")
        sys.exit(1)

    targets = []
    if os.path.isfile(args.target):
        targets.append(args.target)
    elif os.path.isdir(args.target):
        for root, _, files in os.walk(args.target):
            for file in files:
                # filter by supported extensions?
                 if os.path.splitext(file)[1] in EXTENSION_MAP:
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

if __name__ == "__main__":
    main()
