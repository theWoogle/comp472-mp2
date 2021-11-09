# based on code from https://stackabuse.com/minimax-and-alpha-beta-pruning-in-python

import time
import string

# Helper functions
def letter2index(letter: str):
	"""Convert capital letter to index (0-25)"""  
	return int(ord(letter) - 65)  # ordinal of A=65, a=97


index2letter = lambda a : chr(65+a)
"""Convert index (0-25) to capital letter"""  

INTMAX = 100000 # not true but high

class Game:
    MINIMAX = 0
    ALPHABETA = 1
    HUMAN = 2
    AI = 3
    E1 = 4
    E2 = 5


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
        self.a  = self.ALPHABETA
        self.pO = self.AI
        # self.pX = self.HUMAN
        self.pX = self.AI
        self.eX = self.E1
        self.eO = self.E2

        self.average_rec_depth = 0
        self.round_count = 0
        self.total_time = 0

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
        self.evaluated_states = {}
        self.evaluated_states_prior = {}
        
        for i, b in enumerate(self.b_pos):
            print('Enter the coordinate for the block ',i)
            px = int(input('enter the x coordinate: '))
            py = int(input('enter the y coordinate: '))
            self.b_pos[i] = (px,py) #can assume that input is valid
            self.current_state[px][py] = '#'

        # Player X always plays first
        self.player_turn = 'X'
        self.filegametrace = open(F"gameTrace-{self.n}{self.b}{self.s}{self.t}.txt", "a")
        self.numMoves=0
        self.using_e1=False


    def output1_4(self):
        self.filegametrace.write("n="+str(self.n)+" b="+str(self.b)+" s="+str(self.s)+" t="+str(self.t))

        self.filegametrace.write("\nblocs="+str(self.b_pos))
        self.drawboard_onfile()

        self.filegametrace.write("\n\nPlayer 1: ")
        self.filegametrace.write("HUMAN" if self.pX == self.HUMAN else "AI")
        self.filegametrace.write(F" d={self.dX} a=" + "False" if self.a == self.MINIMAX else (F" d={self.dX} a=" +"True"))
        self.filegametrace.write(" e1(regular)" if self.eX == self.E1 else " e2(defensive)\n")#TO DO
        self.filegametrace.write("\nPlayer 2: ")
        self.filegametrace.write("HUMAN" if self.pO == self.HUMAN else "AI")
        self.filegametrace.write(F" d={self.dO} a=" + "False" if self.a == self.MINIMAX else (F" d={self.dX} a=" +"True"))
        self.filegametrace.write(" e1(regular)" if self.eO == self.E1 else " e2(defensive)\n")#TO DO

    def output_5(self,x,y,eval_time):
        self.filegametrace.write("\nPlayer " + self.player_turn +  " plays " + index2letter(x) + str(y) + "\n")
        self.drawboard_onfile()
        self.filegametrace.write("Evaluation time: %.7fs \n" %eval_time)
        self.total_time += eval_time

        visited_states = dict(self.evaluated_states)

        for key in self.evaluated_states_prior:
            visited_states[key] = (self.evaluated_states[key]-self.evaluated_states_prior[key])
        visited_states = {x:y for x,y in visited_states.items() if y!=0} # remove 0s

        states_per_round = sum(visited_states[i] for i in visited_states)
        self.filegametrace.write("Visited states: %i \n" %(states_per_round))
        
        self.filegametrace.write("States evaluated per depth: %s \n"%visited_states)

        avg_depth = 0
        if states_per_round != 0:
            for key in visited_states:
                avg_depth += visited_states[key] * key
            avg_depth = avg_depth/states_per_round

        self.filegametrace.write("\nAverage depth: %.3f\n " %avg_depth)
        # TODO: average recursion depth
        self.evaluated_states_prior = dict(self.evaluated_states)


    def drawboard_onfile(self):
        self.filegametrace.write("\n  ")
        for i in range(0, self.n):
            self.filegametrace.write(string.ascii_uppercase[i])
        self.filegametrace.write("\n +")
        for i in range(0, self.n):
            self.filegametrace.write("-")
        self.filegametrace.write("\n")
        for y in range(0, self.n):
            self.filegametrace.write(str(y))
            self.filegametrace.write("|")
            for x in range(0, self.n):
                self.filegametrace.write(self.current_state[x][y])
            self.filegametrace.write("\n")
        self.filegametrace.write("\n")

    def output_6(self):
        avg_eval_time = self.total_time/self.round_count
        self.filegametrace.write(F'6(b)i   Average evaluation time: {avg_eval_time} \n')
        self.filegametrace.write(F'6(b)ii  Total heuristic evaluations: {sum(self.evaluated_states.values())} \n')
        self.filegametrace.write(F'6(b)iii Evaluations by depth: {self.evaluated_states} \n')
        avg_depth = 0
        for key in self.evaluated_states:
            avg_depth += self.evaluated_states[key] * key
        avg_depth = avg_depth/sum(self.evaluated_states.values())

        self.filegametrace.write(F'6(b)iv  Average evaluation depth: {avg_depth}\n')
        # self.filegametrace.write(F'6(b)v   Average recursion depth:\n')
        self.filegametrace.write(F'6(b)vi  Total moves: {self.round_count}')
        return avg_eval_time, sum(self.evaluated_states.values()), self.evaluated_states, avg_depth, self.round_count

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
                self.filegametrace.write('The winner is X!\n\n')
                self.output_6()
            elif self.result == 'O':
                print('The winner is O!')
                self.filegametrace.write('The winner is O!\n\n')
                self.output_6()
            elif self.result == '.':
                print("It's a tie!")
                self.filegametrace.write("It's a tie!\n\n")
                self.output_6()
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


    #Assigns a positive value to every n-in-a-row the player has
    #A negative value to every n-in-a-row the opponent has
    #An n-in-a-row is worth about an order of magnitude more than an (n-1)-in-a-row
    #The opponent’s rows are worth slightly more than the player’s rows
    #This encourage the player to block before building its own rows.

    def e2(self):
        # o_win = 0
        # x_win = 0
        points=0
        for i in range(0, self.n):
            for j in range(0, self.n):
                ## get line of length s for current tile
                # horizontal right
                hor = [self.current_state[i][x] for x in range(j, j + self.s) if (self.s + j) <= self.n]
                # vertical down
                vert = [self.current_state[y][j] for y in range(i, i + self.s) if (self.s + i) <= self.n]
                # diagonal right down
                diagr = [self.current_state[i + d][j + d] for d in range(0, self.s) if
                         ((i + self.s) <= self.n and (j + self.s) <= self.n)]
                # diagonal left down
                diagl = [self.current_state[i + d][j - d] for d in range(0, self.s) if
                         ((i + self.s) <= self.n and (j - self.s) >= -1)]
                lines = [hor, vert, diagr, diagl]
                for line in lines:
                    if self.player_turn == 'X':
                        points += 1*pow(10,line.count('X'))
                    if self.player_turn == 'O':
                        points -= int(1.5*pow(10,line.count('O')))
        return(points)


    def minimax(self, depth=0, max=False):
        # Minimizing for 'X' and maximizing for 'O'
        # We're initially setting it to INTMAX or -INTMAX as worse than the worst case:
        value = INTMAX+1
        if max:
            value = -INTMAX-1
        x = None
        y = None

        self.visited_states += 1
        result = self.is_end()
        if result == 'X':
            return (-INTMAX, x, y)
        elif result == 'O':
            return (INTMAX, x, y)
        elif result == '.':
            return (0, x, y)
        if depth >= (self.dX if self.player_turn == 'X' else self.dO):
            if depth + self.round_count - 1 in self.evaluated_states:
                self.evaluated_states[depth + self.round_count - 1] += 1
            else:
                self.evaluated_states[depth + self.round_count - 1] = 1
            if self.player_turn == 'X' and self.eX == self.E1 or self.player_turn == 'O' and self.eO == self.E1:
                return(self.e1(), x, y)
            elif self.player_turn == 'X' and self.eX == self.E2 or self.player_turn == 'O' and self.eO == self.E2:
                return(self.e2(), x, y)

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

    def alphabeta(self, depth = 0, alpha=-INTMAX, beta=INTMAX, max=False):
        # Minimizing for 'X' and maximizing for 'O'
        value = INTMAX
        if max:
            value = -INTMAX
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
            if depth + self.round_count - 1 in self.evaluated_states:
                self.evaluated_states[depth + self.round_count - 1] += 1
            else:
                self.evaluated_states[depth + self.round_count - 1] = 1
            if self.player_turn == 'X' and self.eX == self.E1 or self.player_turn == 'O' and self.eO == self.E1:
                return(self.e1(), x, y)
            elif self.player_turn == 'X' and self.eX == self.E2 or self.player_turn == 'O' and self.eO == self.E2:
                return(self.e2(), x, y)

        for i in range(0, self.n):
            for j in range(0, self.n):
                if self.current_state[i][j] == '.':
                    if max:
                        self.current_state[i][j] = 'O'
                        (v, _, _) = self.alphabeta(depth + 1, alpha, beta, max=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        (v, _, _) = self.alphabeta(depth + 1, alpha, beta, max=True)
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
        self.output1_4()
        while True:
            self.draw_board()
            if self.check_end():
                return
            self.round_count += 1
            start = time.time()
            values = [] 
            for a in range(0,self.n):
                for b in range(0,self.n):
                    if(self.current_state[a][b] == '.'):
                        self.current_state[a][b] = self.player_turn
                        values.append(self.e2())
                        self.current_state[a][b] = '.'
            print(*values)
            self.average_rec_depth = 0
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
            eval_time = round(end - start, 7)
            if (self.player_turn == 'X' and player_x == self.HUMAN) or (self.player_turn == 'O' and player_o == self.HUMAN):
                if self.recommend:
                    print(F'Evaluation time: {eval_time}s')
                    print(F'Recommended move: x = {x}, y = {y}')
                (x,y) = self.input_move()
            if (self.player_turn == 'X' and player_x == self.AI) or (self.player_turn == 'O' and player_o == self.AI):
                print(F'Evaluation time: {eval_time}s')
                if (eval_time>self.t):
                    self.check_end(wrong_move=True)
                # print(F'Player {self.player_turn} under AI control plays: x = {x}, y = {y}')
                print(F'Player {self.player_turn} under AI control plays: {string.ascii_uppercase[x]}{y}')
                # self.filegametrace.write(F'Player {self.player_turn} under AI control plays: {string.ascii_uppercase[x]}{y}\n\n')
                # self.filegametrace.write(F'i\tEvaluation time: {round(end - start, 7)}s\n')
                # self.filegametrace.write(F'ii\tHeuristic evaluations:\n')
                # self.filegametrace.write(F'iii\tEvaluations by depth:\n')
                # self.filegametrace.write(F'iv\tAverage evaluation depth:\n')
                # self.filegametrace.write(F'v\tAverage recursion depth:\n\n')
            self.current_state[x][y] = self.player_turn
            self.output_5(x,y,eval_time)
            self.switch_player()


def main():
    g = Game(recommend=True)
    print(index2letter(0))
    # g.play(algo=Game.ALPHABETA,player_x=Game.AI,player_o=Game.AI)
    g.play(algo=Game.ALPHABETA)

if __name__ == "__main__":
    main()
