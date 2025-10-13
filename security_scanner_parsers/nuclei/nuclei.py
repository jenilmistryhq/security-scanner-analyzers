from argparse import ArgumentParser
from datetime import datetime
from json import load, JSONDecodeError
from os.path import exists

from security_scanner_parsers.utils import send_slack_message

def main():
    # Argument parser setup
    parser = ArgumentParser(
        description="Scan a JSON file and count severity levels."
    )
    parser.add_argument(
        "--file", "-f",
        required=True,
        dest="file",
        help="Path to the JSON file to scan."
    )
    parser.add_argument(
        "--slack-webhook", "-s",
        required=True,
        dest="slack_webhook",
        help="Slack webhook URL to send the report."
    )
    args = parser.parse_args()


    # Validate file path
    if not exists(args.file):
        print(f"❌ File not found: {args.file}")
        exit(1)

    # Load JSON data
    try:
        with open(args.file, "r", encoding="utf-8") as f:
            data = load(f)
    except JSONDecodeError:
        print("❌ Error: Invalid JSON format.")
        exit(1)

    # Count severities
    severity_count = {}
    for item in data:
        severity = item.get("info", {}).get("severity", "unknown").lower()
        severity_count[severity] = severity_count.get(severity, 0) + 1

    # Current Timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Display results
    report_lines= [f"*📊 Nuclei Scan Report*\nGenerated at: {current_time}\n", "-" * 40]
    for level, count in severity_count.items():
        report_lines.append(f"{level.capitalize():<10}: {count}")
    report_lines.append("-" * 40)

    print(report_lines) # Printing locally for verification

    
    report = "\n".join(report_lines)
    response = send_slack_message(args.slack_webhook, report)
    if response.status_code == 200:
        print("✅ Report sent to Slack successfully.")
    else:
        print("❌ Failed to send report to Slack.")


if __name__ == "__main__":
    main()
