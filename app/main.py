from dotenv import load_dotenv
load_dotenv()

from logging_config import setup_logging
setup_logging()

from fastapi import FastAPI, Request
import jarbas
import zap
import logging
import json
from datetime import datetime
import zapgroup_svc
import transcribe_audio
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/zap")
async def got_zap(request: Request):
    headers = dict(request.headers)
    body = await request.json()
    # logger.info(f"Requisição POST recebida em /zap: {json.dumps(body, indent=2)}")
    event = body.get('event')
    isGroup = body.get("isGroupMsg") or (event == 'onrevokedmessage' and body.get('author'))
    msgType = body.get('type')
    if event == 'onmessage':
        if isGroup:
            if msgType == 'chat':
                groupChat = {
                    'group_id': body['from'],
                    'message_id': body['id'],
                    'message_type': 'chat',
                    'message_body': body['body'],
                    'from_number': body['author'],
                    'from_name': body['notifyName'],
                    'timestamp': datetime.fromtimestamp(body['t']),
                }
                zapgroup_svc.save_group_chat(groupChat)
            elif msgType == 'image':
                groupChat = {
                    'group_id': body['from'],
                    'message_id': body['id'],
                    'message_type': 'image',
                    'message_body': body.get('caption', ''),
                    'from_number': body['author'],
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
                    'group_id': body['from'],
                    'message_id': body['id'],
                    'message_type': 'audio',
                    'message_body': transcribed,
                    'from_number': body['author'],
                    'from_name': body['notifyName'],
                    'timestamp': datetime.fromtimestamp(body['t']),
                }
                zapgroup_svc.save_group_chat(groupChat)
            else:
                print('--- group chat')
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
    if not zap.start_session('jarbas', webhook='http://172.17.0.1:8000/zap'):
        logger.error("Falha ao iniciar a sessão do Jarbas")
        return
    import uvicorn
    logger.info("Iniciando o servidor Uvicorn")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
