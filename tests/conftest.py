import os
import sys

# Force the project root directory into the Python path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.api.deps import get_db
from app.models.base import Base

# 1. Use an isolated local sqlite file or testing postgres instance for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Overrides the default event loop to share a single loop across the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Initializes a clean, isolated test engine and provisions required tables."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        # Create all table schemas dynamically in our test storage layout
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provides a clean, transaction-isolated session wrapper for individual tests."""
    async_session = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        # Roll back operations after each test to keep environments isolated
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """
    Returns an async test client with overridden database dependencies injected.
    """
    async def _override_get_db():
        yield db_session

    # Override the application database provider with our testing session
    app.dependency_overrides[get_db] = _override_get_db

    # Configure modern transport layer bindings for HTTPX
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as ac:
        yield ac

    # Clear overrides after the client session finishes
    app.dependency_overrides.clear()
