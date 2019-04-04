import socket  # for sockets
import sys  # for exit


def udp_server():
    HOST = 'localhost'
    PORT = 7777

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
    print('Socket bind complete')

    # now keep talking with the client
    while 1:
        # receive data from client (data, addr)
        d = s.recvfrom(1024)
        data = str(d[0], 'utf-8')
        addr = d[1]

        if not data:
            break

        reply = 'OK...' + data

        s.sendto(bytes(reply, 'utf-8'), addr)
        print('Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip())
        # print(":".join("{:02x}".format(ord(c)) for c in data.strip()))
    s.close()


if __name__ == '__main__':
    udp_server()
