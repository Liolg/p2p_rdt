import socket
import pickle
serverName = '127.0.1.1'
serverPort = 12000
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
message = 'lio'
serialized_data = pickle.dumps({'command': 'get', 'data': message.encode()})
clientSocket.sendto(serialized_data, (serverName, serverPort))
clientSocket.settimeout(2)
try:
    modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
except:
    print('time up')
print(modifiedMessage.decode())
clientSocket.close()