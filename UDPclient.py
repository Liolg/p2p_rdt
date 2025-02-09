import socket
import pickle
import pathlib
import os
import io
import random
import math
import time
import asyncio
serverName = '127.0.1.1'
serverPort = 12001
clientName = '127.0.1.1'
clientPort = 13000
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.bind(('', clientPort))
message = 'resources/lio.txt'
serialized_data = pickle.dumps({'command': 'get', 'data': message.encode()})
clientSocket.sendto(serialized_data, (serverName, serverPort))
clientSocket.settimeout(5)
new_file = pathlib.Path('resources/recived.txt').open( 'a+b')
file_chunks_buffer = []
acc = 0

async def send_acc(acc):
    serialized_data = pickle.dumps({'command': 'acc', 'data': acc})
    clientSocket.sendto(serialized_data, (serverName, serverPort))

def buffer_sort_key(el):
    return el['acc']

async def send(response):
    await asyncio.sleep(0.01)
    global acc, new_file
    data = response['data']
    # os.system('clear')
    #print(data['message'].decode())
    #print(data['stream'])
    if acc == data['seq']:
        new_file.write(data['stream'])
        acc = data['seq'] + len(data['stream'])
        if len(file_chunks_buffer) > 0:
            file_chunks_buffer.sort(key = buffer_sort_key)
            while acc == file_chunks_buffer[0]['acc']:    
                new_file.write(file_chunks_buffer[0]['stream'])
                acc = file_chunks_buffer[0]['acc'] + len(file_chunks_buffer[0]['stream'])
                file_chunks_buffer.pop(0)
            for i in range(0, len(file_chunks_buffer)):
                if acc == i['acc']:
                    new_file.write(i['stream'])
                    acc = i['acc'] + len(i['stream'])
        await send_acc(acc)
    else:
        file_chunks_buffer.append({'acc': acc, 'stream': data['stream']})
        #await send_acc(acc)

async def main():
    global new_file
    while True:
        try:
            serialized_response, serverAddress = clientSocket.recvfrom(2048)
            clientSocket.settimeout(5)
            response = pickle.loads(serialized_response)
            if response['ok']:
                await send(response)
            else:
                data = response['data']
                print(data['message'].decode())
                print(file_chunks_buffer)
                break
        except TimeoutError:
            print('time up')
            break
        # except:
        #     print('error')
        #     break

asyncio.run(main())
clientSocket.close()