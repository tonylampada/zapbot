
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture(scope="session")
def mock_send_message():
    mock = MagicMock()
    with patch('zap.send_message', mock):
        yield mock

@pytest.fixture(scope="session", autouse=True)
def mock_zap(mock_send_message):
    import zap
    with patch.object(zap, 'show_all_sessions', return_value=['session1', 'session2']), \
         patch.object(zap, 'generate_token', return_value='mock_token'), \
         patch.object(zap, 'status_session', return_value='CONNECTED'), \
         patch.object(zap, 'start_session'), \
         patch.object(zap, 'send_group_message'), \
         patch.object(zap, 'get_messages', return_value=[]):
        yield


@pytest.fixture(scope="session", autouse=True)
def setup_test_env(mock_zap):
    import database
    database.create_tables()
    import jarbas
    jarbas.start_session(webhook='http://172.17.0.1:8000/zap')
    yield

@pytest.fixture(scope="module")
def testapp():
    client = TestClient(app)
    yield client
