import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

def get_test_engine():
    return create_engine(TEST_DATABASE_URL)

def get_test_session():
    engine = get_test_engine()
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return TestingSessionLocal()

def create_test_database():
    engine = get_test_engine()
    Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = get_test_session()
        yield db
    finally:
        db.close()
