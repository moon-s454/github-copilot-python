import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_timer_helpers_require_complete_board_before_success():
    script = """
const utils = require('./static/timer_utils.js');
const { formatTime, isBoardComplete, shouldStopTimer } = utils;

assert(formatTime(0) === '00:00');
assert(formatTime(65) === '01:05');
assert(formatTime(3599) === '59:59');

assert(isBoardComplete([[5,1,2,4,3,6,7,8,9],[3,4,5,8,7,9,1,2,6],[8,6,7,1,2,5,4,3,0],[2,8,9,7,6,1,3,4,5],[4,3,1,9,5,8,6,7,2],[7,5,6,3,4,2,9,1,8],[1,7,3,5,8,4,2,6,9],[6,2,4,9,1,7,8,5,3],[9,5,8,2,6,3,0,9,1]]) === false);
assert(isBoardComplete([
  [5,1,2,4,3,6,7,8,9],
  [3,4,5,8,7,9,1,2,6],
  [8,6,7,1,2,5,4,3,1],
  [2,8,9,7,6,1,3,4,5],
  [4,3,1,9,5,8,6,7,2],
  [7,5,6,3,4,2,9,1,8],
  [1,7,3,5,8,4,2,6,9],
  [6,2,4,9,1,7,8,5,3],
  [9,5,8,2,6,3,1,4,7],
]) === true);

assert(shouldStopTimer([[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9]], []) === true);
assert(shouldStopTimer([[1,2,3,4,5,6,7,8,0],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9]], []) === false);
assert(shouldStopTimer([[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9]], [[0,0]]) === false);
"""
    result = subprocess.run(
        [sys.executable, '-c', 'import os, subprocess, sys; print("run")'],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    # Use node directly so the test is independent from the Python runtime.
    result = subprocess.run(
        ["node", "-e", script],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr or result.stdout)
