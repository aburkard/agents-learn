"""
pytest test suite for tic_tac_toe_ai.py

Covers:
  - Board class behaviour
  - Every AI strategy: returns a valid move, never crashes on edge cases
  - Minimax correctness: exhaustive proof the AI never loses
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tic_tac_toe_ai import (
    Board,
    ai_minimax,
    ai_random,
    ai_aggressive,
    ai_defensive,
    ai_mcts,
    ai_neural,
    ai_chaos,
    ai_mirror,
    STRATEGIES,
)

EMPTY = '–'


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_board(grid):
    """Build a Board whose grid matches the provided list-of-lists."""
    b = Board()
    b.grid = [row[:] for row in grid]
    return b


def is_valid_move(board, move):
    r, c = move
    return 0 <= r < 3 and 0 <= c < 3 and board.grid[r][c] == EMPTY


# ---------------------------------------------------------------------------
# Board unit tests
# ---------------------------------------------------------------------------

class TestBoard:
    def test_initial_state_is_empty(self):
        b = Board()
        assert b.get_empty_cells() == [(r, c) for r in range(3) for c in range(3)]

    def test_add_token(self):
        b = Board()
        b.add_token(1, 1, 'X')
        assert b.grid[1][1] == 'X'

    def test_add_token_out_of_bounds_raises(self):
        b = Board()
        with pytest.raises(ValueError):
            b.add_token(3, 0, 'X')

    def test_add_token_occupied_raises(self):
        b = Board()
        b.add_token(0, 0, 'X')
        with pytest.raises(ValueError):
            b.add_token(0, 0, 'O')

    def test_check_winner_row(self):
        b = make_board([
            ['X', 'X', 'X'],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
        ])
        assert b.check_winner('X')
        assert not b.check_winner('O')

    def test_check_winner_col(self):
        b = make_board([
            ['O', EMPTY, EMPTY],
            ['O', EMPTY, EMPTY],
            ['O', EMPTY, EMPTY],
        ])
        assert b.check_winner('O')

    def test_check_winner_diag(self):
        b = make_board([
            ['X', EMPTY, EMPTY],
            [EMPTY, 'X', EMPTY],
            [EMPTY, EMPTY, 'X'],
        ])
        assert b.check_winner('X')

    def test_check_winner_anti_diag(self):
        b = make_board([
            [EMPTY, EMPTY, 'O'],
            [EMPTY, 'O', EMPTY],
            ['O', EMPTY, EMPTY],
        ])
        assert b.check_winner('O')

    def test_no_winner_on_empty_board(self):
        b = Board()
        assert not b.check_winner('X')
        assert not b.check_winner('O')

    def test_is_full(self):
        b = make_board([
            ['X', 'O', 'X'],
            ['O', 'X', 'O'],
            ['O', 'X', 'O'],
        ])
        assert b.is_full()

    def test_not_full(self):
        b = Board()
        assert not b.is_full()

    def test_get_empty_cells_count(self):
        b = make_board([
            ['X', EMPTY, EMPTY],
            [EMPTY, 'O', EMPTY],
            [EMPTY, EMPTY, EMPTY],
        ])
        assert len(b.get_empty_cells()) == 7


# ---------------------------------------------------------------------------
# Parametrized: every AI must return a valid move on various board states
# ---------------------------------------------------------------------------

ALL_AI_FUNCS = [ai_minimax, ai_random, ai_aggressive, ai_defensive,
                ai_neural, ai_chaos, ai_mirror]

# ai_mcts is slow so we use a minimal playout count in tests
def ai_mcts_fast(board):
    return ai_mcts(board, n_playouts=20)

ALL_AI_FUNCS_WITH_MCTS = ALL_AI_FUNCS + [ai_mcts_fast]

BOARD_STATES = [
    # Empty board
    [[EMPTY]*3 for _ in range(3)],
    # One move played
    [['X', EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY]],
    # Mid-game board
    [['X', 'O', EMPTY], [EMPTY, 'X', EMPTY], [EMPTY, EMPTY, EMPTY]],
    # Only one cell left
    [['X', 'O', 'X'], ['O', 'X', 'O'], [EMPTY, 'X', 'O']],
]


@pytest.mark.parametrize("ai_func", ALL_AI_FUNCS_WITH_MCTS,
                         ids=[f.__name__ for f in ALL_AI_FUNCS_WITH_MCTS])
@pytest.mark.parametrize("grid", BOARD_STATES)
def test_ai_returns_valid_move(ai_func, grid):
    b = make_board(grid)
    move = ai_func(b)
    assert is_valid_move(b, move), f"{ai_func.__name__} returned invalid move {move}"


# ---------------------------------------------------------------------------
# Every AI must immediately take a winning move when available
# ---------------------------------------------------------------------------

WINNING_BOARD = make_board([
    ['O', 'O', EMPTY],
    ['X', 'X', EMPTY],
    [EMPTY, EMPTY, EMPTY],
])

@pytest.mark.parametrize("ai_func", [ai_minimax, ai_aggressive, ai_defensive, ai_neural],
                         ids=["minimax", "aggressive", "defensive", "neural"])
def test_ai_takes_immediate_win(ai_func):
    b = make_board([
        ['O', 'O', EMPTY],
        ['X', 'X', EMPTY],
        [EMPTY, EMPTY, EMPTY],
    ])
    r, c = ai_func(b)
    b.grid[r][c] = 'O'
    assert b.check_winner('O'), f"{ai_func.__name__} missed a winning move"


# ---------------------------------------------------------------------------
# Defensive AI must block an immediate opponent win
# ---------------------------------------------------------------------------

def test_defensive_blocks_immediate_threat():
    b = make_board([
        ['X', 'X', EMPTY],
        ['O', EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY],
    ])
    r, c = ai_defensive(b)
    assert (r, c) == (0, 2), f"defensive AI should block (0,2), got ({r},{c})"


def test_minimax_blocks_immediate_threat():
    b = make_board([
        ['X', 'X', EMPTY],
        ['O', EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY],
    ])
    r, c = ai_minimax(b)
    assert (r, c) == (0, 2), f"minimax should block (0,2), got ({r},{c})"


# ---------------------------------------------------------------------------
# Minimax correctness: exhaustive game-tree proof the AI never loses
# ---------------------------------------------------------------------------

def _play_all_games(board, is_human_turn, stats):
    if board.check_winner('X'):
        stats['x_wins'] += 1
        stats['games'] += 1
        return
    if board.check_winner('O'):
        stats['o_wins'] += 1
        stats['games'] += 1
        return
    if board.is_full():
        stats['draws'] += 1
        stats['games'] += 1
        return

    if is_human_turn:
        for r, c in board.get_empty_cells():
            board.grid[r][c] = 'X'
            _play_all_games(board, False, stats)
            board.grid[r][c] = EMPTY
    else:
        r, c = ai_minimax(board)
        board.grid[r][c] = 'O'
        _play_all_games(board, True, stats)
        board.grid[r][c] = EMPTY


def test_minimax_never_loses():
    stats = {'x_wins': 0, 'o_wins': 0, 'draws': 0, 'games': 0}
    board = Board()
    _play_all_games(board, True, stats)
    assert stats['games'] > 0, "No games were played"
    assert stats['x_wins'] == 0, f"Minimax lost {stats['x_wins']} game(s)!"


# ---------------------------------------------------------------------------
# STRATEGIES registry sanity
# ---------------------------------------------------------------------------

def test_strategies_registry_format():
    for entry in STRATEGIES:
        name, desc, func = entry
        assert isinstance(name, str) and len(name) > 0
        assert isinstance(desc, str) and len(desc) > 0
        assert callable(func)


def test_strategies_registry_all_return_valid_moves():
    b = Board()  # empty board — every AI should handle it
    for name, desc, func in STRATEGIES:
        move = func(b)
        assert is_valid_move(b, move), f"STRATEGIES entry '{name}' returned invalid move {move}"
