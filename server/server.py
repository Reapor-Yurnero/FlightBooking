import socket  # for sockets
import sys  # for exit

class server():

    def __init__(self):

        # flightdb: Dic[flightID] -> details: departuretime, airfare, availibity, src, dest
        self.flightdb = {"MU110": {"details": [1800, 1000, 10], "src": "Shanghai", "dest": "Beijing"},
                   "HU201": {"details": [1405, 600, 16], "src": "Singapore", "dest": "Bali"}
                   }

        # bookingdb: Dic[Name][flightID] -> quantity of flightID booked by Name
        self.bookingdb = {"Jordan": {"MU110": 3},
                          "Kobe": {"MU110": 10, "HU201": 3}}

        # request history {(requestorname,requestID):result} result is byte array or None
        self.requestHistory = {}

    def start(self):
        HOST = 'localhost'
        PORT = 7777

        # Datagram (udp) socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print('Socket created')
        except socket.error as msg:
            print('Failed to create socket. ' + msg)
            sys.exit()

        # Bind socket to local host and port
        try:
            s.bind((HOST, PORT))
        except socket.error as msg:
            print('Bind failed. ' + msg)
            sys.exit()
        print('Socket bind successfully')

        # start the main loop
        while 1:
            # receive data from client (data, addr)
            d = s.recvfrom(1024)
            #data = str(d[0], 'utf-8')
            # ip and port of request sender
            addr = d[1]

            # TODO: unmarshall data to decode task service


            # TODO: dispatch, excute services and get result


            # TODO: add request info and result into history


            # TODO: marshall result into bytes


            # TODO: reply bytes to request sender


