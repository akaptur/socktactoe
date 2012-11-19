import socket
import sys
import pdb

if __name__ == '__main__':
    HOST = sys.argv.pop() if len(sys.argv) == 2 else "127.0.0.1"
    PORT = 1060
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    print "Client has been assigned sock name", s.getsockname()
    


    while True:    
        msg_recv = s.recv(100)
        while "Not valid" in msg_recv:
            print msg_recv
            msg_to_send = raw_input("Input a move  (0,0 to 2,2)\n")
            s.sendall(msg_to_send)
            msg_recv = s.recv(100)

        if not msg_recv:
            print "Sorry, something went wrong."
            break

        print msg_recv

        if "Game over" in msg_recv:
            print "Thanks for playing!"
            break
        else:
            msg_to_send = raw_input("Input a move  (0,0 to 2,2)\n")
            s.sendall(msg_to_send)