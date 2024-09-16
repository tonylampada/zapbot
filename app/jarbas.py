import zap
import llm
import transcribe_audio
from datetime import datetime, timedelta
import logging
import json
from database import dbsession
logger = logging.getLogger(__name__)
from jarbas_actions import DIARY_LIST, DIARY_CREATE, DIARY_ENTRY_LIST, DIARY_ENTRY_CREATE
import jarbas_actions

GLOBAL = {
    "history": {}
}

MODEL_OVERRIDES = {}
DEFAULT_MODEL = 'llama3.1'
AVAILABLE_MODELS = [
    "llama3.1",
    "dolphin-llama3",
    "mistral-nemo",
]

TOOLS = [DIARY_LIST, DIARY_CREATE, DIARY_ENTRY_LIST, DIARY_ENTRY_CREATE]
TOOLS = [{'type': 'function', 'function': t} for t in TOOLS]

SYSPROMPT_DIARY_AGENT = """
Você é o Jarbas. Um assistente virtual funcionando dentro de uma conversa do whatsapp.
Além de ser um assistente útil, você tem a capacidade de ajudar o seu cliente a lembrar de coisas,
usando as funções disponíveis para manipular diários e registros.
O usuário pode ter diários diferente e, pra ganhar tempo, ao iniciar uma conversa você 
já deve usar a função diary_list pra saber a lista dos diarios e seus IDs.
O caso mais frequente é anotar coisas em algum diário usando a função diary_entry_create.
Também pode ser comum o usuário pedir pra vc fazer algum tipo de análise baseado em registros existentes.
Antes de criar um novo diário com a função diary_create vc deve sempre confirmar com o usuário.
"""

SYSPROMPT_GROUP_AGENT = """
Você é o Jarbas. Um assistente virtual funcionando dentro de um grupo do whatsapp.
Quando solicitado, você deve dar uma resposta.
Mas normalmente você não precisa se envolver na conversa, responda apenas quando vc for chamado pelo nome.
Eu vou te mandar o historico recente do grupo, e vc decide se quer responder ou não.
"""

HELP_TEXT = """COMMANDS
-------------
/help - Shows this message
/model - Shows available models
/model <model_id> - Sets the model to use
/agent - Shows available agents
/agent <agent_id> - Sets the agent to use
"""

def got_chat(user, text, t):
    if _is_command(text):
        return _handle_command(user, text)
    messages = _get_messages_history_and_maybe_reset_and_notify_user(user, SYSPROMPT_DIARY_AGENT)
    user_timestamp = datetime.fromtimestamp(t)
    messages.append({"role": "user", "content": text, "timestamp": user_timestamp})
    llm_messages = [{"role": m['role'], "content": m['content']} for m in messages]
    # agent_msg = llm.chat_completions_ollama(llm_messages, model=_get_model_for(user))
    with dbsession() as db:
        messages_replied = llm.chat_completions_ollama_functions(
            llm_messages, 
            tools=TOOLS, 
            tool_caller=JarbasToolCaller(user, db), 
            model=_get_model_for(user)
        )
    agent_msg = messages_replied[-1]
    reply = agent_msg['content']
    zap.send_message('jarbas', user, reply)
    agent_msg["timestamp"] = datetime.now()
    messages.extend(messages_replied)

def got_group_chat(groupfrom, msgfrom, senderName, text, t):
    zap_messages = zap.get_messages('jarbas', groupfrom, 10)
    reply_llm = _get_group_reply(zap_messages)
    if reply_llm:
        zap.send_group_message('jarbas', groupfrom, reply_llm)

def _get_model_for(user):
    return MODEL_OVERRIDES.get(user) or DEFAULT_MODEL

def _get_group_reply(zap_messages):
    messages = [{"role": "system", "content": SYSPROMPT_GROUP_AGENT}]
    last_message = zap_messages[-1]
    zap_messages = zap_messages[:-1]

    content = ""
    if zap_messages:
        content = "Últimas mensagens do grupo:\n"
        for m in zap_messages:
            senderName = m['senderName']
            zcontent = m["content"]
            content += f"- <{senderName}> {zcontent}"
        content += "\n"
    content += "Nova mensagem:\n"
    senderName = last_message['senderName']
    zcontent = last_message["content"]
    content += f"- <{senderName}> {zcontent}"
    content += "\n"
    content += 'Essa mensagem precisa de uma resposta? Responda apenas com "SIM" ou "NAO".'
    messages.append({"role": "user", "content": content})
    reply_llm = llm.chat_completions_ollama(messages, model="llama3")
    if reply_llm['content'].lower() != 'sim':
        return None
    messages.append(reply_llm)
    messages.append({"role": "user", "content": "Qual a resposta?"})
    reply_llm = llm.chat_completions_ollama(messages, model="llama3")
    return reply_llm['content']


def got_audio(user, audio_base64, t):
    zap.send_message('jarbas', user, "Transcribing audio. Please wait...")
    text = transcribe_audio.transcribe(audio_base64)
    zap.send_message('jarbas', user, "TRANSCRIBED AUDIO\n--------------\n"+text)
    got_chat(user, text, t)


def _get_messages_history_and_maybe_reset_and_notify_user(user, sysprompt):
    sysmessage = {"role": "system", "content": sysprompt, "timestamp": datetime.now()}
    messages = GLOBAL["history"].setdefault(user, [sysmessage])
    if len(messages) > 0:
        last_msg = messages[-1]
        if datetime.now() - last_msg["timestamp"] > timedelta(hours=3):
            messages = [{"role": "system", "content": sysprompt}]
            GLOBAL["history"][user] = messages
            zap.send_message('jarbas', user, "context reset after 3h+ of inactivity")
    return messages

def _is_command(text):
    text = text.strip()
    return text.startswith('/help') or text.startswith('/model') or text.startswith('/agent')

def _handle_command(user, command):
    try:
        if command.startswith('/help'):
            zap.send_message('jarbas', user, HELP_TEXT)
            return
        elif command.startswith('/model'):
            model_id = _cmd_arg(command, 1, int)
            if model_id is not None:
                model_idx = model_id - 1
                if not 0 < model_idx < len(AVAILABLE_MODELS):
                    raise ValueError(f"Invalid model id {model_id}")
                MODEL_OVERRIDES[user] = AVAILABLE_MODELS[model_idx]
            zap.send_message('jarbas', user, _list_models(user))
    except ValueError as e:
        zap.send_message('jarbas', user, f"COMMAND ERROR: {e}")

            
def _list_models(user):
    reply = "MODELS\n-------------\n"
    for i, m in enumerate(AVAILABLE_MODELS):
        prefix = "*" if m == _get_model_for(user) else " "
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

class JarbasToolCaller:
    def __init__(self, user, db):
        self.user = user
        self.db = db

    def call(self, tool_call):
        kwargs = {
            'user_id': self.user,
            'db': self.db,
        }
        try:
            function_name = tool_call['function']['name']
            arguments = tool_call['function']['arguments']
            for k in kwargs:
                if k in arguments:
                    raise ValueError(f"invalid parameter {k}")
            kwargs.update(arguments)
            if function_name == 'diary_list':
                result = jarbas_actions.diary_list(**kwargs)
            elif function_name == 'diary_create':
                result = jarbas_actions.diary_create(**kwargs)
            elif function_name == 'diary_entry_list':
                result = jarbas_actions.diary_entry_list(**kwargs)
            elif function_name == 'diary_entry_create':
                result = jarbas_actions.diary_entry_create(**kwargs)
            else:
                raise ValueError(f"Unknown function: {function_name}")
            zap.send_message('jarbas', self.user, f"Called function succesfully: {function_name}({json.dumps(arguments)})")
        except Exception as e:
            result = {'error': str(e)}
            zap.send_message('jarbas', self.user, f"Called function with error: {function_name}({json.dumps(arguments)}) = {str(e)}")
        return result
