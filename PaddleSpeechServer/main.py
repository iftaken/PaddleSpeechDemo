# todo:
# 1. 开启服务
# 2. 接收录音音频，返回识别结果
# 3. 接收ASR识别结果，返回NLP对话结果
# 4. 接收NLP对话结果，返回TTS音频
from email.mime import audio
import imp
from telnetlib import Telnet
from pydantic import BaseModel
from typing import Optional, List 
import uvicorn
import os
from fastapi import FastAPI, Header, File, UploadFile, Form, Cookie, WebSocket, WebSocketDisconnect
from starlette.responses import FileResponse
from robot import Robot
from util import *
import aiofiles
import datetime
from queue import Queue
from WebsocketManeger import ConnectionManager


app = FastAPI()
chatbot = Robot()
chatbot.init()
manager = ConnectionManager()


class ChunkModel(BaseModel):
    chunk: str


vad_bd = -1
source_dir = "source"
if not os.path.exists(source_dir):
    os.makedirs(source_dir, exist_ok=True)


# 接收文件，返回ASR结果
# 上传文件
@app.post("/asr/offline")
async def speech2textOffline(files: List[UploadFile]):
    # 只有第一个有效
    asr_res = ""
    for file in files[:1]:
        # 生成时间戳
        now_name = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S') + randName() + ".wav"
        out_file_path = os.path.join(source_dir, now_name)
        # if file.filename.endswith(".wav"):
            # 只接收wav文件
            # 检查文件是否存在
        async with aiofiles.open(out_file_path, 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write

        # 返回ASR识别结果
        asr_res = chatbot.speech2text(out_file_path)
        return SuccessRequest(result=asr_res)
        # else:
            # return ErrorRequest(message="文件不是.wav格式")
    return ErrorRequest(message="上传文件为空")

# 流式接收测试
@app.post("/asr/online1")
async def speech2textOnlineRecive(files: List[UploadFile]):
    audio_bin = b''
    for file in files:
        content = await file.read()
        audio_bin += content
    print(f"接收的数据流大小: {len(audio_bin)}")
    return SuccessRequest(message="接收成功")

# websocket 传递识别文本
@app.websocket("/ws/{user}")
async def websocket_endpoint(websocket: WebSocket, user: str):

    await manager.connect(websocket)

    try:
        while True:
            # websocket 不接收，只推送
            data = await websocket.receive_bytes()
            # 用 websocket 流式接收音频数据
            # await manager.send_personal_message(f"你说了: {data}", websocket)
            # await manager.broadcast(f"用户:{user} 说: {data}")
            # print(f"你说了: {data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"用户-{user}-离开")
        print(f"用户-{user}-离开")


@app.post("/nlp/chat")
async def chatOffline(chat:str):
    if not chat:
        return ErrorRequest(message="传入文本为空")
    else:
        res = chatbot.chat(chat)
        return SuccessRequest(result=res)


@app.post("/tts")
async def text2speechOffline(text:str):
    if not text:
        return ErrorRequest(message="文本为空")
    else:
        now_name = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S') + randName() + ".wav"
        out_file_path = os.path.join(source_dir, now_name)
        chatbot.text2speech(text, outpath=out_file_path)
        # 把文件返回去
        return FileResponse(out_file_path, filename=now_name)



if __name__ == '__main__':
    uvicorn.run(app=app, host='0.0.0.0', port=8010)
    





