import os
from unittest.mock import patch, MagicMock
import pytest

@pytest.fixture(scope="session")
def mock_send_message():
    mock = MagicMock()
    with patch('zap.send_message', mock):
        yield mock

@pytest.fixture(scope="session", autouse=True)
def mock_zap(mock_send_message):
    import zap
    
    # def print_send_message_params(*args, **kwargs):
    #     print(f"send_message called with args: {args}, kwargs: {kwargs}")

    with patch.object(zap, 'show_all_sessions', return_value=['session1', 'session2']), \
         patch.object(zap, 'generate_token', return_value='mock_token'), \
         patch.object(zap, 'status_session', return_value='CONNECTED'), \
         patch.object(zap, 'start_session'), \
         patch.object(zap, 'send_group_message'), \
         patch.object(zap, 'get_messages', return_value=[]):
        yield


@pytest.fixture(scope="session", autouse=True)
# @pytest.mark.usefixtures("mock_zap")
def setup_test_env(mock_zap):
    import database
    database.create_tables()
    import jarbas
    jarbas.start_session(webhook='http://172.17.0.1:8000/zap')
    yield
