from queue import Queue
import numpy as np
import os

class AudioMannger:
    def __init__(self, robot, frame_length=160, vad_frame=10, data_width=2):
        # 二进制 pcm 流 
        self.chunk_audios_bin = b''
        self.asr_result = ""
        self.robot = robot
        self.mean_db = 0
        self.mean_db_path = "source/mean_db.py"
        
        # 10ms 一帧
        self.frame_length = frame_length
        # 100 ms 的窗口，检测一次 vad
        self.vad_frame = vad_frame
        # int 16, 两个bytes
        self.data_with = data_width
    
    def init(self):
        if os.path.exists(self.mean_db_path):
            # 平均响度文件存在
            self.mean_db = np.load(self.mean_db_path)
        
    
    def clear(self):
        self.chunk_audios_bin = b''
        self.asr_result = ""
    
    def compute_chunk_db(self, )
    
    def is_speech(self, start):
        if start > len(self.chunk_audios_bin):
            return False
        # 检查从这个 start 开始是否为静音帧
        if 