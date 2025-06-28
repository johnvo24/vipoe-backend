from typing import Optional, List
from pydantic import BaseModel

class ChatMessageRequest(BaseModel):
  model: str = "gemini-1.5-flash"
  search_mode: bool = False
  prompt: str

class Step(BaseModel):
  error_poem: str
  step_content: str
  edited_poem: str
  reasoning_score: Optional[int] = None
  meaning_score: Optional[bool] = None
  imagery_score: Optional[bool] = None

class ChainRequest(BaseModel):
  original_poem: str
  steps: List[Step]