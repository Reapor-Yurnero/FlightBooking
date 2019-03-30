import socket  # for sockets
import sys  # for exit

class server():

    def __init__(self):

        # flightdb: Dic[flightID] -> details: departuretime, airfare, availibity, src, dest
        self.flightdb = \
            {
                "MU110": {"details": [1800, 1000, 10], "src": "Shanghai", "dest": "Beijing"},
                "HU201": {"details": [1405, 600, 16], "src": "Singapore", "dest": "Bali"},
                "MU5125": {"details": [930, 211, 52], "src": "Shanghai", "dest": "Beijing"}
            }

        # bookingdb: Dic[Name][flightID] -> quantity of flightID booked by Name
        self.bookingdb = {"Jordan": {"MU110": 3},
                          "Kobe": {"MU110": 10, "HU201": 3}}

        # request history {(requestorname,requestID):result} result is byte array or None
        self.requesthistory = {}

        # callback list
        self.callbacklist = []

    def initsocket(self):
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
        return s

    def unmarshallstringedbytes(self, data):
        idx = 0
        tokens = []
        while idx != len(data):
            length = ord(data[idx])
            tokens.append(data[idx + 1:idx + length + 1])
            idx = idx + length + 1
        tokens = tuple(tokens)  # make tokens readonly
        return tokens

    def start(self):
        # initialize the socket

        s = self.initsocket()

        # start the main loop

        while 1:
            # TODO: receive data from client (data, addr)
            d = s.recvfrom(1024)
            bytedata = d[0]
            srcaddr = d[1]
            # data = str(d[0], 'utf-8')
            # ip and port of request sender
            # addr = d[1]
            # bytedata = bytes(chr(len(str(0))) + str(0) + chr(len('jordan')) + 'jordan' +
            # chr(len(str(13))) + str(13) + chr(len(str(1))) + str(1) + chr(len("Shanghai")) + "Shanghai" + chr(len("Beijing")) + "Beijing", 'utf-8')
            # b'\x010\x06jordan\x0213\x011\x08Shanghai\x07Beijing'
            data = str(bytedata, 'utf-8')

            # TODO: unmarshall data to tokens list
            #
            tokens = self.unmarshallstringedbytes(data)
            # note that tokens is a string list, all elements are string literal
            messageType = tokens[0]
            if messageType != '0':
                print("wrong message type!")
                sys.exit(0)
            requesterName = tokens[1]
            requestID = tokens[2]
            requestedService = tokens[3]

            #
            # TODO: filter the request and bypass the execution if result already stored
            #
            if (requesterName, requestID) in self.requesthistory:

                # TODO: reply bytes to request sender
                s.sendto(self.requesthistory[(requesterName, requestID)], srcaddr)
                print("reply sent from server")

                # TODO: Callback callbacklist and clean clients expired monitor duration from list

                # end current while loop
                continue

            # TODO: dispatch, execute services and get resultlist

            resultlist = \
                {
                '1': self.findflight,
                '2': self.checkdetails,
                '3': self.bookflight,
                '4': self.monitorflight,
                '5': self.checkorder,
                '6': self.cancelbooking,
                }[requestedService](tokens)

            print(resultlist)

            # TODO: marshall result into byte result
            byteresult = self.marshallresult(resultlist)
            print(byteresult)

            # TODO: add request info and result into history
            self.requesthistory[(requesterName, requestID)] = byteresult

            # TODO: reply bytes to request sender
            s.sendto(byteresult, srcaddr)
            print("reply sent from server")

            # TODO: Callback callbacklist and clean clients expired monitor duration from list

    def marshallresult(self, resultlist):
        # prepare header
        byteresult = bytes(chr(len(str(1)))+str(1), 'utf-8') # messageType = reply
        # append results
        for result in resultlist:
            byteresult += bytes(chr(len(result))+result if type(result) is str else chr(len(str(result)))+str(result),
                                'utf-8')

        return byteresult


    def findflight(self, tokens):
        # arguments: string source, string destination
        # return: string FlightID or string "No flight found"
        print("findFlight called")
        source = tokens[4]
        destination = tokens[5]
        result = [0]  # result[0] = 0 means no result , positive value represents number of applicable flights found

        for flightID in self.flightdb:
            if self.flightdb[flightID]["src"] == source or self.flightdb[flightID]["dest"] == destination:
                print(flightID)
                result[0] += 1
                result.append(flightID)
        return result

    def checkdetails(self, tokens):
        print("checkDetails called")
        return ""

    def bookflight(self, tokens):
        print("bookFlight called")
        return ""

    def monitorflight(self, tokens):
        print("monitorFlight called")
        return ""

    def checkorder(self, token):
        print("checkOrder called")
        return ""

    def cancelbooking(self, token):
        print("cancelBooking called")
        return ""


if __name__ == '__main__':
    aServer = server()
    aServer.start()
