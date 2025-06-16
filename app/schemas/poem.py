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

class PoemCreate(BaseModel):
  genre_id: int
  prompt: str
  title: str
  image_url: Optional[str] = None
  content: str
  note: Optional[str] = None
  tags: Optional[List[str]] = []
  is_public: Optional[bool] = True

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
  genre_name: str
  tags: List[TagResponse] = []

  class Config:
    orm_mode = True
    from_attributes = True