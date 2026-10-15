from backend.routes import health
from fastapi import APIRouter
from ..routes import auth

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(auth.router)
# api_router.include_router(drawings.router)