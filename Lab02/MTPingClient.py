from socket import *
import sys
from time import time, sleep
from queue import Queue
from threading import Thread

UDP_IP = sys.argv[1]
UDP_PORT = int(sys.argv[2])

time_ms = lambda: int(round(time() * 1000))
new_socket = lambda: socket(AF_INET, SOCK_DGRAM).settimeout(1)

def pingClient(q1, q2, send_sock):
    for sequence in range(10):
        message = u'PING {} \r\n'.format(sequence)
        send_sock.sendto(message.encode('utf-8'),
                         (UDP_IP, UDP_PORT))
        q1.put(time_ms())
        q2.get()

def pingServer(q1, q2, recv_sock):
    for sequence in range(10):
        sent = q1.get()
        try:
            data, addr = recv_sock.recvfrom(1024)
            recv = time_ms()
            rtt = 'rtt = {} ms'.format(recv - sent)
        except timeout:
            rtt = 'time out'

        print('ping to {}, seq = {}, {}'.format(UDP_IP,
                                                sequence,
                                                rtt))
        q2.put(1)


if __name__ == '__main__':
    q1 = Queue()
    q2 = Queue()
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.settimeout(1)
    client = Thread(target=pingClient, args=(q1, q2, sock))
    server = Thread(target=pingServer, args=(q1, q2, sock))
    try:
        client.start()
        server.start()
    except KeyboardInterrupt:
        print("Quitting")
