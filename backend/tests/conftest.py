"""
Shared pytest fixtures for the deaddrop Static Scanner test suite.
Uses an in-memory SQLite database so no real Postgres is needed locally.
"""
import os
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Point DATABASE_URL at SQLite before the app modules load
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

from app.database import get_db          # noqa: E402
from app.main import app                 # noqa: E402
from app.models import Base              # noqa: E402

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

_engine = create_async_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
_TestingSession = async_sessionmaker(_engine, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Create all tables before each test, drop after."""
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with _TestingSession() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    """AsyncClient wired to the FastAPI app with the test DB session."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
