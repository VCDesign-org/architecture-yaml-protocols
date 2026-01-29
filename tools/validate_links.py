import yaml
import os
import sys
import argparse

def load_yaml(path):
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"File not found: {path}")
        return None
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML file {path}: {exc}")
        return None

def validate_integrity(root_dir):
    errors = []
    
    # Load all data
    comps_data = load_yaml(os.path.join(root_dir, 'components/components.yaml'))
    bounds_data = load_yaml(os.path.join(root_dir, 'boundaries/boundaries.yaml'))
    conns_data = load_yaml(os.path.join(root_dir, 'connections/connections.yaml'))
    closures_data = load_yaml(os.path.join(root_dir, 'closures/closures.yaml'))
    decisions_data = load_yaml(os.path.join(root_dir, 'decisions/decisions.yaml'))

    if not all([comps_data, bounds_data, conns_data, closures_data, decisions_data]):
        return ["Failed to load one or more YAML files."]

    # Index IDs
    # boundaries
    bound_ids = {b['id'] for b in bounds_data.get('boundaries', [])}
    # connections
    conn_ids = {c['id'] for c in conns_data.get('connections', [])}
    # closures
    closure_ids = {cl['id'] for cl in closures_data.get('closures', [])}
    # decisions
    decision_ids = {d['id'] for d in decisions_data.get('decisions', [])}

    # 1. Validate Components references
    for comp in comps_data.get('components', []):
        cid = comp['id']
        applies = comp.get('applies', {})
        
        # Check boundaries
        for b_id in applies.get('boundaries', []):
            if b_id not in bound_ids:
                errors.append(f"[Component {cid}] References missing Boundary: {b_id}")
        
        # Check connections
        for c_id in applies.get('connections', []):
            if c_id not in conn_ids:
                errors.append(f"[Component {cid}] References missing Connection: {c_id}")
        
        # Check closures
        for cl_id in applies.get('closures', []):
            if cl_id not in closure_ids:
                errors.append(f"[Component {cid}] References missing Closure: {cl_id}")

    # 2. Validate Boundaries -> Decisions references
    for bound in bounds_data.get('boundaries', []):
        bid = bound['id']
        derived = bound.get('derived_from_decisions', [])
        for did in derived:
            if did not in decision_ids:
                errors.append(f"[Boundary {bid}] References missing Decision: {did}")

    return errors

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Validate YAML Referential Integrity')
    parser.add_argument('--root', type=str, default='.', help='Root directory of yaml-collection')
    args = parser.parse_args()

    validation_errors = validate_integrity(args.root)
    
    if validation_errors:
        print("Validation Broken:")
        for e in validation_errors:
            print(f"- {e}")
        sys.exit(1)
    else:
        print("Validation Passed: All links are valid.")
        sys.exit(0)
