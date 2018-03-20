import sys
from socket import AF_INET, SOCK_DGRAM, SOCK_STREAM, socket, timeout
from Threading import thread

PORT_OFFSET = 50000
LOCALHOST = '127.0.0.1'
BUFSIZE = 1024


def runClient(client):
    client.userInput()


def runServer(server):
    server.listen()


class Server:
    def __init__(self, peer):
        port = PORT_OFFSET + int(peer)
        self.peer = peer
        self.udp_sock = socket(AF_INET, SOCK_DGRAM)
        self.udp_sock.bind((LOCALHOST, port))
        self.alive = True

    def setClient(self, client):
        self.client = client

    def listen(self):
        while self.alive:
            data, addr = self.udp_sock.recvfrom(BUFSIZE)
            [msgType, sender, message] = data.split(' ')
            if msgType == 'PING':
                self.response(sender)

    def ping(self, addr):
        message = 'PING ' + str(self.peer) + ' no_data'
        message = message.encode('utf-8')
        port = addr + PORT_OFFSET
        self.udp_sock.sendto(message,
                             (LOCALHOST, port))
        self.udp_sock.settimeout(0.25)
        try:
            data, addr = self.udp_sock.recvfrom(BUFSIZE)
            msgType, sender = data.split(' ')[:2]
        except timeout:
            self.client.handleDeadPeer()

    def response(self, addr):
        message = 'RESPONSE ' + str(self.peer) + ' no_data'
        message = message.encode('utf-8')
        port = addr + PORT_OFFSET
        self.udp_sock.sendto(message,
                             (LOCALHOST, port))


class Client:
    def __init(self, peerId, nId, nnId):
        self.peerId = peerId
        self.nId = nId
        self.nnId = nnId
        self.tpc_sock = socket(AF_INET, SOCK_STREAM)

    def setServer(self, server):
        self.server = server

    def userInput(self):
        while True:
            cmd = input('>').split(' ')

            if cmd[0] == 'quit':
                raise SystemExit
            elif cmd[0] == 'ping':
                self.server.ping(cmd[1])
            elif cmd[0] == 'request':
                self.request(cmd[1])

    def request(self, request):
        return


if __name__ == "main":
    peerId = int(sys.argv[1])
    nId = int(sys.argv[2])
    nnId = int(sys.argv[3])

    client = Client(peerId, nId, nnId)
    server = Server(peerId)

    client.setServer(server)
    server.setClient(client)

    c = thread(target=runClient, args=client)
    s = thread(target=runServer, args=server)

    try:
        c.start()
        s.start()
    except KeyboardInterrupt:
        print("")
