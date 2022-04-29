import numpy as np
import struct
import os
import librosa
import wave
from paddlenlp import Taskflow
import cv2

def Bytes2Int16Slice(feature):
    x = []
    for i in range(len(feature)//2):
        data = feature[i * 2: (i * 2) + 2]
        a = struct.unpack('h', data)
        x.append(a[0])
    return x

def read_pcm(pcm_path):
    if os.path.exists(pcm_path):
        print(pcm_path)
    
    # 读取 pcm 数据为 numpy
    with open(pcm_path, "rb") as f:
        pcm_bin = f.read()
        
    print(len(pcm_bin))
    x = Bytes2Int16Slice(pcm_bin)
    x = np.array(x)
    print(x)
    
    x3 = np.frombuffer(pcm_bin, np.int16)
    print(x3)
    
    with open(pcm_path, "rb") as f:
        x2 = np.fromfile(f, np.int16)
    print(x2)

def read_bin_wav(wav_path):
    with open(wav_path, "rb") as f:
        data = f.read()
        print(len(data))
    pcm_bin = data[44:]
    print(len(pcm_bin) - len(data))
    x3 = np.frombuffer(pcm_bin, np.int16)
    print(x3)
    
    wav, sr = librosa.load(wav_path, sr=16000)
    print(wav)
    

def parse_wav(wav_path):
    f = wave.open(wav_path,"rb")
    params = f.getparams()  
    nchannels, sampwidth, framerate, nframes = params[:4]
    print(f"{nchannels, sampwidth, framerate, nframes}")
    str_data  = f.readframes(nframes)  
    f.close()
    wave_data = np.fromstring(str_data,dtype = np.short)
    print(wave_data[:20])
    print(wave_data.shape)
    
    wav, sr = librosa.load(wav_path, sr=24000)
    print(wav)
    print(wav.shape)
    print(sr)

def resize(png_path, out_path=None):
    img = cv2.imread(png_path)
    print(img.shape)
    img = cv2.resize(img,dsize=(int(img.shape[0]/4.5), int(img.shape[1]/4.5)), interpolation=cv2.INTER_LINEAR)
    print(img.shape)
    

if __name__ == '__main__':
    # pcm_path = "/Users/huangyiming02/Project/github/PaddleSpeechDemo/PaddleSpeechServer/source/20220418145230zrxia.wav"
    # read_bin_wav(pcm_path)
    
    # wav = "/Users/huangyiming02/Project/github/PaddleSpeechDemo/PaddleSpeechServer/source/20220419191710vlgfw.wav"
    # parse_wav(wav)
    
    # 实体信息抽取Demo
    schema = ["时间", "出发地", "目的地", "费用"]
    ie = Taskflow("information_extraction", schema=schema)
    result = ie("我八点钟从上海到北京一共花了五百八十块钱")
    print(result)
    
    # 改变图片大小
    # png_path = "/Users/huangyiming02/Project/github/PaddleSpeech/paddlespeech/server/tests/asr/online/web/static/image/PaddleSpeech_logo.png"
    # resize(png_path)
    
    


