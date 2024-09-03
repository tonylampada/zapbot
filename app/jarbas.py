import zap
import base64
import llm
import transcribe_audio
from datetime import datetime, timedelta

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
    print("sessions", sessions)
    token = zap.generate_token('jarbas')
    print("token", token)
    status = zap.status_session('jarbas', token)
    print("status", status)
    if status == 'CLOSED':
        newsession = zap.start_session('jarbas', token, webhook)
        qrcode = newsession['qrcode']
        saveToFile(qrcode, './data/qrcode.png')
        print("saved qrcode")
        return False
    if status == 'CONNECTED':
        GLOBAL['token'] = token
        return True

def got_chat(user, text, t):
    print(user)
    messages = _get_messages_history_and_maybe_reset_and_notify_user(user)
    user_timestamp = datetime.fromtimestamp(t)
    messages.append({"role": "user", "content": text, "timestamp": user_timestamp})
    agent_msg = llm.chat_completions_ollama([{"role": m['role'], "content": m['content']} for m in messages], model=_get_model_for(user))
    reply = agent_msg['content']
    zap.send_message('jarbas', GLOBAL['token'], user, reply)
    agent_msg["timestamp"] = datetime.now()
    messages.append(agent_msg)

def got_group_chat(groupfrom, msgfrom, senderName, text, t):
    historico = zap.get_last_messages(groupfrom, 10)
    prompt = _group_prompt(historico)
    reply_llm = llm.chat_completions_ollama([{"role": "user", "content": prompt}], model="llama3")
    if reply_llm != "SILENCIO":
        zap.send_group_message('jarbas', GLOBAL['token'], groupfrom, reply_llm)

def _get_model_for(user):
    return MODEL_OVERRIDES.get(user) or DEFAULT_MODEL

def _group_prompt(historico):
    # TODO: montar o prompt direto com as mensagens que vieram do grupo
    return """
    Você é o Jarbas. Um assistente virtual funcionando dentro de um grupo do whatsapp.
    Você é notificado de toda mensagem que chega no grupo.
    Normalmente você não precisa se envolver na conversa.
    Mas, quando solicitado, você deve dar uma resposta.
    Se nao quiser responder nada, responsa esta mensagem com o texto "SILENCIO".
    Caso contrario, sua resposta será enviada para o grupo.
    Segue abaixo as últimas mensagens da conversa:

    <Tony> 
    Bom dia meu amor
    <Samantha>
    Bom dia vc dormiu bem mozinho
    <Tony> 
    Nao!
    Tive um pesadelo!
    <Tony>
    Ô Jarbas, o que significa sonhar com aranha, de acordo com Freud?
    """

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
