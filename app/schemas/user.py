from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
  full_name: str = Field(..., min_length=1, max_length=100)
  username: str = Field(..., min_length=6, max_length=50)
  email: EmailStr
  password: str = Field(..., min_length=8)

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