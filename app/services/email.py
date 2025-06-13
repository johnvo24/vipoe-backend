import os
import smtplib
from email.mime.text import MIMEText
from datetime import timedelta
from app.utils.jwt_utils import create_jwt_token, decode_and_verify_token

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

def create_email_verification_token(email: str) -> str:
    payload = {"sub": email}
    secret_key = os.getenv("SECRET_KEY")
    expires = timedelta(minutes=10)
    return create_jwt_token(payload, secret_key, expires_delta=expires)

def verify_email_verification_token(token: str) -> str:
    secret_key = os.getenv("SECRET_KEY")
    payload = decode_and_verify_token(token, secret_key)
    return payload["sub"]