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

def check_acc(i, win_len):
    for (indexs, lengs, accs) in win_len:
        if i == indexs and accs:
            return True
        else:
            return False
    return False

def key_window(tup):
    index, lenght, accnoleged = tup
    return index

def in_win_len(i):
    for (indexs, lengs, accs) in win_len:
        if i == indexs:
            return True
    return False

async def send(clientAddress, file):
    global acc, win_len, MAX_WINDOW_LEN, MAX_SIZE
    #await asyncio.sleep(0.2)
    for i in range(acc, min((acc + MAX_WINDOW_LEN), len(file)), MAX_SIZE):
        if check_acc(i, win_len) or len(win_len) < MAX_WINDOW_LEN:
            chunk = file[i:i + MAX_SIZE]
            response_msg = f'{math.floor((i + len(chunk)) * 100 / len(file))}%'
            serialized_data = pickle.dumps({'ok': True, 'data': {'message': response_msg.encode(), 'seq': i, 'stream': chunk}})
            await asyncio.sleep(0.005)
            serverSocket.sendto(serialized_data, clientAddress)
            if not in_win_len(i):
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
                        print('waiting acc')
                        payload, clientAddress = serverSocket.recvfrom(2048)
                        serverSocket.settimeout(10)
                        recived_object = pickle.loads(payload)
                        command = recived_object['command']
                        data = recived_object['data']
                        if command == 'acc':
                            if data + 1 > len(file):
                                response_msg = 'Transmition complete'
                                break

                            for i in range(0, len(win_len)):
                                index, lenght, is_acc = win_len[i]
                                if data > index:
                                    win_len[i] = (index, lenght, True)
                            win_len.sort(key = key_window)
                            while len(win_len) > 0 and win_len[0][2]:
                                index, lenght, is_acc = win_len[0]
                                acc = index + lenght
                                win_len.pop(0)
                    except TimeoutError:
                        print('time up')
                        acc = 0
                        win_len = []
                        response_msg = 'time up'
                        break
                    
                if response_msg != 'time up':
                    serialized_data = pickle.dumps({'ok': False, 'data': {'message': response_msg.encode(), 'stream': None}})
                    serverSocket.sendto(serialized_data, clientAddress)
            else:
                response_msg = 'not found'
                serialized_data = pickle.dumps({'ok': False, 'data': {'message': response_msg.encode(), 'stream': None}})
                #time.sleep(0.05)
                serverSocket.sendto(serialized_data, clientAddress)
        else:
            response_msg = 'invalid command'
            serialized_data = pickle.dumps({'ok': False, 'data': {'message': response_msg.encode(), 'stream': None}})
            serverSocket.sendto(serialized_data, clientAddress)
        acc = 0
        win_len = []

acc = 0
acc_list = []
MAX_SIZE = 2
MAX_WINDOW_LEN = MAX_SIZE * 5
win_len = []
asyncio.run(main())