from fastapi import APIRouter
from app.api.v1.telemetry import router as telemetry_router
from app.api.v1.devices import router as devices_router
from app.api.v1.ws import router as ws_router

api_router = APIRouter()

# If app.main imports api_router with prefix="/api/v1", these should just be integrated without doubling up
api_router.include_router(telemetry_router)
api_router.include_router(devices_router)
api_router.include_router(ws_router)

__all__ = ["api_router"]