import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.database import get_db
from src.auth.security import create_test_token, SecurityUtils
from models import Base
from models.user import User, UserRole

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_test_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="function")
def db():
    # Create the database and tables
    init_test_db()
    
    # Get a test database session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up by dropping all tables after the test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_token():
    return create_test_token(UserRole.USER)

@pytest.fixture
def admin_token():
    return create_test_token(UserRole.ADMIN)

@pytest.fixture
def test_user(db):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123!",
        "role": UserRole.USER
    }
    hashed_password = SecurityUtils.get_password_hash(user_data["password"])
    db_user = User(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=hashed_password,
        role=user_data["role"]
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return user_data  # Return user_data instead of db_user for test usage

@pytest.fixture
def admin_user(db):
    user_data = {
        "username": "admin",
        "email": "admin@example.com",
        "password": "Admin123!",
        "role": UserRole.ADMIN
    }
    hashed_password = SecurityUtils.get_password_hash(user_data["password"])
    db_user = User(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=hashed_password,
        role=user_data["role"]
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Remove duplicate test_health_check and login route
