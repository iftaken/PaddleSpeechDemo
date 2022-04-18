<template>
  <div class="home" style="margin:1vw;">
    <el-button :type="recoType" @click="startRecorder()"  style="margin:1vw;">{{ recoText }}</el-button>
    <el-button :type="playType" @click="playRecorder()" style="margin:1vw;"> {{ playText }}</el-button>
  </div>
  <div>
    <h1>{{asrResult}}</h1>
  </div>
</template>
 
<script>
import Recorder from 'js-audio-recorder'
  const recorder = new Recorder({
    sampleBits: 16,                 // 采样位数，支持 8 或 16，默认是16
    sampleRate: 16000,              // 采样率，支持 11025、16000、22050、24000、44100、48000，根据浏览器默认值，我的chrome是48000
    numChannels: 1,                 // 声道，支持 1 或 2， 默认是1
    compiling: true
  })
 
  // 绑定事件-打印的是当前录音数据

  export default {
    name: 'home',
    data () {
      return {
        recoType: "primary",
        recoText: "开始录音",
        playType: "success",
        playText: "播放录音",
        asrResult: "ASR识别结果：",
        webSocketRes: "websocket",
        drawRecordId: null,

        onReco: false,
        onPlay: false,
        ws: '',
       
      }
    },
    mounted () {
        // 定义 play
        recorder.onplayend = () => {
        this.onPlay = false
        this.playText = "播放录音"
        this.playType = "success"
        this.$nextTick(()=>{})
      }
      // 初始化ws
      this.ws = new WebSocket("ws://localhost:8010/ws/user1");

      // 定义消息处理逻辑
      this.ws.addEventListener('message', function (event) {
          console.log('Message from server ', event.data);
      });
      // this.$nextTick(()=>{})
    },
    methods: {
      // 开始录音
      startRecorder () {
        if(!this.onReco){
          recorder.start().then(() => {
            // this.drawRecord()
            setInterval(() => {
              // 持续录音
              let newData = recorder.getNextData();
              if (!newData.length) {
                return;
              }
              this.uploadChunk(newData)
            }, 500)
        }, (error) => {
          console.log("录音出错");
        })
        this.onReco = true
        this.recoType = "danger"
        this.recoText = "结束录音"
        this.$nextTick(()=>{
          })
        } else {
          // 结束录音
          recorder.stop()
          this.drawRecordId && cancelAnimationFrame(this.drawRecordId);
          this.drawRecordId = null;

          this.onReco = false
          this.recoType = "primary"
          this.recoText = "开始录音"
          this.$nextTick(()=>{})
          // 音频导出成wav,然后上传到服务器
          const wavs = recorder.getWAVBlob()
          this.uploadFile(wavs)
          console.log(wavs)
        }
        
      },

      // 录音播放
      playRecorder () {
        if(!this.onPlay){
          // 播放音频
          recorder.play()
          this.onPlay = true
          this.playText = "结束播放"
          this.playType = "warning"
          this.$nextTick(()=>{})
        
        } else {
          recorder.stopPlay()
          this.onPlay = false
          this.playText = "播放录音"
          this.playType = "success"
          this.$nextTick(()=>{})
        }
      },

      // 上传录音文件
      async uploadFile(file){
        const formData = new FormData()
        formData.append('files', file)
        const result = await this.$http.post("/api/asr/offline", formData);
        if (result.data.code === 0) {
              this.asrResult = result.data.result
              this.$message.success(result.data.message);
          } else {
              this.$message.error(result.data.message);
          }
      },
      // 上传chunk语音包
      async uploadChunk(chunkDatas) {
        const formData = new FormData()
        chunkDatas.forEach((chunkData) => {
                var nextBlobData = new Blob([chunkData.buffer], { type: 'audio/pcm' });
                formData.append('files', nextBlobData)
              })
        const result = await this.$http.post("/api/asr/online1", formData);
        if (result.data.code === 0) {
            console.log("chunk 发送成功")
          } else {
            console.log("chunk 发送失败")
          }
      }
      
    },
 
  }
</script>
 
<style lang='less' scoped>
 
</style>