# escalation.py
import os
from dotenv import load_dotenv
from slack_sdk import WebClient

load_dotenv()
client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

def escalate_to_slack_with_buttons(summary, thread_id, reason, requester_email):
    client.chat_postMessage(
        channel=os.getenv("SLACK_CHANNEL_ID"),
        text="Escalation needed",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (f"🚨 *Escalation needed*\n"
                             f"Thread: {thread_id}\nReason: {reason}\nSummary: {summary}")
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Approve"},
                        "style": "primary",
                        "value": f"{thread_id}|{requester_email}",
                        "action_id": "approve_action"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Reject"},
                        "style": "danger",
                        "value": f"{thread_id}|{requester_email}",
                        "action_id": "reject_action"
                    }
                ]
            }
        ]
    )