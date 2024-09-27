import requests
import os
import json
import logging
import ollama
logger = logging.getLogger(__name__)
from datetime import datetime


BASE_URL = os.getenv('IMGEN_BASE_URL', 'http://localhost:8001') # github.com/tonylampada/imgen

def generate(prompt):
    return _get('generate', prompt=prompt)


def _get(command, **kwargs):
    url = f"{BASE_URL}/{command}"
    response = requests.get(url, params=kwargs)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Error. Status code: {response.status_code} {response.text}")


if __name__ == '__main__':
    s = generate("A beautiful landscape with a river and mountains in the background")
    print(s[:100])
