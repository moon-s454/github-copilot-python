(function (root, factory) {
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = factory();
  } else {
    root.LeaderboardUtils = factory();
  }
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  const STORAGE_KEY = 'sudoku-leaderboard-v1';
  const VALID_DIFFICULTIES = new Set(['easy', 'medium', 'hard']);

  function sanitizeName(value) {
    if (typeof value !== 'string') {
      return 'Anonymous';
    }
    const trimmed = value.trim();
    return trimmed || 'Anonymous';
  }

  function clampNonNegativeInteger(value, fallback = 0) {
    if (typeof value === 'number' && Number.isInteger(value)) {
      return Math.max(0, value);
    }
    if (typeof value === 'string' && value.trim() !== '') {
      const parsed = Number(value);
      if (Number.isInteger(parsed) && parsed >= 0) {
        return parsed;
      }
    }
    return fallback;
  }

  function isValidScore(score) {
    if (!score || typeof score !== 'object' || Array.isArray(score)) {
      return false;
    }

    if (typeof score.name !== 'string' || !score.name.trim()) {
      return false;
    }

    if (!Number.isInteger(score.completionSeconds) || score.completionSeconds < 0) {
      return false;
    }

    if (typeof score.completionTime !== 'string' || !score.completionTime.trim()) {
      return false;
    }

    if (!VALID_DIFFICULTIES.has(score.difficulty)) {
      return false;
    }

    if (!Number.isInteger(score.hintsUsed) || score.hintsUsed < 0) {
      return false;
    }

    return true;
  }

  function createScore(score) {
    const raw = score && typeof score === 'object' ? score : {};
    const completionSeconds = Number.isInteger(raw.completionSeconds) && raw.completionSeconds >= 0
      ? raw.completionSeconds
      : clampNonNegativeInteger(raw.completionSeconds, 0);
    const difficulty = VALID_DIFFICULTIES.has(raw.difficulty) ? raw.difficulty : 'easy';
    const hintsUsed = Number.isInteger(raw.hintsUsed) && raw.hintsUsed >= 0
      ? raw.hintsUsed
      : clampNonNegativeInteger(raw.hintsUsed, 0);
    const formattedTime = typeof raw.completionTime === 'string' && raw.completionTime.trim()
      ? raw.completionTime.trim()
      : ((typeof TimerUtils !== 'undefined' && TimerUtils.formatTime)
        ? TimerUtils.formatTime(completionSeconds)
        : '00:00');

    return {
      name: sanitizeName(raw.name),
      completionSeconds,
      completionTime: formattedTime,
      difficulty,
      hintsUsed,
    };
  }

  function normalizeLeaderboard(rawScores) {
    if (!Array.isArray(rawScores)) {
      return [];
    }

    const normalized = rawScores
      .map((entry) => {
        if (!entry || typeof entry !== 'object' || Array.isArray(entry)) {
          return null;
        }

        const candidate = {
          name: sanitizeName(entry.name),
          completionSeconds: Number.isInteger(entry.completionSeconds) && entry.completionSeconds >= 0
            ? entry.completionSeconds
            : null,
          completionTime: typeof entry.completionTime === 'string' ? entry.completionTime.trim() : '',
          difficulty: VALID_DIFFICULTIES.has(entry.difficulty) ? entry.difficulty : null,
          hintsUsed: Number.isInteger(entry.hintsUsed) && entry.hintsUsed >= 0
            ? entry.hintsUsed
            : null,
        };

        return isValidScore(candidate) ? candidate : null;
      })
      .filter(Boolean);

    return sortLeaderboard(normalized);
  }

  function sortLeaderboard(scores) {
    return [...scores].sort((left, right) => {
      if (left.completionSeconds !== right.completionSeconds) {
        return left.completionSeconds - right.completionSeconds;
      }
      if (left.hintsUsed !== right.hintsUsed) {
        return left.hintsUsed - right.hintsUsed;
      }
      return left.name.localeCompare(right.name);
    });
  }

  function limitLeaderboard(scores, maxEntries = 10) {
    return sortLeaderboard(scores).slice(0, maxEntries);
  }

  function getStorage() {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        return window.localStorage;
      }
    } catch (error) {
      return null;
    }
    return null;
  }

  function readLeaderboard(storage = getStorage(), key = STORAGE_KEY) {
    if (!storage || typeof storage.getItem !== 'function') {
      return [];
    }

    try {
      const rawValue = storage.getItem(key);
      if (rawValue === null) {
        return [];
      }
      const parsed = JSON.parse(rawValue);
      return normalizeLeaderboard(parsed);
    } catch (error) {
      return [];
    }
  }

  function writeLeaderboard(storage = getStorage(), key = STORAGE_KEY, scores = []) {
    if (!storage || typeof storage.setItem !== 'function') {
      return false;
    }

    try {
      storage.setItem(key, JSON.stringify(limitLeaderboard(scores, 10)));
      return true;
    } catch (error) {
      return false;
    }
  }

  function addScore(score, storage = getStorage(), key = STORAGE_KEY) {
    const safeScore = createScore(score);
    const nextScores = sortLeaderboard([
      ...readLeaderboard(storage, key),
      safeScore,
    ]);
    const finalScores = limitLeaderboard(nextScores, 10);
    writeLeaderboard(storage, key, finalScores);
    return finalScores;
  }

  return {
    STORAGE_KEY,
    VALID_DIFFICULTIES,
    sanitizeName,
    clampNonNegativeInteger,
    isValidScore,
    createScore,
    normalizeLeaderboard,
    sortLeaderboard,
    limitLeaderboard,
    getStorage,
    readLeaderboard,
    writeLeaderboard,
    addScore,
  };
}));
