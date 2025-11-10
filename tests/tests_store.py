from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.store import Store

SQLALCHEMY_TEST_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_TEST_URL)
TestingSessionLocal = sessionmaker(bind=engine)

def setup_test_db():
    Base.metadata.create_all(bind=engine)

def teardown_test_db():
    Base.metadata.drop_all(bind=engine)

def test_create_store():
    setup_test_db()
    db = TestingSessionLocal()
    store = Store(name="K-Market Kamppi", latitude=60.1699, longitude=24.9332)
    db.add(store)
    db.commit()
    db.refresh(store)
    assert store.id is not None
    assert store.name == "K-Market Kamppi"
    db.close()
    teardown_test_db()