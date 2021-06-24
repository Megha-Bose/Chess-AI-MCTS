import numpy as np
from game import (Game, N, M, pieces)

root = None
chess_game = Game()

# MCTS class

class MctsNode():
    def __init__(self, state, parent=None, parent_action=None, turn=None):
        '''
        Initialise a board state
        '''

        self.state = state
        self.parent = parent

        '''
        white or black turn
        '''

        if parent == None:
            self.turn = 'b'
        else:
            self.turn = 'w' if parent.turn == 'b' else 'b'

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
            possible_moves = curr.get_available_actions()
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
        global chess_game
        '''
        Returns true if game is over else false
        check if either kings is in checkmate position
        '''
        result = chess_game.is_checkmate(self.state, opponent=False) or chess_game.is_checkmate(self.state, opponent=True)
        return result

    def get_available_actions(self):
        global chess_game
        '''
        Returns list of all possible actions from current board state
        '''
        for i in range(N):
            for j in range(N):
                # considering the pieces whose turn is valid
                if self.state[i][j][0] == self.turn:
                    actions_list = chess_game.possible_moves(state=self.state, i=i, j=j)
        print(actions_list)
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

    def get_best_move(self, num_iter):
        global chess_game
        '''
        Play the best move from current state
        '''
        for i in range(num_iter):
            node = self.select()
            result = node.simulate()
            node.backpropagate(result)
        return self.best_child(c_param=0.0)


def run_mcts(root_state, num_iter):
    '''
    gameplay
    '''
    global root
    root = MctsNode(state=root_state)
    return root.get_best_move(num_iter)
