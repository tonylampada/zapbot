from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
import jarbas
import json

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/zap")
async def got_zap(request: Request):
    headers = dict(request.headers)
    body = await request.json()
    # print(json.dumps(body, indent=2))
    if body['event'] == 'onmessage':
        if body['type'] == 'chat':
            msgfrom = body['from']
            text = body['body']
            t = body['t']
            jarbas.got_chat(msgfrom, text, t)
        elif body['type'] == 'ptt':
            msgfrom = body['from']
            audio_base64 = body['body']
            t = body['t']
            jarbas.got_audio(msgfrom, audio_base64, t)
    return {"status": "OK"}

def main():
    if not jarbas.start_session(webhook='http://172.17.0.1:8000/zap'):
        return
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
