# import multiprocessing
import threading
import time
import socketserver
import socket
import sys

LOCALHOST = ''
PORT_OFFSET = 50000

neighbours = [int(sys.argv[2]), int(sys.argv[3]), 0, 0]
my_id = int(sys.argv[1])

kill_flag = False
ping_flag = False


class TCPHandler(socketserver.BaseRequestHandler):
    """
       Request handler for file requests

       "rcq" Request of a file
       Format: rcq <filename> <origin_of_request> 0000

       "rrp" Response to file request
       Format: rrp <filename> <origin_of_request> <location_of_file>

       "dep" Departure message
       Format: dep <origin> <new_successor> <new_second_successor>

       "ded" Ungraceful departure message
       Format: ded <origin> <new_second_predecessor> 0000

       """
    def handle(self):
        data = self.request.recv(1024).decode("utf-8")
        type, arg1, arg2, arg3 = data.split(" ")

        global neighbours, my_id

        if type == "rcq":
            """
            If we have the file, send it back
            Else, forward it
            """

            filename, origin = arg1, arg2
            h = int(filename) % 256

            if (neighbours[2] < h and h <= my_id) or (neighbours[2] > my_id and h > neighbours[2]) or h == my_id:
                message = "rrp " + " ".join([filename, origin, str(my_id)])
                status = "File " + filename + " is stored here."
                action = "A response message, destined for peer " + origin + ", has been sent."
                try:
                    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    tcp.connect(('127.0.0.1', PORT_OFFSET + int(origin)))
                    tcp.send(bytes(message, 'ascii'))
                    tcp.close()
                except:
                    print("Unable to connect")


            else:
                message = "rcq " + " ".join([filename, origin, arg3])
                try:
                    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    tcp.connect(('127.0.0.1', PORT_OFFSET + neighbours[0]))
                    tcp.send(bytes(message, 'ascii'))
                    tcp.close()
                except:
                    print("Unable to connect, trying again in 30 seconds")
                    time.sleep(30)
                    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    tcp.connect(('127.0.0.1', PORT_OFFSET + neighbours[0]))
                    tcp.send(bytes(message, 'ascii'))
                    tcp.close()

                status = "File " + filename + " is not stored here."
                action = "File request message has been forwarded to my successor."

            print(status)
            print(action)

        elif type == "rrp":

            filename, origin, location = arg1, arg2, arg3

            print("Received a message from from peer " + location + ", which has file " + filename)

        elif type == "dep":
            origin = arg1
            if origin != '-1': print("Peer " + str(origin) + " has departed from the network.")
            print("My first successor is now " + arg2)
            print("My second successor is now " + arg3)


            neighbours[0] = int(arg2)
            neighbours[1] = int(arg3)
            UserAction.establish()
        elif type == "ded":
            neighbours[2] = int(arg1)
            neighbours[3] = int(arg2)

            print("My first predecessor is now " + arg1)
            print("My second predecessor is now " + arg2)

            message = "dep -1 {} {}".format(my_id, neighbours[0])
            tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp.connect(('127.0.0.1', PORT_OFFSET + neighbours[2]))
            tcp.send(bytes(message, 'ascii'))
            tcp.close()


            message = "dep -1 {} {}".format(neighbours[2], my_id)
            tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp.connect(('127.0.0.1', PORT_OFFSET + neighbours[3]))
            tcp.send(bytes(message, 'ascii'))
            tcp.close()





        return

class UDPHandler(socketserver.BaseRequestHandler):
    """
        Request handler for pings

        "png" Ping request
        Format: png <origin_of_request> <relationship>

        "prp" Ping response
        Format: prp <origin_of_response> <relationship>

        "est" Establish Relationship
        Format: est <origin_of_message> <relationship>

    """
    def handle(self):
        global my_id, neighbours, ping_flag


        data = self.request[0].decode('utf-8')
        # print(data)
        socket = self.request[1]
        type, origin, relationship = data.split(" ")

        if type == "png":
            message = "prp " + str(my_id) + " -1"
            socket.sendto(bytes(message, 'ascii'), ('127.0.0.1', PORT_OFFSET + int(origin)))
            print("Ping from peer {}".format(origin))
        elif type == "prp":
            print("Ping response from {}".format(origin))
            if int(origin) == neighbours[0]: ping_flag = False
        elif type == "est":
            neighbours[int(relationship)] = int(origin)
            if relationship == '0':
                print("My first successor is now peer {}".format(origin))
            elif relationship == '1':
                print("My second successor is now peer {}".format(origin))
            elif relationship == '2':
                print("{} established as first predecessor".format(origin))
            else:
                print("{} established as second predecessor".format(origin))


class TCPServer(socketserver.ThreadingTCPServer):
    pass

class UDPServer(socketserver.ThreadingUDPServer):
    pass


def inputhandler():

    global neighbours, my_id, kill_flag

    time.sleep(1)
    UserAction.establish()

    while True:
        c = input().lower()
        args = c.split(' ')
        if args[0] == 'quit':
            UserAction.quit()
            break
        elif args[0] == 'ping':
            if len(args) < 2: continue
            UserAction.ping(args[1])

        elif args[0] == 'request':
            if len(args) < 2: continue
            UserAction.request(args[1])

        elif args[0] == 'neighbours':
            UserAction.print_neighbours()

        elif args[0] == 'establish':
            UserAction.establish()

def peer_check():
    """
    The neighbour is assumed to be dead, and if it doesn't respond
    within 3 pings, then neighbours are reestablished

    """
    global kill_flag, ping_flag, neighbours, my_id

    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    time.sleep(10)



    while not kill_flag:
        if neighbours[0] == neighbours[2] or neighbours[0] == my_id:
            UserAction.quit()


        peer_dead = True
        message = "png {} -1".format(my_id)

        for _ in range(3):
            ping_flag = True
            udp.sendto(bytes(message, 'ascii'), ('127.0.0.1', PORT_OFFSET + neighbours[0]))
            time.sleep(1)
            if not ping_flag: peer_dead = False

        if peer_dead:
            print("Peer {} is no longer alive.".format(neighbours[0]))

            message = "ded {} {} 0000".format(my_id, neighbours[2])
            tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp.connect(('127.0.0.1', PORT_OFFSET + neighbours[1]))
            tcp.send(bytes(message, 'ascii'))
            tcp.close()
        time.sleep(30)









class UserAction:
    def __init__(self):
        return

    @staticmethod
    def quit():
        global my_id, neighbours, kill_flag

        message = 'dep {} {} {}'.format(my_id, neighbours[0], neighbours[1])
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect(('127.0.0.1', PORT_OFFSET + neighbours[2]))
        tcp_socket.send(bytes(message, 'ascii'))
        tcp_socket.close()

        message = 'dep {} {} {}'.format(my_id, neighbours[2], neighbours[0])
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect(('127.0.0.1', PORT_OFFSET + neighbours[3]))
        tcp_socket.send(bytes(message, 'ascii'))
        tcp_socket.close()

        global udp_server, tcp_server
        udp_server.shutdown()
        tcp_server.shutdown()

        print("Peer shutting down.")
        print("Goodbye.")
        kill_flag = True
        return

    @staticmethod
    def ping(destination):
        global my_id, neighbours

        if destination == "successor":
            destination = neighbours[0]
        elif destination == "second":
            destination = neighbours[1]
        else:
            try:
                destination = int(destination)
            except ValueException:
                return

        if destination == neighbours[0]: relationship = 2
        elif destination == neighbours[1]: relationship = 3
        else: relationship = -1


        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        message = "png {} {}".format(my_id, relationship)
        udp.sendto(bytes(message, 'ascii'), ('127.0.0.1', PORT_OFFSET + destination))
        print('Sending ping to {}'.format(destination))
        return

    @staticmethod
    def request(filename):
        global my_id, neighbours
        h = int(filename) % 256

        if (neighbours[2] < h and h <= my_id) or (neighbours[2] > my_id and h > neighbours[2]):
            print("You already have that file.")
        else:
            message = 'rcq {} {} 0000'.format(filename, my_id)
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.connect(('127.0.0.1', PORT_OFFSET + neighbours[0]))
            tcp_socket.send(bytes(message, 'ascii'))
            tcp_socket.close()
        return

    @staticmethod
    def print_neighbours():
        global neighbours
        print("First successor is peer " + str(neighbours[0]))
        print("Second successor is peer " + str(neighbours[1]))
        print("First predecessor is peer " + str(neighbours[2]))
        print("Second predecessor is peer " + str(neighbours[3]))
        return

    @staticmethod
    def establish():
        global my_id, neighbours
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.sendto(bytes('est ' + str(my_id) + ' 2', 'ascii'), ('127.0.0.1', PORT_OFFSET + neighbours[0]))
        udp_socket.sendto(bytes('est ' + str(my_id) + ' 3', 'ascii'), ('127.0.0.1', PORT_OFFSET + neighbours[1]))
        return







# if __name__ == "__main__":



tcp_server = TCPServer(('127.0.0.1', PORT_OFFSET + my_id), TCPHandler)
udp_server = UDPServer(('127.0.0.1', PORT_OFFSET + my_id), UDPHandler)

#udp_thread = multiprocessing.Process(name='udp_thread', target=udp_server.serve_forever)
#tcp_thread = multiprocessing.Process(name='tcp_thread', target=tcp_server.serve_forever)
#i_o_thread = multiprocessing.Process(name='i_o_thread', target=inputhandler)

tcp_thread = threading.Thread(target=tcp_server.serve_forever)
udp_thread = threading.Thread(target=udp_server.serve_forever)
i_o_thread = threading.Thread(target=inputhandler)
che_thread = threading.Thread(target=peer_check)

udp_thread.daemon = True
tcp_thread.daemon = True
i_o_thread.daemon = True
che_thread.daemon = True

try:
    while not kill_flag:
        udp_thread.start()
        tcp_thread.start()
        i_o_thread.start()
        che_thread.start()

        udp_thread.join()
        tcp_thread.join()
        i_o_thread.join()
        che_thread.join()

except KeyboardInterrupt:
    print()
    print("That was rude.")



















