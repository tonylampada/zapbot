def test_read_root(testapp):
    response = testapp.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}

def test_got_zap(testapp, mock_send_message):
    data = {
        "event": "onmessage",
        "type": "chat",
        "body": "Bom dia Jarbas, tudo bem?",
        "t": 1640988915,
        "from": "test_user",
        "author": "test_author",
        "isGroupMsg": False,
        "sender": {"formattedName": "Test User"}
    }
    response = testapp.post("/zap", json=data)
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}
    assert mock_send_message.call_count > 0, "send_message was not called"

    zap_messages = [args[3] for args, kwargs in mock_send_message.call_args_list]
    for m in zap_messages:
        assert isinstance(m, str), "msg is not a string"
        assert len(m) > 0, "msg is empty"
    pass

