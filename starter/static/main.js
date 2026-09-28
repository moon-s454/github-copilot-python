// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const THEME_STORAGE_KEY = 'sudoku-theme';
let puzzle = [];
let hintsUsed = 0;
let timerIntervalId = null;
let elapsedSeconds = 0;
let finalElapsedSeconds = 0;
let leaderboardScoreRecorded = false;

function getSafeTheme(themeValue) {
  if (themeValue === 'dark' || themeValue === 'light') {
    return themeValue;
  }
  return 'light';
}

function applyTheme(themeValue) {
  const safeTheme = getSafeTheme(themeValue);
  document.documentElement.setAttribute('data-theme', safeTheme);

  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    const isDarkTheme = safeTheme === 'dark';
    themeToggle.setAttribute('aria-pressed', String(isDarkTheme));
    themeToggle.textContent = isDarkTheme ? 'Light mode' : 'Dark mode';
    themeToggle.setAttribute('aria-label', isDarkTheme ? 'Switch to light mode' : 'Switch to dark mode');
  }
}

function initializeTheme() {
  let savedTheme = 'light';

  try {
    const storedTheme = window.localStorage.getItem(THEME_STORAGE_KEY);
    if (storedTheme) {
      savedTheme = getSafeTheme(storedTheme);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      savedTheme = 'dark';
    }
  } catch (error) {
    savedTheme = 'light';
  }

  applyTheme(savedTheme);

  try {
    window.localStorage.setItem(THEME_STORAGE_KEY, savedTheme);
  } catch (error) {
    // Ignore storage issues gracefully and continue with in-memory theme state.
  }
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
  applyTheme(nextTheme);

  try {
    window.localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
  } catch (error) {
    // Ignore storage issues gracefully and continue with in-memory theme state.
  }
}

function renderTimer() {
  const timerDisplay = document.getElementById('timer-display');
  if (!timerDisplay) {
    return;
  }
  timerDisplay.textContent = TimerUtils.formatTime(elapsedSeconds);
}

function clearTimer() {
  if (timerIntervalId !== null) {
    clearInterval(timerIntervalId);
    timerIntervalId = null;
  }
}

function stopTimer() {
  clearTimer();
  finalElapsedSeconds = elapsedSeconds;
}

function startTimer() {
  clearTimer();
  elapsedSeconds = 0;
  finalElapsedSeconds = 0;
  leaderboardScoreRecorded = false;
  renderTimer();
  timerIntervalId = setInterval(() => {
    elapsedSeconds += 1;
    finalElapsedSeconds = elapsedSeconds;
    renderTimer();
  }, 1000);
}

function getCurrentDifficulty() {
  const selector = document.getElementById('difficulty-select');
  return selector ? selector.value : 'medium';
}

function renderLeaderboard(scores) {
  const leaderboardList = document.getElementById('leaderboard-list');
  if (!leaderboardList) {
    return;
  }
  leaderboardList.innerHTML = '';
  if (!Array.isArray(scores) || scores.length === 0) {
    const emptyItem = document.createElement('li');
    emptyItem.className = 'leaderboard-empty';
    emptyItem.textContent = 'No completed games yet.';
    leaderboardList.appendChild(emptyItem);
    return;
  }

  scores.forEach((entry, index) => {
    const item = document.createElement('li');
    const details = document.createElement('span');
    const safeName = LeaderboardUtils.sanitizeName(entry.name);
    details.textContent = `${index + 1}. ${safeName} — ${entry.completionTime} — ${entry.difficulty} — Hints: ${entry.hintsUsed}`;
    item.appendChild(details);
    leaderboardList.appendChild(item);
  });
}

function loadLeaderboard() {
  const leaderboard = LeaderboardUtils.readLeaderboard();
  renderLeaderboard(leaderboard);
}

function recordCompletedGame() {
  if (leaderboardScoreRecorded) {
    return;
  }

  const enteredName = typeof window !== 'undefined' && typeof window.prompt === 'function'
    ? window.prompt('Enter your name for the leaderboard:', '')
    : null;

  const difficulty = getCurrentDifficulty();
  const score = LeaderboardUtils.createScore({
    name: enteredName,
    completionSeconds: Math.max(0, Number.isInteger(finalElapsedSeconds) ? finalElapsedSeconds : 0),
    completionTime: TimerUtils.formatTime(finalElapsedSeconds),
    difficulty,
    hintsUsed: Number.isInteger(hintsUsed) ? hintsUsed : 0,
  });

  const updatedLeaderboard = LeaderboardUtils.addScore(score);
  renderLeaderboard(updatedLeaderboard);
  leaderboardScoreRecorded = true;
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      const blockRow = Math.floor(i / 3);
      const blockCol = Math.floor(j / 3);
      const blockClass = (blockRow + blockCol) % 2 === 0 ? 'block-light' : 'block-dark';
      input.type = 'text';
      input.maxLength = 1;
      input.className = `sudoku-cell ${blockClass}`;
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.classList.add('prefilled');
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

async function newGame() {
  clearTimer();
  leaderboardScoreRecorded = false;
  const difficulty = document.getElementById('difficulty-select').value;
  const res = await fetch('/new?difficulty=' + encodeURIComponent(difficulty));
  const data = await res.json();
  if (data.error) {
    const msg = document.getElementById('message');
    msg.textContent = data.error;
    msg.style.color = '#d32f2f';
    return;
  }
  renderPuzzle(data.puzzle);
  document.getElementById('message').textContent = '';
  startTimer();
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.textContent = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0] * SIZE + x[1]));
  const boardIsFilled = board.every((row) => row.every((cell) => Number.isInteger(cell) && cell > 0));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = `sudoku-cell ${(Math.floor(Math.floor(idx / SIZE) / 3) + Math.floor((idx % SIZE) / 3)) % 2 === 0 ? 'block-light' : 'block-dark'}`;
    if (incorrect.has(idx)) {
      inp.classList.add('incorrect');
    }
  }
  if (boardIsFilled && TimerUtils.shouldStopTimer(board, data.incorrect)) {
    stopTimer();
    recordCompletedGame();
    msg.style.color = '#388e3c';
    msg.textContent = 'Congratulations! You solved it!';
  } else if (boardIsFilled) {
    msg.style.color = '#d32f2f';
    msg.textContent = 'Some cells are incorrect.';
  } else {
    msg.style.color = '#d32f2f';
    msg.textContent = 'Board is not complete yet.';
  }
}

async function requestHint() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }

  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.textContent = data.error;
    return;
  }

  const idx = data.row * SIZE + data.col;
  const boardInputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const inp = boardInputs[idx];
  inp.value = data.value;
  inp.disabled = true;
  inp.className = `sudoku-cell ${(Math.floor(data.row / 3) + Math.floor(data.col / 3)) % 2 === 0 ? 'block-light' : 'block-dark'} hinted`;

  hintsUsed = data.hints_used || (hintsUsed + 1);
  document.getElementById('hints-used').textContent = 'Hints: ' + hintsUsed;
  msg.style.color = '#333';
  msg.textContent = 'A hint was provided.';
}

// Wire buttons
window.addEventListener('load', () => {
  initializeTheme();
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
  }
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint').addEventListener('click', requestHint);
  loadLeaderboard();
  renderTimer();
  newGame();
});