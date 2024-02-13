import socket, threading
 
class Client:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.HOST = 'localhost'
        self.PORT = 5432
        self.addr = (self.HOST, self.PORT)
        self.client_socket.connect((self.HOST, self.PORT))
    def send(self, data):
        self.client_socket.send(str.encode(data))
        return self.client_socket.recv(2048).decode()
    
    def disconnect(self):
        self.client_socket.close()
