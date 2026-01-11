import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings
import os

# Test database URL (use SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
    echo=False,
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_database():
    """Set up test database."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def admin_token(client: AsyncClient, db_session: AsyncSession) -> str:
    """Create admin user and return auth token."""
    from app.services.auth import AuthService
    from app.schemas.user import UserCreate
    
    # Create admin user
    user_data = UserCreate(
        username="testadmin",
        email="admin@test.com",
        full_name="Test Admin",
        password="testpassword"
    )
    
    auth_service = AuthService()
    user = await auth_service.create_user(db_session, user_data, role="admin")
    
    # Login and get token
    login_data = {"username": "testadmin", "password": "testpassword"}
    response = await client.post("/api/v1/auth/login", json=login_data)
    
    return response.json()["access_token"]


@pytest.fixture
async def user_token(client: AsyncClient, db_session: AsyncSession) -> str:
    """Create regular user and return auth token."""
    from app.services.auth import AuthService
    from app.schemas.user import UserCreate
    
    # Create regular user
    user_data = UserCreate(
        username="testuser",
        email="user@test.com",
        full_name="Test User",
        password="testpassword"
    )
    
    auth_service = AuthService()
    user = await auth_service.create_user(db_session, user_data)
    
    # Login and get token
    login_data = {"username": "testuser", "password": "testpassword"}
    response = await client.post("/api/v1/auth/login", json=login_data)
    
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(user_token: str) -> dict:
    """Create authorization headers."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> dict:
    """Create admin authorization headers."""
    return {"Authorization": f"Bearer {admin_token}"}