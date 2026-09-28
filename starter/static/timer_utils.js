(function (root, factory) {
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = factory();
  } else {
    root.TimerUtils = factory();
  }
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  function formatTime(totalSeconds) {
    const safeSeconds = Number.isFinite(totalSeconds) ? Math.max(0, Math.floor(totalSeconds)) : 0;
    const minutes = Math.floor(safeSeconds / 60);
    const seconds = safeSeconds % 60;
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  }

  function isBoardComplete(board) {
    if (!Array.isArray(board) || board.length !== 9) {
      return false;
    }

    for (let row = 0; row < 9; row += 1) {
      if (!Array.isArray(board[row]) || board[row].length !== 9) {
        return false;
      }

      for (let col = 0; col < 9; col += 1) {
        const value = board[row][col];
        if (!Number.isInteger(value) || value < 1 || value > 9) {
          return false;
        }
      }
    }

    return true;
  }

  function shouldStopTimer(board, incorrectCells) {
    if (!isBoardComplete(board)) {
      return false;
    }

    if (!Array.isArray(incorrectCells)) {
      return false;
    }

    return incorrectCells.length === 0;
  }

  return {
    formatTime,
    isBoardComplete,
    shouldStopTimer,
  };
}));
