from . import helper

def test_help(testapp, mock_send_message):
    replies = helper.zapmsg(testapp, mock_send_message, "/help")
    assert len(replies) == 1, "did not get exactly one reply"
    expected_message = """COMMANDS
-------------
/help - Shows this message
/model - Shows available models
/model <model_id> - Sets the model to use
/agent - Shows available agents
/agent <agent_id> - Sets the agent to use
"""
    assert replies[0] == expected_message

def test_list_and_set_model(testapp, mock_send_message):
    replies = helper.zapmsg(testapp, mock_send_message, "/model")
    expected_message = """MODELS
-------------
*1 - llama3.1
 2 - dolphin-llama3
 3 - mistral-nemo
"""
    assert replies[0] == expected_message
    replies = helper.zapmsg(testapp, mock_send_message, "/model 3")
    expected_message = """MODELS
-------------
 1 - llama3.1
 2 - dolphin-llama3
*3 - mistral-nemo
"""
    assert replies[0] == expected_message
    replies = helper.zapmsg(testapp, mock_send_message, "/model")
    expected_message = """MODELS
-------------
 1 - llama3.1
 2 - dolphin-llama3
*3 - mistral-nemo
"""
    assert replies[0] == expected_message
