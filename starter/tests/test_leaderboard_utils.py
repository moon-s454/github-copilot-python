import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
JS_FILE = ROOT / 'static' / 'leaderboard_utils.js'


def run_node(script: str):
    result = subprocess.run(
        ['node', '-e', script],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr or result.stdout)


def test_score_creation_and_name_sanitization():
    script = f"""
const {{ createScore, sanitizeName, isValidScore }} = require({str(JS_FILE)!r});
assert(sanitizeName('  Alice  ') === 'Alice');
assert(sanitizeName('   ') === 'Anonymous');
assert(sanitizeName(null) === 'Anonymous');
const score = createScore({{ name: '  Bob  ', completionSeconds: 42, completionTime: '00:42', difficulty: 'easy', hintsUsed: 2 }});
assert(score.name === 'Bob');
assert(score.completionSeconds === 42);
assert(score.completionTime === '00:42');
assert(score.difficulty === 'easy');
assert(score.hintsUsed === 2);
assert(isValidScore(score) === true);
"""
    run_node(script)


def test_sorts_fastest_first_and_limits_to_ten():
    script = f"""
const {{ normalizeLeaderboard, sortLeaderboard, limitLeaderboard }} = require({str(JS_FILE)!r});
const data = [
  {{ name: 'slow', completionSeconds: 120, completionTime: '02:00', difficulty: 'hard', hintsUsed: 1 }},
  {{ name: 'fast', completionSeconds: 45, completionTime: '00:45', difficulty: 'medium', hintsUsed: 0 }},
  {{ name: 'middle', completionSeconds: 78, completionTime: '01:18', difficulty: 'easy', hintsUsed: 3 }},
  {{ name: 'fast2', completionSeconds: 30, completionTime: '00:30', difficulty: 'easy', hintsUsed: 0 }},
];
const sorted = sortLeaderboard(data);
assert(sorted[0].name === 'fast2');
assert(sorted[1].name === 'fast');
assert(sorted[2].name === 'middle');
const many = Array.from({{ length: 12 }}, (_, i) => ({{
  name: 'player-' + i,
  completionSeconds: 100 + i,
  completionTime: '00:' + String(100 + i).padStart(2, '0'),
  difficulty: 'medium',
  hintsUsed: 0,
}}));
assert(limitLeaderboard(many).length === 10);
assert(limitLeaderboard(many)[0].completionSeconds === 100);
assert(normalizeLeaderboard([{{ name: 'ok', completionSeconds: 10, completionTime: '00:10', difficulty: 'hard', hintsUsed: 0 }}, 'bad']).length === 1);
"""
    run_node(script)


def test_invalid_scores_and_malformed_storage_are_rejected():
    script = f"""
const {{ isValidScore, normalizeLeaderboard, readLeaderboard }} = require({str(JS_FILE)!r});
assert(isValidScore({{}}) === false);
assert(isValidScore({{ name: 'X', completionSeconds: -1, completionTime: '00:10', difficulty: 'easy', hintsUsed: 0 }}) === false);
assert(isValidScore({{ name: 'X', completionSeconds: 15, completionTime: '00:15', difficulty: 'expert', hintsUsed: 0 }}) === false);
const raw = [
  {{ name: 'valid', completionSeconds: 20, completionTime: '00:20', difficulty: 'medium', hintsUsed: 1 }},
  null,
  'bad score',
  {{ name: 'bad time', completionSeconds: 'oops', completionTime: '00:10', difficulty: 'easy', hintsUsed: 0 }},
];
assert(normalizeLeaderboard(raw).length === 1);
const fakeStorage = {{
  getItem: () => '{{not JSON}}',
  setItem: () => undefined,
}};
assert(readLeaderboard(fakeStorage).length === 0);
"""
    run_node(script)


def test_storage_round_trip_and_difficulty_hints_are_preserved():
    script = f"""
const {{ createScore, addScore, readLeaderboard, writeLeaderboard, STORAGE_KEY }} = require({str(JS_FILE)!r});
const storage = {{
  data: {{}} ,
  getItem(key) {{ return Object.prototype.hasOwnProperty.call(this.data, key) ? this.data[key] : null; }},
  setItem(key, value) {{ this.data[key] = String(value); }},
}};
const score = createScore({{ name: '  Zoe  ', completionSeconds: 54, completionTime: '00:54', difficulty: 'hard', hintsUsed: 3 }});
const updated = addScore(score, storage, STORAGE_KEY);
assert(updated.length === 1);
assert(updated[0].name === 'Zoe');
assert(updated[0].difficulty === 'hard');
assert(updated[0].hintsUsed === 3);
const reloaded = readLeaderboard(storage, STORAGE_KEY);
assert(reloaded.length === 1);
assert(reloaded[0].completionSeconds === 54);
writeLeaderboard(storage, STORAGE_KEY, [score, score]);
assert(readLeaderboard(storage, STORAGE_KEY).length === 2);
"""
    run_node(script)
