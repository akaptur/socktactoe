from multi_tictactoe import Game
import socket
import select
import sys
import pdb
import time

def parse(move_as_string):
    row, col = [int(st) for st in move_as_string.split(",")]
    return (row, col)


def get_valid_remote_move(sc, game_obj):
    try:
        message = sc.recv(3)  # receive three-byte move
    except socket.error:
        time.sleep(0)
        move = get_valid_remote_move(sc, game_obj)  # if at first you don't succeed...
    human_move = parse(message)
    print "move received:", human_move
    if game_obj.validate_remote_move(human_move):
        return human_move
    else:
        sc.sendall("Not valid.  Move again.")
        human_move = get_valid_remote_move(sc, game_obj)
        return human_move  # pass the move back up the stack

def make_listen_sock():
    HOST = sys.argv.pop() if len(sys.argv) == 3 else "127.0.0.1"
    PORT = 1060
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)

    return s

if __name__ == '__main__':
    listen_sock = make_listen_sock()
    print "Listening for games"
    all_sockets = {listen_sock.fileno(): listen_sock}
    all_games = {} # hashed with same keys as all_sockets 

    while True:
        # print "before select call:"
        # print "All sockets", all_sockets
        # print "All games:", all_games
        read_socks, write_socks, _ = select.select(all_sockets, all_sockets, '')
        # print "after select call"
        client_move = [id_num for id_num in all_games if all_games[id_num].player == 'x'] 
        server_move = [id_num for id_num in all_games if all_games[id_num].player == 'o']
        ended_games = [id_num for id_num in all_games if all_games[id_num].game_over()]

        incoming_moves = [id_num for id_num in client_move if id_num in read_socks]
        outgoing_moves = [id_num for id_num in server_move if id_num in write_socks]
        end_and_shut = [id_num for id_num in ended_games if id_num in write_socks]

        # SMVELLY SMVELLY (combine these four lines into two?)
        print "read:", read_socks
        print "write:", write_socks
        print "client move: ", client_move
        print "server_move: ", server_move
        print "in: ", incoming_moves
        print "out: ", outgoing_moves
        print "ended:", ended_games
        print "end and shut:", end_and_shut

        pdb.set_trace()

        # game ready for human move AND socket ready to read

        if listen_sock.fileno() in read_socks:
            game_sock, address = listen_sock.accept()
            game_sock.setblocking(False)  # very important
            id_num = game_sock.fileno()
            print "New game:", id_num
            print "Socket connects", game_sock.getsockname(), "and", game_sock.getpeername()
            g = Game()
            all_games[id_num] = g  # init new TTT Game, add to dict
            all_sockets[id_num] = game_sock # add to dict
            assert g.player == 'x'
            game_sock.sendall("Let's play Tic Tac Toe!\n"+g.board_as_string())

        for id_num in end_and_shut:
            sock = all_sockets[id_num]
            ended_game = all_games[id_num]
            assert ended_game.game_over()
            message = ended_game.end_message()
            sock.sendall(message)
            sock.shutdown(1)
            del all_sockets[id_num]
            del all_games[id_num]




        for id_num in incoming_moves:
            # Gross
            sock = all_sockets[id_num]
            game_in = all_games[id_num]
            assert game_in.player == 'x'
            move = get_valid_remote_move(sock, game_in)
            game_in.make_human_move(move)
            game_in.player = game_in.next_turn(game_in.player)  # switch to next player
            print game_in.player

        for id_num in outgoing_moves:
            sock = all_sockets[id_num]
            game_out = all_games[id_num]
            assert game_out.player == 'o'
            game_out.minimax(game_out.player)
            game_out.player = game_out.next_turn(game_out.player)
            sock.sendall(game_out.board_as_string())

        # write game over handling and dead socket removal

