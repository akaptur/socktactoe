from multi_tictactoe import Game
import socket
import select
import sys
import pdb
import time

class Opponent(object):
    def __init__(self, sock):
        self.sock = sock
        self.sock.setblocking(False)
        self.game = Game()
        self.message = self.game.start_message()+"\n"+self.game.board_as_string()
        self.done = False
        self.err_flag = False

    def fileno(self):
        # This method makes Opponent objects act like i/o objects
        # which means they can be handled by select.select.
        # quack quack
        return self.sock.fileno()

    def get_message(self):
        try:
            some_string = self.sock.recv(128)  
            print "move received:", some_string
            move = int(some_string)
            return move
        except socket.error:
            print "socket error"
            self.err_flag = True
        except TypeError:
            print "Parse error"
        except ValueError:
            print "No move received"

    def handle_client_move(self):
        assert self.game.player == 'x'
        client_move = self.get_message() 

        if not type(client_move) == int or not self.game.validate_move(client_move):
            print "Invalid move received on socket %d" % self.fileno()
            self.message = "Not valid.  Try again."
        else:
            self.game.make_move(client_move, self.game.player)
            print "Move made on socket "+str(self.fileno())+":\n", self.game.board_as_string()
            self.game.player = 'o'
        

def make_listen_sock():
    HOST = sys.argv[1] if len(sys.argv) == 2 else "127.0.0.1"
    PORT = 1060
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    return s

def pending_connection(listen_sock):
    pending_connection, _, _ = select.select([listen_sock], '', '', 0)
    return pending_connection

def get_new_opp(listen_sock):
    game_sock, address = listen_sock.accept()
    new_opp = Opponent(game_sock)
    return new_opp


def filter_opponents(opponents):
    return [opp for opp in opponents if not opp.done]


def process_games(opponents):
    for opp in opponents:
        if opp.game.is_over():
            opp.message = opp.game.end_message()
            opp.done = True
        elif opp.game.player == 'o':
            _, best_move = opp.game.minimax('o', max)
            opp.game.make_move(best_move, 'o')
            if opp.game.is_over():
                opp.message = opp.game.end_message()
                opp.done = True
            else:
                opp.message = opp.game.board_as_string()
            opp.game.player = 'x'


def process_sockets(opponents):
    read_opps, write_opps, _ = select.select(opponents, opponents, '', 0)
    # print "Read:", [s.fileno() for s in read_socks]
    # print "Write:", [s.fileno() for s in write_socks]

    for opp in read_opps:
        if opp.game.player == 'x':
            opp.handle_client_move()

    for opp in write_opps:
        if opp.message:
            try:
                opp.sock.sendall(opp.message)
                opp.message = None
            except Exception as e:
                print "write error on socket %d" % opp.fileno()
                opp.err_flag = True
                print e


if __name__ == '__main__':
    listen_sock = make_listen_sock()
    print "Listening for games"
    opponents = []

    while True:
        if pending_connection(listen_sock):
            opponents += [get_new_opp(listen_sock)]

        process_games(opponents)
        process_sockets(opponents)
        opponents = filter_opponents(opponents)
        
       
