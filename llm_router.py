import ollama, json, os

INTENT_SCHEMA_PROMPT = """You are a service desk triage assistant.
Classify the user's email into JSON with fields:
- intent: one of [leave_policy, password_reset, vpn_troubleshooting,
  access_request, bug_report, billing_query, hardware_request,
  general_question, escalation_needed]
- summary: one-sentence summary of the request
- entities: key facts extracted (system name, account id, urgency, etc.)
- confidence: 0-1 float

Use general_question for anything that doesn't clearly fit the other categories,
including automated notifications, confirmations, or messages that aren't
actually a request for help.

Confidence scoring rules — follow these strictly:
- If the message names a specific system, error code, or concrete symptom, confidence should be 0.7-1.0.
- If the message is vague, references "same as before" or "again" without stating what the issue actually is,
  or contains no specific system name, error code, or actionable detail, confidence MUST be below 0.5.

Respond ONLY with valid JSON, no preamble."""


def classify_email(subject, body):
    resp = ollama.chat(
        model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
        messages=[
            {"role": "system", "content": INTENT_SCHEMA_PROMPT},
            {"role": "user", "content": f"Subject: {subject}\n\nBody: {body}"}
        ],
        format="json"
    )
    raw = resp["message"]["content"]
    print("Log: LLM response ====> ", raw)  # keep for now while testing — remove or swap for logging.debug later

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Model returned malformed/unparseable JSON — fail safe into escalation
        # instead of crashing classify_node and taking down the whole graph run.
        return {
            "intent": "escalation_needed",
            "summary": "Could not parse LLM classification output",
            "entities": {},
            "confidence": 0.0
        }


"""if __name__ == "__main__":
    test_cases = [
        ("Leave question", "How many casual leave days do I get per year?"),
        ("VPN issue", "My VPN keeps disconnecting after 5 minutes with error 809"),
        ("Password reset", "I can't log into the VPN, please reset my password"),
        ("Google notification",
         "Google Account recovered successfully krish.upskill@gmail.com Welcome back to "
         "your account. If you suspect you were locked out of your account because of "
         "changes made by someone else, you should review and protect your account."),
        ("Issue", "It's broken again, same as before, can you just fix it"),
    ]
    for subject, body in test_cases:
        result = classify_email(subject, body)
        print(f"{subject!r} -> intent={result['intent']}, confidence={result['confidence']}")"""