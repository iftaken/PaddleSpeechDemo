# todo:
# 1. 开启服务
# 2. 接收录音音频，返回识别结果
# 3. 接收ASR识别结果，返回NLP对话结果
# 4. 接收NLP对话结果，返回TTS音频

import base64
import os
import json
import datetime

import uvicorn
import aiofiles
from typing import Optional, List 
from pydantic import BaseModel
from fastapi import FastAPI, Header, File, UploadFile, Form, Cookie, WebSocket, WebSocketDisconnect
from starlette.responses import FileResponse
from fastapi.responses import StreamingResponse
from starlette.websockets import WebSocketState as WebSocketState

from src.AudioManeger import AudioMannger
from src.util import *
from src.robot import Robot
from src.WebsocketManeger import ConnectionManager

from paddlespeech.server.engine.asr.online.asr_engine import PaddleASRConnectionHanddler


tts_config = "PaddleSpeech/demos/streaming_tts_server/conf/tts_online_application.yaml"
asr_config = "PaddleSpeech/demos/streaming_asr_server/conf/ws_conformer_application.yaml"
asr_init_path = "source/demo/demo_16k.wav"

app = FastAPI()
chatbot = Robot(asr_config, tts_config, asr_init_path)
# chatbot.init()
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
    # now_name = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S') + randName() + ".pcm"
    # out_file_path = os.path.join(source_dir, now_name)
    # async with aiofiles.open(out_file_path, 'wb') as out_file:
        # await out_file.write(audios.audios)  # async write
    # print(f"接收的数据流大小: {len(audios.audios)}")
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


# 聊天用的ASR
@app.websocket("/ws/asr/offlineStream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            asr_res = None
            # websocket 不接收，只推送
            data = await websocket.receive_bytes()
            # 前端收到数据
            # print("前端get")
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
        # await manager.broadcast(f"用户-{user}-离开")
        # print(f"用户-{user}-离开")


# Online识别的ASR
@app.websocket('/ws/asr/onlineStream')
async def websocket_endpoint(websocket: WebSocket):
    """PaddleSpeech Online ASR Server api

    Args:
        websocket (WebSocket): the websocket instance
    """

    #1. the interface wait to accept the websocket protocal header
    #   and only we receive the header, it establish the connection with specific thread
    await websocket.accept()

    #2. if we accept the websocket headers, we will get the online asr engine instance
    engine = chatbot.asr.engine

    #3. each websocket connection, we will create an PaddleASRConnectionHanddler to process such audio
    #   and each connection has its own connection instance to process the request
    #   and only if client send the start signal, we create the PaddleASRConnectionHanddler instance
    connection_handler = None

    try:
        #4. we do a loop to process the audio package by package according the protocal
        #   and only if the client send finished signal, we will break the loop
        while True:
            # careful here, changed the source code from starlette.websockets
            # 4.1 we wait for the client signal for the specific action
            assert websocket.application_state == WebSocketState.CONNECTED
            message = await websocket.receive()
            websocket._raise_on_disconnect(message)

            #4.2 text for the action command and bytes for pcm data
            if "text" in message:
                # we first parse the specific command
                message = json.loads(message["text"])
                if 'signal' not in message:
                    resp = {"status": "ok", "message": "no valid json data"}
                    await websocket.send_json(resp)

                # start command, we create the PaddleASRConnectionHanddler instance to process the audio data
                # end command, we process the all the last audio pcm and return the final result
                #              and we break the loop
                if message['signal'] == 'start':
                    resp = {"status": "ok", "signal": "server_ready"}
                    # do something at begining here
                    # create the instance to process the audio
                    # connection_handler = chatbot.asr.connection_handler
                    connection_handler = PaddleASRConnectionHanddler(engine)
                    await websocket.send_json(resp)
                elif message['signal'] == 'end':
                    # reset single  engine for an new connection
                    # and we will destroy the connection
                    connection_handler.decode(is_finished=True)
                    connection_handler.rescoring()
                    asr_results = connection_handler.get_result()
                    connection_handler.reset()

                    resp = {
                        "status": "ok",
                        "signal": "finished",
                        'result': asr_results
                    }
                    await websocket.send_json(resp)
                    break
                else:
                    resp = {"status": "ok", "message": "no valid json data"}
                    await websocket.send_json(resp)
            elif "bytes" in message:
                # bytes for the pcm data
                message = message["bytes"]
                print("###############")
                print("len message: ", len(message))
                print("###############")

                # we extract the remained audio pcm 
                # and decode for the result in this package data
                connection_handler.extract_feat(message)
                connection_handler.decode(is_finished=False)
                asr_results = connection_handler.get_result()

                # return the current period result
                # if the engine create the vad instance, this connection will have many period results 
                resp = {'result': asr_results}
                print(resp)
                await websocket.send_json(resp)
    except WebSocketDisconnect:
        pass


@app.post("/nlp/chat")
async def chatOffline(nlp_base:NlpBase):
    chat = nlp_base.chat
    if not chat:
        return ErrorRequest(message="传入文本为空")
    else:
        res = chatbot.chat(chat)
        return SuccessRequest(result=res)

@app.post("/nlp/ie")
async def ieOffline(nlp_base:NlpBase):
    nlp_text = nlp_base.chat
    if not nlp_text:
        return ErrorRequest(message="传入文本为空")
    else:
        res = chatbot.ie(nlp_text)
        return SuccessRequest(result=res)

@app.post("/tts/offline")
async def text2speechOffline(tts_base:TtsBase):
    text = tts_base.text
    if not text:
        return ErrorRequest(message="文本为空")
    else:
        now_name = "tts_"+ datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S') + randName() + ".wav"
        out_file_path = os.path.join(source_dir, now_name)
        # 保存为文件，再转成base64传输
        chatbot.text2speech(text, outpath=out_file_path)
        with open(out_file_path, "rb") as f:
            data_bin = f.read()
        base_str = base64.b64encode(data_bin)
        return SuccessRequest(result=base_str)

@app.post("/tts/online")
async def stream_tts(request_body: TtsBase):
    text = request_body.text
    return StreamingResponse(chatbot.text2speechStream(text=text))


if __name__ == '__main__':
    uvicorn.run(app=app, host='0.0.0.0', port=8010)
    





