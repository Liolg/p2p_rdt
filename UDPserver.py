import socket
import pickle
import pathlib
import math
serverPort = 12000
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print('The server is ready to receive')
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
print('IP Address: ' + IPAddr)
while True:
    payload, clientAddress = serverSocket.recvfrom(2048)
    recived_object = pickle.loads(payload)
    command = recived_object['command']
    data = recived_object['data']
    if command == 'get':
        file_path = pathlib.Path(data.decode())
        if file_path.is_file():
            file = file_path.open('rb').read()
            max_size = 2
            for i in range(0, len(file), max_size):
                chunk = file[i:i + max_size]
                response_msg = f'Downloading {math.floor((i + len(chunk)) * 100 / len(file))}%'
                serialized_data = pickle.dumps({'ok': True, 'data': {'message': response_msg.encode(), 'stream': chunk}})
                serverSocket.sendto(serialized_data, clientAddress)
            response_msg = 'Transmition complete'
            serialized_data = pickle.dumps({'ok': False, 'data': {'message': response_msg.encode(), 'stream': None}})
            serverSocket.sendto(serialized_data, clientAddress)
        else:
            response_msg = 'not found'
            serialized_data = pickle.dumps({'ok': False, 'data': {'message': response_msg.encode(), 'stream': None}})
            serverSocket.sendto(serialized_data, clientAddress)
    elif command == 'set':
        print('not yet')
    else:
        print('error')
