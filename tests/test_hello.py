from . import helper

def test_read_root(testapp):
    response = testapp.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}

def test_got_zap(testapp, mock_send_message):
    text = "Bom dia Jarbas, tudo bem?"
    replies = helper.zapmsg(testapp, mock_send_message, text)
    assert len(replies) > 0, "send_message was not called"
    for r in replies:
        assert isinstance(r, str), "msg is not a string"
        assert len(r) > 0, "msg is empty"
    pass
