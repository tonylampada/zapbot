from dotenv import load_dotenv
load_dotenv()

from logging_config import setup_logging
setup_logging()

from fastapi import FastAPI, Request
import jarbas
import zap
import logging
import json
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
    if body['event'] == 'onmessage':
        if body['type'] == 'chat':
            text = body['body']
            t = body['t']
            isGroup = body["isGroupMsg"]
            if isGroup:
                groupfrom = body['from']
                msgfrom = body['author']
                senderName = body['sender']['formattedName']
                print('--- group chat')
                print(json.dumps(body, indent=2))
                # jarbas.got_group_chat(groupfrom, msgfrom, senderName, text, t)
            else:
                msgfrom = body['from']
                jarbas.got_chat(msgfrom, text, t)
        elif body['type'] == 'ptt':
            msgfrom = body['from']
            audio_base64 = body['body']
            t = body['t']
            jarbas.got_audio(msgfrom, audio_base64, t)
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
