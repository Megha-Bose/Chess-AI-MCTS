import numpy as np

'''
Each board state is a 8x8 array
Example: s1
First char: w: white, b: black, e: empty
Second char: k: king, q: queen, b: bishop, n: knight, r: rook, p: pawn
'''

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

    def __init__(self, state, parent=None, parent_action=None):
        '''
        Initialise a board state
        '''
        self.state = state
        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self._num_visits = 0
        self._num_wins = 0
        self._num_losses = 0
        self._available_actions = self.get_available_actions()

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
                return curr.expand() # expandable node
        return curr # terminal node

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
        weights = [(child.get_q() / child.get_n()) + c_param * np.sqrt((2 * np.log(self.get_n()) / child.get_n())) for child in self.children]
        best_c = np.argmax(weights)
        return self.children[best_c]

    def is_game_over(self):
        '''
        Returns true if game is over else false
        '''
        res = True
        return res

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
        iterations = 100
        for i in range(iterations):
            node = self.select()
            q_val = node.simulate()
            node.backpropagate(q_val)
        return self.best_child(c_param=0.0)


if __name__ == "__main__":
    '''
    gameplay
    '''
    current_state = s1
    root = MctsNode(state = current_state)
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
