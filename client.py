#Client
#D:/XJTLU/Y3S1/CSE205/MyProject/致命女人第一季-02.mp4
import socket
import hashlib
import os
import time
from tqdm import tqdm

# 定义数据包格式
# https://blog.csdn.net/hernofogot/article/details/88382944
# 数据(1024*3) + md5(32) 

file_size_total = 0 # The total size of file
file_size_send = 0 # The sent size of file
BUFFER_DATA_SIZE = 4096 # buffer_size while send
BUFFER_FILE_SIZE = 3072 # buffer_size with file

global client
global client_addr
global file

def getMd5(data):
    md5 = hashlib.md5(data)
    return md5.hexdigest()

def Get_FilePath_FileName_FileExt(file_path):
    filepath, temp_file_name = os.path.split(file_path)
    shotname, extension = os.path.splitext(temp_file_name)
    return filepath, shotname, extension

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # use udp 
    client_addr = ('127.0.0.1', 12000)
except:
    print("Can't connect to Server")
    os._exit(0)

print('Welcome to Client')
# file_path = input('Please input the file path\n')
file_path = 'data.tar.gz'
filepath, shotname, extension = Get_FilePath_FileName_FileExt(file_path)

try:
    file = open(file_path, 'rb')
    file_size_total = os.path.getsize(file_path)
    file_size_send = 0
except:
    print('Can not open file!')
    os._exit(0)

data = bytes(str(file_size_total) + '#' + shotname + extension , encoding='utf8')

client.sendto(data, client_addr)

with tqdm(total=file_size_total, ncols=80) as progress:
    while file_size_send < file_size_total:
        check_flag = False
        file_data = file.read(BUFFER_FILE_SIZE) # 读取文件数据
        if len(file_data) == 0:
            break
        md5_data = bytes(getMd5(file_data), encoding='utf8') # 计算验证段
        send_data = file_data + md5_data # 组合 数据 + 验证段
        while check_flag == False:
            client.sendto(send_data, client_addr) # 数据发送 如果 验证失败 则重新发送
            data_recv, client_addr = client.recvfrom(BUFFER_DATA_SIZE) # 等地验证回复
            if data_recv == md5_data: # 验证通过 继续发送下一段数据
                check_flag = True
        send_size = len(file_data)
        file_size_send += send_size
        progress.update(send_size)

client.close()
file.close()
print('file_name: '  + shotname + extension)
print('size_send: ' + str(file_size_send))

