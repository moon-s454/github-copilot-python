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
    yield
    app_module.CURRENT['puzzle'] = None
    app_module.CURRENT['solution'] = None


def test_index_route_returns_html():
    client = app_module.app.test_client()
    response = client.get('/')

    assert response.status_code == 200
    assert b'Sudoku Game' in response.data


def test_new_game_returns_puzzle_and_sets_solution():
    client = app_module.app.test_client()
    response = client.get('/new?clues=30')

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data['puzzle'], list)
    assert len(data['puzzle']) == 9
    assert all(len(row) == 9 for row in data['puzzle'])
    assert all(cell in range(0, 10) for row in data['puzzle'] for cell in row)

    assert app_module.CURRENT['solution'] is not None
    assert app_module.CURRENT['puzzle'] == data['puzzle']


def test_new_game_accepts_difficulty_levels():
    client = app_module.app.test_client()

    for difficulty, expected in [('easy', 45), ('medium', 35), ('hard', 28)]:
        response = client.get(f'/new?difficulty={difficulty}')
        assert response.status_code == 200, response.get_json()
        puzzle = response.get_json()['puzzle']
        filled = sum(1 for row in puzzle for cell in row if cell != 0)
        assert filled == expected, (difficulty, filled, expected)
        assert app_module.CURRENT['solution'] is not None


def test_new_game_rejects_invalid_difficulty():
    client = app_module.app.test_client()
    response = client.get('/new?difficulty=expert')

    assert response.status_code == 400
    assert 'Invalid difficulty' in response.get_json()['error']


def test_check_solution_accepts_completed_board():
    client = app_module.app.test_client()
    client.get('/new?clues=30')
    board = copy.deepcopy(app_module.CURRENT['solution'])

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': []}


def test_check_solution_reports_incorrect_cells():
    client = app_module.app.test_client()
    client.get('/new?clues=30')
    board = copy.deepcopy(app_module.CURRENT['solution'])
    # find a cell that was not originally prefilled to make an incorrect entry
    original = app_module.CURRENT.get('original_puzzle') or app_module.CURRENT['puzzle']
    made = False
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if original[i][j] == sudoku_logic.EMPTY:
                board[i][j] = (board[i][j] % 9) + 1
                made = True
                wrong_pos = [i, j]
                break
        if made:
            break

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert wrong_pos in response.get_json()['incorrect']


def test_check_solution_requires_active_game():
    client = app_module.app.test_client()
    response = client.post('/check', json={'board': [[0] * 9 for _ in range(9)]})

    assert response.status_code == 400
    assert response.get_json()['error'] == 'No game in progress'
