from socket import *
import sys
from time import time
from queue import Queue

UDP_IP = sys.argv[1]
UDP_PORT = int(sys.argv[2])

time_ms = lambda: int(round(time() * 1000))

def pingClient():
    send_sock = socket(AF_INET, SOCK_DGRAM)
    send_sock.settimeout(1)

    for sequence in range(10):
        message = u'PING {} \r\n'.format(sequence)
        send_sock.sendto(message.encode('utf-8'),
                                        (UDP_IP, UDP_PORT))
        sent = time_ms()
        try:
            data, addr = send_sock.recvfrom(1024)
            recv = time_ms()
            rtt = 'rtt = {} ms'.format(recv - sent)
        except timeout:
            rtt = 'time out'


        print('ping to {}, seq = {}, {}'.format(UDP_IP,
                                                sequence,
                                                rtt))


if __name__ == '__main__':
    pingClient()

