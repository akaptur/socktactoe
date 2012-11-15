import socket
import sys


if __name__ == '__main__':
    HOST = sys.argv.pop() if len(sys.argv) == 3 else "127.0.0.1"
    PORT = 1060
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        s.connect((HOST, PORT))
        print "Client has been assigned sock name", s.getsockname()
        message = s.recv(100)
        print message
        keep_playing = True
        while keep_playing:
            message = raw_input("Input a move  (0,0 to 2,2)\n")
            s.sendall(message)
            message = s.recv(50)  # board is 50 chars
            print message
            if "Game over" in message:
                keep_playing = False
                # sys.exit()  # Hmm, where should this go
