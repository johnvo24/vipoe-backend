from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth import service
from app.modules.auth.schema import UserCreate, UserRead, TokenResponse

router = APIRouter()

@router.post("/register", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return service.register_user(user, db)

@router.post("/verify-email/{token}", response_model=UserRead)
def verify_email(token: str, db: Session = Depends(get_db)):
    return service.verify_email_token(token, db)

@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return service.login_user(form_data, db)
