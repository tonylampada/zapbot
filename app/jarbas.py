import zap
import base64
import llm
import transcribe_audio
from datetime import datetime, timedelta
import logging
import json
logger = logging.getLogger(__name__)

GLOBAL = {
    "history": {}
}

MODEL_OVERRIDES = {
    '5512981440013@c.us': 'dolphin-llama3',
    '5512981812300@c.us': 'dolphin-llama3',
    '5512988653063@c.us': 'dolphin-llama3',
}
DEFAULT_MODEL = 'llama3'

def start_session(webhook=None):
    sessions = zap.show_all_sessions()
    logger.info(f"sessions: {sessions}")
    token = zap.generate_token('jarbas')
    logger.info(f"token: {token}")
    status = zap.status_session('jarbas', token)
    logger.info(f"status: {status}")
    if status != 'CONNECTED':
        newsession = zap.start_session('jarbas', token, webhook)
        qrcode = newsession['qrcode']
        saveToFile(qrcode, './data/qrcode.png')
        logger.info("saved qrcode")
        return False
    GLOBAL['token'] = token
    return True

def got_chat(user, text, t):
    messages = _get_messages_history_and_maybe_reset_and_notify_user(user)
    user_timestamp = datetime.fromtimestamp(t)
    messages.append({"role": "user", "content": text, "timestamp": user_timestamp})
    agent_msg = llm.chat_completions_ollama([{"role": m['role'], "content": m['content']} for m in messages], model=_get_model_for(user))
    reply = agent_msg['content']
    zap.send_message('jarbas', GLOBAL['token'], user, reply)
    agent_msg["timestamp"] = datetime.now()
    messages.append(agent_msg)

def got_group_chat(groupfrom, msgfrom, senderName, text, t):
    zap_messages = zap.get_messages('jarbas', GLOBAL['token'], groupfrom, 10)
    reply_llm = _get_group_reply(zap_messages)
    if reply_llm:
        zap.send_group_message('jarbas', GLOBAL['token'], groupfrom, reply_llm)

def _get_model_for(user):
    return MODEL_OVERRIDES.get(user) or DEFAULT_MODEL

def _get_group_reply(zap_messages):
    sysprompt = """
Você é o Jarbas. Um assistente virtual funcionando dentro de um grupo do whatsapp.
Quando solicitado, você deve dar uma resposta.
Mas normalmente você não precisa se envolver na conversa, responda apenas quando vc for chamado pelo nome.
Eu vou te mandar o historico recente do grupo, e vc decide se quer responder ou não.
"""
    messages = [{"role": "system", "content": sysprompt}]
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
    zap.send_message('jarbas', GLOBAL['token'], user, "Transcribing audio. Please wait...")
    text = transcribe_audio.transcribe(audio_base64)
    zap.send_message('jarbas', GLOBAL['token'], user, "TRANSCRIBED AUDIO\n--------------\n"+text)
    got_chat(user, text, t)


def _get_messages_history_and_maybe_reset_and_notify_user(user):
    messages = GLOBAL["history"].setdefault(user, [])
    if len(messages) > 0:
        last_msg = messages[-1]
        if datetime.now() - last_msg["timestamp"] > timedelta(hours=3):
            messages = []
            GLOBAL["history"][user] = messages
            zap.send_message('jarbas', GLOBAL['token'], user, "context reset after 3h+ of inactivity")
    return messages


def saveToFile(base64_string, path):
    if base64_string.startswith('data:image/png;base64,'):
        base64_string = base64_string.split(',')[1]
    image_data = base64.b64decode(base64_string)
    with open(path, 'wb') as file:
        file.write(image_data)
