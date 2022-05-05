# Paddle Speech Demo

vue实现录音参考资料：https://blog.csdn.net/qq_41619796/article/details/107865602#t1

前端流式播放音频参考仓库：

https://github.com/AnthumChris/fetch-stream-audio
https://bm.enthuses.me/buffered.php?bref=6677

## 前端启动

```shell
cd PaddleSpeechWebClient

# 安装依赖
yarn install

# 测试
yarn dev

```


## 后端启动

```shell
# 启动服务
# 子模块初始化
git submodule update --init --recursive

# 安装 paddleSpeech
cd PaddleSpeechServer/PaddleSpeech
pip install .

# 安装 paddleNLP
cd PaddleSpeechServer/PaddleNLP
pip install .

# 启动 asr, tts, chat, ie 服务
cd PaddleSpeechServer
python main.py

# 现在本地环境中安装 paddlepaddle 2.2.2
# 本地音频服务 （端到端的就先走自己的服务）
python main.py

# 声纹识别服务
# 参照 https://github.com/PaddlePaddle/PaddleSpeech/tree/develop/demos/audio_searching
# 构建好 docker开启服务后
cd PaddleSpeech/demos/audio_searching/
# 构建镜像
docker-compose -f docker-compose.yaml up -d
# 开启声纹识别服务
python src/vpr_search.py
```

## todo

