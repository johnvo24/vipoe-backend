from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth
from app.api import users
from app.api import poems
from app.api import collections

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/user", tags=["User"])
app.include_router(poems.router, prefix="/poem", tags=["Poem"])
app.include_router(collections.router, prefix="/collection", tags=["Collection"])

@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI!"}