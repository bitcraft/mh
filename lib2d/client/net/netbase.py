import socket,select,sys,time
from errors import *
from communicate import SendData, ReceiveData, ReceiveDataUDP



class TCPServer():
    def __init__(self):
        self.sending_socket = None

    def input_func(self,sock,host,port,address):pass
    def output_func(self,sock,host,port,address):pass
    def connect_func(self,sock,host,port):pass
    def client_connect_func(self,sock,host,port,address):pass
    def client_disconnect_func(self,sock,host,port,address):pass
    def quit_func(self,host,port):pass
        
    def connect(self,host,port):
        self.host = host
        self.port = port
        try:
            self.unconnected_socket = socket.socket()
            self.unconnected_socket.bind((self.host,self.port))
            self.unconnected_socket.listen(5)
        except:
            self.unconnected_socket.close()
            raise ServerError("Only one instance of the server on port "+str(self.port)+" may run at one time!")
        self.connect_func(self.unconnected_socket,self.host,self.port)
        self.connected_sockets = []
        self.socketaddresses = {}

    def remove_socket(self,sock):
        address = self.socketaddresses[sock]
        self.client_disconnect_func(sock,self.host,self.port,address)
        self.connected_sockets.remove(sock)
    def serve_forever(self):
        self.looping = True
        while self.looping:
            input_ready,output_ready,except_ready = select.select([self.unconnected_socket]+self.connected_sockets,[],[])
            for sock in input_ready:
                if sock == self.unconnected_socket:
                    #init socket
                    connected_socket, address = sock.accept()
                    self.connected_sockets.append(connected_socket)
                    self.socketaddresses[connected_socket] = address
                    self.client_connect_func(connected_socket,self.host,self.port,address)
                else:
                    try:
                        data = ReceiveData(sock)
                        address = self.socketaddresses[sock]
                        self.input_func(sock,self.host,self.port,address)
                    except:
                        data = "client quit"
                    if data != None:
                        if data == "client quit":
                            self.remove_socket(sock)
                            continue
                        self.sending_socket = sock
                        self.handle_data(data)
                    
    def handle_data(self,data):
        pass
    def send_data(self,data,compress=False):
        try:
            SendData(self.sending_socket,data,compress,includelength=True)
            address = self.socketaddresses[self.sending_socket]
            self.output_func(self.sending_socket,self.host,self.port,address)
        except:
            self.remove_socket(self.sending_socket)
            
    def quit(self):
        for s in self.connected_sockets: s.close()
        self.quit_func(self.host,self.port)


class UDPServer():
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def input_func(self,sock,host,port,address):pass
    def output_func(self,sock,host,port,address):pass
    def connect_func(self,sock,host,port):pass
    def quit_func(self,host,port):pass
        
    def connect(self,host,port):
        self.host = host
        self.port = port
        try:
            self.socket.bind((host, port))
        except:
            self.socket.close()
            raise ServerError("Only one instance of the server on port "+str(self.port)+" may run at one time!")
        self.connect_func(self.socket,self.host,self.port)
    def serve_forever(self):
        self.looping = True
        while self.looping:
            data,self.lastaddress = ReceiveDataUDP(self.socket)
            self.input_func(self.socket,self.host,self.port,self.lastaddress)
            self.handle_data(data)
    def handle_data(self,data):
        pass
    def send_data(self,data,compress=False):
        try:
            SendData(self.socket,data,compress,address=self.lastaddress)
            self.output_func(self.socket,self.host,self.port,self.lastaddress)
        except:
            pass
            #client disconnected
            
    def quit(self):
        self.socket.close()
        self.quit_func(self.host,self.port)

 
class UDPClient:
    def __init__(self):
        pass
    def connect(self,host,port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.socket.connect((self.host,self.port))
        
    def send_data(self,data,compress=False):
        SendData(self.socket,data,compress)
    def wait_for_data(self):
        input_ready,output_ready,except_ready = select.select([self.socket],[],[])
        return ReceiveDataUDP(self.socket)[0]
    def check_for_data(self):
        input_ready,output_ready,except_ready = select.select([self.socket],[],[],0.001)
        if len(input_ready) > 0:
            return ReceiveDataUDP(self.socket)[0]
    
    def quit(self):
        self.socket.close()
