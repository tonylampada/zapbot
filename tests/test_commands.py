def test_help(testapp, mock_send_message):
    data = {
        "event": "onmessage",
        "type": "chat",
        "body": "/help",
        "t": 1640988915,
        "from": "test_user",
        "author": "test_author",
        "isGroupMsg": False,
        "sender": {"formattedName": "Test User"}
    }
    response = testapp.post("/zap", json=data)
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}
    assert mock_send_message.call_count == 1, "send_message was not called"
    zap_messages = [args[3] for args, kwargs in mock_send_message.call_args_list]
    expected_message = """COMMANDS
-------------
/help - Shows this message
/model - Shows available models
/model <model> - Sets the model to use
/agent - Shows available agents
/agent <agent> - Sets the agent to use
"""
    assert zap_messages[0] == expected_message
