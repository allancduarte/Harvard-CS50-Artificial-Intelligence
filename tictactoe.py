"""
Tic Tac Toe Player
"""
import copy
import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    if board == initial_state():
        return X

    Xs = 0
    Os = 0

    for row in board:
        Xs += row.count(X)
        Os += row.count(O)

    if Xs <= Os:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_moves = set()
    for i in range(len(board)):
        for j in range(3):
            if board[i][j] == EMPTY:
                possible_moves.add((i, j))

    return possible_moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action not in actions(board):
        raise Exception("Not a valid action")

    new_board = copy.deepcopy(board)

    new_board[action[0]][action[1]] = player(board)

    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i in range(len(board)):
        if board[i][0] == board[i][1] == board[i][2]:
            if board[i][0] == X:
                return X
            elif board[i][0] == O:
                return O

    for i in range(3):
        if board[0][i] == board[1][i] == board[2][i]:
            if board[0][i] == X:
                return X
            elif board[0][i] == O:
                return O

    if board[0][0] == board[1][1] == board[2][2] or board[0][2] == board[1][1] == board[2][0]:
        if board[1][1] == X:
            return X
        elif board[1][1] == O:
            return O

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) == X or winner(board) == O:
        return True
    else:
        for row in board:
            for item in row:
                if item == EMPTY:
                    return False
        return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def min_value(board):
    if terminal(board):
        return utility(board)
    v = math.inf
    for action in actions(board):
        value = max_value(result(board, action))
        if value < v:
            v = value
    return v


def max_value(board):
    if terminal(board):
        return utility(board)
    v = -math.inf
    for action in actions(board):
        value = min_value(result(board, action))
        if value > v:
            v = value
    return v


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    opt_act = None

    if terminal(board):
        return None

    if player(board) == X:
        inf = -math.inf
        for action in actions(board):
            value = min_value(result(board, action))
            if value > inf:
                inf = value
                opt_act = action

    elif player(board) == O:
        inf = math.inf
        for action in actions(board):
            value = max_value(result(board, action))
            if value < inf:
                inf = value
                opt_act = action
    return opt_act