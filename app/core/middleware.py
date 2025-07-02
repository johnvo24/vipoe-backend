from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

def setup_cors(app, base_url):
  app.add_middleware(
    CORSMiddleware,
    allow_origins=[base_url, "http://127.0.0.1:3000", "http://192.168.17.186:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
  )
  print(f"------------------{settings.DATABASE_URL}")