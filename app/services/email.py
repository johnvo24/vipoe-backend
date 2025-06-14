import smtplib
from email.mime.text import MIMEText
from datetime import timedelta
from app.utils.jwt_utils import create_jwt_token, decode_and_verify_token
from app.core.config import settings

def send_verification_email(email: str, token: str):
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    msg = MIMEText(f"Click to verify your email: {verify_url}")
    msg["Subject"] = "Verify your email"
    msg["From"] = settings.MAIL_USER
    msg["To"] = email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(settings.MAIL_USER, settings.MAIL_PASS)
        server.send_message(msg)

def create_email_verification_token(email: str) -> str:
    payload = {"sub": email}
    secret_key = settings.SECRET_KEY
    expires = timedelta(minutes=10)
    return create_jwt_token(payload, secret_key, expires_delta=expires)

def verify_email_verification_token(token: str) -> str:
    secret_key = settings.SECRET_KEY
    payload = decode_and_verify_token(token, secret_key)
    return payload["sub"]