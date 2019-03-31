import socket  # for sockets
import sys  # for exit
import time # for duration

SERVERADDR = ('localhost', 7777)  # modify this when necessary


class Client():
    def __init__(self):
        self.socketPort = 8888
        while 1:
            self.socketPort = input("Port: ")
            try:
                self.socketPort = int(self.socketPort)
                if self.socketPort < 2000 or self.socketPort > 65536:
                    raise ValueError
                break
            except ValueError:
                print("Input Error: please type in a positive integer from 2000 to 65536!")
                continue
        self.username = ""
        self.requestID = 0
        self.socket = None

    def start(self):
        # TODO: setup socket
        self.socket = self.initsocket()

        # TODO: read username from user and start up the interface main loop
        while 1:
            self.username = input("Type in your name: ")
            if self.username == '':
                print("Input Error: your name should not be empty!")
            else:
                break

        while 1:
            # TODO: interface to let users choose service
            requestedservice = self.serviceinterface()

            # TODO: collect arguments from interface
            arglist = self.getarguments(requestedservice)

            # TODO: marshall argument list into bytecode
            byteargs = self.marshallarguments(requestedservice, arglist)

            # TODO: send bytecode to server socket and receive result bytecode from server and unmarshall into tokens
            tokens = self.sendbyteargsandreceive(self.socket, byteargs)

            # TODO: dispatch tokens to each service and generate corresponding output/do monitor
            self.decodeandexecute(tokens, requestedservice)

            input("Press Return to go back to main menu...")

    def serviceinterface(self):
        print("Welcome {:s}! Select a service:".format(self.username))
        print("1. Find applicable flights from source to destination.")
        print("2. Get detailed information of a flight: departure time, airfare and vacancies.")
        print("3. Book a flight.")
        print("4. Monitor a flight.")
        print("5. Check order information.")
        print("6. Cancel ordered tickets")
        print("7. Exit")
        while 1:
            service = input("Type in the service you want (number 1-7): ")
            try:
                service = int(service)
                if service < 0 or service > 7:
                    raise ValueError
                return service
            except ValueError:
                print("Input Error: please type in a positive integer from 1 to 7!")
                continue

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

    def marshallarguments(self, requestedtype, arglist, messageType=0):
        # prepare message header
        if messageType == 0:
            self.requestID = time.time()  # don't update requestID if it's an ack
        byteargs = bytes(chr(len(str(messageType)))+str(messageType), 'utf-8')  # messageType = request (0) by default
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
        # send acknowledgement
        ack = self.marshallarguments(0, [], 3)
        s.sendto(ack, SERVERADDR)

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

    def decodeandexecute(self, tokens, servicetype):
        if tokens[0] == '1':  # reply message
            if servicetype == 1:
                print("There is(are) {:d} flight(s) applicable:".format(int(tokens[1])) if int(tokens[1]) > 0
                      else "There is no flight applicable")
                for flight in tokens[2:]:
                    print(flight)
            if servicetype == 2:
                print("No such flight!" if tokens[1] == '0'
                      else "Flight will depart at {:02d}:{:02d}, with airfare {:s} and {:s} vancancies"
                      .format(int(tokens[2]) // 100, int(tokens[2]) % 100, tokens[3], tokens[4]))
            if servicetype == 3:
                print(
                    {'1': "Booked successfully!",
                     '0': "Not enough vacancy!",
                     '-1': "No such flight!"}[tokens[1]]
                )
            if servicetype == 4:
                print("Monitor rejected: no such flight!" if tokens[1] == '0' else "Start monitoring...")
                # call monitor
                if tokens[1] == '1':
                    self.monitor(int(tokens[2]))
            if servicetype == 5:
                print("You have booked {:d} flight ticket(s) in all:".format(int(tokens[1])))
                for idx in range(1, 1 + (len(tokens)-2)//2):
                    print("Flight: {:s}, Quantity: {:d}".format(tokens[idx*2], int(tokens[2*idx+1])))
            if servicetype == 6:
                print(
                    {'1': "Canceled successfully!",
                     '0': "You haven't booked that many tickets!",
                     '-1': "No such flight!"}[tokens[1]]
                )

    def monitor(self, duration):
        start_time = time.time()
        while time.time() <= start_time + duration + 1:
            try:
                self.socket.settimeout(1)
                d = self.socket.recvfrom(1024)
                reply = str(d[0], 'utf-8')

                print('Server callback message byte code: ', end='')
                print(d[0])
                print('Stringed byte code: ' + reply)
                tokens = self.unmarshallresultstringedbytes(reply)
                self.paresecbmsg(tokens)
                b = bytes(chr(len(str(1))) + str(1) + chr(len('Callback received')) + 'Callback received', 'utf-8')
                self.socket.sendto(b, SERVERADDR)
                print("callback reply sent by client")
            except socket.timeout as e:
                continue
        self.socket.settimeout(None)
        print("monitor interval ends")

    def paresecbmsg(self, tokens):
        if tokens[0] != '2':
            print("Wrong messageType!")
            sys.exit()
        else:
            print(tokens[1])

if __name__ == '__main__':
    aClient = Client()
    aClient.start()
