import argparse
import sys
import os
import re

def parse_pr_description(desc_file):
    if not os.path.exists(desc_file):
        return ""
    with open(desc_file, 'r') as f:
        return f.read()

def get_section_content(description, section_name):
    """
    Extracts content of a section (e.g., '## Impact Analysis').
    Returns stripped content string, or None if section missing or empty.
    """
    # Regex to find ## Section Name, capture until next ## or end of string
    pattern = re.compile(rf'##\s*{re.escape(section_name)}(.*?)(?:##|$)', re.DOTALL | re.IGNORECASE)
    match = pattern.search(description)
    if match:
        content = match.group(1).strip()
        return content if content else None
    return None

def check_protocol_changes(files):
    # Detect if any protocol-defining files (yaml) are changed
    protocol_files = []
    golden_files = []
    boundary_files = []
    
    for f in files:
        if f.endswith('.yaml') or f.endswith('.yml'):
             protocol_files.append(f)
             if "vcad.contract.yaml" in f:
                 boundary_files.append(f) # Treat main contract as boundary-level critical
        elif "examples/golden" in f:
             golden_files.append(f)
            
    return protocol_files, golden_files, boundary_files

def validate_pr(files, desc_file):
    protocol_changes, golden_changes, boundary_changes = check_protocol_changes(files)
    
    if not protocol_changes and not golden_changes:
        print("No protocol or golden file changes detected. Process gate passed.")
        sys.exit(0)

    description = parse_pr_description(desc_file)
    
    # 0. Boundary Changes (Strictest)
    if boundary_changes:
        # Require "Boundary ID" and "Test Evidence" with CONTENT
        boundary_id = get_section_content(description, "Boundary ID")
        test_evidence = get_section_content(description, "Test Evidence")
        
        missing_sections = []
        if not boundary_id:
            missing_sections.append("## Boundary ID")
        if not test_evidence:
            missing_sections.append("## Test Evidence")
            
        if missing_sections:
            print("Protocol Compliance Error: Boundaries modified.")
            print(f"Changed files: {boundary_changes}")
            print(f"Missing required sections (with content) in PR description: {missing_sections}")
            print("Please explicitly state which Boundary ID is modified and provide Test Evidence.")
            sys.exit(1)

    # 1. Check for Protocol Changes (General)
    if protocol_changes:
        # Require "TODO Update" or "Impact Analysis"
        if "## TODO Update" not in description and "## Impact Analysis" not in description:
            print("Protocol Compliance Error: Protocol files changed.")
            print(f"Changed files: {protocol_changes}")
            print("Please add a '## TODO Update' or '## Impact Analysis' section to your PR description")
            print("to acknowledge the impact of these protocol changes.")
            sys.exit(1)

    # 2. Check for Golden File Changes
    if golden_changes:
        # Require "Impact Analysis" AND "Test Evidence" with content
        impact_content = get_section_content(description, "Impact Analysis")
        test_content = get_section_content(description, "Test Evidence")
        
        missing_content = []
        if not impact_content:
            missing_content.append("## Impact Analysis")
        if not test_content:
            missing_content.append("## Test Evidence")

        if missing_content:
            print("Protocol Compliance Error: Golden Files (IO Contract) changed.")
            print(f"Changed files: {golden_changes}")
            print("Changing a golden file implies a change in the System's Observability Contract.")
            print(f"Please add the following sections with actual content (headers alone are not enough): {missing_content}")
            sys.exit(1)

    print("Protocol/Golden changes detected. PR description validation passed.")
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description='Process Gate: Verify PR Compliance')
    parser.add_argument('--files', type=str, required=True, help='Comma-separated list of changed files')
    parser.add_argument('--desc-file', type=str, required=True, help='Path to file containing PR description')
    args = parser.parse_args()
    
    file_list = [f.strip() for f in args.files.split(',')]
    validate_pr(file_list, args.desc_file)

if __name__ == "__main__":
    main()
