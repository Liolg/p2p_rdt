import socket
import random
import time
import asyncio
import pickle
serverPort = 12000
clientPort = 13000
internetServerPort = 12001
internetServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
internetServerSocket.bind(('', internetServerPort))
print('Internet is ready to flow')
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
print('IP Address: ' + IPAddr)
last_programed = time.time()
i = 0
        

async def send(payload, hostAddress, hostPort):
    await asyncio.sleep(0.1)
    global i, last_programed, clientPort, serverPort
    
    rand_num = random.random() * 10
    if rand_num < 2:
        return
    if hostPort == serverPort:
        print('send to client', pickle.loads(payload))
        internetServerSocket.sendto(payload, (hostAddress, clientPort))
    else:
        print('send to server', pickle.loads(payload))
        internetServerSocket.sendto(payload, (hostAddress, serverPort))

async def listen():
    while True:
        payload, (hostAddress, hostPort) = internetServerSocket.recvfrom(2048)
        #print(payload)
        return (payload, hostAddress, hostPort)

async def main():
    while True:
        payload, hostAddress, hostPort = await listen()
        await send(payload, hostAddress, hostPort)
        #task = asyncio.create_task(send(payload, hostAddress, hostPort))

asyncio.run(main())