from sympy.combinatorics import Permutation

MOVE_PERM_DICT = {
    'R': Permutation(53)(2, 16, 22, 10)(9, 1, 19, 21)(12, 13, 14, 15)(33, 25, 43, 45)(36, 37, 38, 39),
    'L': Permutation(53)(0, 8, 20, 18)(17, 3, 11, 23)(4, 5, 6, 7)(41, 27, 35, 47)(28, 29, 30, 31),
    'F': Permutation(53)(3, 12, 21, 6)(2, 15, 20, 5)(8, 9, 10, 11)(26, 39, 44, 29)(32, 33, 34, 35),
    'B': Permutation(53)(1, 4, 23, 14)(0, 7, 22, 13)(16, 17, 18, 19)(24, 31, 46, 37)(40, 41, 42, 43),
    'U': Permutation(53)(17, 13, 9, 5)(16, 12, 8, 4)(0, 1, 2, 3)(40, 36, 32, 28)(24, 25, 26, 27),
    'D': Permutation(53)(11, 15, 19, 7)(10, 14, 18, 6)(20, 21, 22, 23)(34, 38, 42, 30)(44, 45, 46, 47),
    'M': Permutation(26, 34, 46, 40)(24, 32, 44, 42)(48, 50, 53, 52),
    'E': Permutation(53)(35, 39, 43, 31)(29, 33, 37, 41)(49, 50, 51, 52),
    'S': Permutation(25, 38, 47, 28)(27, 36, 45, 30)(48, 51, 53, 49)
}

SPEFFZ = 'ABCDEFGHIJKLMNOPQRSTUVWXABCDEFGHIJKLMNOPQRSTUVWX'

PIECE_LIST = [[0, 4, 17], [1, 13, 16], [2, 9, 12], [3, 5, 8], [6, 11, 20], [7, 18, 23], [10, 15, 21], [14, 19, 22], [24, 40], [25, 36], [26, 32], [27, 28], [29, 35], [30, 47], [31, 41], [33, 39], [34, 44], [37, 43], [38, 45], [42, 46], [48], [49], [50], [51], [52], [53]]

class Move:
    def __init__(self, layer, turn):
        self.layer = layer
        self.turn = turn
        
    def __str__(self):
        return self.layer + self.turn
    
    def perm(self):
        result = MOVE_PERM_DICT[self.layer]
        if self.turn == "'":
            result = ~result
        elif self.turn == '2':
            result *= result
        
        return result

    def HTM(self):
        if self.layer in 'RUFLBD':
            return 1
        if self.layer in 'MES':
            return 2
        return 0
    
    def inverse(self):
        if self.turn == '':
            inv_turn = "'"
        elif self.turn == "'":
            inv_turn = ''
        else:
            inv_turn = self.turn
        
        return Move(self.layer, inv_turn)
    
    def __eq__(self, other_self):
        return self.layer == other_self.layer and self.turn == other_self.turn

def string_to_move(move_string):
    return Move(move_string[:-1], move_string[-1]) if move_string[-1] in "'2" else Move(move_string, '')

class Algorithm:
    def __init__(self, alg_string):
        self.move_list = [string_to_move(move_string) for move_string in alg_string.split()]
    
    def __str__(self):
        return ' '.join(str(move) for move in self.move_list)

    def perm(self):
        # Permutation of stickers caused by self
        result = Permutation()
        for move in self.move_list:
            result *= move.perm()
        return result
    
    def HTM(self):
        # Length of the algorithm using Half Turn Metric
        return sum(move.HTM() for move in self.move_list)
    
    def simplify(self):
        simplified = False

        turn_value = {
            '': 1,
            "'": -1,
            "2": 2
        }

        while not simplified:
            for i in range(len(self.move_list)-1):
                current_move = self.move_list[i]
                next_move = self.move_list[i+1]

                if current_move.layer == next_move.layer:
                    turn_result = (turn_value[current_move.turn] + turn_value[next_move.turn]) % 4

                    self.move_list.pop(i)
                    if turn_result == 0:
                        self.move_list.pop(i)
                    elif turn_result == 1:
                        self.move_list[i] = Move(current_move.layer, '')
                    elif turn_result == 2:
                        self.move_list[i] = Move(current_move.layer, '2')
                    else:
                        self.move_list[i] = Move(current_move.layer, "'")

                    break

            else:
                simplified = True
    
    def inverse(self):
        inverse_move_list = [move.inverse() for move in self.move_list]
        inverse_move_list.reverse()

        inverse_alg = Algorithm('')
        inverse_alg.move_list = inverse_move_list
        return inverse_alg

    def __add__(self, other_self):
        result = Algorithm('')
        result.move_list = self.move_list + other_self.move_list
        return result
    
    def piece_perm(self):
        # Returns the permutation of pieces induced by self (element of A_26)
        return Permutation([piece_index(self.perm()(piece[0])) for piece in PIECE_LIST])
    
    def __eq__(self, other_self):
        return self.move_list == other_self.move_list

def piece_index(sticker):
    for i, piece in enumerate(PIECE_LIST):
        if sticker in piece:
            return i

def same_piece(i, j):
    return any(i in piece and j in piece for piece in PIECE_LIST)

def blindfold_cycle(scramble, buffer):
    result = []
    x = scramble(buffer)
    while not same_piece(buffer, x):
        result.append(x)
        x = scramble(x)
    return result

def blindfold_sequence(scramble, corner_buffer=2, edge_buffer=44, include_orientation=False):
    # scramble: inverse of the permutation corresponding to the scramble
    # the scramble must fix the centers
    
    corner_seq = blindfold_cycle(scramble, corner_buffer)
    for x in range(24):
        if not (any(same_piece(x, y) for y in corner_seq)
                or same_piece(x, corner_buffer)
                or x == scramble(x)
                or (same_piece(x, scramble(x)) and not include_orientation)):
            launch = [x]
            launch.extend(blindfold_cycle(scramble, x))
            launch.append(scramble(launch[-1]))
            corner_seq.extend(launch)

    edge_seq = blindfold_cycle(scramble, edge_buffer)
    for x in range(24, 48):
        if not (any(same_piece(x, y) for y in edge_seq)
                or same_piece(x, edge_buffer)
                or x == scramble(x)
                or (same_piece(x, scramble(x)) and not include_orientation)):
            launch = [x]
            launch.extend(blindfold_cycle(scramble, x))
            launch.append(scramble(launch[-1]))
            edge_seq.extend(launch)
    
    return corner_seq, edge_seq

def print_blindfold_sequence(scramble_alg, scheme=SPEFFZ, corner_buffer=2, edge_buffer=44, include_orientation=False):
    # scheme: 48 char string with the lettering scheme

    corner_seq, edge_seq = blindfold_sequence(
        ~scramble_alg.perm(),
        corner_buffer=corner_buffer,
        edge_buffer=edge_buffer,
        include_orientation=include_orientation
        )

    print('Scramble:', scramble_alg)
    print('Corners:',
          ' '.join(
              ''.join(scheme[x] for x in corner_seq)[i:i+2]
              for i in range(0, len(corner_seq), 2)
          )
    )
             
    print('Edges:',
          ' '.join(
              ''.join(scheme[x] for x in edge_seq)[i:i+2]
              for i in range(0, len(edge_seq), 2)
          )
    )

from random import choice
def random_sequence(num_moves=20, moveset='RUFLBD'):
    alg = Algorithm('')
    layer = ''
    for _ in range(num_moves):
        layer = choice([x for x in moveset if x != layer])
        turn = choice(" '2")
        alg += Algorithm(layer + turn)
    return alg

def is_valid(move, block):
    # Does the move preserve the given block (list of pieces)?
    piece_perm_support = Algorithm(move.layer + move.turn).piece_perm().support()

    return all(piece not in piece_perm_support for piece in block) or (
        all(piece in piece_perm_support for piece in block if piece < 20)
        and all('ULFRBD'[PIECE_LIST[center][0] - 48] == move.layer for center in block if center >= 20)
    )

def update_block_list(alg, block_list):
    return [list(map(alg.piece_perm(), block)) for block in block_list]

def random_sequence_blocks(block_list, num_moves=20, moveset='RUFLBD'):
    alg = Algorithm('')
    layer = ''
    current_block_list = block_list

    while alg.HTM() < num_moves:
        layer = choice([x for x in moveset if all(is_valid(Move(x, ''), block) for block in current_block_list)])
        move = Algorithm(layer + choice(" '2"))
        alg += move
        current_block_list = update_block_list(move, current_block_list)
        alg.simplify()
        
    return alg