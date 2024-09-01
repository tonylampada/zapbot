import zap
import base64
import llm

GLOBAL = {}

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
        saveToFile(qrcode, './x.png')
        print("saved qrcode")
        return False
    if status == 'CONNECTED':
        GLOBAL['token'] = token
        return True
        # zap.send_message('jarbas', token, '5512981440013', 'hello from jarbas')

def got_zap(user, text):
    r = llm.chat_completions(text)
    reply = r['choices'][0]['message']['content']
    zap.send_message('jarbas', GLOBAL['token'], user, reply)

def saveToFile(base64_string, path):
    if base64_string.startswith('data:image/png;base64,'):
        base64_string = base64_string.split(',')[1]
    image_data = base64.b64decode(base64_string)
    with open(path, 'wb') as file:
        file.write(image_data)
