import os
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

# Railway provides postgres:// — SQLAlchemy async requires postgresql+asyncpg://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# asyncpg doesn't accept sslmode/channel_binding as URL params — strip them and use connect_args
_parsed = urlparse(DATABASE_URL)
_params = {k: v for k, v in parse_qs(_parsed.query).items()
           if k not in ("sslmode", "channel_binding")}
_ssl = "sslmode=require" in DATABASE_URL
DATABASE_URL = urlunparse(_parsed._replace(query=urlencode({k: v[0] for k, v in _params.items()})))

engine = create_async_engine(DATABASE_URL, echo=False, connect_args={"ssl": _ssl})
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
