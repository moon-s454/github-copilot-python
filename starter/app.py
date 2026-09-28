from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    # Snapshot of the original puzzle as delivered to the client (prefilled cells)
    'original_puzzle': None,
    # Hints state
    'hints_used': 0,
    'hinted_positions': []  # list of (r, c) tuples
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty')
    clues_value = request.args.get('clues')

    try:
        if difficulty is not None:
            clues = sudoku_logic.get_clues_for_difficulty(difficulty)
        elif clues_value is not None:
            clues = int(clues_value)
        else:
            clues = 35
        puzzle, solution = sudoku_logic.generate_puzzle(clues)
    except (TypeError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400

    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    # Keep an immutable snapshot of which cells were originally prefilled
    CURRENT['original_puzzle'] = sudoku_logic.deep_copy(puzzle)
    # Reset hint tracking
    CURRENT['hints_used'] = 0
    CURRENT['hinted_positions'] = []
    return jsonify({'puzzle': puzzle})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    original = CURRENT.get('original_puzzle')
    hinted = set(tuple(x) for x in CURRENT.get('hinted_positions', []))

    # Validate shapes minimally
    if not isinstance(board, list) or len(board) != sudoku_logic.SIZE:
        return jsonify({'error': 'Invalid board'}), 400

    # Reject attempts to modify locked cells (original prefilled or hinted)
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if original and original[i][j] != sudoku_logic.EMPTY:
                # originally prefilled: client must not change this value
                if board[i][j] != original[i][j]:
                    return jsonify({'error': 'Attempted to modify a locked cell'}), 400
            if (i, j) in hinted:
                # hinted cells should now be locked to the hinted value stored in CURRENT['puzzle']
                if board[i][j] != CURRENT['puzzle'][i][j]:
                    return jsonify({'error': 'Attempted to modify a locked cell'}), 400

    incorrect = []
    # Only compare non-empty user-entered editable cells against solution.
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            val = board[i][j]
            # ignore empty cells
            if not val:
                continue
            # skip originally prefilled positions (they're locked and already validated above)
            if original and original[i][j] != sudoku_logic.EMPTY:
                continue
            # skip hinted positions (locked)
            if (i, j) in hinted:
                continue
            # compare user-entered value to solution
            if val != solution[i][j]:
                incorrect.append([i, j])

    return jsonify({'incorrect': incorrect})


@app.route('/hint', methods=['POST'])
def hint():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    original = CURRENT.get('original_puzzle')
    if original is None:
        return jsonify({'error': 'Game state unavailable'}), 400

    # Validate client's board
    if not isinstance(board, list) or len(board) != sudoku_logic.SIZE:
        return jsonify({'error': 'Invalid board'}), 400

    hinted = set(tuple(x) for x in CURRENT.get('hinted_positions', []))

    # Find an eligible cell: originally empty and currently empty on the submitted board
    found = None
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if original[i][j] != sudoku_logic.EMPTY:
                continue
            if (i, j) in hinted:
                continue
            # only hint if client also shows the cell as empty
            if board[i][j] == sudoku_logic.EMPTY:
                found = (i, j)
                break
        if found:
            break

    if not found:
        return jsonify({'error': 'No eligible cell for hint'}), 400

    r, c = found
    v = solution[r][c]
    # Apply hint to the server-side puzzle and mark as hinted/locked
    CURRENT['puzzle'][r][c] = v
    CURRENT['hinted_positions'].append([r, c])
    CURRENT['hints_used'] = CURRENT.get('hints_used', 0) + 1

    return jsonify({'row': r, 'col': c, 'value': v, 'hints_used': CURRENT['hints_used']})

if __name__ == '__main__':
    app.run(debug=True)