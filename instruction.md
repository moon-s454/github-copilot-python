# Flask Sudoku Project Guidance

## Project purpose

This project is a Flask-based Sudoku game being modernized from legacy Python code. The goal is to preserve the original game concept while improving maintainability, readability, accessibility, and testability.

The codebase should evolve gradually without turning into an over-engineered application. Keep the implementation simple, purposeful, and easy to follow.

## Core principles

### 1. Keep the project modular and maintainable

- Separate Sudoku game logic from Flask routes and presentation code.
- Keep generation, validation, solving, and board-state logic in dedicated Python modules or functions.
- Avoid mixing business logic directly into route handlers or template rendering.
- Prefer small, focused functions and classes with clear responsibilities.
- Keep the architecture easy to reason about and easy to test.

### 2. Prioritize readable, Pythonic code

- Follow PEP 8 styling conventions.
- Use clear naming for variables, functions, and modules.
- Use type hints where they improve clarity without adding noise.
- Favor explicit, readable logic over clever or compact code.
- Add sensible error handling for invalid input, missing state, and unexpected values.

### 3. Keep logic separate from presentation

- Sudoku generation, solving, validation, and difficulty rules belong in separate logic modules.
- Flask routes should orchestrate requests and responses, not contain complex game logic.
- HTML, CSS, and JavaScript should focus on presentation and interaction, not puzzle rules.
- This separation keeps the game easier to maintain and easier to test.

## Functional requirements

### Puzzle generation and uniqueness

- Generated Sudoku puzzles must have exactly one unique solution.
- The puzzle generator must produce valid Sudoku boards that satisfy the unique-solution requirement.
- Do not accept generator logic that creates ambiguous or underconstrained boards.

### Difficulty levels

- Support Easy, Medium, and Hard difficulty levels.
- Difficulty must control the number of prefilled cells in the generated puzzle.
- Ensure the board size and game mechanics remain consistent across all levels.

### Locked cells and interactions

- Prefilled cells must be locked and not editable by the user.
- Hint-filled cells must also be locked once displayed.
- User-entered values should be editable and visually distinct from locked numbers.
- Invalid entries should provide immediate visual feedback so the user understands the problem without delay.

### Planned game features

The application should eventually include:

- Check
- Hint
- Timer
- Top 10 leaderboard
- localStorage persistence
- Dark Mode

These features should be added incrementally and integrated cleanly with the existing architecture.

## UI and accessibility requirements

### Responsive design

- The UI must work well on both desktop and mobile devices.
- Layout, controls, and input areas should remain usable on smaller screens without breaking the game flow.

### Visual structure and styling

- The 3x3 Sudoku regions must have alternating visual styling.
- Light and dark modes must both be supported.
- Text and controls must remain readable in both themes.
- Visual differentiation should help the user understand the board structure clearly.

### Accessibility and interaction

- Prefer accessible semantic HTML.
- Use keyboard-friendly interactions wherever possible.
- Ensure visible focus states are present on interactive elements.
- Provide clear feedback for invalid inputs, hints, and completion states.
- Avoid relying solely on color to communicate meaning.

## Testing expectations

- Tests must be maintained throughout development.
- Run the relevant tests after every significant change.
- Do not remove or weaken tests simply to make them pass.
- When a bug is fixed or a feature is added, add or update tests when appropriate.
- Prefer small, targeted tests around logic such as board generation, validation, unique-solution checks, and difficulty behavior.

## Copilot usage guidance

- Treat GitHub Copilot suggestions as drafts, not as final truth.
- Evaluate generated code before accepting it.
- Review for correctness, maintainability, performance, and security.
- Reject suggestions that add unnecessary complexity or obscure logic.
- Keep changes aligned with the project’s goals instead of chasing clever but unrelated improvements.

## Dependency and architecture guidance

- Avoid unnecessary dependencies.
- Avoid unnecessary architectural complexity.
- Prefer a small, understandable solution over a framework-heavy or over-abstracted one.
- Do not introduce large libraries or patterns that are not justified by the project scope.
- Favor incremental progress over broad rewrites.

## Change discipline

- Make changes incrementally.
- Keep each change focused on one purpose.
- Avoid unrelated modifications.
- Do not broaden the scope of a fix just because a nearby area looks messy.
- Maintain a stable, testable path from one step to the next.

## Expected project structure

The project should remain organized and understandable as it evolves. A likely structure is:

```text
project-root/
├── README.md
├── requirements.txt
├── app.py                  # Flask app entry point / route setup
├── sudoku_logic.py         # core Sudoku logic
├── config.py               # optional config settings
├── utils/                  # optional shared utilities
├── models/                 # optional domain models if needed
├── services/               # optional service layer for game operations
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   └── index.html
├── tests/
│   ├── test_app.py
│   ├── test_sudoku_logic.py
│   └── additional tests as needed
└── instruction.md
```

This structure is a guideline, not a requirement to over-engineer. The main priority is clarity, separation of concerns, and maintainability.

## Development workflow

1. Start with the existing behavior and identify the smallest safe improvement.
2. Keep game logic isolated from route and UI code.
3. Add or update tests before or alongside the implementation change when possible.
4. Run the relevant test suite after substantial changes.
5. Review Copilot output critically before accepting it.
6. Keep the codebase readable and focused.
7. Avoid large refactors that mix unrelated concerns.
8. Add features only when they fit the project’s goals and are supported by tests and good design.

## Success criteria

The project should be considered in good shape when:

- puzzle generation is valid and uniquely solvable,
- difficulty settings work consistently,
- locked cells are protected,
- invalid entries are surfaced immediately,
- the UI remains responsive and accessible,
- the logic remains separate from Flask and presentation code,
- tests remain green and continue to protect the codebase,
- the application remains easy to understand and extend.

This project should evolve as a clean, maintainable Flask Sudoku application, not as a fragile legacy app patched without structure or discipline.
