from pydantic_settings import BaseSettings

class Settings(BaseSettings):
  # SECURE_COOKIES: bool
  DATABASE_URL: str = "postgresql://johnvo:johnjohn@db:5432/vipoedb"
  FRONTEND_URL: str = "http://localhost:3000"
  MAIL_USER: str
  MAIL_PASS: str
  SECRET_KEY: str
  CLOUDINARY_URL: str
  GEMINI_API_KEY: str
  GOOGLE_API_KEY: str
  SEARCH_ENGINE_ID: str

  class Config:
    env_file = ".env"

settings = Settings()