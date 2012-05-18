from lib2d.client.net.tcp import TCPClient
from lib2d.common.packets import make_packet



class Client(object):
    """
    connects to a server and allows the player to play
    """


    version = 1

    def __init__(self, user, passwd, addr, port):
        self.user = user
        self.passwd = passwd
        self.connect()


    def connect(self):
        self.conn = TCPClient()
        self.conn.connect("127.0.0.1", 25565)


    def login(self):
        packet = make_packet("login",
                            protocol=self.version,
                            username=self.user,
                            password=self.passwd)

        self.conn.send_data(packet)
