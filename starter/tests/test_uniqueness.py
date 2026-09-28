import copy
import sudoku_logic


def test_count_solutions_zero():
    board = sudoku_logic.create_empty_board()
    # Introduce a direct contradiction: two '1's in first row
    board[0][0] = 1
    board[0][1] = 1
    assert sudoku_logic.count_solutions(board, limit=2) == 0


def test_count_solutions_exactly_one():
    # Full solved board should have exactly one solution
    puzzle, solution = sudoku_logic.generate_puzzle(clues=81)
    assert sudoku_logic.count_solutions(solution, limit=2) == 1


def test_count_solutions_multiple():
    # Empty board should have multiple solutions
    empty = sudoku_logic.create_empty_board()
    assert sudoku_logic.count_solutions(empty, limit=2) >= 2


def test_generated_puzzle_has_unique_solution_and_matches_solution():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)
    # Puzzle must be consistent with returned solution
    for r in range(sudoku_logic.SIZE):
        for c in range(sudoku_logic.SIZE):
            if puzzle[r][c] != sudoku_logic.EMPTY:
                assert puzzle[r][c] == solution[r][c]

    # Puzzle must have exactly one solution
    assert sudoku_logic.count_solutions(puzzle, limit=2) == 1
