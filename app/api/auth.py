from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.hashing import hash_password
from app.models import User
from app.schemas.user import UserCreate, UserRead
import uuid
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.auth.hashing import verify_password
from app.auth.jwt import create_access_token
from app.services.email import send_verification_email, create_email_verification_token

router = APIRouter()

@router.post("/register", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_db)):
  # Check existing username and email
  if db.query(User).filter(User.email == user.email).first():
    raise HTTPException(status_code=400, detail="Email already registered")
  if db.query(User).filter(User.username == user.username).first():
    raise HTTPException(status_code=400, detail="Username already exists")
  # Generate verification token
  verification_token = create_email_verification_token(user.email)
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
  send_verification_email(
    email=user.email,
    token=verification_token
  )
  return new_user

@router.post("/verify-email/{token}", response_model=UserRead)
def verify_email(token: str, db: Session = Depends(get_db)):
  user = db.query(User).filter(User.verification_token == token).first()
  if not user:
    raise HTTPException(status_code=400, detail="Invalid or expired token")
  user.is_verified = True
  user.verification_token = None
  db.commit()
  db.refresh(user)
  print(user.__dict__)
  return user


# @router.post("/login", response_model=TokenResponse)
# async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#   user = db.query(User).filter(User.username == form_data.username).first()
#   if not user or not verify_password(form_data.password, user.password):
#     raise HTTPException(status_code=401, detail="Invalid credentials")
#   access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(hours=1))
#   return {"access_token": access_token, "token_type": "bearer"}
