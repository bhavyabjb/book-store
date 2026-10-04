import os

os.environ.setdefault("JWT_SECRET", "test-secret-key")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.core.db import Base, get_db
from app.main import app
from app.models.coupon import Coupon


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16-alpine") as container:
        yield container


@pytest.fixture(scope="session")
def sync_db_url(postgres_container) -> str:
    return postgres_container.get_connection_url()  # postgresql+psycopg2://...


@pytest.fixture(scope="session")
def async_db_url(sync_db_url) -> str:
    return sync_db_url.replace("postgresql+psycopg2", "postgresql+asyncpg")


@pytest.fixture(scope="session", autouse=True)
def _create_schema(sync_db_url):
    """Create all tables once for the whole test session using a plain sync engine."""
    engine = create_engine(sync_db_url)
    Base.metadata.create_all(engine)
    yield
    engine.dispose()


@pytest.fixture(autouse=True)
def _clean_tables(sync_db_url):
    """Truncate all tables before every test so tests don't leak state into each other."""
    engine = create_engine(sync_db_url)
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
    engine.dispose()
    yield


@pytest_asyncio.fixture
async def async_engine(async_db_url):
    engine = create_async_engine(async_db_url, future=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_engine):
    session_factory = async_sessionmaker(bind=async_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(async_engine, db_session):
    session_factory = async_sessionmaker(bind=async_engine, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    db_session.add(Coupon(code="SAVE100", discount_amount=100, discount_pct=None, active=True))
    await db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
