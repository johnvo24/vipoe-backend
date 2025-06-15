from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy .orm import Session
from app.database import get_db
from app.models import User
from app.utils.jwt_utils import decode_and_verify_token
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
  )
  try:
    payload = decode_and_verify_token(token, settings.SECRET_KEY)
    username: str = payload.get("sub")
    if username is None:
      raise credentials_exception 
  except JWTError:
    raise credentials_exception
  
  user = db.query(User).filter(User.username == username).first()
  if user is None:
    raise credentials_exception
  return user