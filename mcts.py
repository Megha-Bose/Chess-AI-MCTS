import chess
import numpy as np

root = None

# MCTS class


class MctsNode():
    def __init__(self, state, parent=None, parent_action=None):
        '''
        Initialise a board state
        '''

        self.state = state
        self.board = chess.Board(state)
        self.parent = parent

        if self.parent and self.parent.board.turn == chess.BLACK:
            self.board.turn = chess.WHITE
        else:
            self.board.turn = chess.BLACK

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
            if len(curr._available_actions) == 0:
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
            new_board = curr.move(possible_moves[chosen_move])
            curr = MctsNode(state=new_board, parent=curr,
                            parent_action=chosen_move)
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
        # print(len(self.children))
        weights = [(child.get_q() / child.get_n()) + c_param * np.sqrt((2 *
                                                                        np.log(self.get_n()) / child.get_n())) for child in self.children]
        best_c = np.argmax(weights)
        return self.children[best_c]

    def is_game_over(self):
        result = (self.board.is_checkmate() or self.board.is_stalemate(
        ) or self.board.is_seventyfive_moves() or self.board.is_fivefold_repetition() or self.board.is_insufficient_material())
        return result

    def get_available_actions(self):
        actions_list = list(self.board.legal_moves)
        return actions_list

    def move(self, action):
        '''
        Returns board state after action
        '''
        next_state = self.board.copy()
        next_state.push(action)
        return next_state.fen()

    def get_result(self):
        '''
        Returns result of the game
        1 for win, -1 for loss, and 0 for tie
        '''
        '''
        hardcoded white to human, black to computer
        '''
        if self.board.outcome().winner == chess.WHITE:
            res = -1
        elif self.board.outcome().winner == chess.BLACK:
            res = 1
        elif self.board.outcome().winner == None:
            res = 0
        return res

    def get_best_move(self, num_iter):
        '''
        Play the best move from current state
        '''
        for i in range(int(num_iter)):
            node = self.select()
            result = node.simulate()
            node.backpropagate(result)
        # print(len(self.children))
        return self.best_child(c_param=0.0).parent_action


def run_mcts(root_state, num_iter):
    '''
    gameplay
    '''
    global root
    print(num_iter)
    root = MctsNode(state=root_state)
    if root.is_game_over():
        return root
    return root.get_best_move(num_iter)
