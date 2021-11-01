# based on code from https://stackabuse.com/minimax-and-alpha-beta-pruning-in-python

import time
import string

# Helper functions
def letter2index(letter: str):
	"""Convert capital letter to index (0-25)"""  
	return int(ord(letter) - 65)  # ordinal of A=65, a=97

INTMAX = 100000 # not true but high

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
        self.n = 4
        self.b = 0
        self.s = 4
        self.dX = 4
        self.dO = 4
        self.t  = 3
        self.a  = self.MINIMAX
        self.pO = self.AI
        self.pX = self.HUMAN

        if(askInputs):
            self.n = int(input('Size of the board:'))
            self.b = int(input('Number of blocks (#):'))
            self.s = int(input('Winning Line-Up Size:'))
            self.dX = int(input('Maximum depth of the adversarial search for player 1:'))
            self.dO = int(input('Maximum depth of the adversarial search for player 2:'))
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

    def gameTrace(self):
        file1 = open("gameTrace-"+str(self.n)+str(self.b)+str(self.s)+str(self.t)+".txt", "a")

        file1.write("n="+str(self.n)+" b="+str(self.b)+" s="+str(self.s)+" t="+str(self.t))

        file1.write("\n\nblocs="+str(self.b_pos))

        file1.write("\n\nPlayer 1: ")
        file1.write("HUMAN" if self.pX == self.HUMAN else ("AI d="+str(self.d1)))
        file1.write(" a="+ "False" if self.a == self.MINIMAX else ("True"))
        file1.write(" (e1 or e2)\n")#TO DO
        file1.write("\n\nPlayer 2: ")
        file1.write("HUMAN" if self.pX == self.HUMAN else ("AI d=" + str(self.d1)))
        file1.write(" a=" + "False" if self.a == self.MINIMAX else ("True"))
        file1.write(" (e1 or e2)\n")  # TO DO

        #Print the Initial table
        file1.write("\n  ")
        for i in range(0,self.n):
            file1.write(string.ascii_uppercase[i])
        file1.write("\n +")
        for i in range(0,self.n):
            file1.write("-")
        file1.write("\n")
        for y in range(0, self.n):
            file1.write(str(y))
            file1.write("|")
            for x in range(0, self.n):
                file1.write(self.current_state[x][y])
            file1.write("\n")
        file1.write("\n")


    def draw_board(self):
        print()
        print("  ",end="")
        for i in range(0, self.n):
            print(string.ascii_uppercase[i], end="")
        print("\n +", end="")
        for i in range(0, self.n):
            print("-", end="")
        print()
        for y in range(0, self.n):
            print(str(y)+"|", end="")
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

    def is_end(self): #cmust get updated
        tie = True
        for i in range(0,self.n):
            for j in range(0,self.n):
                ## get line of length s for current tile
                # horizontal right
                if self.current_state[i][j] == '.' : # empty tile exists --> can't be tie
                    tie = False 
                    break
                if self.current_state[i][j] == '#' :
                    break
                hor = [self.current_state[i][x] for x in range(j,j+self.s) if (self.s+j)<=self.n]
                # vertical down
                vert = [self.current_state[y][j] for y in range(i,i+self.s) if (self.s+i)<=self.n]
                # diagonal right down
                diagr = [self.current_state[i+d][j+d] for d in range(0,self.s) if ((i+self.s) <= self.n and (j+self.s) <= self.n)]
                # diagonal left down
                diagl = [self.current_state[i+d][j-d] for d in range(0,self.s) if ((i+self.s) <= self.n and (j-self.s) >= -1)]
                lines = [hor, vert, diagr, diagl]
                for line in lines:
                    if len(line) == self.s:
                        if all(elem == 'X' for elem in line) or all(elem == 'O' for elem in line):
                            return line[0]

        return ('.' if tie else None)

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
        """ 
        Returns simple e1 for the current state of the board
        """

        o_win = 0
        x_win = 0
        for i in range(0,self.n):
            for j in range(0,self.n):
                ## get line of length s for current tile
                # horizontal right
                hor = [self.current_state[i][x] for x in range(j,j+self.s) if (self.s+j)<=self.n]
                # vertical down
                vert = [self.current_state[y][j] for y in range(i,i+self.s) if (self.s+i)<=self.n]
                # diagonal right down
                diagr = [self.current_state[i+d][j+d] for d in range(0,self.s) if ((i+self.s) <= self.n and (j+self.s) <= self.n)]
                # diagonal left down
                diagl = [self.current_state[i+d][j-d] for d in range(0,self.s) if ((i+self.s) <= self.n and (j-self.s) >= -1)]
                lines = [hor,vert,diagr, diagl]
                for line in lines:
                    if any(tile == '#' for tile in line):
                        break
                    elif not(all(tile == '.' for tile in line)): # no need to give both 1 point
                        if not (any(tile == 'X' for tile in line)):
                            o_win += 1
                        if not (any(tile == 'O' for tile in line)):
                            x_win += 1
        return (o_win - x_win)

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

    def minimax(self, depth=0, max=False):
        # Minimizing for 'X' and maximizing for 'O'
        # Possible values are:
        # -INTMAX - win for 'X'
        # 0  - a tie
        # INTMAX  - loss for 'X'
        # We're initially setting it to 2 or -2 as worse than the worst case:
        value = INTMAX+1
        if max:
            value = -INTMAX-1
        x = None
        y = None

        result = self.is_end()
        if result == 'X':
            return (-INTMAX, x, y)
        elif result == 'O':
            return (INTMAX, x, y)
        elif result == '.':
            return (0, x, y)
        if depth >= (self.dX if self.player_turn == 'X' else self.dO):
            return (self.e1(), x, y)

        for i in range(0, self.n):
            for j in range(0, self.n):
                if self.current_state[i][j] == '.':
                    if max:
                        self.current_state[i][j] = 'O'
                        (v, _, _) = self.minimax(depth+1, max=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        (v, _, _) = self.minimax(depth+1, max=True)
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
        for i in range(0, self.n):
            for j in range(0, self.n):
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
            values = [] 
            for a in range(0,self.n):
                for b in range(0,self.n):
                    if(self.current_state[a][b] == '.'):
                        self.current_state[a][b] = self.player_turn
                        values.append(self.e1())
                        self.current_state[a][b] = '.'
            print(*values)
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
    g.gameTrace()
    g.play(algo=Game.MINIMAX)

if __name__ == "__main__":
    main()
