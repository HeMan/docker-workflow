from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import pytest_asyncio
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.community.postgres import PostgresContainer

from alembic import command
from app.database import get_db
from app.main import app

BASE_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def database_url() -> AsyncGenerator[str]:
    with PostgresContainer("postgres:18-alpine", driver="asyncpg") as postgres:
        yield postgres.get_connection_url()


@pytest.fixture(scope="session")
def _migrated(database_url: str) -> None:
    cfg = Config(str(BASE_DIR / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(cfg, "head")


@pytest_asyncio.fixture
async def db_session(database_url: str, _migrated: None) -> AsyncGenerator[AsyncSession]:
    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        # Each test gets a clean table; the container itself is reused for speed.
        await session.execute(text("TRUNCATE TABLE todos RESTART IDENTITY"))
        await session.commit()
        yield session
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
