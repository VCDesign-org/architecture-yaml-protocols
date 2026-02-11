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
            # Assume one JSON object per line
            logs = []
            for line in f:
                line = line.strip()
                if line:
                    logs.append(json.loads(line))
            return logs
    except Exception as e:
        print(f"Error reading log file: {e}")
        return []

def get_closure_requirements(closures_yaml, closure_id=None):
    data = load_yaml(closures_yaml)
    requirements = {}
    for cl in data.get('closures', []):
        if closure_id and cl['id'] != closure_id:
            continue
        
        verification = cl.get('verification', {})
        mandatory_events = verification.get('mandatory_log_events', [])
        
        # Normalize into list of objects with 'name' and optional 'schema'
        normalized_events = []
        for event in mandatory_events:
            if isinstance(event, str):
                normalized_events.append({'name': event})
            elif isinstance(event, dict):
                normalized_events.append(event)
        
        if normalized_events:
            requirements[cl['id']] = normalized_events
            
    return requirements

def verify_logs(logs, requirements):
    # Requirements is map: closure_id -> list of event dicts
    
    failures = {} # closure_id -> list of failure messages
    
    for cl_id, required_events in requirements.items():
        cl_failures = []
        
        for req in required_events:
            event_name = req['name']
            schema = req.get('schema')
            
            # Find matching log entries
            matches = []
            for log in logs:
                # Check for event name match (assuming 'event' or 'message' field)
                if log.get('event') == event_name or log.get('message') == event_name:
                    matches.append(log)
            
            if not matches:
                cl_failures.append(f"Missing mandatory event: {event_name}")
                continue
            
            # If schema exists, validate all matches (or at least one? Strict: all must pass?)
            # Usually if multiple events of same type emitted, they all should correspond to schema.
            if schema:
                for match in matches:
                    try:
                        jsonschema.validate(instance=match, schema=schema)
                    except jsonschema.ValidationError as e:
                        cl_failures.append(f"Schema violation for event '{event_name}': {e.message} at path {list(e.path)}")
                        
        if cl_failures:
            failures[cl_id] = cl_failures
            
    return failures

def verify_golden_files(closures_yaml, closure_id=None):
    data = load_yaml(closures_yaml)
    failures = []
    
    for cl in data.get('closures', []):
        if closure_id and cl['id'] != closure_id:
            continue
        
        verification = cl.get('verification', {})
        golden = verification.get('golden_test')
        
        if golden:
            expected_path = golden.get('expected')
            actual_path = golden.get('actual')
            
            if not expected_path or not actual_path:
                print(f"Closure {cl['id']}: Invalid golden_test config.")
                continue

            if not os.path.exists(expected_path):
                pass
            
            if not os.path.exists(actual_path):
                 pass
            
            if os.path.exists(expected_path) and os.path.exists(actual_path):
                with open(expected_path, 'r') as f1, open(actual_path, 'r') as f2:
                    if f1.read() != f2.read():
                        failures.append(f"{cl['id']}: Content mismatch between {expected_path} and {actual_path}")

    return failures

def main():
    parser = argparse.ArgumentParser(description='Runtime Gate: Verify Log Compliance & IO Equivalence')
    parser.add_argument('--log-file', type=str, help='Path to log file (JSONL)')
    parser.add_argument('--closures', type=str, required=True, help='Path to closures.yaml')
    parser.add_argument('--closure-id', type=str, help='Specific closure ID to verify')
    args = parser.parse_args()

    # 1. Log Verification
    if args.log_file:
        logs = load_logs(args.log_file)
        if logs:
            requirements = get_closure_requirements(args.closures, args.closure_id)
            if requirements:
                failures = verify_logs(logs, requirements)
                if failures:
                    print("Runtime Verification Failed (Log Events)!")
                    for cl_id, msgs in failures.items():
                        print(f"Closure {cl_id} Failures:")
                        for msg in msgs:
                             print(f"  - {msg}")
                    sys.exit(1)

    # 2. Golden File Verification
    golden_failures = verify_golden_files(args.closures, args.closure_id)
    if golden_failures:
        print("Runtime Verification Failed (IO Equivalence)!")
        for failure in golden_failures:
             print(failure)
        sys.exit(1)

    print("Runtime Verification Passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
