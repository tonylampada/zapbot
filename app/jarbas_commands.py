import zap

HELP_TEXT = """COMMANDS
-------------
/help - Shows this message
/model - Shows available models
/model <model_id> - Sets the model to use
/agent - Shows available agents
/agent <agent_id> - Sets the agent to use
"""

def is_command(text):
    text = text.strip()
    return text.startswith('/help') or text.startswith('/model') or text.startswith('/agent')

def handle_command(user, command):
    from jarbas import jarbasModels
    try:
        if command.startswith('/help'):
            zap.send_message('jarbas', user, HELP_TEXT)
            return
        elif command.startswith('/model'):
            model_id = _cmd_arg(command, 1, int)
            available_models = jarbasModels.models()
            if model_id is not None:
                model_idx = model_id - 1
                if not 0 < model_idx < len(available_models):
                    raise ValueError(f"Invalid model id {model_id}")
                jarbasModels.setfor(user, available_models[model_idx])
            zap.send_message('jarbas', user, _list_models(user))
    except ValueError as e:
        zap.send_message('jarbas', user, f"COMMAND ERROR: {e}")

def _list_models(user):
    from jarbas import jarbasModels
    reply = "MODELS\n-------------\n"
    for i, m in enumerate(jarbasModels.models()):
        prefix = "*" if m == jarbasModels.getfor(user) else " "
        reply += f"{prefix}{i+1} - {m}\n"
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
