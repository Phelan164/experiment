from fastapi import APIRouter

from src.api.routes import chat

api_router = APIRouter()
api_router.include_router(chat.router)