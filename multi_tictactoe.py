# from random import randint
# import pdb


class Game():
    def __init__(self):
        self.matrix = [[' ',' ',' '],[' ',' ',' '],[' ',' ',' ']]
        self.player = 'x'

    def user_move(self):
        yourmove = raw_input("Enter your move as 0,0 to 2,2\n")
        i = int(yourmove[0])
        j = int(yourmove[2])
        if self.matrix[i][j] != ' ':
            print "That square is occupied.  Try again."
            self.user_move()
        else:
            self.matrix[i][j] = 'x'

    def validate_remote_move(self, (row, col)):
        if self.matrix[row][col] != ' ':
            return False
        else:
            return True

    def make_human_move(self, (row, col)):
        self.matrix[row][col] = 'x'

    def legal_moves(self):
        moves = []
        for i in range(0, 3):
            for j in range(0, 3):
                if self.matrix[i][j] == ' ':
                    moves.append([i, j])
        return moves

    def move(self, player):
        if player == 'o':
            self.minimax(player)
        else:
            self.user_move()

    def next_turn(self, player):
        return 'o' if player == 'x' else 'x'

    def winner_if_any(self):
        winner = None
        for i in range(0, 3):
            if self.matrix[i][0] == self.matrix[i][1] and self.matrix[i][1] == self.matrix[i][2] and self.matrix[i][0] != ' ':
                winner = self.matrix[i][0]
        for j in range(0, 3):
            if self.matrix[0][j] == self.matrix[1][j] and self.matrix[1][j] == self.matrix[2][j] and self.matrix[0][j] != ' ':
                winner = self.matrix[0][j]
        if self.matrix[0][0] == self.matrix[1][1] and self.matrix[1][1] == self.matrix[2][2] and self.matrix[1][1] != ' ':
            winner = self.matrix[0][0]
        if self.matrix[0][2] == self.matrix[1][1] and self.matrix[1][1] == self.matrix[2][0] and self.matrix[1][1] != ' ':
            winner = self.matrix[1][1]
        return winner

    def end_message(self, winner):
        if winner == 'x':
            message = "Game over. You win!"
        elif winner == 'o':
            message = "Game over. You lose!"
        else:
            message = "Game over. Tie game."
        return message

    def print_board(self):
        for i in range(0, 2):
            for j in range(0, 2):
                print self.matrix[i][j], '|',
            print self.matrix[i][2]
            print " -  -  - "
        for j in range(0, 2):
            print self.matrix[2][j], '|',
        print self.matrix[2][2]

    def utility(self):  # utility is from player o's perspective (1 if o wins, -1 if o loses)
        winner = self.winner_if_any()
        if winner == 'o':
            util = 1
        elif winner == 'x':
            util = -1
        else:
            util = 0
        return util

    def game_over(self):
        empty_squares = 0
        for i in range(0, 3):  # looping through rows (but not cols - count does that for us)
            empty_squares += self.matrix[i].count(' ')

        if self.winner_if_any():
            return True
        elif empty_squares == 0:
            return True
        else:
            return False

    def max_value(self):  # maximizing player is computer ('o')
        if self.game_over():
            return self.utility()
        else:
            maxval = -10           # initialize
            children = []
            availmoves = self.legal_moves()
            for i in range(0, len(availmoves)):
                self.matrix[availmoves[i][0]][availmoves[i][1]] = 'o'     # do move
                children.append(self.min_value())                         # evaluate move
                self.matrix[availmoves[i][0]][availmoves[i][1]] = ' '     # undo move
        return max(max(children), maxval)

    def min_value(self):  # minimizing player is user ('x')
        if self.game_over():
            return self.utility()
        else:
            minval = 10
            children = []
            availmoves = self.legal_moves()
            for i in range(0, len(availmoves)):
                self.matrix[availmoves[i][0]][availmoves[i][1]] = 'x'    # play move (player is 'x' or 'o')
                children.append(self.max_value())
                self.matrix[availmoves[i][0]][availmoves[i][1]] = ' '    # undo move
        return min(min(children), minval)

    def minimax(self, player):
        availmoves = self.legal_moves()
        options = []
        for i in range(0, len(availmoves)):
            self.matrix[availmoves[i][0]][availmoves[i][1]] = 'o'
            options.append(self.min_value())
            self.matrix[availmoves[i][0]][availmoves[i][1]] = ' '    # undo move
        print "options are:", options
        max_val = max(options)
        print "max is ", max_val
        location = options.index(max_val)
        print availmoves[location]
        row, col = availmoves[location]
        self.matrix[row][col] = 'o'

    def send_as_string(self):
        b = reduce(lambda x, y: x + y, self.matrix)  # flatten list of lists
        out = "".join([b[0], " | ", b[1], " | ", b[2], "\n",
                " -  -  - \n",
                b[3], " | ", b[4], " | ", b[5], "\n",
                " -  -  - \n",
                b[6], " | ", b[7], " | ", b[8], "\n"])
        return out


def play_game():
    b = Game()
    # b.print_board()

    if b.player == 'o':
        print "Computer's turn first"
    else:
        print "Your turn first"

    while not b.game_over():
        b.move(b.player)
        # print "player is", player, "winner_if_any is", b.winner_if_any(), "utility is ", b.utility()
        b.player = b.next_turn(b.player)
        b.print_board()

    winner = b.winner_if_any()
    print b.end_message(winner)

if __name__ == '__main__':
    b = Game()
    print b.send_as_string()
    # play_game()
