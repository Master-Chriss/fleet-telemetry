from app.core.database import get_db

# We export get_db to unify route imports across different router domains
__all__ = ["get_db"]
