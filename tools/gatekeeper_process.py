import argparse
import sys
import os
import re

PROTOCOL_DIRS = [
    'boundaries',
    'closures',
    'components',
    'connections',
    'decisions',
    'profile'
]

def is_protocol_file(filepath):
    # Check if file is in one of the protocol directories and is a YAML file
    parts = filepath.split(os.sep)
    if len(parts) > 1 and parts[0] in PROTOCOL_DIRS and filepath.endswith('.yaml'):
        return True
    return False

def check_process_gate(changed_files, pr_description):
    # 1. Identify if any protocol file is modified
    protocol_changed = False
    for f in changed_files:
        if is_protocol_file(f.strip()):
            protocol_changed = True
            break
    
    if not protocol_changed:
        print("No protocol changes detected. Process gate passed.")
        return True

    # 2. If protocol changed, check PR description for TODO update section
    # We look for something like "## TODO Update" or "## Impact Analysis"
    # Case insensitive
    if not pr_description:
         print("Protocol Compliance Error: Protocol files changed but PR description is empty.")
         return False

    required_section_pattern = r'#+\s*(todo|update|impact)'
    if re.search(required_section_pattern, pr_description, re.IGNORECASE):
        print("Protocol changes detected. PR description validation passed (TODO section found).")
        return True
    else:
        print("Protocol Compliance Error: Protocol files changed.")
        print("Please add a '## TODO Update' or '## Impact Analysis' section to your PR description")
        print("to acknowledge the impact of these protocol changes.")
        return False

def main():
    parser = argparse.ArgumentParser(description='Gatekeeper Process: Verify PR Process Compliance')
    parser.add_argument('--files', type=str, help='Comma separated list of changed files')
    parser.add_argument('--desc-file', type=str, help='Path to file containing PR description')
    args = parser.parse_args()

    files = []
    if args.files:
        files = args.files.split(',')
    
    description = ""
    if args.desc_file:
        try:
            with open(args.desc_file, 'r') as f:
                description = f.read()
        except Exception as e:
            print(f"Error reading description file: {e}")
            sys.exit(1)

    if check_process_gate(files, description):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
