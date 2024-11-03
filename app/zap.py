import requests
import os
import base64
import logging
logger = logging.getLogger(__name__)

BASE_URL = os.getenv('WPPCONNECT_BASE_URL', 'http://localhost:21465')
SECRET_KEY = os.getenv('WPPCONNECT_SECRET_KEY')

TOKENS = {}

def start_session(sessionName, webhook=None):
    if TOKENS.get(sessionName):
        return True, None, None
    sessions = _show_all_sessions()
    logger.info(f"sessions: {sessions}")
    token = _generate_token(sessionName)
    logger.info(f"token: {token}")
    status = _status_session(sessionName, token)
    logger.info(f"status: {status}")
    if status == 'CONNECTED':
        TOKENS[sessionName] = token
        return True, None, status
    else:
        newsession = _start_session(sessionName, token, webhook)
        print(newsession)
        qrcode = newsession['qrcode']
        if qrcode:
            _saveToFile(qrcode, './data/qrcode.png')
            logger.info("saved qrcode")
        return False, qrcode, status


def _generate_token(sessionName):
    url = f"{BASE_URL}/api/{sessionName}/{SECRET_KEY}/generate-token"
    response = requests.post(url)
    if response.status_code == 201:
        r = response.json()
        return r['token']
    else:
        raise Exception(f"Failed to generate token. Status code: {response.status_code} {response.json()}")

def _show_all_sessions():
    r = _get(f'{SECRET_KEY}/show-all-sessions')
    return r['response']

def _status_session(sessionName, token):
    r = _get(f'{sessionName}/status-session', token)
    return r['status']

def _start_session(sessionName, token, webhook=None):
    return _post('start-session', sessionName, token, waitQrCode=True, webhook=webhook)

def send_message(sessionName, phone, message):
    return _post('send-message', sessionName, TOKENS[sessionName], expectCode=201, phone=phone, message=message, isGroup=False, isNewsletter=False)

def send_group_message(sessionName, phone, message):
    return _post('send-message', sessionName, TOKENS[sessionName], expectCode=201, phone=phone, message=message, isGroup=True, isNewsletter=False)

def send_image(sessionName, phone, filename, caption, base64):
    return _post('send-image', sessionName, TOKENS[sessionName], expectCode=201, phone=phone, filename=filename, caption=caption, base64=base64, isGroup=False, isNewsletter=False)

def list_chats(sessionName, onlyGroups):
    return _post('list-chats', sessionName, TOKENS[sessionName], onlyGroups=onlyGroups)

def get_messages(sessionName, phone, count):
    r = _get(f'{sessionName}/get-messages/{phone}', TOKENS[sessionName], count=count)
    return [{
        "id": o.get("id"),
        "body": o.get("body"),
        "content": o.get("content"),
        "type": o.get("type"),
        "t": o.get("t"),
        "senderName": (o.get("sender") or {}).get("name"),
        "author": o.get("author"),
    } for o in r['response']]

def _post(command, sessionName, token, expectCode=200, **kwargs):
    url = f"{BASE_URL}/api/{sessionName}/{command}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.post(url, headers=headers, json=kwargs)
    if response.status_code == expectCode:
        return response.json()
    else:
        raise Exception(f"Error. Status code: {response.status_code} {response.json()}")

def _get(command, token=None, **kwargs):
    url = f"{BASE_URL}/api/{command}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(url, headers=headers, params=kwargs)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error. Status code: {response.status_code} {response.json()}")

def _saveToFile(base64_string, path):
    if base64_string.startswith('data:image/png;base64,'):
        base64_string = base64_string.split(',')[1]
    image_data = base64.b64decode(base64_string)
    with open(path, 'wb') as file:
        file.write(image_data)


if __name__ == "__main__":
    # base64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA'
    base64 = "data:image/png;base64,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"
    start_session('jarbas')
    send_image('jarbas', '5512981440013', 'imagem.jpg', 'olha isso', base64)
