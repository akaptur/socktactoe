# from random import randint
import pdb


class Game():


    def __init__(self):
        self.matrix = [' ',' ',' ',' ',' ',' ',' ',' ',' ']
        self.player = 'x'

    def validate_move(self, square):
        try:
            return self.matrix[square] == ' '
        except: #mostly catching index errors
            print "validate move error:", square
            return False

    def make_move(self, square, player):
        self.matrix[square] = player

    def legal_moves(self):
        return [m for m in range(9) if self.matrix[m] == ' ']

    def winner_if_any(self):
        WINCOMBOS = [[0,1,2], [3,4,5], [6,7,8],
                     [0,3,6], [1,4,7], [2,5,8],
                     [0,4,8], [2,4,6]]
        
        for line in WINCOMBOS:
            a, b, c = line
            s = set([self.matrix[a], self.matrix[b], self.matrix[c]])
            if len(s) == 1 and ' ' not in s:
                winner = s.pop()
                return winner

    def end_message(self):
        winner = self.winner_if_any()
        message = {'x': "You win!", 'o': "You lose!", None: "Tie game."}
        return "Game over. "+message[winner]+'\n'+self.board_as_string()

    def start_message(self):
        return "Let's play tic tac toe!"

    def utility(self):  # utility is from player o's perspective (1 if o wins, -1 if o loses)
        util = {'o': 1, 'x': -1, None: 0}
        return util[self.winner_if_any()]

    def is_over(self):
        empty_squares = sum(self.matrix[sq]== ' ' for sq in range(9))
        return self.winner_if_any() or not empty_squares

    def minimax(self, player='o', func=max):
        child_player = 'x' if player == 'o' else 'o'
        child_func = min if func == max else max

        if self.is_over():
            return self.utility(), None
        else:
            children = []
            for m in self.legal_moves():
                self.matrix[m] = player
                util, _ = self.minimax(child_player, child_func)
                children.append((util, m))
                self.matrix[m] = ' '
        return func(children, key=lambda x: x[0]) 

    def board_as_string(self):
        b = self.matrix
        out = "".join(
                [b[0], " | ", b[1], " | ", b[2], "\n",
                " -  -  - \n",
                b[3], " | ", b[4], " | ", b[5], "\n",
                " -  -  - \n",
                b[6], " | ", b[7], " | ", b[8], "\n"])
        return out

if __name__ == '__main__':
    pdb.set_trace()
