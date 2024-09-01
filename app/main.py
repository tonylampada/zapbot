from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
import jarbas
import os
import zap

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/zap")
async def got_zap(request: Request):
    headers = dict(request.headers)
    body = await request.json()
    if body['event'] == 'onmessage':
        msgfrom = body['from']
        text = body['body']
        jarbas.got_zap(msgfrom, text)
    return {"status": "OK"}

def main():
    if not jarbas.start_session(webhook='http://172.17.0.1:8000/zap'):
        return
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()