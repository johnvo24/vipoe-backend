from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy .orm import Session
from app.database import get_db
from app.models import User
from app.utils.jwt_utils import decode_and_verify_token
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(
  request: Request, 
  db: Session = Depends(get_db),
  token_from_header: Optional[str] = Depends(oauth2_scheme)
):
  token = token_from_header or request.cookies.get("vipoe_access_token")
  if not token:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Not authenticated",
    )
  
  try:
    payload = decode_and_verify_token(token, settings.SECRET_KEY)
    username: str = payload.get("sub")
    if not username:
      raise HTTPException(status_code=401, detail="Invalid token") 
  except JWTError:
    raise HTTPException(status_code=401, detail="Invalid token")
  
  user = db.query(User).filter(User.username == username).first()
  if not user:
    raise HTTPException(status_code=401, detail="User not found")
  
  return user