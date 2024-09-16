def zapmsg(testapp, mock_send_message, text):
    data = {
        "event": "onmessage",
        "type": "chat",
        "body": text,
        "t": 1640988915,
        "from": "test_user",
        "author": "test_author",
        "isGroupMsg": False,
        "sender": {"formattedName": "Test User"}
    }
    response = testapp.post("/zap", json=data)
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}
    zap_messages = [args[3] for args, kwargs in mock_send_message.call_args_list]
    mock_send_message.reset_mock()
    return zap_messages
