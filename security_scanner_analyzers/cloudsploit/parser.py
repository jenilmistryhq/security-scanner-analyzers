from collections import Counter
from security_scanner_analyzers.utils import load_json, generate_report, send_to_slack

def cloudsploit_count_field(data, field_name, skip_values=["ok"]):
    count_dict = {}
    for item in data:
        value = item.get(field_name, "unknown").lower()
        if skip_values and value in skip_values:
            continue
        count_dict[value] = count_dict.get(value, 0) + 1
    return count_dict

def summarize_failures(data):
    """
    Analyzes the JSON to find what actually failed.
    Returns a formatted string for Slack.
    """
    # Filter for only failed items
    failed_items = [item for item in data if item.get("status", "").lower() == "fail"]
    
    if not failed_items:
        return "\n:white_check_mark: No failures detected."

    # 1. Group by Category (e.g., IAM, EC2, S3)
    categories = [item.get("category", "Unknown") for item in failed_items]
    cat_counts = Counter(categories)
    
    # 2. Get Unique Failing Plugins (deduplicated)
    failing_plugins = {item.get("plugin", "Unknown") for item in failed_items}

    # Build the text report
    details = []
    details.append("\n*--- :mag: Failure Analysis ---*")
    
    # Add Category Breakdown
    details.append("*Failures by Category:*")
    for cat, count in cat_counts.most_common():
        details.append(f"• {cat}: {count}")

    # Add specific failing rules (UNLIMITED LIST)
    details.append(f"\n*Unique Failing Rules ({len(failing_plugins)}):*")
    sorted_plugins = sorted(list(failing_plugins))
    
    # Loop through ALL plugins without slicing [:15]
    plugin_list = "\n".join([f"• {p}" for p in sorted_plugins])
    details.append(plugin_list)

    return "\n".join(details)

def main(file_path, slack_url=None):
    data = load_json(file_path)
    
    # 1. Get the basic stats
    status_count = cloudsploit_count_field(data, "status")
    base_report = generate_report(":cloud: CloudSploit Status Report", status_count)
    
    # 2. Generate the detailed breakdown
    detailed_analysis = summarize_failures(data)
    
    # 3. Combine them
    full_report = f"{base_report}\n{detailed_analysis}"

    # 4. Decide: Send to Slack OR Print to Console
    if slack_url:
        # Slack has a message size limit (~4000 chars), but usually handles lists well.
        # If it fails to send, it might be too long.
        send_to_slack(slack_url, full_report)
        print("Success: Report sent to Slack.")
    else:
        # Local Preview
        print("\n" + "="*40)
        print("   LOCAL PREVIEW (NOT SENT TO SLACK)")
        print("="*40)
        print(full_report)
        print("="*40 + "\n")