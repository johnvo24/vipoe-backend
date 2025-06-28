import google.generativeai as genai
from app.core.config import settings

class Gemini():
  def __init__(self, api_key):
    self.name = "gemini-1.5-flash"
    genai.configure(api_key=api_key)
    self.model = genai.GenerativeModel("gemini-1.5-flash")
    
  def __generate__(self, prompt: str):
    result = self.model.generate_content(f"{prompt}")
    return result.text
  
GEMINI_INSTANCE = Gemini(api_key=settings.GEMINI_API_KEY)