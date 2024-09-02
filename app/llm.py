import requests
import os

# BASE_URL = os.getenv('LLM_BASE_URL', 'http://localhost:1234') # LM studio
BASE_URL = os.getenv('LLM_BASE_URL', 'http://localhost:11434') # ollama

def get_models():
    return _get('v1/models')

def chat_completions(messages, model='default-model'):
    return _post('v1/chat/completions', messages=messages, model=model)

def chat_completions_ollama(messages, model='llama3'):
    print("model", model)
    r = _post('api/chat', messages=messages, model=model, stream=False)
    return r['message']

def embeddings(input_text, model='default-model'):
    return _post('v1/embeddings', input=input_text, model=model)

def _post(command, expectCode=200, **kwargs):
    url = f"{BASE_URL}/{command}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    response = requests.post(url, headers=headers, json=kwargs)
    print(response.status_code)
    a = response.text
    print("a", a)
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
    try:
        messages = [
            # {"role": "user", "content": "Hello, how are you?"},
            # {
            #     "role": "assistant",
            #     "content": "I'm a large language model, so I don't have emotions or feelings like humans do. However, I're here to help and support you in any way I can. How about you? How's your day going?"
            # },
            # {"role": "user", "content": "Pretend you have."}
            # {"role": "user", "content": "Tell me a joke"},
            # {"role": "assistant", "content": "Why did the chicken cross the street? To get to the other side! Haha"},
            # {"role": "user", "content": "Another"},
        ]
        response = chat_completions_ollama(messages)
        import json
        print(json.dumps(response, indent=2))
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    _dummy_test()
