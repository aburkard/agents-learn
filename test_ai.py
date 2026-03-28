"""Exhaustive test: play every possible game where X goes first. The minimax AI (O) should never lose."""
from tic_tac_toe import Board, ai_move

stats = {'x_wins': 0, 'o_wins': 0, 'draws': 0, 'games': 0}


def play_all_games(board, is_human_turn):
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
        # Try every possible human move
        for r, c in board.get_empty_cells():
            board.grid[r][c] = 'X'
            play_all_games(board, False)
            board.grid[r][c] = '–'
    else:
        # AI picks its move via minimax
        r, c = ai_move(board)
        board.grid[r][c] = 'O'
        play_all_games(board, True)
        board.grid[r][c] = '–'


board = Board()
play_all_games(board, True)

print(f"Total games played: {stats['games']}")
print(f"X wins: {stats['x_wins']}")
print(f"O wins: {stats['o_wins']}")
print(f"Draws:  {stats['draws']}")

assert stats['x_wins'] == 0, f"AI lost {stats['x_wins']} games!"
print("\nPASSED: AI never loses across all possible games.")
