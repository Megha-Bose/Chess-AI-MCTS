import numpy as np

'''
Each board state is a 8x8 array
Example: s1
First char: w: white, b: black, e: empty
Second char: k: king, q: queen, b: bishop, n: knight, r: rook, p: pawn
'''
# board dimension
N = 8
# no. of type of pieces
M = 6
pieces = ['k', 'q', 'r', 'b', 'n', 'p']
white_codes = ['\u2654', '\u2655', '\u2656', '\u2657', '\u2658', '\u2659']
black_codes = ['\u265A', '\u265B', '\u265C', '\u265D', '\u265E', '\u265F']
w = {pieces[i]: white_codes[i] for i in range(M)}
b = {pieces[i]: black_codes[i] for i in range(M)}


start_state = [
    [b['r'], b['n'], b['b'], b['q'], b['k'], b['b'], b['n'], b['r']],
    [b['p'], b['p'], b['p'], b['p'], b['p'], b['p'], b['p'], b['p']],
    ['    ', '    ', '    ', '    ', '    ', '    ', '    ', '    '],
    ['    ', '    ', '    ', '    ', '    ', '    ', '    ', '    '],
    ['    ', '    ', '    ', '    ', '    ', '    ', '    ', '    '],
    ['    ', '    ', '    ', '    ', '    ', '    ', '    ', '    '],
    [w['p'], w['p'], w['p'], w['p'], w['p'], w['p'], w['p'], w['p']],
    [w['r'], w['n'], w['b'], w['q'], w['k'], w['b'], w['n'], w['r']],
]

s1 = [
    ['bk', 'em', 'em', 'em', 'em', 'em', 'em', 'em'],
    ['em', 'bn', 'em', 'wr', 'em', 'wp', 'em', 'em'],
    ['br', 'em', 'bp', 'em', 'em', 'bn', 'wn', 'em'],
    ['em', 'em', 'bp', 'bp', 'bp', 'em', 'wp', 'bp'],
    ['bp', 'bp', 'em', 'bp', 'wn', 'em', 'wp', 'em'],
    ['em', 'em', 'em', 'em', 'em', 'em', 'em', 'em'],
    ['em', 'em', 'em', 'wk', 'em', 'em', 'em', 'em'],
    ['em', 'em', 'em', 'em', 'em', 'em', 'em', 'em'],
]

# MCTS class


class MctsNode():

    def __init__(self, color, iterations, state, parent=None, parent_action=None):
        '''
        Initialise a board state
        '''
        self.color = color
        self.opponent_color = 'black' if self.color == 'white' else 'white'
        self.iterations = iterations

        self.state = state
        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self._num_visits = 0
        self._num_wins = 0
        self._num_losses = 0
        self._available_actions = self.get_available_actions()

        # king and opponent king safety status for check and checkmate
        self.king_status = []
        self.opponent_king_status = []

    def get_q(self):
        '''
        Returns expected reward from a node,i.e., q value
        '''
        return self._num_wins - self._num_losses

    def get_n(self):
        '''
        Returns number of visits to a node till now
        '''
        return self._num_visits

    def expand(self):
        '''
        Returns new state expanded from current
        state after taking a possible action
        '''
        action = self._available_actions.pop()
        new_state = self.move(action)
        new_child_node = MctsNode(new_state, parent=self, parent_action=action)
        self.children.append(new_child_node)
        return new_child_node

    def select(self):
        '''
        Returns node to start simulation from
        '''
        curr = self
        while not curr.is_terminal():
            if self._available_actions and len(self._available_actions) == 0:
                curr = curr.best_child()
            else:
                return curr.expand()  # expandable node
        return curr  # terminal node

    def simulate(self):
        '''
        Game simulated from expanded node
        till an outcome is returned
        '''
        # we use rollout policy here
        curr = self
        while not curr.is_game_over():
            possible_moves = curr.get_actions()
            chosen_move = np.random.randint(len(possible_moves))
            curr = curr.move(possible_moves[chosen_move])
        return curr.get_result()

    def backpropagate(self, result):
        '''
        Once we have the result, the number of
        win/loss and number of visits is updated
        till the parent node is reached
        '''
        if result == 1:
            self._num_wins += 1
        elif result == -1:
            self._num_losses += 1
        self._num_visits += 1
        if self.parent != None:
            self.parent.backpropagate(result)

    def is_terminal(self):
        '''
        Returns true if the node is a terminal node
        '''
        return self.is_game_over()

    def best_child(self, c_param=0.1):
        '''
        Returns child with maximum value
        '''
        weights = [(child.get_q() / child.get_n()) + c_param * np.sqrt((2 *
                                                                        np.log(self.get_n()) / child.get_n())) for child in self.children]
        best_c = np.argmax(weights)
        return self.children[best_c]

    def orthogonal_safety(self, i1, j1, i2, j2):
        if i1 == i2:
            safe = False
            '''
            if i coords match, check j coords for intermediate empty cells
            '''
            max = j1 if j1 > j2 else j2
            min = j2 if max == j1 else j1
            for j_coord in range(min+1, max-1):
                if self.state[i1][j_coord] != 'em':
                    safe = True
                    break
            return safe
        elif j1 == j2:
            safe = False
            '''
            if j coords match, check i coords for intermediate empty cells
            '''
            max = i1 if i1 > i2 else i2
            min = i2 if max == i1 else i1
            for i_coord in range(min+1, max-1):
                if self.state[i_coord][j1] != 'em':
                    safe = True
                    break
            return safe
        else:
            return True

    def diagonal_safety(self, i1, j1, i2, j2):
        if i1 == i2 or j1 == j2:
            return True
        else:
            slope = abs((i1-i2)/(j1-j2))
            if slope == 1:
                safe = False
                ''' right orientation, check for intermediate empty cells
                '''
                step_i = 1 if i1 < i2 else -1
                step_j = 1 if j1 < j2 else -1

                for i_coord in range(i1, i2, step_i):
                    for j_coord in range(j1, j2, step_j):
                        if i_coord not in [i1, i2] and j_coord not in [j1, j2]:
                            if self.state[i_coord][j_coord] != 'em':
                                safe = True
                                break
                return safe
            else:
                return True

    def is_king_check(self, king_i, king_j, opponent=False):
        '''
        if opponent=True, opponent king check is computed
        else computer's king
        '''
        king_color = self.color[0] if opponent == False else self.opponent_color[0]
        opponent_color = 'w' if king_color == 'b' else 'b'
        for i in range(N):
            for j in range(N):
                '''
                check each opponent piece's position w.r.t to computer's king
                or vice versa, depending on opponent value passed
                '''
                if self.state[i][j][0] == opponent_color:
                    piece_type = self[i][j][1]
                    ''' condition for kings to be adjacent
                    '''
                    if piece_type == 'k':
                        if abs(king_i-i) == 1 and abs(king_j-j) == 1:
                            return True

                    elif piece_type == 'q':
                        '''
                        queen search - orthogonal and diagonal
                        '''
                        if self.orthogonal_safety(king_i, king_j, i, j) == False:
                            return True
                        if self.diagonal_safety(king_i, king_j, i, j) == False:
                            return True

                    elif piece_type == 'r':
                        '''
                        rook search - orthogonal
                        '''
                        if self.orthogonal_safety(king_i, king_j, i, j) == False:
                            return True

                    elif piece_type == 'b':
                        '''
                        bishop search - diagonal
                        '''
                        if self.diagonal_safety(king_i, king_j, i, j) == False:
                            return True

                    elif piece_type == 'n':
                        '''
                        knight search - L-shaped hop
                        '''
                        if abs(king_i - i) == 2 and abs(king_j - j) == 1:
                            return True
                        elif abs(king_i - i) == 1 and abs(king_j - j) == 2:
                            return True

                    elif piece_type == 'p':
                        '''
                        pawn search - 1-step diagonal in forward direction
                        i value condition depends on color
                        '''
                        if king_color == 'w':
                            if (king_i - i) == 1 and abs(king_j - j) == 1:
                                return True
                        else:
                            if (king_i - i) == -1 and abs(king_j - j) == 1:
                                return True

    def is_checkmate(self, opponent=False):
        res = False
        '''finding king's position - king_i, king_j'''

        ''' king color depends on opponent value passed'''
        king = self.color[0] + \
            'k' if opponent == False else self.opponent_color[0]+'k'
        for king_i in range(N):
            if king in self.state[king_i]:
                king_j = self.state[king_i].index(king)

        if self.is_king_check(king_i, king_j, opponent):
            res = True
            '''
            check for king blocking/dodging check
            (yet to implement blocking check through intercept & capture)
            '''

            '''
            check for all adjacent squares
            with x and y generating index range
            '''
            x = [king_i-1, king_j-1]
            y = [king_i+1, king_j+1]

            Range = [i for i in range(N)]

            for i_coord in x:
                for j_coord in y:
                    if x in Range and y in Range:
                        if self.state[x][y] != 'em':
                            if self.is_king_check(x, y, opponent) == False:
                                res = False
                                break
        return res

    def is_game_over(self):
        '''
        Returns true if game is over else false
        check if either kings is in checkmate position
        '''
        result = self.is_checkmate(
            opponent=False) or self.is_checkmate(opponent=True)
        return result

    def get_available_actions(self):
        '''
        Returns list of all possible actions from current board state
        '''
        actions_list = None
        return actions_list

    def move(self, action):
        '''
        Returns board state after action
        '''
        next_state = None
        return next_state

    def get_result(self):
        '''
        Returns result of the game
        1 for win, -1 for loss, and 0 for tie
        '''
        res = 1
        return res

    def get_best_move(self):
        '''
        Play the best move from current state
        '''
        for i in range(self.iterations):
            node = self.select()
            q_val = node.simulate()
            node.backpropagate(q_val)
        return self.best_child(c_param=0.0)


if __name__ == "__main__":
    '''
    gameplay
    '''
    current_state = s1
    root = MctsNode(color='white', iterations=100, state=current_state)
    selected_node = root.get_best_move()


# To convert board state to FEN
# import io

# def board_to_fen(board):
#     with io.StringIO() as s:
#         for row in board:
#             empty = 0
#             for cell in row:
#                 c = cell[0]
#                 if c in ('w', 'b'):
#                     if empty > 0:
#                         s.write(str(empty))
#                         empty = 0
#                     s.write(cell[1].upper() if c == 'w' else cell[1].lower())
#                 else:
#                     empty += 1
#             if empty > 0:
#                 s.write(str(empty))
#             s.write('/')
#         # Moving one position back to overwrite '/'
#         s.seek(s.tell() - 1)
#         s.write(' w KQkq - 0 1')
#         return s.getvalue()
