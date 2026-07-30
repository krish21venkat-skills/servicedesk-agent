import smtplib, os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send_reply(to_addr, subject, body, in_reply_to=None):
    msg = MIMEText(body)
    msg["Subject"] = f"Re: {subject}"
    msg["From"] = os.getenv("EMAIL_ADDRESS")
    msg["To"] = to_addr
    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
    print("Send email to === ", to_addr)
    with smtplib.SMTP_SSL(os.getenv("SMTP_SERVER"), 465) as server:
        server.login(os.getenv("EMAIL_ADDRESS"), os.getenv("EMAIL_APP_PASSWORD"))
        server.send_message(msg)

"""if __name__ == "__main__":
    send_reply(
        to_addr=os.getenv("EMAIL_ADDRESS"),  # send to yourself for the first test
        subject="Test ticket",
        body="This is a test reply from send_reply()."
    )
    print("Email sent.")"""