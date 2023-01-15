from twisted.internet import protocol, reactor
import pygame

clock = pygame.time.Clock()

class EchoServer(protocol.Protocol):
    def __init__(self, game, FPS):
        self.game = game
        self.FPS = FPS
    def connectionMade(self, game):
        game.connected = 1

    def dataReceived(self, data):
        recv_pack = eval(data.decode())
        self.game.pack = recv_pack
        send_pack = self.game.info
        self.transport.write(str(send_pack).encode())
        clock.tick(self.FPS)

    def connectionLost(self, reason):
        self.game.connected = 0


class EchoClient(protocol.Protocol):
    def __init__(self, game, FPS):
        self.game = game
        self.FPS = FPS
    def connectionMade(self):
        self.game.connected = 1
        send_pack = self.game.info
        self.transport.write(str(send_pack).encode())
        clock.tick(self.FPS)

    def dataReceived(self, data):
        recv_pack = eval(data.decode())
        self.game.pack = recv_pack
        send_pack = self.game.info
        self.transport.write(str(send_pack).encode())
        clock.tick(self.FPS)

    def connectionLost(self, reason):
        self.game.connected = 0
        print("connection lost")


class ClientFactory(protocol.ClientFactory):
    protocol = EchoClient

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed - goodbye!")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print("Connection lost - goodbye!")
        reactor.stop()


def client(ip):
    f = ClientFactory()
    reactor.connectTCP(ip, 8080, f)
    reactor.run(installSignalHandlers=False)


def server():
    print('server started')
    factory = protocol.ServerFactory()
    factory.protocol = EchoServer
    reactor.listenTCP(8080, factory)
    reactor.run(installSignalHandlers=False)
