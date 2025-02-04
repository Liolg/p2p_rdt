import socket
import pickle
import pathlib
import os
serverName = '127.0.1.1'
serverPort = 12000
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
message = 'resources/lio.txt'
serialized_data = pickle.dumps({'command': 'get', 'data': message.encode()})
clientSocket.sendto(serialized_data, (serverName, serverPort))
clientSocket.settimeout(2)
new_file = pathlib.Path('resources/recived.txt').open( 'a+b')
while True:
    try:
        serialized_response, serverAddress = clientSocket.recvfrom(2048)
        response = pickle.loads(serialized_response)
        if response['ok']:
            data = response['data']
            # os.system('clear')
            print(data['message'].decode())
            print(data['stream'])
            new_file.write(data['stream'])
        else:
            data = response['data']
            print(data['message'].decode())
            break
    except:
        print('time up')
clientSocket.close()