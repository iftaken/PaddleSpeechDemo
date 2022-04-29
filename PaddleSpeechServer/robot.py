from paddlenlp import Taskflow
from paddlespeech.cli.tts.infer import TTSExecutor
from paddlespeech.cli.asr.infer import ASRExecutor
import os
import librosa
import soundfile as sf
import logging
    
    

class Robot:
    def __init__(self) -> None:
        self.asr_model = ASRExecutor()
        self.chat_model = Taskflow("dialogue")
        self.tts_model = TTSExecutor()
        
        self.asr_name = "conformer_wenetspeech"
        self.am_name = "fastspeech2_csmsc"
        self.voc_name = "mb_melgan_csmsc"
        
        self.logger = logging.getLogger("Robot")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        # 日志输出格式
        self.formatter = logging.Formatter('[%(asctime)s] - %(levelname)s: %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(self.formatter)
        self.logger.addHandler(ch)

    
    def init(self): 
        # tts init
        self.logger.info("语音合成 服务初始化")
        text = "今天天气真好"
        wavDir = os.path.join(os.path.dirname(__file__),'../wav')
        self.wavDir = wavDir
        if not os.path.exists(wavDir):
            os.makedirs(wavDir)
        outpath = os.path.join(wavDir, 'demo.wav')
        self.tts_model(text, am=self.am_name, voc=self.voc_name, output=outpath)
        
        # asr init
        self.logger.info("语音识别 服务初始化")
        wav,_ = librosa.load(outpath, sr=16000)
        outpath_16k = os.path.join(wavDir, 'demo_16k.wav')
        sf.write(outpath_16k, wav, 16000)
        result = self.asr_model(outpath_16k, model=self.asr_name,lang='zh',
                 sample_rate=16000)
        self.logger.info(f"初始化识别结果: {result}")
        
        # audio init
        self.logger.info("录音功能初始化")
        
        self.tts_outpath = os.path.join(self.wavDir, 'tts.wav')
        self.record_path = os.path.join(self.wavDir, 'record.wav')
        
        self.logger.info("初始化服务完成")
        

    def speech2text(self, audio_file):
        self.asr_model.preprocess(self.asr_name, audio_file)
        self.asr_model.infer(self.asr_name)
        res = self.asr_model.postprocess()
        return res
    
    def text2speech(self, text, outpath):
        try:
            self.tts_model.infer(text=text, lang="zh", am=self.am_name, spk_id=0)
            res = self.tts_model.postprocess(output=outpath)
        except Exception as e:
            print(e)
            res = None
        return res

    def chat(self, text):
        result = self.chat_model([text])
        return result[0]
    


if __name__ == '__main__':
    robot = Robot()
    robot.init()
    # robot.start()
    # res = robot.speech2text("resource/demo_16k.wav")
    # print(res)
    res = robot.chat("今天天气真不错")
    print(res)
    
    