from dotenv import load_dotenv
load_dotenv()

import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
import os

# Initialize Sentry
SENTRY_DSN = os.getenv('SENTRY_DSN')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=1.0
    )


from logging_config import setup_logging
setup_logging()

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import jarbas
import zap
import llm
import logging
import json
from datetime import datetime
import zapgroup_svc
import transcribe_audio
logger = logging.getLogger(__name__)

app = FastAPI()

if SENTRY_DSN:
    app.add_middleware(SentryAsgiMiddleware)

def _start_zap():
    return zap.start_session('jarbas', webhook='http://172.17.0.1:8000/zap')

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/dapau")
def read_root():
    raise Exception("Dapau")

@app.get("/connect")
def connect():
    started, qrcode, status = _start_zap()
    if started or not qrcode:
        return {"status": status}
    elif qrcode:
        return _webpage_with_image(qrcode)

def _webpage_with_image(qrcode):
    if not qrcode.startswith("data:image/png;base64"):
        qrcode = f"data:image/png;base64,{qrcode}"
    html_content = f"""
    <html>
        <body>
            <h2>Scan the QR code to connect</h2>
            <img src="{qrcode}" alt="QR Code"/>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/zap")
async def got_zap(request: Request):
    headers = dict(request.headers)
    body = await request.json()
    # logger.info(f"Requisição POST recebida em /zap: {json.dumps(body, indent=2)}")
    event = body.get('event')
    isGroup = body.get("isGroupMsg") or (event == 'onrevokedmessage' and body.get('author'))
    msgType = body.get('type')
    ignore_events = {'onpresencechanged', 'onparticipantschanged', 'onreactionmessage'}
    if event in ignore_events:
        pass
    elif event == 'onmessage':
        if isGroup:
            ignoredTypes = {'ciphertext'}
            group_id = body['from']
            message_id = body['id']
            from_number = body['author']
            if msgType in ignoredTypes:
                pass
            elif msgType == 'chat':
                groupChat = {
                    'group_id': group_id,
                    'message_id': message_id,
                    'message_type': 'chat',
                    'message_body': body['body'],
                    'from_number': from_number,
                    'from_name': body['notifyName'],
                    'timestamp': datetime.fromtimestamp(body['t']),
                }
                zapgroup_svc.save_group_chat(groupChat)
            elif msgType == 'image':
                try:
                    imgDescription = _describe_image(body['body'])
                except Exception as e:
                    print(f"Error describing image: {e}")
                    imgDescription = f"[IMG ERROR] {e}"
                caption = body.get('caption', '')
                message_body = f"{caption}\n----------- IMAGE -----------\n{imgDescription}"
                groupChat = {
                    'group_id': group_id,
                    'message_id': message_id,
                    'message_type': 'image',
                    'message_body': message_body,
                    'from_number': from_number,
                    'from_name': body['notifyName'],
                    'timestamp': datetime.fromtimestamp(body['t']),
                }
                zapgroup_svc.save_group_chat(groupChat)
            elif msgType == 'ptt':
                audio_base64 = body['body']
                try:
                    transcribed = transcribe_audio.transcribe(audio_base64)
                except Exception as e:
                    logger.error(f"Erro ao transcrever áudio: {e}")
                    transcribed = f"AUDIO TRANSCRIBE ERROR: {e}"
                groupChat = {
                    'group_id': group_id,
                    'message_id': message_id,
                    'message_type': 'audio',
                    'message_body': transcribed,
                    'from_number': from_number,
                    'from_name': body['notifyName'],
                    'timestamp': datetime.fromtimestamp(body['t']),
                }
                zapgroup_svc.save_group_chat(groupChat)
            elif msgType == 'gp2':
                msgSubtype = body.get('subtype')
                if msgSubtype == 'remove':
                    from_name = body.get('sender', {}).get('pushname', 'UKNKOWN_AUTHOR')
                    recipient_numbers = ', '.join(body.get('recipients', []))
                    message_body = f"[ADMIN_ACTION] {from_name} removeu {recipient_numbers}"
                    groupChat = {
                        'group_id': group_id,
                        'message_id': message_id,
                        'message_type': 'removeuser',
                        'message_body': message_body,
                        'from_number': from_number,
                        'from_name': from_name,
                        'timestamp': datetime.fromtimestamp(body['t']),
                    }
                    zapgroup_svc.save_group_chat(groupChat)
                else:
                    print('--- group chat gp2')
                    print(json.dumps(body, indent=2))
            else:
                print('--- group chat of unknown type')
                print(json.dumps(body, indent=2))
                # jarbas.got_group_chat(groupfrom, msgfrom, senderName, text, t)
        else:
            if msgType == 'chat':
                text = body['body']
                t = body['t']
                msgfrom = body['from']
                jarbas.got_chat(msgfrom, text, t)
            elif msgType == 'ptt':
                msgfrom = body['from']
                audio_base64 = body['body']
                t = body['t']
                jarbas.got_audio(msgfrom, audio_base64, t)
            elif msgType == 'image':
                msgfrom = body['from']
                img_base64 = body['body']
                caption = body.get('caption', '')
                t = body['t']
                jarbas.got_chat(msgfrom, caption, t, img_base64)
            else:
                print('--- unknown onmessage')
                print(json.dumps(body, indent=2))
    elif event == 'onrevokedmessage':
        if isGroup:
            zapgroup_svc.deleted_message(body['from'], body['refId'])
        else:
            pass # nada a fazer
    else:
        print('--- unknown event')
        print(json.dumps(body, indent=2))
    return {"status": "OK"}

def main():
    logger.info("Iniciando a aplicação")
    _start_zap()
    import uvicorn
    logger.info("Iniciando o servidor Uvicorn")
    uvicorn.run(app, host="0.0.0.0", port=8000)


def _describe_image(image_base64):
    messages = [
        {"role": "user", "content": "Escreva uma descrição para esta imagem. Em português.", "images": [image_base64]},
    ]
    response = llm.chat_completions_ollama(messages, 'llava-llama3')
    return response['content']


if __name__ == "__main__":
    main()
