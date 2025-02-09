import socket
import pickle
import pathlib
import math
import time
import asyncio
serverPort = 12000
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print('The server is ready to receive')
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
print('IP Address: ' + IPAddr)

def not_sended(i, win_len):
    for (indexs, lens, accs) in win_len:
        if i == indexs:
            return False
    return True

def key_window(tup):
    index, lenght, accnoleged = tup
    return index

async def send(clientAddress, file):
    global acc, win_len, MAX_WINDOW_LEN, MAX_SIZE
    #await asyncio.sleep(0.2)
    for i in range(acc, min((acc + MAX_WINDOW_LEN), len(file)), MAX_SIZE):
        if not_sended(i, win_len):
            chunk = file[i:i + MAX_SIZE]
            response_msg = f'Downloading {math.floor((i + len(chunk)) * 100 / len(file))}%'
            serialized_data = pickle.dumps({'ok': True, 'data': {'message': response_msg.encode(), 'seq': i, 'stream': chunk}})
            await asyncio.sleep(0.01)
            serverSocket.sendto(serialized_data, clientAddress)
            win_len.append((i, len(chunk), False))

async def main():
    global acc, win_len, MAX_WINDOW_LEN, MAX_SIZE
    while True:
        print('waiting get')
        serverSocket.settimeout(None)
        payload, clientAddress = serverSocket.recvfrom(2048)
        recived_object = pickle.loads(payload)
        command = recived_object['command']
        data = recived_object['data']
        if command == 'get':
            file_path = pathlib.Path(data.decode())
            if file_path.is_file():
                file = file_path.open('rb').read()
                while True:
                    try:
                        await send(clientAddress, file)
                        payload, clientAddress = serverSocket.recvfrom(2048)
                        serverSocket.settimeout(5)
                        recived_object = pickle.loads(payload)
                        command = recived_object['command']
                        data = recived_object['data']
                        if command == 'acc':
                            if data + 1 > len(file):
                                break

                            for i in range(0, len(win_len)):
                                index, lenght, is_acc = win_len[i]
                                if data >= index:
                                    win_len[i] = (index, lenght, True)
                                    break
                            win_len.sort(key = key_window)
                            while len(win_len) > 0 and list(win_len[0])[2]:
                                index, lenght, is_acc = win_len[0]
                                acc = index + lenght
                                win_len.pop(0)
                    except TimeoutError:
                        print('time up')
                        acc = 0
                        win_len = []
                        break

                response_msg = 'Transmition complete'
                serialized_data = pickle.dumps({'ok': False, 'data': {'message': response_msg.encode(), 'stream': None}})
                #time.sleep(0.05)
                serverSocket.sendto(serialized_data, clientAddress)
            else:
                response_msg = 'not found'
                serialized_data = pickle.dumps({'ok': False, 'data': {'message': response_msg.encode(), 'stream': None}})
                #time.sleep(0.05)
                serverSocket.sendto(serialized_data, clientAddress)
        
        acc = 0
        win_len = []

acc = 0
acc_list = []
MAX_SIZE = 2
MAX_WINDOW_LEN = MAX_SIZE * 2
win_len = []
asyncio.run(main())