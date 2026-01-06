from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.security.bcrypt_hashing import hash_password, verify_password
from app.core.security.jwt import create_jwt_token
from app.core.config import settings
from app.models.user import User
from app.modules.auth.schema import UserCreate, UserRead, TokenResponse
from app.services.email_service import (
  create_email_verification_token, 
  send_verification_email,
  verify_email_verification_token
)

def register_user(user: UserCreate, db: Session) -> UserRead:
  # Check existing username and email
  if db.query(User).filter(User.email == user.email).first():
    raise HTTPException(status_code=400, detail="Email already registered")
  if db.query(User).filter(User.username == user.username).first():
    raise HTTPException(status_code=400, detail="Username already exists")
  
  # Generate verification token
  verification_token = create_email_verification_token(user.email)
    
  # Create new user
  new_user = User(
    username=user.username,
    email=user.email,
    password=hash_password(user.password),
    full_name=user.full_name,
    is_verified=False,
    verification_token=verification_token
  )
  
  db.add(new_user)
  db.commit()
  db.refresh(new_user)
  
  # Send verification email
  try:
      send_verification_email(
          email=user.email,
          token=verification_token
      )
  except Exception as e:
      # Log the error but don't fail registration
      print(f"Failed to send verification email: {e}")
  
  return new_user


def verify_email_token(token: str, db: Session) -> UserRead:
    """Verify user email using verification token."""
    try:
        # Verify the token and get email
        email = verify_email_verification_token(token)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
    # Find user by email and verification token
    user = db.query(User).filter(
        User.email == email,
        User.verification_token == token
    ).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token or user not found")
    
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    
    # Mark user as verified
    user.is_verified = True
    user.verification_token = None
    user.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(user)
    
    return user


def login_user(form_data: OAuth2PasswordRequestForm, db: Session) -> TokenResponse:
    """Authenticate user and return access token."""
    # Find user by username or email
    user = db.query(User).filter(
        (User.username == form_data.username) | (User.email == form_data.username)
    ).first()
    
    # Verify credentials
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if email is verified
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified. Please check your email for verification link.")
    
    # Generate access token
    access_token = create_jwt_token(
        payload={"sub": user.username},
        secret_key=settings.SECRET_KEY,
        expires_delta=timedelta(hours=24)  # Extended to 24 hours
    )
    
    # Update last login
    user.last_login = datetime.now(timezone.utc)
    user.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(user)
    
    print(f"User {user.username} logged in at {user.last_login}")
    
    return TokenResponse(access_token=access_token, token_type="bearer")


def resend_verification_email(email: str, db: Session) -> dict:
    """Resend verification email to user."""
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    
    # Generate new verification token
    verification_token = create_email_verification_token(user.email)
    user.verification_token = verification_token
    user.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    
    # Send verification email
    try:
        send_verification_email(
            email=user.email,
            token=verification_token
        )
        return {"message": "Verification email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send verification email: {str(e)}")


def get_user_by_username(username: str, db: Session) -> User:
    """Get user by username for authentication purposes."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_user_by_email(email: str, db: Session) -> User:
    """Get user by email for authentication purposes."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user