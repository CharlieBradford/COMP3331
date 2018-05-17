import multiprocessing
import threading
import _thread
import socketserver
import socket
import sys

LOCALHOST = ''
PORT_OFFSET = 50000



class TCPHandler(socketserver.BaseRequestHandler):
    """
       Request handler for file requests

       "rcq" Request of a file
       Format: rcq <filename> <origin_of_request> 0000

       "rrp" Response to file request
       Format: rrp <filename> <origin_of_request> <location_of_file>

       "dep" Departure message
       Format: dep <origin> <new_successor> <new_second_successor>

       """
    def handle(self):
        data = self.request.recv(1024).decode("utf-8")
        print(data)
        type, arg1, arg2, arg3 = data.split(" ")

        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        global neighbours, my_id

        if type == "rcq":
            """
            If we have the file, send it back
            Else, forward it
            """

            filename, origin = arg1, arg2
            hash = int(filename) % 256

            if neighbours[2] > hash <= myid:
                message = "rrp " + [filename, origin, my_id].join(" ")
                self.request.send(bytes(message, 'ascii'))
                status = "File " + filename + " is stored here."
                action = "A response message, destined for peer " + origin + ", has been sent."

            else:
                message = "rcq " + " ".join([filename, origin, arg3])
                tcp.connect(('127.0.0.1', PORT_OFFSET + neighbours[0]))
                tcp.send(bytes(message, 'ascii'))
                tcp.detach()

                status = "File " + filename + " is not stored here."
                action = "File request message has been forwarded to my successor."

            print(status)
            print(action)

        elif type == "rrp":
            """
            If we are the origin of the request, return,
            Else, send to predecessor 
            """

            filename, origin, location = arg1, arg2, arg3

            if my_id == int(origin):
                print("Received a message from from peer " + location + ", which has file " + filename)
            else:
                psocket.send(bytes(data))

        elif type == "dep":
            origin = arg1
            if origin == neighbours[0]:
                print("Peer " + str(origin) + " has departed from the network.")
            self.request.send(bytes("Departure confirmed.", "ascii"))

            neighbours[0] = arg2
            neighbours[1] = arg3
        return

class UDPHandler(socketserver.BaseRequestHandler):
    """
        Request handler for pings

        "png" Ping request
        Format: png <origin_of_request> <relationship>

        "prp" Ping response
        Format: prp <origin_of_response> <relationship>

        "est" Establish predecessor
        Format: est <origin_of_message> <relationship>
    """
    def handle(self):
        global my_id, neighbours


        data = self.request[0].decode('utf-8')
        print(data)
        socket = self.request[1]
        type, origin, relationship = data.split(" ")

        if type == "png":
            message = "prp " + str(my_id)
            socket.sendto(bytes(message, 'ascii'), self.client_address)
            print("Ping from {}".format(origin))
        elif type == "prp":
            'No action'
            print("Ping response from {}".format(origin))
        elif type == "est":
            neighbours[int(relationship)] = origin
            print("{} established as {}".format(origin, relationship))

class TCPServer(socketserver.ThreadingTCPServer):
    pass

class UDPServer(socketserver.ThreadingUDPServer):
    pass


def inputhandler():

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    global neighbours, my_id

    while True:
        c = input().lower()
        args = c.split(' ')
        if len(args) < 2: continue
        if args[0] == 'quit':
            _thread.interrupt_main()
        elif args[0] == 'ping':
            if int(args[1]) == neighbours[0]: relationship = 2
            elif int(args[1]) == neighbours[1]: relationship = 3
            else: relationship = -1

            message = "png {} {}".format(my_id, '-1')
            udp_socket.sendto(bytes(message, 'ascii'), ('127.0.0.1', PORT_OFFSET + int(args[1])))
            print('Sending ping to {}'.format(args[1]))
        elif args[0] == 'request':
            message = 'rcq {} {} 0000'.format(args[1], my_id)
            tcp_socket.connect(('127.0.0.1', PORT_OFFSET + neighbours[0]))
            tcp_socket.send(bytes(message, 'ascii'))
            tcp_socket.detach()









# if __name__ == "__main__":
neighbours = [int(sys.argv[2]), int(sys.argv[3]), 0, 0]
my_id = int(sys.argv[1])



tcp_server = TCPServer(('127.0.0.1', PORT_OFFSET + my_id), TCPHandler)
udp_server = UDPServer(('127.0.0.1', PORT_OFFSET + my_id), UDPHandler)

#udp_thread = multiprocessing.Process(name='udp_thread', target=udp_server.serve_forever)
#tcp_thread = multiprocessing.Process(name='tcp_thread', target=tcp_server.serve_forever)
#i_o_thread = multiprocessing.Process(name='i_o_thread', target=inputhandler)

tcp_thread = threading.Thread(target=tcp_server.serve_forever)
udp_thread = threading.Thread(target=udp_server.serve_forever)
i_o_thread = threading.Thread(target=inputhandler)

udp_thread.daemon = True
tcp_thread.daemon = True
i_o_thread.daemon = True

try:
    while True:
        udp_thread.start()
        tcp_thread.start()
        i_o_thread.start()

        udp_thread.join()
        tcp_thread.join()
        i_o_thread.join()
except KeyboardInterrupt:
    print()
    print("That was rude.")



















