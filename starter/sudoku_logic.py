import copy
import random

SIZE = 9
EMPTY = 0
DIFFICULTY_SETTINGS = {
    'easy': 45,
    'medium': 35,
    'hard': 28,
}


def deep_copy(board):
    return copy.deepcopy(board)


def get_clues_for_difficulty(difficulty):
    if not isinstance(difficulty, str):
        raise ValueError("Invalid difficulty {!r}. Expected one of: easy, medium, hard.".format(difficulty))

    normalized = difficulty.strip().lower()
    if normalized not in DIFFICULTY_SETTINGS:
        valid = ', '.join(sorted(DIFFICULTY_SETTINGS))
        raise ValueError("Invalid difficulty {!r}. Expected one of: {}.".format(difficulty, valid))

    return DIFFICULTY_SETTINGS[normalized]

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def remove_cells(board, clues):
    # Validate clues
    if not isinstance(clues, int) or clues < 0 or clues > SIZE * SIZE:
        raise ValueError("clues must be an int between 0 and {}".format(SIZE * SIZE))

    # Attempt to remove cells one at a time while preserving uniqueness.
    # Work on a shuffled list of positions to randomize removals.
    positions = [(r, c) for r in range(SIZE) for c in range(SIZE)]
    random.shuffle(positions)

    # Count currently filled cells
    filled = sum(1 for r in range(SIZE) for c in range(SIZE) if board[r][c] != EMPTY)
    target = clues

    for row, col in positions:
        if filled <= target:
            break
        if board[row][col] == EMPTY:
            continue

        backup = board[row][col]
        board[row][col] = EMPTY

        # Use the external solution counter to verify uniqueness.
        # Import locally to avoid circular deps in some test runners.
        sol_count = count_solutions(board, limit=2)
        if sol_count == 1:
            filled -= 1
        else:
            # Revert removal if uniqueness is lost or zero solutions found.
            board[row][col] = backup

def generate_puzzle(clues=35):
    if not isinstance(clues, int) or clues < 0 or clues > SIZE * SIZE:
        raise ValueError("clues must be an int between 0 and {}".format(SIZE * SIZE))

    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution


def is_board_valid(board):
    """Validate that the board has no duplicate non-empty values in any row, column or 3x3 box."""
    # Rows
    for r in range(SIZE):
        seen = set()
        for c in range(SIZE):
            val = board[r][c]
            if val == EMPTY:
                continue
            if not (1 <= val <= SIZE):
                return False
            if val in seen:
                return False
            seen.add(val)

    # Columns
    for c in range(SIZE):
        seen = set()
        for r in range(SIZE):
            val = board[r][c]
            if val == EMPTY:
                continue
            if val in seen:
                return False
            seen.add(val)

    # Boxes
    for br in range(0, SIZE, 3):
        for bc in range(0, SIZE, 3):
            seen = set()
            for r in range(br, br + 3):
                for c in range(bc, bc + 3):
                    val = board[r][c]
                    if val == EMPTY:
                        continue
                    if val in seen:
                        return False
                    seen.add(val)

    return True


def count_solutions(board, limit=2):
    """Count solutions for a given board up to `limit`.

    Returns an integer: 0 (no solutions), 1 (exactly one), or >=limit (more than one).

    Does not mutate the caller's board.
    Validates the initial board for contradictions before searching.
    """
    if not isinstance(limit, int) or limit < 1:
        raise ValueError("limit must be an int >= 1")

    if not is_board_valid(board):
        return 0

    b = deep_copy(board)
    solutions = 0

    def solve():
        nonlocal solutions
        # Early exit if we've reached the limit
        if solutions >= limit:
            return

        # Find the empty cell with the fewest candidates (MRV heuristic)
        best_r = best_c = None
        best_candidates = None
        for r in range(SIZE):
            for c in range(SIZE):
                if b[r][c] == EMPTY:
                    candidates = []
                    for n in range(1, SIZE + 1):
                        if is_safe(b, r, c, n):
                            candidates.append(n)
                    if not candidates:
                        return
                    if best_candidates is None or len(candidates) < len(best_candidates):
                        best_candidates = candidates
                        best_r, best_c = r, c

        # If no empty cells, we've found a complete solution
        if best_r is None:
            solutions += 1
            return

        for n in best_candidates:
            b[best_r][best_c] = n
            solve()
            b[best_r][best_c] = EMPTY
            if solutions >= limit:
                return

    solve()
    return solutions
