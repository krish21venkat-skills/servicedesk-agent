# 

import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import email_sender, rpa_tool

load_dotenv()

app = App(token=os.getenv("SLACK_BOT_TOKEN"))

@app.action("approve_action")
def handle_approve(ack, body, logger):
    ack()  # tells Slack "got it" — required within 3 seconds
    value = body["actions"][0]["value"]
    thread_id, requester_email = value.split("|")

    username = requester_email.split("@")[0]
    result = rpa_tool.reset_password_via_portal(username)
    print(f"[{thread_id}] Approved — action result: {result}")

@app.action("reject_action")
def handle_reject(ack, body, logger):
    ack()
    value = body["actions"][0]["value"]
    thread_id, requester_email = value.split("|")

    email_sender.send_reply(
        requester_email, "Your request",
        "Your request was reviewed and could not be approved at this time."
    )
    print(f"[{thread_id}] Rejected — rejection email sent")

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    print("Listening for Slack button clicks...")
    handler.start()