import zap

HELP_TEXT = """COMMANDS
-------------
/help - Shows this message
/model - Shows available models
/model <model_id> - Sets the model to use
/agent - Shows available agents
/agent <agent_id> - Sets the agent to use
/reset - Clears chat memory
"""

def is_command(text):
    text = text.strip()
    return text.startswith('/help') or text.startswith('/model') or text.startswith('/agent') or text.startswith('/reset')

def handle_command(user, command, db):
    try:
        if command.startswith('/help'):
            return _handle_help(user)
        elif command.startswith('/model'):
            return _handle_model(user, command)
        elif command.startswith('/agent'):
            return _handle_agent(user, command)
        elif command.startswith('/reset'):
            return _handle_reset(user, db)
    except ValueError as e:
        zap.send_message('jarbas', user, f"COMMAND ERROR: {e}")

def _handle_help(user):
    zap.send_message('jarbas', user, HELP_TEXT)

def _handle_model(user, command):
    from jarbas import jarbasModels
    model_id = _cmd_arg(command, 1, int)
    available_models = jarbasModels.models()
    if model_id is not None:
        model_idx = model_id - 1
        if not 0 <= model_idx < len(available_models):
            raise ValueError(f"Invalid model id {model_id}")
        jarbasModels.setfor(user, available_models[model_idx])
    zap.send_message('jarbas', user, _list_models(user))

def _handle_agent(user, command):
    from jarbas import jarbasAgents
    agent_id = _cmd_arg(command, 1, int)
    available_agents = jarbasAgents.agents()
    if agent_id is not None:
        agent_idx = agent_id - 1
        if not 0 <= agent_idx < len(available_agents):
            raise ValueError(f"Invalid agent id {agent_id}")
        jarbasAgents.setfor(user, available_agents[agent_idx])
    zap.send_message('jarbas', user, _list_agents(user))

def _handle_reset(user, db):
    from jarbas_agents import chatMemory
    from jarbas import jarbasAgents
    agent = jarbasAgents.getfor(user)
    chatMemory.reset(user, agent.sysprompt(user, db))
    zap.send_message('jarbas', user, "Memória da conversa apagada")

def _list_models(user):
    from jarbas import jarbasModels
    reply = "MODELS\n-------------\n"
    for i, m in enumerate(jarbasModels.models()):
        prefix = "*" if m == jarbasModels.getfor(user) else " "
        reply += f"{prefix}{i+1} - {m}\n"
    return reply

def _list_agents(user):
    from jarbas import jarbasAgents
    reply = "AGENTS\n-------------\n"
    for i, a in enumerate(jarbasAgents.agents()):
        prefix = "*" if a == jarbasAgents.getfor(user) else " "
        reply += f"{prefix}{i+1} - {a.name}\n"
    return reply

def _cmd_arg(command, pos, convert=None):
    parts = command.split()
    if len(parts) <= pos:
        return None
    arg = parts[pos]
    if convert:
        try:
            arg = convert(arg)
        except Exception as e:
            raise ValueError(f"Invalid argument {arg} on position {pos}. Expected {convert}")
    return arg
