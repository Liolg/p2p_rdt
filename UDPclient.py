import socket
import pickle
import pathlib
import os
import io
serverName = '127.0.1.1'
serverPort = 12000
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
message = 'resources/lio.txt'
serialized_data = pickle.dumps({'command': 'get', 'data': message.encode()})
clientSocket.sendto(serialized_data, (serverName, serverPort))
clientSocket.settimeout(2)
new_file = pathlib.Path('resources/recived.txt').open( 'a+b')
file_chunks_buffer = []

acc = 0
while True:
    try:
        serialized_response, serverAddress = clientSocket.recvfrom(2048)
        response = pickle.loads(serialized_response)
        if response['ok']:
            data = response['data']
            # os.system('clear')
            print(data['message'].decode())
            print(data['stream'])
            if acc == data['acc']:
                new_file.write(data['stream'])
                acc = data['acc'] + len(data['stream'])
                for i in range(0, len(file_chunks_buffer)):
                    if acc == i['acc']:
                        new_file.write(i['stream'])
                        acc = i['acc'] + len(i['stream'])
            else:
                file_chunks_buffer.append({'acc': acc, 'stream': data['stream']})
        else:
            data = response['data']
            print(data['message'].decode())
            break
    except TimeoutError:
        print('time up')
        break
    except:
        print('error')
        break
clientSocket.close()