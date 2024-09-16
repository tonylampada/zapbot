import zap
import llm
import transcribe_audio
from datetime import datetime, timedelta
import logging
from database import dbsession
logger = logging.getLogger(__name__)
import jarbas_commands
from jarbas_agents import diary_agent, jarbas_agent


SYSPROMPT_GROUP_AGENT = """
Você é o Jarbas. Um assistente virtual funcionando dentro de um grupo do whatsapp.
Quando solicitado, você deve dar uma resposta.
Mas normalmente você não precisa se envolver na conversa, responda apenas quando vc for chamado pelo nome.
Eu vou te mandar o historico recente do grupo, e vc decide se quer responder ou não.
"""

class JarbasModels:
    default = 'llama3.1'
    available = [
        "llama3.1",
        "dolphin-llama3",
        "mistral-nemo",
    ]
    overrides = {}
    def getfor(self, user):
        return self.overrides.get(user) or self.default
    
    def setfor(self, user, agent):
        self.overrides[user] = agent
    
    def models(self):
        return self.available

class JarbasAgents:
    default = jarbas_agent
    available = [jarbas_agent, diary_agent]
    overrides = {}
    def getfor(self, user):
        return self.overrides.get(user) or self.default
    
    def setfor(self, user, model):
        self.overrides[user] = model
    
    def agents(self):
        return self.available

jarbasModels = JarbasModels()
jarbasAgents = JarbasAgents()

def got_chat(user, text, t):
    if jarbas_commands.is_command(text):
        return jarbas_commands.handle_command(user, text)
    agent = jarbasAgents.getfor(user)
    messages_replied = agent.chat(user, text, t)
    reply = messages_replied[-1]['content']
    zap.send_message('jarbas', user, reply)

def got_group_chat(groupfrom, msgfrom, senderName, text, t):
    zap_messages = zap.get_messages('jarbas', groupfrom, 10)
    reply_llm = _get_group_reply(zap_messages)
    if reply_llm:
        zap.send_group_message('jarbas', groupfrom, reply_llm)

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

