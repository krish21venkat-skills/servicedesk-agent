
import imaplib, email, os
from email.header import decode_header
from dotenv import load_dotenv
load_dotenv()

def fetch_unread_emails(limit=5):
    mail = imaplib.IMAP4_SSL(os.getenv("IMAP_SERVER"))
    mail.login(os.getenv("EMAIL_ADDRESS"), os.getenv("EMAIL_APP_PASSWORD"))
    mail.select("inbox")
    _, ids = mail.search(None, "UNSEEN")
    results = []
    for eid in ids[0].split()[:limit]:
        _, data = mail.fetch(eid, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])
        subject = decode_header(msg["Subject"])[0][0]
        subject = subject.decode() if isinstance(subject, bytes) else subject
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")
        
        print("Sub: ", subject)
        results.append({
            "id": eid.decode(), "from": msg["From"],
            "subject": subject, "body": body, "thread_id": msg["Message-ID"]
        })
    mail.logout()
    #print(results)
    return results
#fetch_unread_emails()