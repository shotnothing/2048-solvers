BITS_PER_TILE = 5
NCOLS = NROWS = 4
ROW_MASK      = (1 << BITS_PER_TILE * NCOLS) - 1
_ROW_LEFT_TABLE  : list[int] = [0] * (1 << 20)
_ROW_RIGHT_TABLE : list[int] = [0] * (1 << 20)

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
    mask = 0x1F
    for row in range(1 << 20):
        # Extract tile exponents (little‑endian)
        tiles = [ (row >> (i * BITS_PER_TILE)) & mask for i in range(4) ]

        # Slide and merge left
        out = []
        skip = False
        for i in range(4):
            if tiles[i] == 0:
                continue
            if not skip and i + 1 < 4 and tiles[i] == tiles[i+1] and tiles[i] != 0:
                out.append(tiles[i] + 1)
                skip = True
            else:
                if skip:
                    skip = False
                    continue
                out.append(tiles[i])
        out.extend([0] * (4 - len(out)))

        # Pack back into bits
        left_bits = 0
        for i, v in enumerate(out):
            left_bits |= v << (i * BITS_PER_TILE)
        _ROW_LEFT_TABLE[row] = left_bits

        # Right table via mirroring (not strictly necessary tbh, but I think it's faster 
        # than reversing at runtime)
        _ROW_RIGHT_TABLE[row] = _reverse_row_bits(
            _ROW_LEFT_TABLE[ _reverse_row_bits(row) ]
        )

def _transpose(bitset: int) -> int:
    res = 0
    mask = 0x1F
    for r in range(4):
        for c in range(4):
            tile = (bitset >> ((r * 4 + c) * BITS_PER_TILE)) & mask
            res  |= tile << ((c * 4 + r) * BITS_PER_TILE)
    return res

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
