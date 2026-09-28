import sys
import os

# Ensure the starter package directory is on sys.path for test discovery
TEST_DIR = os.path.dirname(os.path.dirname(__file__))
if TEST_DIR not in sys.path:
    sys.path.insert(0, TEST_DIR)

import sudoku_logic


def is_valid_complete_board(board):
    for row in board:
        if sorted(row) != list(range(1, 10)):
            return False

    for col in range(sudoku_logic.SIZE):
        column_values = [board[row][col] for row in range(sudoku_logic.SIZE)]
        if sorted(column_values) != list(range(1, 10)):
            return False

    for top_row in range(0, sudoku_logic.SIZE, 3):
        for left_col in range(0, sudoku_logic.SIZE, 3):
            box = []
            for row in range(top_row, top_row + 3):
                for col in range(left_col, left_col + 3):
                    box.append(board[row][col])
            if sorted(box) != list(range(1, 10)):
                return False

    return True


def test_create_empty_board():
    board = sudoku_logic.create_empty_board()
    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_is_safe_detects_conflicts():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5
    assert sudoku_logic.is_safe(board, 0, 1, 5) is False
    assert sudoku_logic.is_safe(board, 0, 1, 4) is True

    board[0][1] = 3
    assert sudoku_logic.is_safe(board, 0, 2, 3) is False
    assert sudoku_logic.is_safe(board, 1, 3, 3) is True


def test_generate_puzzle_returns_a_valid_solution_and_puzzle():
    puzzle, solution = sudoku_logic.generate_puzzle(35)

    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert all(len(row) == sudoku_logic.SIZE for row in solution)

    assert all(cell in range(0, 10) for row in puzzle for cell in row)
    assert all(cell in range(1, 10) for row in solution for cell in row)
    assert is_valid_complete_board(solution)

    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if puzzle[row][col] != sudoku_logic.EMPTY:
                assert puzzle[row][col] == solution[row][col]


def test_get_clues_for_difficulty_returns_expected_counts():
    assert sudoku_logic.get_clues_for_difficulty('easy') == 45
    assert sudoku_logic.get_clues_for_difficulty('medium') == 35
    assert sudoku_logic.get_clues_for_difficulty('hard') == 28

    try:
        sudoku_logic.get_clues_for_difficulty('expert')
        assert False, 'Expected ValueError for invalid difficulty'
    except ValueError as exc:
        assert 'Invalid difficulty' in str(exc)


def test_generate_puzzle_by_difficulty_matches_requested_clue_counts():
    for difficulty, expected in [('easy', 45), ('medium', 35), ('hard', 28)]:
        clues = sudoku_logic.get_clues_for_difficulty(difficulty)
        puzzle, solution = sudoku_logic.generate_puzzle(clues)
        filled = sum(1 for row in puzzle for cell in row if cell != sudoku_logic.EMPTY)
        assert filled == expected, (difficulty, filled, expected)
        assert sudoku_logic.count_solutions(puzzle, limit=2) == 1
        for row in range(sudoku_logic.SIZE):
            for col in range(sudoku_logic.SIZE):
                if puzzle[row][col] != sudoku_logic.EMPTY:
                    assert puzzle[row][col] == solution[row][col]
