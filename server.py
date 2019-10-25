#Server
import socket
import hashlib
import os
from tqdm import tqdm

# 定义数据包格式
# https://blog.csdn.net/hernofogot/article/details/88382944
# 数据(1024*3) + 分组号码 + md5(32) 

file_size_recv = 0
file_size_total = 0
BUFFER_DATA_SIZE = 4096 # buffer_size while send
BUFFER_FILE_SIZE = 3072 # buffer_size with file

save_file_path = './recieve'
global file


try:
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_addr = ('127.0.0.1', 12000)
    server.bind(server_addr)
    print('Create server success ')
except:
    print('Create server faild ')
    os._exit(0)


def getMd5(data):
    md5 = hashlib.md5(data)
    return md5.hexdigest()

data_recv, client_addr = server.recvfrom(BUFFER_DATA_SIZE)
file_size_total, file_name = str(data_recv, encoding='utf8').split('#')
file_size_total = int(file_size_total)

try: 
    file = open(save_file_path + '/' + file_name, 'wb+')
except:
    print('Connet to server successful')
    os._exit(0)


with tqdm(total=file_size_total, ncols=80) as progress:
    while file_size_recv < file_size_total:
        error_flag = True
        server.settimeout(30)
        data, client_addr = server.recvfrom(BUFFER_DATA_SIZE) # 接收一次数据
        if len(data) == 0:
            continue
        real_data = data[0:-32] # 截取真实数据
        md5_recv = data[-32:] # 截取验证段
        md5_data = bytes(getMd5(real_data), encoding='utf8') # 获取接收到得数据的验证段
        while error_flag == True :
            server.sendto(md5_data, client_addr) # 回复md5验证
            if md5_recv == md5_data: # 如果验证成功
                error_flag = False
            else :
                data, client_addr = server.recvfrom(BUFFER_DATA_SIZE) # 验证失败 重新接收一次数据
                real_data = data[0:-32] # 截取真实数据
                md5_recv = data[-32:-1] # 截取验证段
                md5_data = bytes(getMd5(real_data), encoding='utf8') # 获取接收到得数据的验证段
        file.write(real_data) # 写入文件数据
        recv_size = len(real_data) # 真实接收长度
        file_size_recv += recv_size # 更新接收大小
        progress.update(recv_size) # 更新进度条

file.close()
server.close()
print('file_name: ' + file_name)
print('size_recv: ' + str(file_size_recv) + ' byte')