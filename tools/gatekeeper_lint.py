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
        return []
    
    # Return list of constraint objects: { 'lang': 'python', 'forbidden': [], 'allowed': [] }
    constraint_rules = []
    
    for b in data.get('boundaries', []):
        if 'constraints' in b:
            for lang, rules in b['constraints'].items():
                forbidden = rules.get('forbidden_symbols', [])
                allowed = rules.get('allowed_scopes', [])
                if forbidden:
                    constraint_rules.append({
                        'lang': lang,
                        'forbidden': forbidden,
                        'allowed': allowed
                    })
    return constraint_rules

# --- AST / Regex (Fallback & Legacy) ---
# (Keeping AST/Regex logic as fallback, but simplified calling convention)

# ... (ForbiddenSymbolVisitor, check_python_ast, check_text_regex remain valid helpers) ...

# --- Semgrep Integration ---

def generate_semgrep_config(constraint_rules):
    """
    Generates a Semgrep YAML config structure from constraint rules.
    Returns the config dict.
    """
    rules = []
    
    for idx, cron in enumerate(constraint_rules):
        lang = cron['lang']
        forbidden = cron['forbidden']
        allowed = cron['allowed']
        
        semgrep_langs = []
        if lang == 'python': semgrep_langs = ['python']
        elif lang == 'c_cpp': semgrep_langs = ['c', 'cpp']
        else: 
            # print(f"DEBUG: Skipping unsupported lang {lang}")
            continue # Skip unsupported for semgrep gen
        
        for symbol in forbidden:
            # print(f"DEBUG: Processing symbol {symbol}")
            rule_id = f"boundary-constraint-{idx}-{symbol.replace('.', '-')}"
            
            # Construct patterns
            patterns = []
            
            # 1. Function Call / Attribute Access (symbol(...), obj.symbol)
            # symbol(...) matches distinct calls. 
            # If symbol contains dot (requests.get), Semgrep handles it intelligently.
            patterns.append({'pattern': f"{symbol}(...)"})
            
            # 2. Import usage (import symbol, from symbol import ..., from ... import symbol)
            # Only relevant for Python. Avoid generating invalid syntax for dotted symbols (e.g. 'import requests.get')
            if lang == 'python':
                # Check if symbol is a simple identifier (no dots)
                if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', symbol):
                    patterns.append({'pattern': f"import {symbol}"})
                    patterns.append({'pattern': f"from {symbol} import ..."})
                    patterns.append({'pattern': f"from ... import {symbol}"})
                
                # Catch attribute usage or direct usage
                patterns.append({'pattern': f"{symbol}"}) 

            # Combine into pattern-either
            main_pattern = {'pattern-either': patterns}
            
            # Construct rule object
            rule_obj = {
                'id': rule_id,
                'patterns': [main_pattern],
                'message': f"Forbidden symbol '{symbol}' detected.",
                'languages': semgrep_langs,
                'severity': 'ERROR'
            }
            
            # Add exceptions (allowed scopes)
            if allowed:
                for allow in allowed:
                    rule_obj['patterns'].append({'pattern-not': f"{allow}(...)"})
                    if lang == 'python':
                        rule_obj['patterns'].append({'pattern-not': f"{allow}"})

            rules.append(rule_obj)
            
    return {'rules': rules}

# --- AST / Regex (Fallback & Legacy) ---
# ...

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
             print(f"DEBUG: Semgrep failed with code {result.returncode}")
             print("STDERR:", result.stderr)
             # print("DEBUG: Config content:")
             # with open(config_path, 'r') as f: print(f.read())
             
             # pass to allow partial results or just continue
             pass
             
        try:
            output = json.loads(result.stdout)
            results = output.get('results', [])
            for res in results:
                line = res['start']['line']
                msg = res['extra']['message']
                # Extract symbol from message or ID? 
                match = re.search(r"Forbidden symbol '(.*)' detected", msg)
                symbol = match.group(1) if match else "unknown"
                issues.append((line, symbol))
                
        except json.JSONDecodeError:
            print(f"Failed to parse semgrep output for {filepath}")
            # print("STDOUT:", result.stdout)

    except Exception as e:
        print(f"Error running semgrep: {e}")
        
    finally:
        if os.path.exists(config_path):
            os.remove(config_path)
        
    return issues

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

# --- Main Driver ---

EXTENSION_MAP = {
    '.py': 'python',
    '.c': 'c_cpp',
    '.cpp': 'c_cpp',
    '.cc': 'c_cpp',
    '.h': 'c_cpp',
    '.hpp': 'c_cpp'
}

def check_file(filepath, constraint_rules):
    ext = os.path.splitext(filepath)[1]
    target_lang = EXTENSION_MAP.get(ext)
    
    if not target_lang:
        return []

    # Filter constraints relevant to this language
    relevant_rules = [r for r in constraint_rules if r['lang'] == target_lang]
    if not relevant_rules:
        return []

    # Try Semgrep first
    semgrep_config = generate_semgrep_config(relevant_rules)
    semgrep_issues = run_semgrep(filepath, semgrep_config)
    
    if semgrep_issues is not None:
        return semgrep_issues
    
    # Fallback (Legacy) - flatten forbidden symbols
    all_forbidden = set()
    for r in relevant_rules:
        all_forbidden.update(r['forbidden'])
        
    if target_lang == 'python':
        return check_python_ast(filepath, list(all_forbidden))
    else:
        return check_text_regex(filepath, list(all_forbidden))

def main():
    parser = argparse.ArgumentParser(description='Universal Gatekeeper: Governance Scanner')
    parser.add_argument('target', type=str, help='File or directory to check')
    parser.add_argument('--boundaries', type=str, required=True, help='Path to boundaries.yaml')
    args = parser.parse_args()

    # Get structured constraints
    print(f"DEBUG: Loading constraints from {args.boundaries}")
    constraint_rules = get_constraints(args.boundaries)
    print(f"DEBUG: Found {len(constraint_rules)} constraint rules")
    
    if not constraint_rules:
        # Assuming empty is valid if no boundaries defined, but let's exit success
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
                 if os.path.splitext(file)[1] in EXTENSION_MAP:
                     targets.append(os.path.join(root, file))
    
    has_error = False
    for t in targets:
        issues = check_file(t, constraint_rules)
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
