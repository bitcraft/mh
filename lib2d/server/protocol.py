from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.protocols.policies import TimeoutMixin


SUPPORTED_PROTOCOL = 1

class Lib2dProtocol(object, Protocol, TimeoutMixin):
    """
    Lib2d server protocol
    """


    excess = ""
    packet = None

    state = STATE_UNAUTHENTICATED

    buf = ""
    parser = None
    handler = None

    player = None
    username = None
    motd = "Lib2d Server"

    _health = 20
    _latency = 0

    def __init__(self):

        self.handlers = {
            0: self.ping,
            1: self.login,
            2: self.chat,
            3: self.position,
            4: self.orientation,
            255: self.quit,
        }

        self.setTimeout(30)

    def ping(self, container):
        now = timestamp_from_clock(reactor)
        then = container.pid
        self.latency = now - then

    def login(self, container):
        if container.protocol < SUPPORTED_PROTOCOL:
            self.error("This server doesn't support your ancient client.")
        elif container.protocol > SUPPORTED_PROTOCOL:
            self.error("This server doesn't support your newfangled client.")
        else:
            reactor.callLater(0, self.authenticated)

    def chat(self, container):
        pass

    def position(self, container):
        pass

    def orientation(self, container):
        pass

    def quit(self, container):
        pass

    def challenged(self):
        """
        Called when the client has started authentication with the server.
        """

        self.state = STATE_CHALLENGED

    def authenticated(self):
        """
        Called when the client has successfully authenticated with the server.
        """

        self.state = STATE_AUTHENTICATED

        self._ping_loop.start(30)

    def error(self, message):
        """
        Error out.

        This method sends ``message`` to the client as a descriptive error
        message, then closes the connection.
        """

        self.transport.write(make_error_packet(message))
        self.transport.loseConnection()


    # Following methods are for Twisted

    def dataReceived(self, data):
        self.buf += data
        packets, self.buf = parse_packets(self.buf)

        if packets:
            self.resetTimeout()

        for header, payload in packets:
            if header in self.handlers:
                self.handlers[header](payload)
            else:
                log.err("Didn't handle parseable packet %d!" % header)
                log.err(payload)

    def connectionLost(self, reason):
        if self._ping_loop.running:
            self._ping_loop.stop()

    def timeoutConnection(self):
        self.error("Connection timed out")

    def write_packet(self, header, **payload):
        """
        Send a packet to the client.
        """

        self.transport.write(make_packet(header, **payload))


