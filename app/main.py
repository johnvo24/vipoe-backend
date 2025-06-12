from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth
# from app.api import users
from app.api import poems
from app.api import collections
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# include routers
app.include_router(auth.router, prefix="api/v1/auth", tags=["Authentication"])
# app.include_router(users.router, prefix="api/v1/user", tags=["User"])
# app.include_router(poems.router, prefix="api/v1/poem", tags=["Poem"])
# app.include_router(collections.router, prefix="api/v1/collection", tags=["Collection"])

@app.get("/")
async def read_root():
    return {"message": "Welcome to Vipoe backend!"}