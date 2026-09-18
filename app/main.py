from fastapi import FastAPI
from app.core.config import settings
from app.core.database import lifespan
from app.api.router import api_router

app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)

# Bind our organized API router layout
app.include_router(api_router, prefix=settings.API_V1_STR)
