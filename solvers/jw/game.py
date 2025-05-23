import time
import random

BITS_PER_TILE = 5
NCOLS = NROWS = 4
ROW_MASK      = (1 << BITS_PER_TILE * NCOLS) - 1
_ROW_LEFT_TABLE  = None
_ROW_RIGHT_TABLE = None

def to_board(bitset):
    mask  = (1 << BITS_PER_TILE) - 1
    board = [[0] * NCOLS for _ in range(NROWS)]

    for i in range(NROWS * NCOLS):
        r, c = divmod(i, NCOLS)
        board[r][c] = (bitset >> (i * BITS_PER_TILE)) & mask
    return board

def to_bitset(board):
    nrows  = len(board)
    ncols  = len(board[0]) if nrows else 0
    mask   = (1 << BITS_PER_TILE) - 1

    bitset = 0
    for r, row in enumerate(board):
        for c, val in enumerate(row):
            assert val <= mask, f"value {val} cannot fit in {BITS_PER_TILE} bits"
            bitset |= (val & mask) << ((r * ncols + c) * BITS_PER_TILE)
    return bitset

def print_board(board, label = None):
    if label:
        print(label)
        
    max_val = 2 ** max(max(row) for row in board)
    for row in board:
        print(" ".join(
            ' ' * (len(str(max_val)) - len(str(2**val)) + 1)
            + f"{2**val if val > 0 else '.'}" for val in row))
        

def _reverse_row_bits(row: int) -> int:
    t0 = (row & 0x000001F) << 15
    t1 = (row & 0x0003E0) << 5
    t2 = (row & 0x007C00) >> 5
    t3 = (row & 0x0F8000) >> 15
    return t0 | t1 | t2 | t3

def _build_row_tables():
    global _ROW_LEFT_TABLE, _ROW_RIGHT_TABLE
    _ROW_LEFT_TABLE = [0] * (1 << BITS_PER_TILE * NCOLS)
    _ROW_RIGHT_TABLE = [0] * (1 << BITS_PER_TILE * NCOLS)
    mask = 0x1F

    for row in range(1 << 20):
        tiles = [(row >> (i * BITS_PER_TILE)) & mask for i in range(4)]

        # Slide left
        compressed = [t for t in tiles if t]

        merged = []
        i = 0
        while i < len(compressed):
            if i + 1 < len(compressed) and compressed[i] == compressed[i + 1]:
                merged.append(compressed[i] + 1)
                i += 2
            else:
                merged.append(compressed[i])
                i += 1

        merged.extend([0] * (4 - len(merged)))

        # Pack back to bits
        left_bits = 0
        for idx, val in enumerate(merged):
            left_bits |= val << (idx * BITS_PER_TILE)
        _ROW_LEFT_TABLE[row] = left_bits

    for row in range(1 << 20):
        _ROW_RIGHT_TABLE[row] = _reverse_row_bits(
            _ROW_LEFT_TABLE[_reverse_row_bits(row)]
        )
        
    print(f'sum of left table: {sum(_ROW_LEFT_TABLE)}')
    print(f'sum of right table: {sum(_ROW_RIGHT_TABLE)}')

def _transpose(bitset: int) -> int:
    res = 0
    mask = 0x1F
    for r in range(4):
        for c in range(4):
            tile = (bitset >> ((r * 4 + c) * BITS_PER_TILE)) & mask
            res  |= tile << ((c * 4 + r) * BITS_PER_TILE)
    return res

import random

def get_empty_tiles(bitset: int) -> list[int]:
    mask = (1 << BITS_PER_TILE) - 1
    empty_indices = [
        i for i in range(NROWS * NCOLS)
        if ((bitset >> (i * BITS_PER_TILE)) & mask) == 0
    ]
    return empty_indices


def generate_tile(bitset: int, rng: random.Random | None = None) -> int:
    # Deterministic tests with injected RNG
    if rng is None:
        rng = random

    empty_indices = get_empty_tiles(bitset)
    if not empty_indices:
        # assert False, "No space to generate tile"
        return bitset

    pos   = rng.choice(empty_indices)
    val   = 1 if rng.random() < 0.9 else 2
    shift = pos * BITS_PER_TILE

    return bitset | (val << shift)

def get_action_space(bitset: int) -> list[int]:
    out = []
    if left(bitset) != bitset:
        out.append(left)
    if up(bitset) != bitset:
        out.append(up)
    if right(bitset) != bitset:
        out.append(right)
    if down(bitset) != bitset:
        out.append(down)
    return out

def get_max_tile(bitset: int) -> int:
    mask     = (1 << BITS_PER_TILE) - 1
    max_exp  = 0
    for i in range(NROWS * NCOLS):
        max_exp = max(max_exp, (bitset >> (i * BITS_PER_TILE)) & mask)
    return 1 << max_exp


def left(bitset: int) -> int:
    res = 0
    for r in range(4):
        row_bits = (bitset >> (r * 20)) & ROW_MASK
        res     |= _ROW_LEFT_TABLE[row_bits] << (r * 20)
    return res


def right(bitset: int) -> int:
    res = 0
    for r in range(4):
        row_bits = (bitset >> (r * 20)) & ROW_MASK
        res     |= _ROW_RIGHT_TABLE[row_bits] << (r * 20)
    return res


def up(bitset: int) -> int:
    return _transpose( left(_transpose(bitset)) )


def down(bitset: int) -> int:
    return _transpose( right(_transpose(bitset)) )





class Game:
    def __init__(self, board = None):
        if board is None:
            self.start_board = [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ]
        else:
            self.start_board = board

        self.start_bitset = to_bitset(self.start_board)

    def watch_game(self, ai):
        bs = self.start_bitset

        for i in range(100000):
            bs = generate_tile(bs)
            action_space = get_action_space(bs)
            print_board(to_board(bs), f"Turn {i}: Random tile")
            if action_space:
                bs = ai(bs, action_space)
            else:
                break
            print_board(to_board(bs), f"Turn {i}: Taken action")
            
    def run_game(self, ai, max_iters=1000000, num_games=10000):
        game_results = []

        for game_index in range(num_games):
            bs = self.start_bitset

            start_iter = time.time()

            for i in range(max_iters):
                bs = generate_tile(bs)
                action_space = get_action_space(bs)
                if action_space:
                    bs = ai(bs, action_space)
                else:
                    break
                
            time_taken = time.time() - start_iter
            game_results.append({
                'num_turns_taken': i,
                'max_tile_reached': get_max_tile(bs),
                'time_taken': time_taken,
            })

        return game_results, ai.__name__
        
    def print_results(self, game_results, ai_name):
        print(f'Test: {ai_name}')

        num_games = len(game_results)
        print()
        print(f'Number of games played: {num_games}')
        print(f'Total time taken: {sum(result["time_taken"] for result in game_results)} seconds')
        print(f'Games per second: {num_games / sum(result["time_taken"] for result in game_results)}')
        print(f'Turns per second: {sum(result["num_turns_taken"] for result in game_results) / sum(result["time_taken"] for result in game_results)}')

        print()
        print(f'Max number of turns before game over: {max(result["num_turns_taken"] for result in game_results)}')
        print(f'Min number of turns before game over: {min(result["num_turns_taken"] for result in game_results)}')
        print(f'Average number of turns before game over: {sum(result["num_turns_taken"] for result in game_results) / len(game_results)}')

        print()
        print(f'Max tile reached: {max(result["max_tile_reached"] for result in game_results)}')
        print(f'Min tile reached: {min(result["max_tile_reached"] for result in game_results)}')
        print(f'Average max tile reached: {sum(result["max_tile_reached"] for result in game_results) / len(game_results)}')

    def plot_results(self, game_results, ai_name):
        import pandas as pd
        import matplotlib.pyplot as plt

        df = pd.DataFrame(game_results)

        plt.hist(df['max_tile_reached'], bins=100)
        plt.title(f'Max tile reached for {ai_name}')
        plt.show()

        plt.hist(df['num_turns_taken'], bins=100)
        plt.title(f'Number of turns before game over for {ai_name}')
        plt.show()