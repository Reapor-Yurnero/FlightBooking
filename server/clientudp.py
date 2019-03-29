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
        msg = input('Enter message to send : ')
        b = bytes(msg, 'utf-8')
        try:
            # Set the whole string
            s.sendto(b, (host, port))

            # receive data from client (data, addr)
            d = s.recvfrom(1024)
            reply = str(d[0], 'utf-8')
            addr = d[1]

            print('Server reply : ' + reply)

        except socket.error as msg:
            print(msg)
            sys.exit()


if __name__ == '__main__':
    udp_client()