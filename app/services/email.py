import os
import smtplib
from email.mime.text import MIMEText

def send_verification_email(email: str, token: str):
    verify_url = f"{os.getenv('FRONTEND_URL')}/verify-email?token={token}"
    msg = MIMEText(f"Click to verify your email: {verify_url}")
    msg["Subject"] = "Verify your email"
    msg["From"] = os.getenv("MAIL_FROM", "no-reply@vipoe.com")
    msg["To"] = email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(os.getenv("MAIL_USER"), os.getenv("MAIL_PASS"))
        server.send_message(msg)