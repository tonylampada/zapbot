import os
import requests
import base64

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

def status_session(sessionName, token):
    r = _get(f'{sessionName}/status-session', token)
    return r['status']

def start_session(sessionName, token, webhook=None):
    return _post('start-session', sessionName, token, waitQrCode=True, webhook=webhook)

def saveToFile(base64_string, path):
    if base64_string.startswith('data:image/png;base64,'):
        base64_string = base64_string.split(',')[1]
    image_data = base64.b64decode(base64_string)
    with open(path, 'wb') as file:
        file.write(image_data)

def gera_qrcode_mas_nao_loga():
    token = generate_token('jarbas')
    print("token", token)
    status = status_session('jarbas', token)
    newsession = start_session('jarbas', token)
    qrcode = newsession['qrcode']
    saveToFile(qrcode, './qrcode_zoado.png')

if __name__ == '__main__':
    gera_qrcode_mas_nao_loga()