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

def get_enforcement_text(check_type, value):
    """
    Returns a descriptive warning based on the check value.
    """
    value = value.lower()
    if value == 'block' or value == 'strict':
        return f"BLOCK (Violations will be rejected by {check_type})"
    elif value == 'warn':
        return f"WARNING (Violations will generate alerts but allow merge)"
    elif value == 'require_todo_update':
        return "REQUIRE_TODO (Must include '## TODO Update' in PR description)"
    elif value == 'require_approval':
        return "REQUIRE_APPROVAL (Must have Architect approval)"
    else:
        return f"{value.upper()}"

def generate_prompt(comp_id, root_dir, profile_name="enforce"):
    # Load Governance Profile
    profile_path = os.path.join(root_dir, 'profile/profile.yaml')
    profile_data = load_yaml(profile_path) if os.path.exists(profile_path) else {}
    profile = profile_data.get('profiles', {}).get(profile_name, {})

    # Load all data
    try:
        comps = load_yaml(os.path.join(root_dir, 'components/components.yaml'))
        contracts = load_yaml(os.path.join(root_dir, 'contracts/vcad.contract.yaml'))
        conns = load_yaml(os.path.join(root_dir, 'connections/connections.yaml'))
        decisions = load_yaml(os.path.join(root_dir, 'decisions/decisions.yaml'))
    except FileNotFoundError as e:
        return f"Error loading YAML files: {e}"

    comp = find_component(comps, comp_id)
    if not comp:
        return f"Component not found: {comp_id}"

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

    # Governance Profile Section
    if profile:
        output.append(f"# GOVERNANCE PROFILE: {profile_name.upper()}")
        output.append(f"> {profile.get('description', '')}")
        output.append("")
        output.append("## Enforcement Rules")
        checks = profile.get('checks', {})
        
        static_rule = get_enforcement_text("Gatekeeper Lint", checks.get('static', 'unknown'))
        runtime_rule = get_enforcement_text("Runtime Gate", checks.get('runtime', 'unknown'))
        process_rule = get_enforcement_text("Process Gate", checks.get('process', 'unknown'))
        
        output.append(f"- **Static Analysis**: {static_rule}")
        output.append(f"- **Runtime Verification**: {runtime_rule}")
        output.append(f"- **Process Gate**: {process_rule}")
        output.append("")

    output.append("## Contracts (MUST/MUST NOT)")
    # Add warnings only if enforcement is Block/Strict
    if profile.get('checks', {}).get('static') in ['block', 'strict']:
        output.append("> [!WARNING]")
        output.append("> These contracts are enforced by `gatekeeper_core.py`. Violations will be automatically rejected.")
        output.append("")
    
    policies = contracts.get('policies', {})
    
    output.append("### Resource Policies")
    for rp in policies.get('resource_policy', []):
        output.append(f"- **{rp['category']}** ({rp.get('level', 'restricted').upper()}): {rp['description']}")

    output.append("")
    output.append("### Side-Effect Policies")
    for sp in policies.get('side_effect_policy', []):
        output.append(f"- **{sp['category']}** ({sp.get('level', 'restricted').upper()}): {sp['description']}")
        
    output.append("")
    output.append("## Connections (Interactions)")
    # Filter connections where this component is 'from' or 'to'?
    # Or just list all linked ones if we had linking logic. 
    # Current component.yaml has 'applies.connections' which mimics old style.
    # For now, let's just dump what's in 'applies' if it exists.
    # But since we removed specific IDs from boundaries, we rely on Categories now.
    # Connections still have IDs in connections.yaml.
    
    c_ids = comp.get('applies', {}).get('connections', [])
    if c_ids:
        for c in conns.get('connections', []):
            if c['id'] in c_ids:
                output.append(f"- **{c['id']}** ({c['protocol']}): {c['description']}")
                output.append(f"  - From: {c['from']} -> To: {c['to']}")

    output.append("")
    output.append("## Verification Contracts")
    
    # Observability
    obs_contracts = contracts.get('contracts', {}).get('observability_contract', [])
    if obs_contracts:
        output.append("### Observability Contract")
        for obs in obs_contracts:
            output.append(f"- Event: **{obs['event']}**")
            output.append(f"  - Required Fields: {obs.get('required_fields')}")
            output.append(f"  - Description: {obs.get('description')}")
            
    return "\n".join(output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate AI Prompt for Component')
    parser.add_argument('component_id', type=str, help='Component ID (e.g., comp-api-01)')
    parser.add_argument('--root', type=str, default='.', help='Root directory of yaml-collection')
    parser.add_argument('--profile', type=str, default='enforce', help='Governance Profile (explore/enforce/lockdown)')
    args = parser.parse_args()

    print(generate_prompt(args.component_id, args.root, profile_name=args.profile))
