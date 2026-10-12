import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use isolated in-memory or test SQLite database
os.environ["DATABASE_URL"] = "sqlite:///./test_dharma_diamond.db"

from app.db.session import Base, get_db
from app.main import app
from app.core.security import create_access_token, get_password_hash
from app.models.user import User
from app.models.inventory_location import Location
from app.models.party import Supplier, Customer

TEST_ENGINE = create_engine("sqlite:///./test_dharma_diamond.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=TEST_ENGINE)
    Base.metadata.create_all(bind=TEST_ENGINE)
    db = TestingSessionLocal()
    
    # Create test admin
    admin = User(
        email="test_admin@dharmadiamond.com",
        hashed_password=get_password_hash("pass123"),
        full_name="Test Admin",
        role="admin",
        is_active=True
    )
    # Create test sales user
    sales = User(
        email="test_sales@dharmadiamond.com",
        hashed_password=get_password_hash("pass123"),
        full_name="Test Sales",
        role="sales_staff",
        is_active=True
    )
    # Create test read-only user
    readonly = User(
        email="test_readonly@dharmadiamond.com",
        hashed_password=get_password_hash("pass123"),
        full_name="Test ReadOnly",
        role="read_only",
        is_active=True
    )
    # Create test vault location
    vault = Location(
        code="TEST_VAULT",
        name="Test Main Vault",
        is_active=True
    )
    # Create test supplier
    sup = Supplier(
        business_name="Test Surat Exports",
        contact_person="Ramesh",
        country="India",
        currency="INR",
        is_active=True
    )
    # Create test customer
    cust = Customer(
        name="Test HNW Customer",
        phone="+91 99999 88888",
        customer_type="Retail",
        is_active=True
    )
    db.add_all([admin, sales, readonly, vault, sup, cust])
    db.commit()
    db.close()
    
    yield
    
    # Cleanup
    Base.metadata.drop_all(bind=TEST_ENGINE)
    if os.path.exists("./test_dharma_diamond.db"):
        os.remove("./test_dharma_diamond.db")

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def admin_headers(db_session):
    admin = db_session.query(User).filter(User.email == "test_admin@dharmadiamond.com").first()
    token = create_access_token(subject=admin.id, role=admin.role)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sales_headers(db_session):
    sales = db_session.query(User).filter(User.email == "test_sales@dharmadiamond.com").first()
    token = create_access_token(subject=sales.id, role=sales.role)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def readonly_headers(db_session):
    ro = db_session.query(User).filter(User.email == "test_readonly@dharmadiamond.com").first()
    token = create_access_token(subject=ro.id, role=ro.role)
    return {"Authorization": f"Bearer {token}"}
