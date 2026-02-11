import yaml
import sys
import os
import argparse

def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def find_component(components_data, comp_id):
    for c in components_data.get('components', []):
        if c['id'] == comp_id:
            return c
    return None

def get_items_by_ids(data, ids, kind_key='boundaries'):
    # data is like { 'boundaries': [...] }
    items = []
    source_list = data.get(kind_key, [])
    for item_id in ids:
        found = next((x for x in source_list if x['id'] == item_id), None)
        if found:
            items.append(found)
    return items

def generate_prompt(comp_id, root_dir):
    # Load all data
    try:
        comps = load_yaml(os.path.join(root_dir, 'components/components.yaml'))
        bounds = load_yaml(os.path.join(root_dir, 'boundaries/boundaries.yaml'))
        conns = load_yaml(os.path.join(root_dir, 'connections/connections.yaml'))
        closer = load_yaml(os.path.join(root_dir, 'closures/closures.yaml'))
        decisions = load_yaml(os.path.join(root_dir, 'decisions/decisions.yaml'))
    except FileNotFoundError as e:
        return f"Error loading YAML files: {e}"

    comp = find_component(comps, comp_id)
    if not comp:
        return f"Component not found: {comp_id}"

    # Resolve links
    applies = comp.get('applies', {})
    b_ids = applies.get('boundaries', [])
    c_ids = applies.get('connections', [])
    cl_ids = applies.get('closures', [])
    
    # Contracts are now merged into boundaries/closures in components.yaml
    
    my_bounds = get_items_by_ids(bounds, b_ids, 'boundaries')
    my_conns = get_items_by_ids(conns, c_ids, 'connections')
    my_closures = get_items_by_ids(closer, cl_ids, 'closures')
    # Pre-fetch decision map for O(1) loop
    decision_map = {d['id']: d for d in decisions.get('decisions', [])}

    # Build Prompt
    output = []
    output.append(f"You are implementing code for the component: **{comp['name']}** ({comp['id']})\n")
    output.append(f"## Context")
    output.append(f"{comp.get('description', '')}\n")
    
    output.append("## Scope (Paths)")
    for p in comp['paths']['include']:
        output.append(f"- Include: `{p}`")
    for p in comp['paths']['exclude']:
        output.append(f"- Exclude: `{p}`")
    output.append("")

    output.append("## Boundaries (MUST/MUST NOT)")
    output.append("> [!WARNING]")
    output.append("> These boundaries are enforced by `gatekeeper_lint.py`. Violations will be automatically rejected.")
    output.append("")
    
    if not my_bounds:
        output.append("None")
    for b in my_bounds:
        output.append(f"- **{b['name']}**: {b['description']}")
        if 'constraints' in b:
             constraints = b['constraints']
             for lang, rules in constraints.items():
                 output.append(f"  - [CONSTRAINT] {lang}: Forbidden {rules.get('forbidden_symbols', [])}")
        
        # Include Decision context if available
        derived_ids = b.get('derived_from_decisions', [])
        for did in derived_ids:
            if did in decision_map:
                d_desc = decision_map[did].get('description', 'No description')
                output.append(f"  - Decision ({did}): {d_desc}")
    output.append("")

    output.append("## Connections (Interactions)")
    if not my_conns:
        output.append("None")
    for c in my_conns:
        output.append(f"- **{c['id']}** ({c['protocol']}): {c['description']}")
        output.append(f"  - From: {c['from']} -> To: {c['to']}")
    output.append("")

    output.append("## Closures (Failure Handling)")
    if not my_closures:
        output.append("None")
    for cl in my_closures:
        output.append(f"- **{cl['id']}**: {cl['description']}")
        output.append(f"  - Handling: {cl['handling']}")
        if 'verification' in cl:
            v = cl['verification']
            output.append(f"  - [VERIFICATION] Exit Code: {v.get('exit_code')}")
            output.append(f"  - [VERIFICATION] Logs: {v.get('mandatory_log_events', [])}")
            output.append(f"  - [VERIFICATION] Test: `{v.get('test_command')}`")
    
    return "\n".join(output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate AI Prompt for Component')
    parser.add_argument('component_id', type=str, help='Component ID (e.g., comp-api-01)')
    parser.add_argument('--root', type=str, default='.', help='Root directory of yaml-collection')
    args = parser.parse_args()

    print(generate_prompt(args.component_id, args.root))
