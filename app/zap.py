import requests
import os

BASE_URL = os.getenv('WPPCONNECT_BASE_URL', 'http://localhost:21465')
SECRET_KEY = os.getenv('WPPCONNECT_SECRET_KEY')

def generate_token(sessionName):
    url = f"{BASE_URL}/api/{sessionName}/{SECRET_KEY}/generate-token"
    response = requests.post(url)
    if response.status_code == 201:
        r = response.json()
        return r['token']
    else:
        print(response)
        raise Exception(f"Failed to generate token. Status code: {response.status_code} {response.json()}")

def show_all_sessions():
    r = _get(f'{SECRET_KEY}/show-all-sessions')
    return r['response']

def status_session(sessionName, token):
    r = _get(f'{sessionName}/status-session', token)
    return r['status']

def start_session(sessionName, token, webhook=None):
    return _post('start-session', sessionName, token, waitQrCode=True, webhook=webhook)

def send_message(sessionName, token, phone, message):
    return _post('send-message', sessionName, token, expectCode=201, phone=phone, message=message, isGroup=False, isNewsletter=False)

def send_group_message(sessionName, token, phone, message):
    return _post('send-message', sessionName, token, expectCode=201, phone=phone, message=message, isGroup=True, isNewsletter=False)

def list_chats(sessionName, token):
    return _post('list-chats', sessionName, token)

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

def _get(command, token=None):
    url = f"{BASE_URL}/api/{command}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error. Status code: {response.status_code} {response.json()}")

if __name__ == '__main__':
    token = generate_token('jarbas')
    print("token", token)
    r = send_group_message('jarbas', token, '5512981440013-1574914013', 'olá classe')
    print("r", r)