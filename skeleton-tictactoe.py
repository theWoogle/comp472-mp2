# based on code from https://stackabuse.com/minimax-and-alpha-beta-pruning-in-python

import time

# Helper functions
def letter2index(letter: str):
	"""Convert capital letter to index (0-25)"""  
	return int(ord(letter) - 65)  # ordinal of A=65, a=97


class Game:
    MINIMAX = 0
    ALPHABETA = 1
    HUMAN = 2
    AI = 3


    def __init__(self, recommend = True):
        self.initialize_game()
        self.recommend = recommend

    def initialize_game(self):
        
        askInputs=False
        # Standard values for testing
        self.n = 5
        self.b = 0
        self.s = 3
        self.d1 = 3
        self.d2 = 3
        self.t  = 3
        self.a  = self.MINIMAX
        self.pO = self.AI
        self.pX = self.AI

        if(askInputs):
            self.n = int(input('Size of the board:'))
            self.b = int(input('Number of blocks (#):'))
            self.s = int(input('Winning Line-Up Size:'))
            self.d1 = int(input('Maximum depth of the adversarial search for player 1:'))
            self.d2 = int(input('Maximum depth of the adversarial search for player 2:'))
            self.t = int(input('Maximum allowed time to return move [s]:'))
            self.a = self.MINIMAX if bool(input('Use minimax (FALSE) or alphabeta (TRUE)?:')) else self.ALPHABETA
            self.pO = self.HUMAN if bool(input('Player 2 (O) is human (TRUE) or AI (FALSE)?:')) else self.AI
            self.pX = self.HUMAN if bool(input('Player 1 (X) is human (TRUE) or AI (FALSE)?:')) else self.AI
        
        self.current_state = [['.' for i in range(self.n)]for j in range(self.n)] # list of n lists with n points
        self.b_pos = [tuple()] * self.b
        
        for i, b in enumerate(self.b_pos):
            print('Enter the coordinate for the block ',i)
            px = int(input('enter the x coordinate: '))
            py = int(input('enter the y coordinate: '))
            self.b_pos[i] = (px,py) #can assume that input is valid
            self.current_state[px][py] = '#'

        # Player X always plays first
        self.player_turn = 'X'

    def draw_board(self):
        print()
        for y in range(0, self.n):
            for x in range(0, self.n):
                print(self.current_state[x][y], end="")
            print()
        print()

    def is_valid(self, px, py):
        if px < 0 or px > self.n or py < 0 or py > self.n: # updated for size n
            return False
        elif self.current_state[px][py] != '.':
            return False
        else:
            return True

    def is_end(self):
        # Vertical win
        for i in range(0, 3):
            if (self.current_state[0][i] != '.' and
             self.current_state[0][i] == self.current_state[1][i] and
             self.current_state[1][i] == self.current_state[2][i]):
                return self.current_state[0][i]
        # Horizontal win
        for i in range(0, 3):
            if (self.current_state[i] == ['X', 'X', 'X']):
                return 'X'
            elif (self.current_state[i] == ['O', 'O', 'O']):
                return 'O'
        # Main diagonal win
        if (self.current_state[0][0] != '.' and
         self.current_state[0][0] == self.current_state[1][1] and
         self.current_state[0][0] == self.current_state[2][2]):
            return self.current_state[0][0]
        # Second diagonal win
        if (self.current_state[0][2] != '.' and
         self.current_state[0][2] == self.current_state[1][1] and
         self.current_state[0][2] == self.current_state[2][0]):
            return self.current_state[0][2]
        # Is whole board full?
        for i in range(0, 3):
            for j in range(0, 3):
                # There's an empty field, we continue the game
                if (self.current_state[i][j] == '.'):
                    return None
        # It's a tie!
        return '.'

    def check_end(self, wrong_move = False):
        if wrong_move:
            # Opponent wins if AI inputs wrong move
            self.result = 'O' if self.player_turn == 'X' else 'O'
        else:
            self.result = self.is_end()
        # Printing the appropriate message if the game has ended
        if self.result != None:
            if self.result == 'X':
                print('The winner is X!')
            elif self.result == 'O':
                print('The winner is O!')
            elif self.result == '.':
                print("It's a tie!")
            self.initialize_game()
        return self.result

    def input_move(self):
        while True:
            coordinates = input('Player enter your move (e.g. A4):')
            px = letter2index(coordinates[0])
            py = int(coordinates[1])
            if self.is_valid(px, py):
                return (px,py)
            else:
                if ((self.player_turn == 'X' and self.pX ==self.AI) 
                    or (self.player_turn == 'O' and self.pO == self.AI)):
                    self.check_end(wrong_move = True)
                print('The move is not valid! Try again.')

    def switch_player(self):
        if self.player_turn == 'X':
            self.player_turn = 'O'
        elif self.player_turn == 'O':
            self.player_turn = 'X'
        return self.player_turn

    
    # easier/faster: considers lines (hor,ver,diag) of size s in general
    # with x_win: line is open for x to win = s adjacent Xs possible
    # similar for O
    def e1(self):
        o_win = 0
        x_win = 0
        for i in range(0,self.n-self.s):
            for j in range(0,self.n-self.s):
                ## get line of length s for current tile
                # horizontal right
                hor = [self.current_state[i][x] for x in range(j,j+self.s)]
                # vertical down
                vert = [self.current_state[y][j] for y in range(i,i+self.s)]
                # diagonal right down
                diag = [self.current_state[i+d][j+d] for d in range(0,self.s)]
                lines = [hor,vert,diag]
                for line in lines:
                    if any(tile == '#' for tile in line):
                        break
                    elif all(tile == '.' for tile in line):
                        o_win += 1
                        x_win += 1
                    elif not (any(tile == 'X' for tile in line)):
                        o_win += 1
                    elif not (any(tile == 'O' for tile in line)):
                        x_win += 1
        return (o_win - x_win)

        # # for every valid move
        # for i in range(0,self.n):
        #     for j in range(0,self.n):
        #         if (self.is_valid(i,j)):
        #             board_eval = self.current_state
        #             board_eval[i][j] = self.player_turn


    # winning path: empty path of size s around current tile
    # winning path empty: 1 point
    # wining path any symbol: 10 points
    # winning path equal amount of symbols: 0 points
    # winning path my>opponent and enough blanks to win: 50 points
    # winning path opponent s-1 symbols: 100 points
    # winning path s-1 own symbols: 200 points
    # return sum of points per path in current tile

    # or:
    # with x_s1 = nb of lines with (s-1)Xs and at least 1 blank
    # x_s2 = nb of lines with (s-2)Xs and  at least two blanks
    # ...
    # similar for O
    # def e2(self):

    def minimax(self, max=False):
        # Minimizing for 'X' and maximizing for 'O'
        # Possible values are:
        # -1 - win for 'X'
        # 0  - a tie
        # 1  - loss for 'X'
        # We're initially setting it to 2 or -2 as worse than the worst case:
        value = 2
        if max:
            value = -2
        x = None
        y = None
        result = self.is_end()
        if result == 'X':
            return (-1, x, y)
        elif result == 'O':
            return (1, x, y)
        elif result == '.':
            return (0, x, y)
        for i in range(0, 3):
            for j in range(0, 3):
                if self.current_state[i][j] == '.':
                    if max:
                        self.current_state[i][j] = 'O'
                        (v, _, _) = self.minimax(max=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        (v, _, _) = self.minimax(max=True)
                        if v < value:
                            value = v
                            x = i
                            y = j
                    self.current_state[i][j] = '.'
        return (value, x, y)

    def alphabeta(self, alpha=-2, beta=2, max=False):
        # Minimizing for 'X' and maximizing for 'O'
        # Possible values are:
        # -1 - win for 'X'
        # 0  - a tie
        # 1  - loss for 'X'
        # We're initially setting it to 2 or -2 as worse than the worst case:
        value = 2
        if max:
            value = -2
        x = None
        y = None
        result = self.is_end()
        if result == 'X':
            return (-1, x, y)
        elif result == 'O':
            return (1, x, y)
        elif result == '.':
            return (0, x, y)
        for i in range(0, 3):
            for j in range(0, 3):
                if self.current_state[i][j] == '.':
                    if max:
                        self.current_state[i][j] = 'O'
                        (v, _, _) = self.alphabeta(alpha, beta, max=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        (v, _, _) = self.alphabeta(alpha, beta, max=True)
                        if v < value:
                            value = v
                            x = i
                            y = j
                    self.current_state[i][j] = '.'
                    if max:
                        if value >= beta:
                            return (value, x, y)
                        if value > alpha:
                            alpha = value
                    else:
                        if value <= alpha:
                            return (value, x, y)
                        if value < beta:
                            beta = value
        return (value, x, y)

    def play(self,algo=None,player_x=None,player_o=None):
        if algo == None:
            algo = self.a
        if player_x == None:
            player_x = self.pX
        if player_o == None:
            player_o = self.pO
        while True:
            self.draw_board()
            if self.check_end():
                return
            start = time.time()
            if algo == self.MINIMAX:
                if self.player_turn == 'X':
                    (_, x, y) = self.minimax(max=False)
                else:
                    (_, x, y) = self.minimax(max=True)
            else: # algo == self.ALPHABETA
                if self.player_turn == 'X':
                    (m, x, y) = self.alphabeta(max=False)
                else:
                    (m, x, y) = self.alphabeta(max=True)
            end = time.time()
            if (self.player_turn == 'X' and player_x == self.HUMAN) or (self.player_turn == 'O' and player_o == self.HUMAN):
                if self.recommend:
                    print(F'Evaluation time: {round(end - start, 7)}s')
                    print(F'Recommended move: x = {x}, y = {y}')
                (x,y) = self.input_move()
            if (self.player_turn == 'X' and player_x == self.AI) or (self.player_turn == 'O' and player_o == self.AI):
                print(F'Evaluation time: {round(end - start, 7)}s')
                print(F'Player {self.player_turn} under AI control plays: x = {x}, y = {y}')
            self.current_state[x][y] = self.player_turn
            self.switch_player()

def main():
    g = Game(recommend=True)
    # g.play(algo=Game.ALPHABETA,player_x=Game.AI,player_o=Game.AI)
    g.play(algo=Game.MINIMAX)

if __name__ == "__main__":
    main()