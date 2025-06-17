from fastapi import FastAPI
from app.core.config import settings
from app.core.middleware import setup_cors
from app.api import router

def create_app():
    app = FastAPI()
    setup_cors(app, settings.FRONTEND_URL)
    app.include_router(router)
    return app

app = create_app()

@app.get("/")
async def read_root():
    return {"message": "Welcome to Vipoe backend!"}