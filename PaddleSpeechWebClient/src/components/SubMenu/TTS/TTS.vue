<template>
    <div class="ttsbox">
        <!-- <el-button type="success" @click="getTts(ttsd)" style="margin:1vw;"> TTS </el-button> -->
        <!-- <el-button type="success" @click="getTtsChunk(ttsText)" style="margin:1vw;"> 流式TTS Old</el-button> -->
        <!-- <el-button type="success" @click="getTtsChunkNew(ttsText)" style="margin:1vw;"> 流式TTS New</el-button> -->
        <el-button type="success" @click="getTtsChunkWav(ttsText)" style="margin:1vw;"> 流式TTS Wav</el-button>
        <el-button type="success" @click="getTtsChunkWavWS(ttsText)" style="margin:1vw;"> 流式TTS WS</el-button>

        <el-button type="success" @click="getTts(ttsText)" style="margin:1vw;"> 端到端TTS </el-button>
        
        <el-input v-model="ttsText"  
           :autosize="{ minRows: 2, maxRows: 4 }"
           type="textarea"
           placeholder="Please input"></el-input>
    </div>
</template>

<script>
import Recorder from 'js-audio-recorder'

// 全局承接流式 chunk 块
var chunks = []
var AudioContext = window.AudioContext || window.webkitAudioContext;
var chunk_index = 0
var source = ''
var reciveOver = false
var palyIndex = 0

// 定义播放相关函数
// 初始化播放器
var audioCtx = new AudioContext({
                latencyHint: 'interactive',
                sampleRate: 24000,
            });

// 定义流式播放函数
function playAudioDataChunkRead(inputChunk){
    chunks.push(inputChunk)
    if(wav_buffer){
        audioCtx.decodeAudioData(wav_buffer, buffer => {
            source = audioCtx.createBufferSource();
            // 定义播放结束的回调函数
            source.onended = () => {
                if(index < inputChunks.length - 1) {
                    // 播放下一块儿
                    playAudioDataChunk(inputChunks, index + 1)
                } else {
                    if(reciveOver) {
                        console.log("流式播放完毕")
                    } else {
                        console.log("等待数据")
                        if(index >= inputChunks.length - 1){

                        }
                        playAudioDataChunk(inputChunks, index)
                    }
                    }  
                }
            source.buffer = buffer
            // console.log('buffer', buffer)
            source.connect(audioCtx.destination);
            source.start();
        }, function(e) {
            // Recorder.throwError(e);
        });
    } 
}


// 定义流式播放函数
function playAudioDataChunk(inputChunks, index){
    var wav_buffer = inputChunks[index]
    if(wav_buffer){
        audioCtx.decodeAudioData(wav_buffer, buffer => {
            console.log(buffer)
            source = audioCtx.createBufferSource();
            // 定义播放结束的回调函数
            source.onended = () => {
                if(index < inputChunks.length - 1) {
                    // 播放下一块儿
                    // console.log("播放下一个")
                    playAudioDataChunk(inputChunks, index + 1)
                } else {
                    if(reciveOver) {
                        console.log("流式播放完毕")
                        _reset()
                    } else {
                        console.log("等待数据")
                        if(index >= inputChunks.length - 1){

                        }
                        playAudioDataChunk(inputChunks, index)
                    }
                    }  
                }
            source.buffer = buffer
            // console.log('buffer', buffer)
            source.connect(audioCtx.destination);
            source.start();
        }, function(e) {
            // Recorder.throwError(e);
        });
    } 
}

// 定义新的流式播放服务
var _audioSrcNodes = []
const _audioCtx = new (window.AudioContext || window.webkitAudioContext)({ latencyHint: 'interactive' });
var _playStartedAt = 0
var _totalTimeScheduled = 0

function _reset(){
    _playStartedAt = 0
    _totalTimeScheduled = 0
    _audioSrcNodes = []
}



function _schedulePlayback({channelData, length, numberOfChannels, sampleRate}) {
    const audioSrc = _audioCtx.createBufferSource(),
          audioBuffer = _audioCtx.createBuffer(numberOfChannels, length, sampleRate);
    // var audioBuffer = ""
    // _audioCtx.decodeAudioData(wavData).then(function(buffer){
    //     console.log("buffer", buffer)
    //     audioBuffer = buffer
    // })
    
    audioSrc.onended = () => {
      _audioSrcNodes.shift();

    };
    _audioSrcNodes.push(audioSrc);

    // Use performant copyToChannel() if browser supports it
    audioBuffer.copyToChannel(channelData, 0);

    let startDelay = 0;
    if (!_playStartedAt) {
      startDelay = 300 / 1000;
      _playStartedAt = _audioCtx.currentTime + startDelay;
    }
    // console.log(audioBuffer)
    audioSrc.buffer = audioBuffer;
    audioSrc.connect(_audioCtx.destination);
    
    const startAt = _playStartedAt + _totalTimeScheduled;
    audioSrc.start(startAt);

    _totalTimeScheduled+= audioBuffer.duration;
  }


function _schedulePlaybackWav({wavData, length, numberOfChannels, sampleRate}) {
    audioCtx.decodeAudioData(wavData, audioBuffer => {
            // console.log(audioBuffer)
            const audioSrc = _audioCtx.createBufferSource()
            audioSrc.onended = () => {
                _audioSrcNodes.shift();
                };
            _audioSrcNodes.push(audioSrc);
            let startDelay = 0;
            if (!_playStartedAt) {
                startDelay = 10 / 1000;
                _playStartedAt = _audioCtx.currentTime + startDelay;
                }
            audioSrc.buffer = audioBuffer;
            audioSrc.connect(_audioCtx.destination);
            
            // console.log("_playStartedAt", _playStartedAt)
            const startAt = _playStartedAt + _totalTimeScheduled;
            // console.log("startAt", startAt)
            audioSrc.start(startAt);

            _totalTimeScheduled+= audioBuffer.duration;

        })

    
        //   audioBuffer = _audioCtx.createBuffer(numberOfChannels, length, sampleRate);
    // var audioBuffer = ""
    // console.log(wavData)
    // _audioCtx.decodeAudioData(wavData).then(function(decodedData){
    //     console.log("buffer", decodedData)
    //     audioBuffer = decodedData
    // })
    
    // audioSrc.onended = () => {
    //   _audioSrcNodes.shift();

    // };
    // _audioSrcNodes.push(audioSrc);

    // Use performant copyToChannel() if browser supports it
    // audioBuffer.copyToChannel(channelData, 0);

    
  }





// base64转换
function base64ToUint8Array(base64String) {
            const padding = '='.repeat((4 - base64String.length % 4) % 4);
            const base64 = (base64String + padding)
                            .replace(/-/g, '+')
                            .replace(/_/g, '/');

            const rawData = window.atob(base64);
            const outputArray = new Uint8Array(rawData.length);

            for (let i = 0; i < rawData.length; ++i) {
                    outputArray[i] = rawData.charCodeAt(i);
            }
            return outputArray;
            }
    export default {
        name: "TTS",
        data(){
            return {
                ttsText: '山有木兮木有枝，心悦君兮君不知。人生若只如初见，何事秋风悲画扇。十年生死两茫茫，不思量，自难忘。曾经沧海难为水，除却巫山不是云。',
                audioCtx: '',
                source: '',
                typedArray: '',
                ttsResult: '',
                ws: ''
            }
        },
        mounted () {
            this.audioCtx = new AudioContext({
                latencyHint: 'interactive',
                sampleRate: 24000,
            });
            this.audioCtx.onstatechange = function() {
            console.log("hhhh");
            };
            this.audioCtx.onplayend = function() {
            console.log("播放结束")
            }
            this.source = this.audioCtx.createBufferSource();
            this.source.onended = () => {
                console.log("播放结束hhhhhhh")
                }
            
            this.ws = new WebSocket("ws://localhost:8010/ws/tts/online")
            this.ws.addEventListener('message', function (event) {
                var temp = JSON.parse(event.data);
                console.log("ws_tts_chunk:", temp.done)
                // 接收的数据刷进播放器
                if(!temp.done){
                    var chunk = temp.wav
                    var arraybuffer = base64ToUint8Array(chunk)
                    var view = new DataView(arraybuffer.buffer);
                    console.log('tts chunk data', view)
                    
                    var length = view.buffer.byteLength / 2
                    
                    view = Recorder.encodeWAV(view, 24000, 24000, 1, 16, true) 
                    _schedulePlaybackWav({
                        wavData: view.buffer,
                        length: length,
                        numberOfChannels: 1,
                        sampleRate: 24000
                    })
                } else {
                    reciveOver = true
                    // _reset()
                } 

            })

            },
        methods: {
          base64ToUint8Array(base64String) {
            const padding = '='.repeat((4 - base64String.length % 4) % 4);
            const base64 = (base64String + padding)
                            .replace(/-/g, '+')
                            .replace(/_/g, '/');

            const rawData = window.atob(base64);
            const outputArray = new Uint8Array(rawData.length);

            for (let i = 0; i < rawData.length; ++i) {
                    outputArray[i] = rawData.charCodeAt(i);
            }
            return outputArray;
            },
        // 流式获取TTS数据
        onChunkedResponseComplete(){
            console.log('all done')
        },
        processChunkedResponse(response){
            console.log("chunk response", response)
            var text = '';
            var reader = response.body.getReader()
            var decoder = new TextDecoder();

            return readChunk()

            function readChunk() {
                return reader.read().then(appendChunks)
            }

            function appendChunks(result) {
                var chunk = decoder.decode(result.value);
                if(chunk.length > 0) {
                    // 非空
                    // 解码转换，添加wav文件头
                    var arraybuffer = base64ToUint8Array(chunk)
                    let view = new DataView(arraybuffer.buffer);
                    view = Recorder.encodeWAV(view, 24000, 24000, 1, 16, true)
                    chunks.push(view.buffer)
                    if(chunk_index === 0) {
                        // 启动流式播放
                        playAudioDataChunk(chunks, chunk_index)
                    }
                    chunk_index += 1
                    // console.log(chunks)
                }
                
                if (result.done) {
                    return text;
                } else {
                    return readChunk();
                }
            }
        },
        onChunkedResponseError(err){
            console.error(err)
        },

        async getTtsChunkWav(nlpText){
            // base64
            // 初始化 chunks
            chunks = []
            chunk_index = 0
            reciveOver = false
            _reset()
            // 初始化播放
            let ttsPara = {
                text: nlpText,
                spk_id: 0,
                speed: 1.0,
                volume: 1.0,
                sample_rate: 0,
                save_path: ''
            }
            
            var request = new Request('/api/tts/online', {
                method: 'POST',
                headers: new Headers({
                    'Content-Type': 'application/json'
                }),
                body: JSON.stringify(ttsPara)
            });
            // 使用 XMLHttpRequest
            // const xhr = new XMLHttpRequest();

            // 使用fetch流式获取数据
            const response = await fetch(request)
            const decoder = new TextDecoder();
            const reader = response.body.getReader(),
                contentLength = response.headers.get('content-length'), // requires CORS access-control-expose-headers: content-length
                totalBytes = contentLength? parseInt(contentLength, 10) : 0;

            // 异步获取数据
            const read = async () => {
                const { value, done } = await reader.read()               
                if (!done) {
                    console.log("value length: ", value.length)

                    var chunk = decoder.decode(value)
                    console.log("chunk length: ", chunk.length)
                    var arraybuffer = base64ToUint8Array(chunk)
                    var view = new DataView(arraybuffer.buffer);
                    console.log('tts chunk data', view)
                    
                    var length = view.buffer.byteLength / 2
                    
                    view = Recorder.encodeWAV(view, 24000, 24000, 1, 16, true) 
                    _schedulePlaybackWav({
                        wavData: view.buffer,
                        length: length,
                        numberOfChannels: 1,
                        sampleRate: 24000
                    })
                    return read();
                } else {
                    reciveOver = true
                    _reset()
                }
            }
            read()
        },

        async getTtsChunkWavWS(nlpText){
            // 初始化 chunks
            chunks = []
            chunk_index = 0
            reciveOver = false
            _reset()
            this.ws.send(nlpText)
        },


        // 合成TTS音频
        async getTts(nlpText){
            this.ttsResult = await this.$http.post("/api/tts/offline", { text : nlpText});
            this.typedArray = this.base64ToUint8Array(this.ttsResult.data.result)
            this.playAudioData( this.typedArray.buffer )
        },  
        playAudioData( wav_buffer ) {
        this.audioCtx.decodeAudioData(wav_buffer, buffer => {
            this.source = this.audioCtx.createBufferSource();
            this.source.buffer = buffer
            // console.log('buffer', buffer)
            // debugger
            // 连接扬声器设备
            this.source.connect(this.audioCtx.destination);
            this.source.start();
        }, function(e) {
            // Recorder.throwError(e);
        });
        },
        },
        
    }
</script>

<style lang='less' scoped>
 .ttsbox {
  border: 4px solid #F00;
//   position: fixed;
  top:60%;
  width: 100%;
  height: 20%;
  overflow: auto;
 }
</style>