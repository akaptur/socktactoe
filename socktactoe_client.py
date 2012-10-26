import socket
import sys


if __name__ == '__main__':
    HOST = sys.argv.pop() if len(sys.argv) == 3 else "127.0.0.1"
    PORT = 1060
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        s.connect((HOST, PORT))
        print "Client has been assigned sock name", s.getsockname()
        keep_playing = True
        while keep_playing:
            message = raw_input("Input a move \n")
            s.sendall(message)
            message = s.recv(50)  # board is 50 chars
            print message
            if "Game over" in message:
                sys.exit()
