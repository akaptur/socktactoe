from multi_tictactoe import Game
import socket
import select
import sys
import pdb
import time

# TODO: better logging
# TODO: error handling when client unexpectedly disconnects (ctrl-c)
# TODO: neaten loops (add more functions)
# TODO: structure the network code to be able to play e.g. checkers just as seamlessly

class Opponent(object):
    def __init__(self, sock):
        self.sock = sock
        self.sock.setblocking(False)
        self.game = Game()
        self.message = self.game.start_message()+"\n"+self.game.board_as_string()
        self.game_over = False
        self.err_flag = False

    def fileno(self):
        # This method makes Opponent objects quack like i/o objects
        # which means they can be handled by select.select.
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

    def handle_client_move(self):
        assert self.game.player == 'x'
        client_move = self.get_message() 

        if not type(client_move) == int or not self.game.validate_move(client_move):
            print "Invalid move received on socket %d" % self.sock.fileno()
            self.message = "Not valid.  Try again."
        else:
            self.game.make_move(client_move, self.game.player)
            print "Move made on socket ", self.sock.fileno(), ":\n", self.game.board_as_string()
            self.game.player = 'o'
        

def make_listen_sock():
    HOST = sys.argv[1] if len(sys.argv) == 2 else "127.0.0.1"
    PORT = 1060
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    return s

def check_for_new_opponent(opponents, listen_sock):
    pending_connection, _, _ = select.select([listen_sock], '', '', 0)
    if pending_connection:
        game_sock, address = listen_sock.accept()
        opp = Opponent(game_sock)
        opponents.append(opp)
    return opponents


def filter_opponents(opponents):
    opps_to_delete = []

    for opp in opponents:
        if opp.err_flag or (opp.game.is_over() and not opp.message):
            opps_to_delete.append(opp)

    return [opp for opp in opponents if opp not in opps_to_delete]


def process_games(opponents):
    for opp in opponents:
        if opp.game.is_over():
            opp.message = opp.game.end_message()

        elif opp.game.player == 'o':
            _, best_move = opp.game.minimax()
            opp.game.make_move(best_move, 'o')
            if opp.game.is_over():
                opp.message = opp.game.end_message()
            else:
                opp.message = opp.game.board_as_string()
            opp.game.player = 'x'


def process_sockets(opponents):

    read_socks, write_socks, _ = select.select(opponents, opponents, '', 0)
    print "Read:", read_socks, '\nWrite:', write_socks

    # pdb.set_trace()

    for opp in read_socks:
        if opp.game.player == 'x':
            opp.handle_client_move()

    for opp in write_socks:
        if opp.message:
            try:
                opp.sock.sendall(opp.message)
                opp.message = None
            except:
                print "write error on socket %d" % opp.fileno()


if __name__ == '__main__':
    listen_sock = make_listen_sock()
    print "Listening for games"
    opponents = []

    while True:
        opponents = check_for_new_opponent(opponents, listen_sock)
        opponents = filter_opponents(opponents)

        process_games(opponents)      
        process_sockets(opponents)
       
