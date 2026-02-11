import argparse
import json
import os
import sys
import yaml
from typing import List, Dict, Any

# Ensure we can import from local tools modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.adapters.generic_adapter import GenericAdapter

def load_yaml(path: str) -> Dict[str, Any]:
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def scan_file(filepath: str, contracts: Dict[str, Any]) -> List[Dict[str, Any]]:
    violations = []
    
    # In v0.2, we default to GenericAdapter for everything.
    # Future logic: 
    # ext = os.path.splitext(filepath)[1]
    # if ext == '.py': adapter = PythonAdapter(...)
    # else: adapter = GenericAdapter(...)
    
    adapter = GenericAdapter({})
    
    policies = contracts.get('policies', {})
    
    # Check Resource Policies
    for policy in policies.get('resource_policy', []):
        results = adapter.check_resource_policy(filepath, policy)
        for res in results:
            violations.append({
                "boundary_id": "generic-resource", # Placeholder
                "rule_id": policy['category'],
                "severity": policy.get('level', 'warning').upper(),
                "evidence": f"{os.path.basename(filepath)}:{res['line']}: {res['message']}",
                "fix_hint": f"Consult {policy['category']} policy in vcad.contract.yaml."
            })

    # Check Side Effect Policies
    for policy in policies.get('side_effect_policy', []):
        results = adapter.check_side_effect_policy(filepath, policy)
        for res in results:
            violations.append({
                "boundary_id": "generic-side-effect",
                "rule_id": policy['category'],
                "severity": policy.get('level', 'warning').upper(),
                "evidence": f"{os.path.basename(filepath)}:{res['line']}: {res['message']}",
                "fix_hint": f"Consult {policy['category']} policy in vcad.contract.yaml."
            })
            
    return violations

def main():
    parser = argparse.ArgumentParser(description='VC-AD Gatekeeper Core v0.2')
    parser.add_argument('targets', nargs='+', help='Files or directories to scan')
    parser.add_argument('--contract', default='contracts/vcad.contract.yaml', help='Path to contract definition')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    args = parser.parse_args()
    
    if not os.path.exists(args.contract):
        print(f"Contract file not found: {args.contract}", file=sys.stderr)
        sys.exit(1)

    try:
        contracts = load_yaml(args.contract)
    except Exception as e:
        print(f"Error loading contract: {e}", file=sys.stderr)
        sys.exit(1)
        
    all_violations = []
    
    for target in args.targets:
        if os.path.isfile(target):
            all_violations.extend(scan_file(target, contracts))
        elif os.path.isdir(target):
            for root, _, files in os.walk(target):
                for file in files:
                    # Scan common source files
                    if file.endswith(('.py', '.c', '.cpp', '.cc', '.js', '.ts', '.go', '.rs')):
                        filepath = os.path.join(root, file)
                        all_violations.extend(scan_file(filepath, contracts))

    if args.json:
        print(json.dumps(all_violations, indent=2))
    else:
        if not all_violations:
            print("No violations found.")
        for v in all_violations:
            print(f"[{v['severity']}] {v['rule_id']}: {v['evidence']}")
            
    # Exit 1 if any PROHIBITED violation found
    if any(v['severity'] == 'PROHIBITED' for v in all_violations):
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
