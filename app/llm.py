import requests
import os

BASE_URL = os.getenv('LLM_BASE_URL', 'http://localhost:1234')

def get_models():
    return _get('v1/models')

def chat_completions(prompt, model='default-model'):
    messages = [{"role": "user", "content": prompt}]
    return _post('v1/chat/completions', messages=messages, model=model)

def completions(prompt, model='default-model'):
    return _post('v1/completions', prompt=prompt, model=model)

def embeddings(input_text, model='default-model'):
    return _post('v1/embeddings', input=input_text, model=model)

def _post(command, expectCode=200, **kwargs):
    url = f"{BASE_URL}/{command}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    response = requests.post(url, headers=headers, json=kwargs)
    if response.status_code == expectCode:
        return response.json()
    else:
        raise Exception(f"Error. Status code: {response.status_code} {response.json()}")

def _get(command):
    url = f"{BASE_URL}/{command}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error. Status code: {response.status_code} {response.json()}")

def _dummy_test():
    prompt = "Hello, how are you?"
    try:
        response = chat_completions(prompt)
        print("Response:", response)
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    _dummy_test()
