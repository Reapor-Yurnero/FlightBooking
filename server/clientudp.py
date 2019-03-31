import socket  # for sockets
import sys  # for exit
import time

def simpleunmarshall(stringdata):
    idx = 0
    tokens = []
    while idx != len(stringdata):
        length = ord(stringdata[idx])
        tokens.append(stringdata[idx + 1:idx + length + 1])
        idx = idx + length + 1
    print("Tokenized reply: ", end='')
    print(tokens)
    return tokens

def udp_client():
    # create dgram udp socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        print('Failed to create socket')
        sys.exit()

    try:
        s.bind(('127.0.0.1', 9999))
    except socket.error as msg:
        print('Bind failed. ' + msg)
        sys.exit()

    host = 'localhost'
    port = 7777
    blist = []
    # test sevice one
    blist.append(bytes(chr(len(str(0))) + str(0) + chr(len('jordan')) + 'jordan' + chr(len(str(13))) + str(13) + chr(
           len(str(1))) + str(1) + chr(len("Shanghai")) + "Shanghai" + chr(len("Beijing")) + "Beijing", 'utf-8'))

    # test service two
    blist.append(bytes(chr(len(str(0))) + str(0) + chr(len('jordan')) + 'jordan' + chr(len(str(14))) + str(14) + chr(
            len(str(2))) + str(2) + chr(len("HU201")) + "HU201", 'utf-8'))

    # test service three
    blist.append(bytes(chr(len(str(0))) + str(0) + chr(len('James')) + 'James' + chr(len(str(13))) + str(13) + chr(
        len(str(3))) + str(3) + chr(len("HU201")) + "HU201" + chr(len(str(5))) + str(5), 'utf-8'))

    # test service three
    blist.append(bytes(chr(len(str(0))) + str(0) + chr(len('James')) + 'James' + chr(len(str(13))) + str(13) + chr(
        len(str(3))) + str(3) + chr(len("HU201")) + "HU201" + chr(len(str(5))) + str(5), 'utf-8'))

    # test service five
    blist.append(bytes(chr(len(str(0))) + str(0) + chr(len('James')) + 'James' + chr(len(str(14))) + str(14) + chr(
        len(str(5))) + str(5), 'utf-8'))

    # test service six
    blist.append(bytes(chr(len(str(0))) + str(0) + chr(len('James')) + 'James' + chr(len(str(15))) + str(15) + chr(
        len(str(6))) + str(6) + chr(len("HU201")) + "HU201" + chr(len(str(3))) + str(3), 'utf-8'))

    # test service five
    blist.append(bytes(chr(len(str(0))) + str(0) + chr(len('Kobe')) + 'Kobe' + chr(len(str(18))) + str(18) + chr(
        len(str(5))) + str(5), 'utf-8'))




    for b in blist:
        try:
            # Set the whole string
            s.sendto(b, (host, port))
            print("request sent")
            # receive data from server (data, addr)
            d = s.recvfrom(1024)
            reply = str(d[0], 'utf-8')

            print('Server reply byte code: ', end='')
            print(d[0])
            print('Stringed byte code: ' + reply)
            tokens = simpleunmarshall(reply)
        except socket.error as msg:
            print(msg)
            sys.exit()
        time.sleep(3)


if __name__ == '__main__':
    udp_client()