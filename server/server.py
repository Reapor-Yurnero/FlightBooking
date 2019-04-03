import socket  # for sockets
import sys  # for exit
import time  # for duration
import json

HOST = ''
PORT = 2222


class Server:

    def __init__(self, reliableudp=True):

        # flightdb: Dic[flightID] -> details: departuretime, airfare, availibity, src, dest
        self.flightdb = \
            {
                "MU110": {"details": [1800, 1000.3, 10], "src": "Shanghai", "dest": "Beijing", "modified": False},
                "HU201": {"details": [1405, 600.2, 16], "src": "Singapore", "dest": "Bali", "modified": False},
                "MU5125": {"details": [930, 211.1, 52], "src": "Shanghai", "dest": "Beijing", "modified": False}
            }

        # bookingdb: Dic[Name][flightID] -> quantity of flightID booked by Name
        self.bookingdb = {"Jordan": {"MU110": 3},
                          "Kobe": {"MU110": 10, "HU201": 3}}

        try:
            fp1 = open("flights.json", 'r')
            fp2 = open('booking.json', 'r')
            self.flightdb = json.load(fp1)
            self.bookingdb = json.load(fp2)
        except FileNotFoundError as e:
            print("No input databases, using the default one now")

        # request history {(requestorname,requestID):result} result is byte array or None
        self.requesthistory = {}

        # callback list
        self.callbacklist = []

        # switch for reliable udp (filter duplicated request + no re-execute)
        self.reliableudp = reliableudp

    def start(self):
        # initialize the socket

        s = self.initsocket()

        # start the main loop

        while 1:
            # TODO: reset modified flag
            for flight in self.flightdb.items():
                flight[1]["modified"] = False

            # TODO: receive data from client (data, addr)
            try:
                d = s.recvfrom(1024)
            except socket.timeout as e:
                continue
            except socket.error as msg:
                print(msg)
                sys.exit()
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
            if messageType == '3':
                self.request_ack(tokens)
                continue
            elif messageType != '0':
                print("wrong message type!")
                print(tokens)
                sys.exit(0)
            requesterName = tokens[1]
            requestID = tokens[2]
            requestedService = tokens[3]

            #
            # TODO: filter the request and bypass the execution if result already stored
            #
            if self.reliableudp and (requesterName, requestID) in self.requesthistory:

                # TODO: reply bytes to request sender
                s.sendto(self.requesthistory[(requesterName, requestID)], srcaddr)
                print("duplicated request from {:s}({:s}), reply sent from server".format(requesterName, requestID))

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

            # print(resultlist)

            # TODO: marshall result into byte result
            byteresult = self.marshallresult(resultlist)
            # print(byteresult)

            # TODO: add request info and result into history
            self.requesthistory[(requesterName, requestID)] = byteresult
            print("New request and result are added into request history: ", end="")
            print(self.requesthistory)

            # TODO: reply bytes to request sender
            try:
                s.sendto(byteresult, srcaddr)
                print("Reply sent by server: ", end="")
                print(byteresult)
            except socket.error as msg:
                print(msg)
                sys.exit()

            # TODO: receive acknowledgement from client


            # TODO: Callback callbacklist and clean clients with expired monitor duration from list
            self.callback(s)

            # TODO: Add Client with necessary info to callbacklist if requested monitoring
            if requestedService == '4' and resultlist[0] == 1:
                self.callbacklist.append([srcaddr, tokens[4], time.time()+int(tokens[5])])
                print("Callback list updated: ", end='')
                print(self.callbacklist)

    def initsocket(self):

        # Datagram (udp) socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print('Socket created')
        except socket.error as msg:
            print('Failed to create socket. ')
            print(msg)
            sys.exit()

        # Bind socket to local host and port
        try:
            s.bind((HOST, PORT))
        except socket.error as msg:
            print('Bind failed. ')
            print(msg)
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

    def marshallresult(self, resultlist):
        # prepare header
        byteresult = bytes(chr(len(str(1)))+str(1), 'utf-8')  # messageType = reply
        # append results
        for result in resultlist:
            byteresult += bytes(chr(len(result))+result if type(result) is str else chr(len(str(result)))+str(result),
                                'utf-8')

        return byteresult

    def findflight(self, tokens):
        # arguments: string source, string destination
        # return: resultlist[0] = 0 means no result , positive value represents number of applicable flights found
        # following elements are the applicable flightNO
        source = tokens[4]
        destination = tokens[5]
        print("Service findFlight({:s}, {:s}) called by ({:s}, {:s})".format(source, destination, tokens[1], tokens[2]))
        resultlist = [0]

        for flightID in self.flightdb:
            if self.flightdb[flightID]["src"] == source and self.flightdb[flightID]["dest"] == destination:
                print(flightID)
                resultlist[0] += 1
                resultlist.append(flightID)
        return resultlist

    def checkdetails(self, tokens):
        # arguments: string flightNO
        # return: resultlist[0]: exist or not, if 1, resultlist[1:4] fills the details info requested, if 0, no exist
        flightID = tokens[4]
        resultlist = [0]
        print("Service checkDetails({:s}) called by {:s}({:s})".format(flightID, tokens[1], tokens[2]))

        if flightID in self.flightdb:
            resultlist[0] = 1
            resultlist += self.flightdb[flightID]["details"]
        return resultlist

    def bookflight(self, tokens):
        # arguments: string flightNO, int quantity (>0)
        # return: resultlist[0]=1:succeeed, 0:failed because of not enough vacancy, -1:failed because of no such flight
        requestername = tokens[1]
        flightNO = tokens[4]
        requestedquantity = int(tokens[5])
        print("Service bookFlight({:s}, {:d}) called by {:s}({:s})"
              .format(flightNO, requestedquantity, tokens[1], tokens[2]))
        resultlist = [-1]
        if flightNO in self.flightdb and self.flightdb[flightNO]["details"][2] >= requestedquantity:
            resultlist[0] = 1
            self.flightdb[flightNO]["modified"] = True  # set the flag correspondingly
            self.flightdb[flightNO]["details"][2] -= requestedquantity
            if requestername in self.bookingdb:
                self.bookingdb[requestername][flightNO] = self.bookingdb[requestername][flightNO] + requestedquantity \
                    if flightNO in self.bookingdb[requestername] else requestedquantity
            else:
                self.bookingdb[requestername] = {}
                self.bookingdb[requestername][flightNO] = requestedquantity

        elif flightNO in self.flightdb and self.flightdb[flightNO]["details"][2] < requestedquantity:
            resultlist[0] = 0
        print(self.flightdb)
        print(self.bookingdb)
        return resultlist

    def monitorflight(self, tokens):
        # arguments: string FlightNO, int duration
        # return: returnlist[0]=1: approved; 0: no such flight. returnlist[1]=duration
        flightNO = tokens[4]
        resultlist = [0]
        print("Service monitorFlight({:s}, {:s}) called by {:s}({:s})".format(flightNO, tokens[5], tokens[1], tokens[2]))
        if flightNO in self.flightdb:
            resultlist[0] = 1
            resultlist.append(int(tokens[5]))

        return resultlist

    def checkorder(self, tokens):
        # arguments: None
        # return resultlist[0]=0:no tickets ordered;pos num:total quantity of tickets ordered
        # resultlist[1:]: string flightNO, int quantity, string flightNO, int quantity, ...
        print("Service checkOrder called by {:s}({:s})".format(tokens[1], tokens[2]))
        requestername = tokens[1]
        resultlist = [0]
        if requestername in self.bookingdb:
            for item in self.bookingdb[requestername].items():
                resultlist.append(item[0])
                resultlist.append(item[1])
                resultlist[0] += item[1]

        return resultlist

    def cancelbooking(self, tokens):
        # arguments: string flightNo, int quantity (>0)
        # return: resultlist[0]=1:succeeed, 0:failed because of no enought booked quantity,
        # -1:failed because of no such flight
        requestername = tokens[1]
        flightNO = tokens[4]
        cancelquantity = int(tokens[5])
        print("Service cancelBooking({:s}, {:d}) called by {:s}({:s})"
              .format(flightNO, cancelquantity, tokens[1], tokens[2]))
        resultlist = [-1]
        if flightNO in self.flightdb and self.checkuserquantity(requestername, flightNO) >= cancelquantity:
            resultlist[0] = 1
            self.flightdb[flightNO]["modified"] = True  # set the flag correspondingly
            self.flightdb[flightNO]["details"][2] += cancelquantity
            self.bookingdb[requestername][flightNO] -= cancelquantity
            if self.bookingdb[requestername][flightNO] == 0:
                self.bookingdb[requestername].pop(flightNO)
        elif flightNO in self.flightdb:
            resultlist[0] = 0

        print(self.flightdb)
        print(self.bookingdb)
        return resultlist

    def request_ack(self, tokens):
        # arguments: None
        # return: None
        if (tokens[1], tokens[2]) in self.requesthistory:
            del self.requesthistory[(tokens[1], tokens[2])]
            print("Acknowledgement ({:s},{:s}) received, clear from the history: ".format(tokens[1], tokens[2]), end="")
            print(self.requesthistory)
        else:
            print("Acknowledgement's corresponding request ({:s},{:s}) does not exist!".format(tokens[1], tokens[2]))
            sys.exit()

    # helper function for cancelbooking
    # arguments: string username, string flightNO
    # return: int quantity of the flightNO ticket booked by username (>=0)
    def checkuserquantity(self, user, flightNO):
        quantity = 0
        if user in self.bookingdb and flightNO in self.bookingdb[user]:
            quantity = self.bookingdb[user][flightNO]
        return quantity

    def callback(self, s):
        for cbtarget in self.callbacklist:
            if cbtarget[2] < time.time():
                self.callbacklist.remove(cbtarget)
                print("Callback list updated: ", end='')
                print(self.callbacklist)
            elif self.flightdb[cbtarget[1]]["modified"]:
                # construct string message
                cbmessage = "Flight " + cbtarget[1] + " now has " \
                            + str(self.flightdb[cbtarget[1]]["details"][2]) + " vacancies!"
                # prepare header for bytecode
                cbbytecode = bytes(chr(len(str(2))) + str(2), 'utf-8')  # messageType = callback
                # marshalling
                cbbytecode += bytes(chr(len(cbmessage)) + cbmessage, 'utf-8')
                d = None
                while 1:
                    try:
                        s.settimeout(1)
                        s.sendto(cbbytecode, cbtarget[0])
                        print("Callback message sent by server: \"{:s}\"".format(cbmessage))
                        # try to receive reply from callback target
                        while 1:
                            d = s.recvfrom(1024)
                            cbreplystring = str(d[0], 'utf-8')
                            cbreplytokens = self.unmarshallstringedbytes(cbreplystring)
                            if cbreplytokens[0] == '3':
                                # acknowledge from other client come
                                self.request_ack(cbreplytokens)
                                continue
                            if cbreplytokens[0] != '1':
                                print("wrong callback reply messageType!")
                                print(cbreplytokens)
                                sys.exit()
                            break
                        print("Server receive callback reply from client:", end='')
                        print(cbreplytokens)
                        break
                    except socket.timeout as e:
                        continue
                    except socket.error as msg:
                        print(msg)
                        sys.exit()
                s.settimeout(None)

    def dumpjson(self):
        with open('dump_flights.json','w') as fp:
            json.dump(self.flightdb, fp)

        with open('dump_booking.json','w') as fp:
            json.dump(self.bookingdb, fp)


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'False':
        aServer = Server(False)
        print("Manually chose udp reliability: {:s}".format(sys.argv[1]))
    else:
        aServer = Server()
    try:
        aServer.start()
    finally:
        aServer.dumpjson()
