import socket, select



class TCPClient:
    def __init__(self):
        pass


    def connect(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.create_connection((self.host, self.port))
        

    def send_data(self, data):
        try:
            self.socket.send(data)
        except:
            raise
            self.sock.close()


    def wait_for_data(self):
        input_ready,output_ready,except_ready = select.select([self.socket],[],[])
        return ReceiveData(self.socket)


    def check_for_data(self):
        input_ready,output_ready,except_ready = select.select([self.socket],[],[],0.001)
        if len(input_ready) > 0:
            return ReceiveData(self.socket)
    

    def quit(self):
        self.socket.close()
