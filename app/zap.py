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
        return True
    sessions = _show_all_sessions()
    logger.info(f"sessions: {sessions}")
    token = _generate_token(sessionName)
    logger.info(f"token: {token}")
    status = _status_session(sessionName, token)
    logger.info(f"status: {status}")
    if status != 'CONNECTED':
        newsession = _start_session(sessionName, token, webhook)
        qrcode = newsession['qrcode']
        _saveToFile(qrcode, './data/qrcode.png')
        logger.info("saved qrcode")
        return False
    TOKENS[sessionName] = token
    return True

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
