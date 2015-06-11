#By Jason Lustbader jal584 and Juliusz Choinski

#!/usr/bin/env python
import struct, string, math
from copy import deepcopy


class SudokuBoard:
    """This will be the sudoku board game object your player will manipulate."""

    def __init__(self, size, board):
        """the constructor for the SudokuBoard"""
        self.BoardSize = size  # the size of the board
        self.CurrentGameBoard = board  # the current state of the game board

    def set_value(self, row, col, value):
        """This function will create a new sudoku board object with the input
        value placed on the GameBoard row and col are both zero-indexed"""

        # add the value to the appropriate position on the board
        self.CurrentGameBoard[row][col] = value
        #return a new board of the same size with the value added
        return SudokuBoard(self.BoardSize, self.CurrentGameBoard)


    def print_board(self):
        """Prints the current game board. Leaves unassigned spots blank."""
        div = int(math.sqrt(self.BoardSize))
        dash = ""
        space = ""
        line = "+"
        sep = "|"
        for i in range(div):
            dash += "----"
            space += "    "
        for i in range(div):
            line += dash + "+"
            sep += space + "|"
        for i in range(-1, self.BoardSize):
            if i != -1:
                print "|",
                for j in range(self.BoardSize):
                    if self.CurrentGameBoard[i][j] > 9:
                        print self.CurrentGameBoard[i][j],
                    elif self.CurrentGameBoard[i][j] > 0:
                        print "", self.CurrentGameBoard[i][j],
                    else:
                        print "  ",
                    if (j + 1 != self.BoardSize):
                        if ((j + 1) // div != j / div):
                            print "|",
                        else:
                            print "",
                    else:
                        print "|"
            if ((i + 1) // div != i / div):
                print line
            else:
                print sep


def parse_file(filename):
    """Parses a sudoku text file into a BoardSize, and a 2d array which holds
    the value of each cell. Array elements holding a 0 are considered to be
    empty."""

    f = open(filename, 'r')
    BoardSize = int(f.readline())
    NumVals = int(f.readline())

    # initialize a blank board
    board = [[0 for i in range(BoardSize)] for j in range(BoardSize)]

    #populate the board with initial values
    for i in range(NumVals):
        line = f.readline()
        chars = line.split()
        row = int(chars[0])
        col = int(chars[1])
        val = int(chars[2])
        board[row - 1][col - 1] = val

    return board


def is_complete(sudoku_board):
    """Takes in a sudoku board and tests to see if it has been filled in
    correctly."""
    BoardArray = sudoku_board.CurrentGameBoard
    size = len(BoardArray)
    subsquare = int(math.sqrt(size))

    # check each cell on the board for a 0, or if the value of the cell
    #is present elsewhere within the same row, column, or square
    for row in range(size):
        for col in range(size):
            if BoardArray[row][col] == 0:
                return False
            for i in range(size):
                if ((BoardArray[row][i] == BoardArray[row][col]) and i != col):
                    return False
                if ((BoardArray[i][col] == BoardArray[row][col]) and i != row):
                    return False
            #determine which square the cell is in
            SquareRow = row // subsquare
            SquareCol = col // subsquare
            for i in range(subsquare):
                for j in range(subsquare):
                    if ((BoardArray[SquareRow * subsquare + i][SquareCol * subsquare + j]
                             == BoardArray[row][col])
                        and (SquareRow * subsquare + i != row)
                        and (SquareCol * subsquare + j != col)):
                        return False
    return True


def init_board(file_name):
    """Creates a SudokuBoard object initialized with values from a text file"""
    board = parse_file(file_name)
    return SudokuBoard(len(board), board)


def solve(initial_board, forward_checking=False, MRV=False, MCV=False,
          LCV=False):
    """Takes an initial SudokuBoard and solves it using back tracking, and zero
    or more of the heuristics and constraint propagation methods (determined by
    arguments). Returns the resulting board solution. """

    curr = deepcopy(initial_board)
    BoardArray = initial_board.CurrentGameBoard
    size = len(BoardArray)

    if is_complete(curr):
        curr.print_board()
        return True

    if MRV == True: coords = find_MRV(initial_board)
    elif MCV == True: coords = find_MCV(initial_board)
    elif LCV == True: coords = find_LCV(initial_board)
    else: coords = find_empty(initial_board)

    #forward checking
    if forward_checking == True:
        return

    #backtracking
    for i in range(1, size + 1):
        if validMove(curr, coords[0], coords[1], i):
            curr.set_value(coords[0], coords[1], i)

            if solve(curr, forward_checking, MRV, MCV, LCV):
                return True

            curr.set_value(coords[0], coords[1], 0)

    return False


def find_empty(sudoku_board):
    """returns coordinates of first open empty square in sudoku board, a default method
    """
    BoardArray = sudoku_board.CurrentGameBoard
    size = len(BoardArray)

    for i in range(size):
        for j in range(size):
            if BoardArray[i][j] == 0: return [i, j]

    return False

def find_MRV(sudoku_board):
    """returns the coordinates of the blank square in the grid that has
    the fewest remaining possible values, and returns false if there are no moves left"""
    BoardArray = sudoku_board.CurrentGameBoard
    size = len(BoardArray)
    coords = [0, 0]  # coordinates of the MRV, default to 0, 0
    minvalues = size + 1  # the minimum number of values, default to first open square

    for row in range(size):
        for col in range(size):
            if BoardArray[row][col] == 0:
                moves = []  # possible moves
                for num in range(1, size + 1):  # checks the numbers
                    if validMove(sudoku_board, row, col, num): moves.append(num)
                if len(moves) == 1:  #
                    return [row, col]
                elif len(moves) < minvalues:
                    minvalues = len(moves)
                    coords = [row, col]

    if minvalues == size + 1: return False

    return coords


def find_MCV(sudoku_board):
    """returns the coordinates of the blank square in the grid that is
    involved in the largest number of constraints with unassigned variables"""
    BoardArray = sudoku_board.CurrentGameBoard
    size = len(BoardArray)
    subsquare = int(math.sqrt(size))
    coords = [0, 0]  # coordinates of the MRV, default to 0, 0
    hi_constraints = 0  # the max number of constraints, default to first open square

    for row in range(size):
        for col in range(size):
            if BoardArray[row][col] == 0:
                constraints = 0
                for i in range(size):  # first check row + column constraints
                    if BoardArray[row][i] == 0: constraints += 1
                    if BoardArray[i][col] == 0: constraints += 1
                SquareRow = row // subsquare
                SquareCol = col // subsquare
                for i in range(subsquare):  # lastly check subsquare constraints
                    for j in range(subsquare):
                        if ((BoardArray[SquareRow * subsquare + i][SquareCol * subsquare + j]
                                 == 0)
                            and (SquareRow * subsquare + i != row)
                            and (SquareCol * subsquare + j != col)): constraints += 1

                if constraints > hi_constraints:
                    hi_constraints = constraints
                    coords = [row, col]

    if hi_constraints == 0: return False

    return coords

def find_LCV:
    """
    returns the coordinates of the blank square in the grid that is
    involved in the fewest number of constraints with unassigned variables
    """
    BoardArray = sudoku_board.CurrentGameBoard
    size = len(BoardArray)
    subsquare = int(math.sqrt(size))
    coords = [0, 0]  # coordinates of the MRV, default to 0, 0
    low_constraints = size*size  # the max number of constraints, default to first open square

    for row in range(size):
        for col in range(size):
            if BoardArray[row][col] == 0:
                constraints = 0
                for i in range(size):  # first check row + column constraints
                    if BoardArray[row][i] == 0: constraints += 1
                    if BoardArray[i][col] == 0: constraints += 1
                SquareRow = row // subsquare
                SquareCol = col // subsquare
                for i in range(subsquare):  # lastly check subsquare constraints
                    for j in range(subsquare):
                        if ((BoardArray[SquareRow * subsquare + i][SquareCol * subsquare + j]
                                 == 0)
                            and (SquareRow * subsquare + i != row)
                            and (SquareCol * subsquare + j != col)): constraints += 1

                if constraints < low_constraints:
                    low_constraints = constraints
                    coords = [row, col]

    if low_constraints == size*size: return False

    return coords

def validMove(sudoku_board, row, col, val):
    """returns true if inserting val at row, col is valid,
    and false otherwise"""
    BoardArray = sudoku_board.CurrentGameBoard
    size = len(BoardArray)
    subsquare = int(math.sqrt(size))

    # 1st check row
    for c in range(size):
        if BoardArray[row][c] == val: return False

    #Next check col
    for r in range(size):
        if BoardArray[r][col] == val: return False

    #Lastly check subsquare
    SquareRow = row // subsquare
    SquareCol = col // subsquare
    for i in range(subsquare):
        for j in range(subsquare):
            if BoardArray[SquareRow * subsquare + i][SquareCol * subsquare + j] == val: return False

    #if passes, return true
    return True


sb = init_board("input_puzzles/easy/9_9.sudoku")
sb.print_board()
solve(sb)


