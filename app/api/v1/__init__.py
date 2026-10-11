from fastapi import APIRouter

from app.api.v1 import auth, ghats, analysis, admin, whatsapp, sources

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(ghats.router)
api_router.include_router(analysis.router)
api_router.include_router(admin.router)
api_router.include_router(whatsapp.router)
api_router.include_router(sources.router)
