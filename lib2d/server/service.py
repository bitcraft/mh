from twisted.application.internet import TCPClient, TCPServer
from twisted.application.service import Application, MultiService
from twisted.application.strports import service as serviceForEndpoint
from twisted.internet.protocol import Factory
from twisted.python import log

from lib2d.config import read_configuration
from lib2d.server.factory import Lib2dFactory



def services_for_endpoints(endpoints, factory):
    l = []
    for endpoint in endpoints:
        server = serviceForEndpoint(endpoint, factory)
        # XXX hack for bravo.web:135, which wants this. :c
        server.args = [None, factory]
        server.setName("%s (%s)" % (factory.name, endpoint))
        l.append(server)
    return l


class Lib2dService(MultiService):

    def __init__(self):
        MultiService.__init__(self)

        self.config = read_configuration()
        self.factorylist = list()
        self.irc = False
        self.ircbots = list()
        self.configure_services()

    def addService(self, service):
        MultiService.addService(self, service)

    def removeService(self, service):
        MultiService.removeService(self, service)

    def configure_services(self):
        for section in self.config.sections():
            if section.startswith("world "):
                factory = BravoFactory(self.config, section[6:])
                interfaces = self.config.getlist(section, "interfaces")

                for service in services_for_endpoints(interfaces, factory):
                    self.addService(service)

                self.factorylist.append(factory)

service = Lib2dService()

application = Application("lib2d-server")
service.setServiceParent(application)
