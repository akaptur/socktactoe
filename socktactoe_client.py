import socket
import sys
import pdb
import random

MODE = sys.argv[1] if len(sys.argv) == 2 else "single-player"

HOST = sys.argv[2] if len(sys.argv) == 3 else "127.0.0.1"
PORT = 1060

class Client(object):
    def __init__(self, mode):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        print "Client has been assigned sock name", self.sock.getsockname()
        self.done = False
        self.mode = mode

    def play(self):
        msg_recv = self.sock.recv(100)
        if not msg_recv:
            print "Sorry, something went wrong."
            # pdb.set_trace()
            self.done = True

        print msg_recv

        if "Game over" in msg_recv:
            print "Thanks for playing!"
            self.done = True
        else:
            if self.mode == "random":
                msg_to_send = str(random.randint(0,8))
                print "random move: "+msg_to_send
            elif self.mode == "single-player":
                msg_to_send = raw_input("Input a move (0 to 8)\n")
            self.sock.sendall(msg_to_send)


if __name__ == '__main__':
    c = Client(MODE)
    while not c.done:
        c.play()

