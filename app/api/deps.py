from app.core.database import get_db
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

# 1. Instruct FastAPI to watch for an 'X-API-Key' property in HTTP Request Headers
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def validate_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Dependency validator that intercepts requests to ensure incoming edge packets
    provide authentic cryptographic header keys matching our server environment secrets.
    """
    if not api_key or api_key != settings.API_KEY_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials. Invalid or missing X-API-Key header."
        )
    return api_key


# We export get_db to unify route imports across different router domains
__all__ = ["get_db"]
