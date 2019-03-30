import socket  # for sockets
import sys  # for exit


def udp_client():
    # create dgram udp socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        print('Failed to create socket')
        sys.exit()

    try:
        s.bind(('127.0.0.1', 8888))
    except socket.error as msg:
        print('Bind failed. ' + msg)
        sys.exit()

    host = 'localhost';
    port = 7777;
    while (1):
        #msg = input('Enter message to send : ')
        #b = bytes(msg, 'utf-8')
        b = bytes(chr(len(str(0))) + str(0) + chr(len('jordan')) + 'jordan' + chr(len(str(13))) + str(13) + chr(
                len(str(1))) + str(1) + chr(len("Shanghai")) + "Shanghai" + chr(len("Beijing")) + "Beijing", 'utf-8')
        try:
            # Set the whole string
            s.sendto(b, (host, port))

            # receive data from client (data, addr)
            d = s.recvfrom(1024)
            reply = str(d[0], 'utf-8')
            addr = d[1]

            print('Server reply byte code: ')
            print(d[0])
            print('string: ' + reply)
            idx = 0
            tokens = []
            while idx != len(reply):
                length = ord(reply[idx])
                tokens.append(reply[idx+1:idx+length+1])
                idx = idx+length+1
            print(tokens)
            break

        except socket.error as msg:
            print(msg)
            sys.exit()


if __name__ == '__main__':
    udp_client()