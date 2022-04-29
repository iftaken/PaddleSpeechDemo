# Paddle Speech Demo

vue实现录音参考资料：https://blog.csdn.net/qq_41619796/article/details/107865602#t1

前端流式播放音频参考仓库：

https://github.com/AnthumChris/fetch-stream-audio
https://bm.enthuses.me/buffered.php?bref=6677

## 前端

```shell
cd PaddleSpeechWebClient

# 安装依赖
yarn install

# 测试
yarn dev

```


## 后端

```shell
# 启动服务
# 安装paddlespeech (声纹的接口代码还没有合，接口改了)
git clone https://github.com/PaddlePaddle/PaddleSpeech.git
cd PaddleSpeech
pip install .

# 现在本地环境中安装 paddlepaddle 2.2.2
# 本地音频服务 （端到端的就先走自己的服务）
python main.py

# paddlespeech 流式服务

# 流式 tts
cd paddlespeech/server
python bin/main.py --config_file conf/tts_online_application.yaml

# 流式 asr
cd paddlespeech/server
python bin/main.py --config_file conf/ws_conformer_application.yaml

# 声纹识别服务
# 参照 https://github.com/PaddlePaddle/PaddleSpeech/tree/develop/demos/audio_searching
# 构建好 docker开启服务后
cd PaddleSpeech/demos/audio_searching/
python src/vpr_search.py
```

## todo

1. BUG: 流式TTS播放不连贯，有爆破音
2. BUG: 聊天页面响应速度慢，有时候会重复播放多个tts音频
3. Function: ASR增加音频上传功能
4. Function: VPR增加录音下载功能
5. BUG: ASR 流式识别和端到端识别串在一起
