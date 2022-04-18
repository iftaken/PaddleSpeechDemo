import numpy as np
import struct


def Bytes2Int16Slice(feature):
    x = []
    for i in range(len(feature)//2):
        data = feature[i * 2: (i * 2) + 2]
        a = struct.unpack('h', data)
        x.append(a[0])
    return x

def read_pcm(pcm_path):
    # 读取 pcm 数据为 numpy
    with open(pcm_path, "rb") as f:
        pcm_bin = f.read()
        
    print(len(pcm_bin))
    x = Bytes2Int16Slice(pcm_bin)
    x = np.array(x)
    print(x)
    
    with open(pcm_path, "rb") as f:
        x2 = np.fromfile(f, np.int16)
    print(x2)
    

if __name__ == '__main__':
    pcm_path = "source/20220414195249bpsvz.pcm"
    read_pcm(pcm_path)
    


