from multi_tictactoe import Game
import socket
import sys


def parse(move_as_string):
    row, col = [int(st) for st in move_as_string.split(",")]
    return (row, col)


def get_valid_remote_move(sc, game_obj):
    message = sc.recv(3)  # receive three-byte move
    human_move = parse(message)
    print "move received:", human_move
    if game_obj.validate_remote_move(human_move):
        return human_move
    else:
        sc.sendall("Not valid.  Move again.")
        human_move = get_valid_remote_move(sc, game_obj)
        return human_move  # pass the move back up the stack


if __name__ == '__main__':
    HOST = sys.argv.pop() if len(sys.argv) == 3 else "127.0.0.1"
    PORT = 1060
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1)

    while True:
        print "Listening at", s.getsockname()
        sc, sockname = s.accept()
        print "Accepted connection from", sockname
        print "Socket connects", sc.getsockname(), "and", sc.getpeername()
        g = Game()  # start with human move
        while not g.game_over():
            remote_move = get_valid_remote_move(sc, g)
            g.make_human_move(remote_move)
            if g.game_over():
                end_message = g.end_message(g.winner_if_any())
                sc.sendall(end_message)
                sc.close()
            else:
                g.minimax(g.player)
                g.player = g.next_turn(g.player)
                board_as_string = g.send_as_string()
                sc.sendall(board_as_string)
