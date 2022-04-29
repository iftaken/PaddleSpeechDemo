# todo:
# 1. 开启服务
# 2. 接收录音音频，返回识别结果
# 3. 接收ASR识别结果，返回NLP对话结果
# 4. 接收NLP对话结果，返回TTS音频
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
from AudioManeger import AudioMannger
import base64


app = FastAPI()
chatbot = Robot()
chatbot.init()
manager = ConnectionManager()
aumanager = AudioMannger(chatbot)
aumanager.init()


class NlpBase(BaseModel):
    chat: str

class TtsBase(BaseModel):
    text: str 

class Audios:
    def __init__(self) -> None:
        self.audios = b""

audios = Audios()

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
    audios.audios += audio_bin
    print(f"audios长度变化: {len(audios.audios)}")
    return SuccessRequest(message="接收成功")

# 采集环境噪音大小
@app.post("/asr/collectEnv")
async def collectEnv(files: List[UploadFile]):
     for file in files[:1]:
        content = await file.read()  # async read
        # 初始化, wav 前44字节是头部信息
        aumanager.compute_env_volume(content[44:])
        return SuccessRequest(message="采集环境噪音成功")

# 停止录音
@app.get("/asr/stopRecord")
async def stopRecord():
    now_name = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S') + randName() + ".pcm"
    out_file_path = os.path.join(source_dir, now_name)
    async with aiofiles.open(out_file_path, 'wb') as out_file:
        await out_file.write(audios.audios)  # async write
    print(f"接收的数据流大小: {len(audios.audios)}")
    audios.audios = b""
    aumanager.stop()
    print("Online录音暂停")
    return SuccessRequest(message="停止成功")

# 恢复录音
@app.get("/asr/resumeRecord")
async def resumeRecord():
    aumanager.resume()
    print("Online录音恢复")
    return SuccessRequest(message="Online录音恢复")


# websocket 传递识别文本
@app.websocket("/ws/{user}")
async def websocket_endpoint(websocket: WebSocket, user: str):
    await manager.connect(websocket)

    try:
        while True:
            asr_res = None
            # websocket 不接收，只推送
            
            data = await websocket.receive_bytes()
            # 前端收到数据
            print("前端get")
            # 用 websocket 流式接收音频数据
            if not aumanager.is_pause:
                asr_res = aumanager.stream_asr(data)
            else:
                print("录音暂停")
            if asr_res:
                await manager.send_personal_message(asr_res, websocket)
                aumanager.clear_asr()

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"用户-{user}-离开")
        print(f"用户-{user}-离开")


@app.post("/nlp/chat")
async def chatOffline(nlp_base:NlpBase):
    chat = nlp_base.chat
    if not chat:
        return ErrorRequest(message="传入文本为空")
    else:
        res = chatbot.chat(chat)
        return SuccessRequest(result=res)


@app.post("/tts/offline")
async def text2speechOffline(tts_base:TtsBase):
    text = tts_base.text
    if not text:
        return ErrorRequest(message="文本为空")
    else:
        now_name = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S') + randName() + ".wav"
        out_file_path = os.path.join(source_dir, now_name)
        chatbot.text2speech(text, outpath=out_file_path)
        with open(out_file_path, "rb") as f:
            data_bin = f.read()
        base_str = base64.b64encode(data_bin)
        return SuccessRequest(result=base_str)



if __name__ == '__main__':
    uvicorn.run(app=app, host='0.0.0.0', port=8010)
    





