from . import helper

def test_help(testapp, mock_send_message):
    replies = helper.zapmsg(testapp, mock_send_message, "/help")
    assert len(replies) == 1, "did not get exactly one reply"
    expected_message = """COMMANDS
-------------
/help - Shows this message
/model - Shows available models
/model <model> - Sets the model to use
/agent - Shows available agents
/agent <agent> - Sets the agent to use
"""
    assert replies[0] == expected_message
