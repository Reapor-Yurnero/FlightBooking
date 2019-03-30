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

    host = 'localhost';
    port = 7777;

    b = bytes(chr(len(str(0))) + str(0) + chr(len('jordan')) + 'jordan' + chr(len(str(16))) + str(16) + chr(
        len(str(4))) + str(4) + chr(len("HU201")) + "HU201" + chr(len(str(30))) + str(30), 'utf-8')

    while 1:
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
            # monitor
            if tokens[1] == '1':
                start_time = time.time()
                print("start monitoring")
                while time.time() <= start_time + 30:
                    try:
                        s.settimeout(1)
                        d = s.recvfrom(1024)
                        reply = str(d[0], 'utf-8')

                        print('Server callback message byte code: ', end='')
                        print(d[0])
                        print('Stringed byte code: ' + reply)
                        tokens = simpleunmarshall(reply)

                        b = bytes(chr(len(str(1))) + str(1) + chr(len('Callback received')) + 'Callback received', 'utf-8')
                        s.sendto(b, (host, port))
                        print("callback reply sent by client")
                    except socket.timeout as e:
                        continue
                print("monitor interval ends")
            break
        except socket.error as msg:
            print(msg)
            sys.exit()


if __name__ == '__main__':
    udp_client()

    # blist = []
    # test sevice one
    # b = bytes(chr(len(str(0))) + str(0) + chr(len('jordan')) + 'jordan' + chr(len(str(13))) + str(13) + chr(
    #        len(str(1))) + str(1) + chr(len("Guangzhou")) + "Guangzhou" + chr(len("Beijing")) + "Beijing", 'utf-8')

    # test service two
    # b = bytes(chr(len(str(0))) + str(0) + chr(len('jordan')) + 'jordan' + chr(len(str(13))) + str(13) + chr(
    #         len(str(2))) + str(2) + chr(len("HU301")) + "HU301", 'utf-8')

    # test service three
    # blist.append(bytes(chr(len(str(0))) + str(0) + chr(len('jordan')) + 'jordan' + chr(len(str(13))) + str(13) + chr(
    #     len(str(3))) + str(3) + chr(len("HU201")) + "HU201" + chr(len(str(5))) + str(5), 'utf-8'))

    # test service five
    # blist.append(bytes(chr(len(str(0))) + str(0) + chr(len('jordan')) + 'jordan' + chr(len(str(14))) + str(14) + chr(
    #     len(str(5))) + str(5), 'utf-8'))

    # test service six
    # blist.append(bytes(chr(len(str(0))) + str(0) + chr(len('Jordan')) + 'Jordan' + chr(len(str(15))) + str(15) + chr(
    #     len(str(6))) + str(6) + chr(len("HU201")) + "HU201" + chr(len(str(3))) + str(3), 'utf-8'))

    # test service five
    # blist.append(bytes(chr(len(str(0))) + str(0) + chr(len('jordan')) + 'jordan' + chr(len(str(16))) + str(16) + chr(
    #     len(str(5))) + str(5), 'utf-8'))