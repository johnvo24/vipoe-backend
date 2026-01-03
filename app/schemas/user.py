from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator
import re

class UserCreate(BaseModel):
  full_name: str = Field(..., min_length=1, max_length=100)
  username: str = Field(..., min_length=6, max_length=16, pattern=r"^[a-zA-Z0-9_]+$")
  email: EmailStr
  password: str = Field(..., min_length=8, max_length=100)

  @validator("full_name", "username", pre=True)
  def strip_whitespace(cls, v):
    return v.strip() if isinstance(v, str) else v

  @validator("password")
  def validate_password(cls, v):
    pattern = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$")
    if not pattern.match(v):
      raise ValueError("Password must contain at least one uppercase, one lowercase, one number, and one special character.")
    return v

class UserRead(BaseModel):
  id: int
  full_name: str
  username: str
  email: EmailStr
  avt_url: Optional[str] = None
  bio: Optional[str] = None
  phone: Optional[str] = None
  location: Optional[str] = None
  date_of_birth: Optional[datetime] = None
  is_verified: bool
  role: str
  created_at: datetime
  updated_at: datetime
  last_login: Optional[datetime] = None

  class Config:
    orm_mode = True

class UserUpdate(BaseModel):
  full_name: Optional[str] = Field(None, min_length=1, max_length=100)
  # email: Optional[EmailStr] = None
  # avt_url: Optional[str] = None
  bio: Optional[str] = None
  phone: Optional[str] = None
  location: Optional[str] = None
  date_of_birth: Optional[datetime] = None

  class Config:
    orm_mode = True

class FollowCreate(BaseModel):
    followed_id: int

class FollowResponse(BaseModel):
    id: int
    follower_id: int
    followed_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class UserWithFollowInfo(UserRead):
    is_following: bool = False
    followers_count: int = 0
    following_count: int = 0