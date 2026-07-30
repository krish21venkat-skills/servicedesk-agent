from escalation import escalate_to_slack_with_buttons

escalate_to_slack_with_buttons(
    summary="User locked out of VPN, password reset failed twice",
    thread_id="thread-001",
    reason="tool call failed twice",
    requester_email="you@yourtestaccount.com"
)