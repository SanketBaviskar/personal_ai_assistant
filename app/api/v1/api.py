from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, connectors, chat, drive, documents, calendar

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(connectors.router, prefix="/connectors", tags=["connectors"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(drive.router, prefix="/drive", tags=["drive"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
