import zap
import json
import llm
from datetime import datetime, timedelta
from database import dbsession
import jarbas_actions
from jarbas_actions import DIARY_LIST, DIARY_CREATE, DIARY_ENTRY_LIST, DIARY_ENTRY_CREATE

class ChatMemory:
    messagehistory = {}

    def getfor(self, user, sysprompt):
        messages = self.messagehistory.get(user)
        if not messages:
            return self.reset(user, sysprompt)
        return messages[:]
    
    def reset(self, user, sysprompt):
        messages = [{"role": "system", "content": sysprompt, "timestamp": datetime.now()}]
        self.messagehistory[user] = messages
        return messages[:]
    
    def setfor(self, user, messages):
        self.messagehistory[user] = messages

class Agent:
    def __init__(self, name, sysprompt, tools):
        self.name = name
        self.sysprompt = sysprompt
        self.tools = [{'type': 'function', 'function': t} for t in tools] if tools else None
    
    def chat(self, user, text, t):
        from jarbas import jarbasModels
        messages = _get_messages_history_and_maybe_reset_and_notify_user(user, self.sysprompt)
        user_timestamp = datetime.fromtimestamp(t)
        messages.append({"role": "user", "content": text, "timestamp": user_timestamp})
        llm_input_messages = [{"role": m['role'], "content": m['content']} for m in messages]
        with dbsession() as db:
            messages_replied = llm.chat_completions_ollama_functions(
                llm_input_messages, 
                tools=self.tools, 
                tool_caller=JarbasToolCaller(user, db), 
                model=jarbasModels.getfor(user)
            )
        messages_replied[-1]["timestamp"] = datetime.now()
        chatMemory.setfor(user, messages + messages_replied)
        return messages_replied

def _get_messages_history_and_maybe_reset_and_notify_user(user, sysprompt):
    messages = chatMemory.getfor(user, sysprompt)
    if len(messages) > 0:
        last_msg = messages[-1]
        if datetime.now() - last_msg["timestamp"] > timedelta(hours=3):
            return _reset(user, sysprompt, "context reset after 3h+ of inactivity")
    return messages

def _reset(user, sysprompt, zap_reply):
    messages = chatMemory.reset(user, sysprompt)
    zap.send_message('jarbas', user, zap_reply)
    return messages

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

SYSPROMPT_JARBAS_AGENT = """
Você é o Jarbas. Um assistente virtual funcionando dentro de uma conversa do whatsapp.
Você é um cara gente boa, sempre disposto a ajudar. Tem uma personalidade leve, brincalhona, zoeira.
Trata seu usuário com uma certa intimidade, bota um emoji de vez em quando.
"""


chatMemory = ChatMemory()
jarbas_agent = Agent('jarbas', SYSPROMPT_JARBAS_AGENT, tools=None)
diary_agent = Agent('diario', SYSPROMPT_DIARY_AGENT, [DIARY_LIST, DIARY_CREATE, DIARY_ENTRY_LIST, DIARY_ENTRY_CREATE])

