from fastapi import APIRouter
from app.api.v1.telemetry import router as telemetry_router

api_router = APIRouter()
# Aggregate v1 routes cleanly
api_router.include_router(telemetry_router, prefix="/v1")
