import argparse
import sys
import os
import yaml
import json
import jsonschema

def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def load_logs(log_file):
    try:
        with open(log_file, 'r') as f:
            logs = []
            for line in f:
                line = line.strip()
                if line:
                    logs.append(json.loads(line))
            return logs
    except Exception as e:
        print(f"Error reading log file: {e}")
        return []

def verify_observability(logs, contracts):
    failures = []
    observability_rules = contracts.get('contracts', {}).get('observability_contract', [])
    
    for rule in observability_rules:
        event_name = rule.get('event')
        required_fields = rule.get('required_fields', [])
        
        # Check if event exists at least once (if it's a "Must emit" rule)
        # Note: The current contract doesn't explicitly say "optional" or "required" per request, 
        # but implies "if this event happens, it must have these fields" OR "this event must happen".
        # For v0.2, let's assume if it is in the contract, we expect to see it IF the verify log is for a relevant flow.
        # However, checking "missing event" globally might be too strict for a general log file unless we know the context.
        # Let's focus on: IF event found, MUST have required_fields.
        
        found_count = 0
        for log in logs:
            if log.get('event') == event_name or log.get('message') == event_name:
                found_count += 1
                missing_fields = [f for f in required_fields if f not in log]
                if missing_fields:
                    failures.append(f"Event '{event_name}' missing required fields: {missing_fields}")
        
    return failures

def verify_io_contract(contracts, profile='enforce'):
    failures = []
    io_rules = contracts.get('contracts', {}).get('io_contract', [])
    
    for rule in io_rules:
        if rule.get('type') == 'golden_test':
            expected = rule.get('expected')
            actual = rule.get('actual')
            rule_id = rule.get('id', 'unknown')
            
            if not expected or not actual:
                continue
                
            if not os.path.exists(expected):
                failures.append(f"[{rule_id}] Expected file missing: {expected}")
                continue
            if not os.path.exists(actual):
                failures.append(f"[{rule_id}] Actual file missing: {actual}")
                continue
                
            with open(expected, 'r') as f1, open(actual, 'r') as f2:
                if f1.read() != f2.read():
                    failures.append(f"[{rule_id}] Content mismatch: {expected} vs {actual}")

    return failures

def generate_ai_message(failures):
    """
    Generates a concise rejection message for AI agents.
    """
    msg = "Runtime Verification Failed.\n"
    msg += "The following contract violations were detected:\n"
    for f in failures:
        msg += f"- {f}\n"
    msg += "\nPlease fix the implementation to satisfy the observability and IO contracts."
    return msg

def main():
    parser = argparse.ArgumentParser(description='Runtime Gate v0.2')
    parser.add_argument('--log-file', type=str, help='Path to log file (JSONL)')
    parser.add_argument('--contract', type=str, default='contracts/vcad.contract.yaml', help='Path to contract definition')
    args = parser.parse_args()

    if not os.path.exists(args.contract):
        print(f"Contract file not found: {args.contract}")
        sys.exit(1)

    try:
        contracts = load_yaml(args.contract)
    except Exception as e:
        print(f"Error loading contracts: {e}")
        sys.exit(1)

    all_failures = []

    # 1. Observability Verification
    if args.log_file:
        logs = load_logs(args.log_file)
        if logs:
            obs_failures = verify_observability(logs, contracts)
            all_failures.extend(obs_failures)

    # 2. IO Verification
    io_failures = verify_io_contract(contracts)
    all_failures.extend(io_failures)

    if all_failures:
        print(generate_ai_message(all_failures))
        sys.exit(1)

    print("Runtime Verification Passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
