from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class GenreResponse(BaseModel):
  id: int
  name: str
  description: Optional[str] = None

  class Config:
    orm_mode = True

class TagResponse(BaseModel):
  id: int
  name: str
  
  class Config:
    orm_mode = True
    from_attributes = True

class PoemBaseResponse(BaseModel):
  id: int
  genre_id: int
  user_id: int
  prompt: str
  title: str
  image_url: Optional[str] = None
  content: str
  note: Optional[str] = None
  is_public: bool
  created_at: datetime
  updated_at: datetime
  class Config:
    orm_mode = True
    from_attributes = True

class PoemResponse(PoemBaseResponse):
  user_name: str
  full_name: str
  avt_url: Optional[str] = None
  genre_name: str
  tags: List[TagResponse] = []
  is_saved: bool = False
  like_count: int = 0
  is_liked: bool = False

  class Config:
    orm_mode = True
    from_attributes = True

class CommentCreate(BaseModel):
  content: str

class CommentResponse(BaseModel):
  id: int
  user_id: int
  poem_id: int
  content: str
  created_at: datetime
  user_name: str
  full_name: str
  avt_url: Optional[str] = None

  class Config:
    orm_mode = True
    from_attributes = True