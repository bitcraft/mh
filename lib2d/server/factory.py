from collections import defaultdict

from twisted.python import log
from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.internet.task import LoopingCall

from lib2d.server.protocol import Lib2dServerProtocol

from lib2d.common.packets import make_packet



class Lib2dFactory(Factory):
    """
    Class accepts connections and creates Lib2dProtocol objects
    The factory also manages one game world.
    """

    protocol = Lib2dServerProtocol

    timestamp = None
    time = 0

    def __init__(self, config, name):
        """
        Create factory and open a world
        """

        self.name = name
        self.config = config
        self.world = None
        self.protocols = dict()
        self.connectedIPs = defaultdict(int)


    def startFactory(self):
        log.msg("Starting factory for: {}".format(self.name))

        self.timestamp = reactor.seconds()
        self.time_loop = LoopingCall(self.updateTime)
        self.time_loop.start(2)


    def stopFactory(self):
        """
        Shutdown the factory gracefully
        """

        log.msg("shutting down factory...")

        self.time_loop.stop()


    def build_protocol(self, addr):
        """
        Create a new Twisted protocol. 
        """

        log.msg("Starting connection for {}".format(addr))
        p = self.protocol(self.config, self.name)
        p.host = addr.host
        p.factory = self

        return p


    def teardown_protocol(self, protocol):
        """
        Close a connection
        """

        username = protocol.username
        host = protocol.host

        if username in self.protocols:
            del self.protocols[username]

        self.connectedIPs[host] -= 1


    def createGameobject(self, x, y, z, name, **kwargs):
        """
        Create a new gameobject in the world for the connected player
        """

        pass


    def updateTime(self):
        t = reactor.seconds()

        self.time += 20 * (t - self.timestamp)
        self.timestamp = t


    def broadcastTime(self):
        p = makePacket("time", timestamp=int(self.time))
        self.broadcast(p)


    def chat(self, msg):
        """
        send a chat message to all connected players
        """

        for user in self.protocols:
            pass

        log.msg("Chat: {}".format(msg))

        p = makePacket("chat", message=msg)
        self.broadcast(p)


    def broadcastForOthers(self, packet, protocol):
        """
        Send packet to all except the sender
        """

        for player in self.protocols.itervalues():
            if player is not protocol:
                player.transport.write(packet)


    def broadcast(self, packet):
        """
        Send packet to all connected players
        """

        for player in self.protocols.itervalues():
            player.transport.write(packet)
