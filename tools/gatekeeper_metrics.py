import json
import argparse
import sys
from datetime import datetime

def parse_logs(log_file):
    pr_data = {}
    
    try:
        with open(log_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON: {line}")
                    continue
                
                pr_id = entry.get('pr_id')
                if not pr_id:
                    continue
                
                if pr_id not in pr_data:
                    pr_data[pr_id] = {
                        'commits': [],
                        'checks': [],
                        'merges': []
                    }
                
                # Parse timestamp
                ts_str = entry.get('timestamp')
                try:
                    # ISO 8601 parsing (simple)
                    ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                except ValueError:
                    print(f"Skipping invalid timestamp: {ts_str}")
                    continue

                event = entry.get('event')
                entry['parsed_ts'] = ts
                
                if event == 'commit':
                    pr_data[pr_id]['commits'].append(entry)
                elif event == 'gatekeeper_check':
                    pr_data[pr_id]['checks'].append(entry)
                elif event == 'merge':
                    pr_data[pr_id]['merges'].append(entry)
                    
    except FileNotFoundError:
        print(f"File not found: {log_file}")
        sys.exit(1)

    return pr_data

def calculate_metrics(pr_data):
    time_to_green_list = []
    rejection_counts = []
    
    for pr_id, data in pr_data.items():
        # Sort events by timestamp
        commits = sorted(data['commits'], key=lambda x: x['parsed_ts'])
        checks = sorted(data['checks'], key=lambda x: x['parsed_ts'])
        
        if not commits:
            continue
            
        first_commit_ts = commits[0]['parsed_ts']
        
        # Calculate Rejections
        # A rejection is a gatekeeper_check validation failure
        failures = [c for c in checks if c.get('status') == 'failure']
        rejection_count = len(failures)
        rejection_counts.append(rejection_count)
        
        # Calculate Time-to-Green
        # Time from first commit to first SUCCESSFUL check
        # We assume "Green" means passing all checks
        successes = [c for c in checks if c.get('status') == 'success']
        
        if successes:
            first_success_ts = successes[0]['parsed_ts']
            if first_success_ts > first_commit_ts:
                duration = first_success_ts - first_commit_ts
                # Convert to minutes
                minutes = duration.total_seconds() / 60.0
                time_to_green_list.append(minutes)
    
    return time_to_green_list, rejection_counts

def main():
    parser = argparse.ArgumentParser(description='Gatekeeper Metrics: Analyze Governance Impact')
    parser.add_argument('--log-file', type=str, required=True, help='Path to log file (JSONL)')
    args = parser.parse_args()
    
    pr_data = parse_logs(args.log_file)
    time_to_green, rejections = calculate_metrics(pr_data)
    
    print("## Governance Metrics")
    print(f"Total PRs Analyzed: {len(pr_data)}")
    
    if time_to_green:
        avg_ttg = sum(time_to_green) / len(time_to_green)
        print(f"Average Time-to-Green: {avg_ttg:.2f} minutes")
    else:
        print("Average Time-to-Green: N/A (No successful PRs)")
        
    if rejections:
        total_rejections = sum(rejections)
        avg_rejections = total_rejections / len(rejections)
        print(f"Total Rejections: {total_rejections}")
        print(f"Referrals (Rejections) per PR: {avg_rejections:.2f}")
    else:
        print("Total Rejections: 0")

if __name__ == "__main__":
    main()
