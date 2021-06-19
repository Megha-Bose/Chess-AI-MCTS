# board dimension
N = 8
# no. of type of pieces
M = 6
pieces = ['k', 'q', 'r', 'b', 'n', 'p']


class Game:
    '''
    Each board state is a 8x8 array
    Example: s1
    First char: w: white, b: black, e: empty
    Second char: k: king, q: queen, b: bishop, n: knight, r: rook, p: pawn
    '''

    '''
    unicodes for chess symbols
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

    def __init__(self, color='w', iterations=100, start_state=s1):
        opponent_color = 'b' if color == 'w' else 'w'
        self.game_info = {
            'COLOR': color,
            'OPPONENT COLOR': opponent_color,
            'ITERATIONS': iterations,
            'START STATE': start_state
        }

    def orthogonal_safety(self, state, i1, j1, i2, j2):
        '''
        i and j - coordinates of pieces
        '''
        if i1 == i2:
            safe = False
            '''
            if i coords match, check j coords for intermediate empty cells
            '''
            max = j1 if j1 > j2 else j2
            min = j2 if max == j1 else j1
            for j_coord in range(min+1, max-1):
                if state[i1][j_coord] != 'em':
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
                if state[i_coord][j1] != 'em':
                    safe = True
                    break
            return safe
        else:
            return True

    def diagonal_safety(self, state, i1, j1, i2, j2):
        '''
        i and j - coordinates of pieces
        '''
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
                            if state[i_coord][j_coord] != 'em':
                                safe = True
                                break
                return safe
            else:
                return True

    def is_king_check(self, state, king_i, king_j, opponent=False):
        '''
        if opponent=True, opponent king check is computed
        else computer's king
        '''
        if opponent == False:
            king_color = self.game_info['COLOR']
            opponent_color = self.game_info['OPPONENT COLOR']
        else:
            king_color = self.game_info['OPPONENT COLOR']
            opponent_color = self.game_info['COLOR']

        for i in range(N):
            for j in range(N):
                '''
                check each opponent piece's position w.r.t to computer's king
                or vice versa, depending on opponent value passed
                '''
                if state[i][j][0] == opponent_color:
                    piece_type = state[i][j][1]
                    ''' condition for kings to be adjacent
                    '''
                    if piece_type == 'k':
                        if abs(king_i-i) == 1 and abs(king_j-j) == 1:
                            return True

                    elif piece_type == 'q':
                        '''
                        queen search - orthogonal and diagonal
                        '''
                        if self.orthogonal_safety(state, king_i, king_j, i, j) == False:
                            return True
                        if self.diagonal_safety(state, king_i, king_j, i, j) == False:
                            return True

                    elif piece_type == 'r':
                        '''
                        rook search - orthogonal
                        '''
                        if self.orthogonal_safety(state, king_i, king_j, i, j) == False:
                            return True

                    elif piece_type == 'b':
                        '''
                        bishop search - diagonal
                        '''
                        if self.diagonal_safety(state, king_i, king_j, i, j) == False:
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
        return False

    def is_checkmate(self, state, opponent=False):
        res = False
        '''finding king's position - king_i, king_j'''

        ''' king color depends on opponent value passed'''
        king = self.game_info['COLOR'] + \
            'k' if opponent == False else self.game_info['OPPONENT COLOR']+'k'
        for king_i in range(N):
            if king in state[king_i]:
                king_j = state[king_i].index(king)

        if self.is_king_check(state, king_i, king_j, opponent):
            res = True
            '''
            check for king blocking/dodging check
            (yet to implement blocking check through intercept & capture)
            '''

            '''
            check for all adjacent squares
            with x and y generating index range
            '''
            x = [king_i-1, king_i, king_i+1]
            y = [king_j-1, king_j, king_j+1]

            Range = [i for i in range(N)]

            for i_coord in x:
                for j_coord in y:
                    if x in Range and y in Range:
                        if state[i_coord][j_coord] == 'em':
                            if self.is_king_check(state, i_coord, j_coord, opponent) == False:
                                res = False
                                break
        return res

    def get_actions_list(self, state, i, j, possible):
        color = state[i][j][0]
        piece = state[i][j][1]

        actions_list = []
        for element in possible:
            check = state[element[0]][element[1]
                                      ][0] != color and state[element[0]][element[1]][1] != 'k'
            if check == False:
                continue

            # 'check' is true only when cell at element coord is
            # not same color and not king

            # if gap is empty
            if i < element[0]:
                step_i = 1
            elif i > element[0]:
                step_i = -1
            else:
                step_i = 0

            if j < element[1]:
                step_j = 1
            elif j > element[1]:
                step_j = -1
            else:
                step_j = 0

            i_coord = i+step_i
            j_coord = j+step_j

            path = True
            while i_coord != element[0] or j_coord != element[1]:
                if state[i_coord][j_coord] != 'em':
                    path = False
                    break
                i_coord += step_i
                j_coord += step_j
            if path == True:
                actions_list.append((i, j, element[0], element[1]))

    def possible_moves(self, state, i, j):
        color = state[i][j][0]
        piece = state[i][j][1]

        for i_coord in range(N):
            for j_coord in range(N):
                if state[i_coord][j_coord][0] == color and state[i_coord][j_coord][1] == 'k':
                    king_i = i_coord
                    king_j = j_coord

        # action_list - list of actions represented by
        # 4-value tuple elements - (x, y, x', y')
        actions_list = []
        opponent = (color != self.game_info['COLOR'])

        if self.is_king_check(state, king_i, king_j, opponent):
            if self.is_checkmate(state):
                print('CHECKMATE')
                return None
            else:
                # handle check by blocking/dodging
                pass
        if piece == 'k':
            # king
            # check adjacent squares
            x = [i-1, i, i+1]
            y = [j-1, j, j+1]

            Range = [i for i in range(N)]

            for i_coord in x:
                for j_coord in y:
                    '''print(i_coord, end=' ')
                    print(j_coord)'''
                    if i_coord in Range and j_coord in Range:
                        if state[i_coord][j_coord][0] != color and self.is_king_check(state, i_coord, j_coord, opponent) == False:
                            if i_coord != i and j_coord != j:
                                actions_list.append((i, j, i_coord, j_coord))
        if piece == 'q':
            # queen
            # check orthogonal & diagonal squares
            Range = [i for i in range(N)]
            possible = []
            # horizontal
            for j_coord in Range:
                if j_coord != j:
                    possible.append((i, j_coord))
            # vertical
            for i_coord in Range:
                if i_coord != i:
                    possible.append((i_coord, j))
            # diagonal
            step_list = [1, -1]
            for i_step in step_list:
                for j_step in step_list:
                    i_coord = i + i_step
                    j_coord = j + j_step
                    while i_coord in Range and j_coord in Range:
                        possible.append((i_coord, j_coord))

                        i_coord += i_step
                        j_coord += j_step
            result = self.get_actions_list(state, i, j, possible)
            if result != None:
                for element in result:
                    actions_list.append(element)

        if piece == 'r':
            # check orthogonal & diagonal squares
            Range = [i for i in range(N)]
            possible = []
            # horizontal
            for j_coord in Range:
                if j_coord != j:
                    possible.append((i, j_coord))
            # vertical
            for i_coord in Range:
                if i_coord != i:
                    possible.append((i_coord, j))
            # print(possible)
            result = self.get_actions_list(state, i, j, possible)

            if result != None:
                for element in result:
                    actions_list.append(element)

        if piece == 'b':
            # bishop
            # diagonal
            step_list = [1, -1]
            for i_step in step_list:
                for j_step in step_list:
                    i_coord = i + i_step
                    j_coord = j + j_step
                    while i_coord in Range and j_coord in Range:
                        possible.append((i_coord, j_coord))

                        i_coord += i_step
                        j_coord += j_step
            result = self.get_actions_list(state, i, j, possible)
            if result != None:
                for element in result:
                    actions_list.append(element)

        if piece == 'n':
            pass

        if piece == 'p':
            pass

        return actions_list
