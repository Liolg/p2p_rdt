import socket
import pickle
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
        modifiedMessage = data.decode().upper()
        serverSocket.sendto(modifiedMessage.encode(), clientAddress)
    elif command == 'set':
        print('not yet')
    else:
        print('error')
