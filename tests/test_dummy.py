import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add the parent directory of 'tests' to sys.path
# print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from app.main import app

client = TestClient(app)

import pytest
from fastapi.testclient import TestClient
from main import app
from database import get_db
from tests.test_config import override_get_db, create_test_database

@pytest.fixture(scope="module")
def test_app():
    app.dependency_overrides[get_db] = override_get_db
    create_test_database()
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_read_root(test_app):
    response = test_app.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}

# Add more tests here as needed

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}
