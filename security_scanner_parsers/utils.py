from requests import post

def send_slack_message(webhook_url, msg):
    message_for_slack= {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": msg,
                }
            }
        ]
    }


    response = post(webhook_url, json=message_for_slack)

    if response.status_code != 200:
        print(f"❌ Failed to send message to Slack: {response.status_code}")

    return response
