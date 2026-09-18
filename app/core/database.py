from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# Cast PostgresDsn object cleanly to a string string representation for SQLAlchemy
DATABASE_URL = str(settings.POSTGRES_DSN)

# 1. Initialize the high-performance async connection engine pool
async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,          # Toggle to True if you want to inspect raw SQL outputs
    pool_size=20,        # Number of permanent connections held open in pool
    max_overflow=10,     # Maximum additional burst connections allowed under sudden peak load
    pool_pre_ping=True   # Automatically verifies connections are alive before using them
)

# 2. Build the thread-safe transactional session generator factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 3. Define the Global Application Lifespan Context Manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages global application state startup and shutdown execution sequences.
    """
    print("🚀 SYSTEM STARTUP: Initializing non-blocking async network connection pools...")
    yield
    print("🛑 SYSTEM SHUTDOWN: Gracefully flushing and closing database connection pools...")
    await async_engine.dispose()

# 4. Dependency Injection Resource Provider


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yields an isolated, thread-safe asynchronous database transaction session context.
    Guarantees session closing upon request completion or sudden route crash.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
