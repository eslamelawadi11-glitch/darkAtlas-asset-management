import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.config import settings


# Override ARRAY type for SQLite
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String
from sqlalchemy.types import TypeDecorator


class ArrayOfString(TypeDecorator):
    """ARRAY substitute for SQLite — stores as comma-separated string"""
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return ""
        return ",".join(value)

    def process_result_value(self, value, dialect):
        if not value:
            return []
        return value.split(",")


# Patch ARRAY before models load
import app.models.asset as asset_module
asset_module.Asset.tags.property.columns[0].type = ArrayOfString()

# In-memory SQLite for tests
SQLALCHEMY_TEST_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session")
def client():
    from app.main import app

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def headers():
    return {"X-API-Key": settings.API_KEY}