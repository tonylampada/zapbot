import zap
import base64
import llm
from datetime import datetime, timedelta

GLOBAL = {
    "history": {}
}

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
        # zap.send_message('jarbas', token, '5512981440013', 'hello from jarbas')

def got_zap(user, text, t):
    messages = GLOBAL["history"].setdefault(user, [])
    if len(messages) > 0:
        last_msg = messages[-1]
        if datetime.now() - last_msg["timestamp"] > timedelta(hours=3):
            messages = []
            GLOBAL["history"][user] = messages
            zap.send_message('jarbas', GLOBAL['token'], user, "context reset after 3h+ of inactivity")
    user_timestamp = datetime.fromtimestamp(t)
    messages.append({"role": "user", "content": text, "timestamp": user_timestamp})
    r = llm.chat_completions([{"role": m['role'], "content": m['content']} for m in messages])
    agent_msg = r['choices'][0]['message']
    reply = agent_msg['content']
    zap.send_message('jarbas', GLOBAL['token'], user, reply)
    agent_msg["timestamp"] = datetime.now()
    messages.append(agent_msg)

def saveToFile(base64_string, path):
    if base64_string.startswith('data:image/png;base64,'):
        base64_string = base64_string.split(',')[1]
    image_data = base64.b64decode(base64_string)
    with open(path, 'wb') as file:
        file.write(image_data)
