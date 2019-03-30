import socket  # for sockets
import sys  # for exit
import time # for duration

SERVERADDR = ('localhost', 7777)  # modify this when necessary

class Client():
    def __init__(self, port=8888):
        self.socketPort = port
        self.username = ""
        self.requestID = 0

    def start(self):
        # TODO: setup socket
        s = self.initsocket()

        # TODO: read username from user and start up the interface main loop
        self.username = input("Type in your name: ")

        while 1:
            # TODO: interface to let users choose service
            print("Welcome {:s}! Select a service:".format(self.username))
            print("1. Find applicable flights from source to destination.")
            print("2. Get detailed information of a flight: departure time, airfare and vacancies.")
            print("3. Book a flight.")
            print("4. Monitor a flight.")
            print("5. Check order information.")
            print("6. Cancel ordered tickets")
            print("7. Exit")
            requestedservice = int(input("Type in the service you want (number 1-7): "))

            # TODO: collect arguments from interface
            arglist = self.getarguments(requestedservice)

            # TODO: marshall argument list into bytecode
            byteargs = self.marshallarguments(requestedservice, arglist)

            # TODO: send bytecode to server socket and receive result bytecode from server and unmarshall into tokens
            self.sendbyteargsandreceive(s, byteargs)

            # TODO: dispatch tokens to each service and generate corresponding output/do monitor

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
            s.bind(('localhost', self.socketPort))
        except socket.error as msg:
            print('Bind failed. ')
            print(msg)
            sys.exit()

        print('Socket bind successfully')
        return s

    def getarguments(self, servicetype):
        # note: input validity checking should be done in this step
        arglist = []
        if servicetype == 1:
            arglist.append(input("Source city: "))
            arglist.append(input("Destination city: "))
        elif servicetype == 2:
            arglist.append(input("Flight number you want to enquire: "))
        elif servicetype == 3:
            arglist.append(input("Flight number you want to book: "))
            inputvalid = False
            while not inputvalid:
                quantity = input("Quantity (positive integer): ")
                try:
                    quantity = int(quantity)
                    if quantity <= 0:
                        raise ValueError
                    arglist.append(quantity)
                    inputvalid = True
                except ValueError:
                    print("Input Error: please type in a positive integer as desired quantity!")
                    continue
        elif servicetype == 4:
            arglist.append(input("Flight number you want to monitor: "))
            inputvalid = False
            while not inputvalid:
                duration = input("How long do you want to monitor? [10, 120] second: ")
                try:
                    duration = int(duration)
                    if duration <= 10 or duration >= 120:
                        raise ValueError
                    arglist.append(duration)
                    inputvalid = True
                except ValueError:
                    print("Input Error: please type in a positive integer in between 10 and 120!")
                    continue
        elif servicetype == 5:
            # Don't need any argument
            print("wait a second, proceeding...")
        elif servicetype == 6:
            arglist.append(input("Flight number you want to cancel: "))
            inputvalid = False
            while not inputvalid:
                quantity = input("Quantity (positive integer): ")
                try:
                    quantity = int(quantity)
                    if quantity <= 0:
                        raise ValueError
                    arglist.append(quantity)
                    inputvalid = True
                except ValueError:
                    print("Input Error: please type in a positive integer as desired quantity!")
                    continue
        elif servicetype == 7:
            print("exiting...")
            sys.exit()
        else:
            print("Input Error: Please type in an integer from 1 to 7")
            time.sleep(1)

        print(arglist)
        return arglist

    def marshallarguments(self, requestedtype, arglist):
        # prepare message header
        self.requestID += 1
        byteargs = bytes(chr(len(str(0)))+str(0), 'utf-8')  # messageType = request
        byteargs += bytes(chr(len(self.username)) + self.username, 'utf-8')  # requesterName
        byteargs += bytes(chr(len(str(self.requestID))) + str(self.requestID), 'utf-8')  # requestID
        byteargs += bytes(chr(len(str(requestedtype))) + str(requestedtype), 'utf-8')  # requestedtype
        # append arguments
        for arg in arglist:
            byteargs += bytes(chr(len(arg))+arg if type(arg) is str else chr(len(str(arg)))+str(arg), 'utf-8')
        print(byteargs)
        return byteargs

    def sendbyteargsandreceive(self, s, byteargs):
        # note: retransmit request if timeout
        resulttokens = []
        while 1:
            s.settimeout(1)
            try:
                s.sendto(byteargs, SERVERADDR)

                d = s.recvfrom(1024)
                resultstring = str(d[0], 'utf-8')
                resulttokens = self.unmarshallresultstringedbytes(resultstring)
                break
            except socket.timeout as e:
                continue
            except socket.error as msg:
                print(msg)
                sys.exit()
        s.settimeout(None)
        print(resulttokens)
        return resulttokens

    def unmarshallresultstringedbytes(self, data):
        idx = 0
        tokens = []
        while idx != len(data):
            length = ord(data[idx])
            tokens.append(data[idx + 1:idx + length + 1])
            idx = idx + length + 1
        tokens = tuple(tokens)  # make tokens readonly
        return tokens

if __name__ == '__main__':
    aClient = Client()
    aClient.start()
