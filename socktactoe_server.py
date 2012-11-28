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
        self.id_num = sock.fileno()
        self.game = Game()
        self.message = self.game.start_message()+"\n"+self.game.board_as_string()
        self.game_over = False
        self.err_flag = False



def parse(move_as_string):
    try:
        move = int(move_as_string) 
        return move
    except:
        return "Parse error"
        


def get_message(sock):
    try:
        some_string = sock.recv(128)  # move is only three bytes, but want to catch all of invalid move at once
        print "move received:", some_string
        return some_string
    except socket.error as (err_num, err_string):
        print "socket error"
        return "Error"+str(err_num)


def make_listen_sock():
    HOST = sys.argv[1] if len(sys.argv) == 2 else "127.0.0.1"
    PORT = 1060
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)

    return s

def accept_connection(opponents, listen_sock):
    game_sock, address = listen_sock.accept()
    opp = Opponent(game_sock)
    opponents[opp.sock] = opp
    return opponents

def handle_client_move(opp):
    assert opp.game.player == 'x'
    
    msg = get_message(opp.sock) 
    if "Error" in msg:
        print msg
        opp.err_flag = True
    client_move = parse(msg)

    if not type(client_move) == int or not opp.game.validate_move(client_move):
        print "Invalid move received on socket %d" % opp.sock.fileno()
        opp.message = "Not valid.  Try again."
    else:
        opp.game.make_move(client_move, opp.game.player)
        print "Move made on socket ", opp.sock.fileno(), ":\n", opp.game.board_as_string()
        opp.game.player = 'o'


def process_games(opponents):
    closed_socks = []

    for opp in opponents.values():

        if opp.err_flag: 
            closed_socks.append(opp.sock)

        if opp.game_over and not opp.message:
            opp.sock.close()
            closed_socks.append(opp.sock)

        elif opp.game.is_over():
            opp.message = opp.game.end_message()
            opp.game_over = True

        elif opp.game.player == 'o':
            util, best_move = opp.game.minimax()
            opp.game.make_move(best_move, 'o')
            if opp.game.is_over():
                opp.message = opp.game.board_as_string()+'\n'+opp.game.end_message()
                opp.game_over = True
            else:
                opp.message = opp.game.board_as_string()
            opp.game.player = 'x'

    opponents = dict((k,opp) for (k, opp) in opponents.items() if opp.sock not in closed_socks)
    return opponents

def process_sockets(opponents, listen_sock):
    all_sockets = opponents.keys() + [listen_sock]
    # print "All sockets:", all_sockets

    read_socks, write_socks, _ = select.select(all_sockets, all_sockets, '')
    # print "Read:", read_socks, '\nWrite:', write_socks

    # pdb.set_trace()

    for sock in read_socks:
        if sock is listen_sock:
            opponents = accept_connection(opponents, listen_sock)

        else:
            opp = opponents[sock]
            if opp.game.player == 'x':
                handle_client_move(opp)


    for sock in write_socks:
        opp = opponents[sock]
        if opp.message and not opp.err_flag:
            try:
                opp.sock.sendall(opp.message)
                opp.message = None
            except:
                pass

if __name__ == '__main__':
    listen_sock = make_listen_sock()
    print "Listening for games"
    opponents = {}

    while True:
        opponents = process_games(opponents)        
        process_sockets(opponents, listen_sock)
       
