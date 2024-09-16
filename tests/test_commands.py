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
/reset - Clears chat memory
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

def test_list_and_set_agent(testapp, mock_send_message):
    replies = helper.zapmsg(testapp, mock_send_message, "/agent")
    expected_message = """AGENTS
-------------
*1 - jarbas
 2 - diario
"""
    assert replies[0] == expected_message
    replies = helper.zapmsg(testapp, mock_send_message, "/agent 2")
    expected_message = """AGENTS
-------------
 1 - jarbas
*2 - diario
"""
    assert replies[0] == expected_message
    replies = helper.zapmsg(testapp, mock_send_message, "/agent")
    expected_message = """AGENTS
-------------
 1 - jarbas
*2 - diario
"""
    assert replies[0] == expected_message


def test_reset(testapp, mock_send_message):
    replies = []
    replies += helper.zapmsg(testapp, mock_send_message, "Conta uma piada")
    assert len(replies) == 1
    replies += helper.zapmsg(testapp, mock_send_message, "Outra")
    assert len(replies) == 2
    replies += helper.zapmsg(testapp, mock_send_message, "/reset")
    assert len(replies) == 3
    assert replies[2] == "Memória da conversa apagada"
    replies += helper.zapmsg(testapp, mock_send_message, "Outra")
    assert len(replies) == 4
    # assert replies[0] nao eh uma piada

