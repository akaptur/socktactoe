from multi_tictactoe import Game
import socket
import select
import sys
import pdb
import time

# TODO: better logging
# TODO: error handling when client unexpectedly disconnects (ctrl-c)
# TODO: objectify

# class TTT_Server(Object):
#     def __init__(self):



def parse(move_as_string):
    try:
        row, col = [int(st) for st in move_as_string.split(",")]
        return (row, col)
    except:
        return None


def get_message(sock):
    try:
        some_string = sock.recv(128)  # move is only three bytes, but want to catch all of invalid move at once
        print "move received:", some_string
        return some_string
    except socket.error as (err_num, err_string):
        return "Error"+str(err_num)


def make_listen_sock():
    HOST = sys.argv.pop() if len(sys.argv) == 2 else ""
    PORT = 1060
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)

    return s

def handle_client_move(id_num, socket_list):
    sock, game, msg_queued, _, _ = socket_list[id_num]
    assert game.player == 'x'
    
    msg = get_message(sock) 
    # if "Error" in msg:
    #     print msg
    #     socket_list[id_num][4] = True
    client_move = parse(msg)

    if not client_move or not game.validate_move(client_move):
        print "Invalid move received on socket %d" % sock.fileno()
        msg_queued = "Not valid.  Try again."
    else:
        game.make_move(client_move, game.player)
        print "Move made on socket ", sock.fileno(), ":\n", game.board_as_string()
        game.player = 'o'

    socket_list[id_num][2] = msg_queued  # why did this ever work?


if __name__ == '__main__':
    listen_sock = make_listen_sock()
    listen_id = listen_sock.fileno()
    print "Listening for games"

    game_sockets = {}
    # Form: {File_number: (socket, game, message)}

    while True:
        #######################
        ### GAME PROCESSING ###
        #######################
        closed_socks = []
        for id_num in game_sockets.keys():
            sock, game, msg_queued, game_over, err_flag = game_sockets[id_num]

            if err_flag:
                closed_socks.append(id_num)

            if game_over and not msg_queued:
                sock.close()
                closed_socks.append(id_num)

            elif game.is_over():
                msg_queued = game.end_message()
                game_over = True

            elif game.player == 'o':
                game.minimax()
                if game.is_over():
                    msg_queued = game.board_as_string()+'\n'+game.end_message()
                    game_over = True
                else:
                    msg_queued = game.board_as_string()
                game.player = 'x'

            game_sockets[id_num] = [sock, game, msg_queued, game_over, err_flag]

        for id_num in closed_socks:
            del game_sockets[id_num]

        #########################
        ### SOCKET PROCESSING ###
        #########################
        all_sockets = game_sockets.keys() + [listen_id]
        print "All sockets:", all_sockets

        read_socks, write_socks, _ = select.select(all_sockets, all_sockets, '')
        print "Read:", read_socks, '\nWrite:', write_socks
        #  Perhaps surprising that this works, since all_sockets is just a list of filenumbers.
        #  However, select.select is just looking for file numbers and looking up the corresponding socket objects.

        for id_num in read_socks:
            if id_num == listen_id:
                game_sock, address = listen_sock.accept()
                game_sock.setblocking(False)  # very important
                game_id_num = game_sock.fileno()
                print "New game:", game_id_num
                print "Socket connects", game_sock.getsockname(), "and", game_sock.getpeername()
                g = Game()  # init new TTT Game
                msg_queued = "Let's play Tic Tac Toe!\n"+g.board_as_string()
                game_over = False
                err_flag = False
                game_sockets[game_id_num] = [game_sock, g, msg_queued, game_over, err_flag] # add to dict

            else:
                sock, game, _, _, _ = game_sockets[id_num]
                if game.player == 'x':
                    handle_client_move(id_num, game_sockets)


        for id_num in write_socks:
            sock, _, message, _, _ = game_sockets[id_num]
            if message:
                sock.sendall(message)
                game_sockets[id_num][2] = None  # reset message to None once sent



