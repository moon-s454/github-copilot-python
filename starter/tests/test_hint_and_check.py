import copy

import pytest

import sys
import os

# Ensure the starter package directory is on sys.path for test discovery
TEST_DIR = os.path.dirname(os.path.dirname(__file__))
if TEST_DIR not in sys.path:
    sys.path.insert(0, TEST_DIR)

import app as app_module
import sudoku_logic


@pytest.fixture(autouse=True)
def reset_game_state():
    app_module.CURRENT['puzzle'] = None
    app_module.CURRENT['solution'] = None
    app_module.CURRENT['original_puzzle'] = None
    app_module.CURRENT['hints_used'] = 0
    app_module.CURRENT['hinted_positions'] = []
    yield
    app_module.CURRENT['puzzle'] = None
    app_module.CURRENT['solution'] = None
    app_module.CURRENT['original_puzzle'] = None
    app_module.CURRENT['hints_used'] = 0
    app_module.CURRENT['hinted_positions'] = []


def test_hint_fills_one_empty_cell_and_locks():
    client = app_module.app.test_client()
    client.get('/new?clues=30')
    original = copy.deepcopy(app_module.CURRENT['original_puzzle'])
    # Build an empty board matching client view (only original prefilled copied)
    board = copy.deepcopy(original)
    for r in range(sudoku_logic.SIZE):
        for c in range(sudoku_logic.SIZE):
            if board[r][c] != sudoku_logic.EMPTY:
                # keep prefilled values
                continue
            board[r][c] = 0

    res = client.post('/hint', json={'board': board})
    assert res.status_code == 200
    data = res.get_json()
    assert 'row' in data and 'col' in data and 'value' in data
    r, c = data['row'], data['col']
    # Server-side puzzle should now contain the hinted value and be locked
    assert app_module.CURRENT['puzzle'][r][c] == data['value']
    assert [r, c] in app_module.CURRENT['hinted_positions']


def test_hint_increments_and_new_resets():
    client = app_module.app.test_client()
    client.get('/new?clues=30')
    original = copy.deepcopy(app_module.CURRENT['original_puzzle'])
    board = copy.deepcopy(original)
    for r in range(sudoku_logic.SIZE):
        for c in range(sudoku_logic.SIZE):
            if board[r][c] != sudoku_logic.EMPTY:
                continue
            board[r][c] = 0

    res1 = client.post('/hint', json={'board': board})
    assert res1.status_code == 200
    v1 = res1.get_json()['hints_used']
    assert v1 == 1

    res2 = client.post('/hint', json={'board': app_module.CURRENT['puzzle']})
    assert res2.status_code == 200
    v2 = res2.get_json()['hints_used']
    assert v2 == 2

    # New game resets counter
    client.get('/new?clues=30')
    assert app_module.CURRENT['hints_used'] == 0


def test_hint_does_not_overwrite_user_entry():
    client = app_module.app.test_client()
    client.get('/new?clues=30')
    original = copy.deepcopy(app_module.CURRENT['original_puzzle'])
    board = copy.deepcopy(original)
    # Put a user value in first empty cell
    placed = False
    for r in range(sudoku_logic.SIZE):
        for c in range(sudoku_logic.SIZE):
            if board[r][c] == sudoku_logic.EMPTY:
                board[r][c] = 7
                placed = True
                break
        if placed:
            break

    res = client.post('/hint', json={'board': board})
    assert res.status_code == 200
    data = res.get_json()
    # Ensure the hinted cell is not the one we filled
    assert not (data['row'] == r and data['col'] == c)


def test_check_rejects_modification_of_original_prefilled():
    client = app_module.app.test_client()
    client.get('/new?clues=30')
    original = copy.deepcopy(app_module.CURRENT['original_puzzle'])
    board = copy.deepcopy(app_module.CURRENT['solution'])
    # Modify an original prefilled cell to a different value
    for rr in range(sudoku_logic.SIZE):
        for cc in range(sudoku_logic.SIZE):
            if original[rr][cc] != sudoku_logic.EMPTY:
                board[rr][cc] = (board[rr][cc] % 9) + 1
                bad_r, bad_c = rr, cc
                break
        else:
            continue
        break

    res = client.post('/check', json={'board': board})
    assert res.status_code == 400
    assert 'locked cell' in res.get_json()['error']


def test_check_ignores_empty_cells_and_reports_incorrects():
    client = app_module.app.test_client()
    client.get('/new?clues=30')
    solution = copy.deepcopy(app_module.CURRENT['solution'])
    # Start from the original client-visible puzzle so prefilled values are present
    original = copy.deepcopy(app_module.CURRENT.get('original_puzzle') or app_module.CURRENT['puzzle'])
    board = copy.deepcopy(original)
    # Ensure empty cells are zeros and put one incorrect non-empty value in an empty cell
    made = False
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] == sudoku_logic.EMPTY:
                board[i][j] = (solution[i][j] % 9) + 1
                wrong = [i, j]
                made = True
                break
        if made:
            break

    res = client.post('/check', json={'board': board})
    assert res.status_code == 200
    data = res.get_json()
    assert wrong in data['incorrect']