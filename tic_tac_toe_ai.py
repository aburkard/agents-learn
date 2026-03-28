import random
import math

class Board:
    def __init__(self):
        self.grid = [['–'] * 3 for _ in range(3)]
        self.last_human_move = None

    def add_token(self, row, col, token):
        if not (0 <= row < 3 and 0 <= col < 3):
            raise ValueError("Position out of bounds")
        if self.grid[row][col] != '–':
            raise ValueError("Position already occupied")
        self.grid[row][col] = token

    def print_board(self):
        print("  0 1 2")
        for i, row in enumerate(self.grid):
            print(f"{i} {'|'.join(row)}")

    def is_full(self):
        return all(self.grid[r][c] != '–' for r in range(3) for c in range(3))

    def check_winner(self, token):
        g = self.grid
        for i in range(3):
            if g[i][0] == g[i][1] == g[i][2] == token:
                return True
            if g[0][i] == g[1][i] == g[2][i] == token:
                return True
        if g[0][0] == g[1][1] == g[2][2] == token:
            return True
        if g[0][2] == g[1][1] == g[2][0] == token:
            return True
        return False

    def get_empty_cells(self):
        return [(r, c) for r in range(3) for c in range(3) if self.grid[r][c] == '–']


LINES = [
    [(0,0),(0,1),(0,2)], [(1,0),(1,1),(1,2)], [(2,0),(2,1),(2,2)],
    [(0,0),(1,0),(2,0)], [(0,1),(1,1),(2,1)], [(0,2),(1,2),(2,2)],
    [(0,0),(1,1),(2,2)], [(0,2),(1,1),(2,0)],
]


# --- Minimax (Perfect) ---

def minimax(board, is_maximizing):
    if board.check_winner('O'):
        return 1
    if board.check_winner('X'):
        return -1
    if board.is_full():
        return 0
    empty = board.get_empty_cells()
    if is_maximizing:
        best = -2
        for r, c in empty:
            board.grid[r][c] = 'O'
            best = max(best, minimax(board, False))
            board.grid[r][c] = '–'
        return best
    else:
        best = 2
        for r, c in empty:
            board.grid[r][c] = 'X'
            best = min(best, minimax(board, True))
            board.grid[r][c] = '–'
        return best


def ai_minimax(board):
    empty = board.get_empty_cells()
    best_score = -2
    best_move = empty[0]
    for r, c in empty:
        board.grid[r][c] = 'O'
        score = minimax(board, False)
        board.grid[r][c] = '–'
        if score > best_score:
            best_score = score
            best_move = (r, c)
    return best_move


# --- Random ---

def ai_random(board):
    return random.choice(board.get_empty_cells())


# --- Aggressive ---

def ai_aggressive(board):
    empty = board.get_empty_cells()
    # Try to win first
    for r, c in empty:
        board.grid[r][c] = 'O'
        if board.check_winner('O'):
            board.grid[r][c] = '–'
            return (r, c)
        board.grid[r][c] = '–'
    # Try to set up 2-in-a-row (don't bother blocking)
    best = None
    best_score = -1
    for r, c in empty:
        board.grid[r][c] = 'O'
        score = 0
        for line in LINES:
            vals = [board.grid[lr][lc] for lr, lc in line]
            if vals.count('O') == 2 and vals.count('–') == 1:
                score += 1
        board.grid[r][c] = '–'
        if score > best_score:
            best_score = score
            best = (r, c)
    if best and best_score > 0:
        return best
    return random.choice(empty)


# --- Defensive ---

def ai_defensive(board):
    empty = board.get_empty_cells()
    # Win if possible (can't ignore a free win)
    for r, c in empty:
        board.grid[r][c] = 'O'
        if board.check_winner('O'):
            board.grid[r][c] = '–'
            return (r, c)
        board.grid[r][c] = '–'
    # Block opponent wins
    for r, c in empty:
        board.grid[r][c] = 'X'
        if board.check_winner('X'):
            board.grid[r][c] = '–'
            return (r, c)
        board.grid[r][c] = '–'
    # Otherwise pick randomly (no offensive setup)
    return random.choice(empty)


# --- MCTS ---

def mcts_playout(board, starting_player):
    """Play out a random game from the current position, return 1 if O wins, -1 if X wins, 0 draw."""
    # Make a copy
    g = [row[:] for row in board.grid]
    player = starting_player
    while True:
        empty = [(r, c) for r in range(3) for c in range(3) if g[r][c] == '–']
        if not empty:
            return 0
        r, c = random.choice(empty)
        g[r][c] = player
        # Check win
        for line in LINES:
            vals = [g[lr][lc] for lr, lc in line]
            if vals[0] == vals[1] == vals[2] == player:
                return 1 if player == 'O' else -1
        player = 'X' if player == 'O' else 'O'


def ai_mcts(board, n_playouts=1000):
    empty = board.get_empty_cells()
    best_move = empty[0]
    best_score = -float('inf')
    for r, c in empty:
        board.grid[r][c] = 'O'
        # Check immediate win
        if board.check_winner('O'):
            board.grid[r][c] = '–'
            return (r, c)
        wins = 0
        for _ in range(n_playouts):
            result = mcts_playout(board, 'X')
            wins += result
        board.grid[r][c] = '–'
        if wins > best_score:
            best_score = wins
            best_move = (r, c)
    return best_move


# --- Neural Network (simulated) ---

def nn_evaluate(board, token):
    """Heuristic evaluation using weighted position scoring."""
    opponent = 'X' if token == 'O' else 'O'
    g = board.grid

    # Position weights: center > corners > edges
    pos_weight = {
        (0,0): 3, (0,2): 3, (2,0): 3, (2,2): 3,
        (1,1): 4,
        (0,1): 2, (1,0): 2, (1,2): 2, (2,1): 2,
    }

    score = 0.0
    # Material score
    for r in range(3):
        for c in range(3):
            if g[r][c] == token:
                score += pos_weight[(r, c)]
            elif g[r][c] == opponent:
                score -= pos_weight[(r, c)]

    # Line connectivity bonuses
    for line in LINES:
        vals = [g[r][c] for r, c in line]
        own = vals.count(token)
        opp = vals.count(opponent)
        if opp == 0:
            if own == 2:
                score += 10
            elif own == 1:
                score += 1
        if own == 0:
            if opp == 2:
                score -= 8  # slightly less weight on defense for beatable feel
            elif opp == 1:
                score -= 0.5

    # Win/loss
    if board.check_winner(token):
        score += 100
    if board.check_winner(opponent):
        score -= 100

    return score


def ai_neural(board):
    empty = board.get_empty_cells()
    best_move = empty[0]
    best_score = -float('inf')
    for r, c in empty:
        board.grid[r][c] = 'O'
        # Check immediate win
        if board.check_winner('O'):
            board.grid[r][c] = '–'
            return (r, c)
        score = nn_evaluate(board, 'O')
        # Add a tiny bit of randomness for variety
        score += random.uniform(-0.5, 0.5)
        board.grid[r][c] = '–'
        if score > best_score:
            best_score = score
            best_move = (r, c)
    return best_move


# --- Chaos ---

def ai_chaos(board):
    if random.random() < 0.3:
        return ai_minimax(board)
    else:
        return ai_random(board)


# --- Mirror ---

def ai_mirror(board):
    empty = board.get_empty_cells()

    if board.last_human_move is not None:
        r, c = board.last_human_move
        # Try several mirror/rotation transforms
        transforms = [
            (2 - r, 2 - c),      # 180-degree rotation
            (c, r),               # reflect over main diagonal
            (2 - c, 2 - r),      # reflect over anti-diagonal
            (r, 2 - c),          # horizontal mirror
            (2 - r, c),          # vertical mirror
        ]
        for tr, tc in transforms:
            if (tr, tc) in empty:
                return (tr, tc)

    # Fallback: random
    return random.choice(empty)


# --- Strategy registry ---

STRATEGIES = [
    ("Minimax (Perfect)", "Unbeatable. Uses full game-tree search.", ai_minimax),
    ("Random", "Picks a random legal move. Easy to beat.", ai_random),
    ("Aggressive", "Hunts for wins but forgets to block you.", ai_aggressive),
    ("Defensive", "Blocks every threat but never sets up its own attack.", ai_defensive),
    ("MCTS (1000 playouts)", "Monte Carlo Tree Search. Strong but occasionally beatable.", lambda b: ai_mcts(b, 1000)),
    ("Neural Network (simulated)", "Weight-based evaluation. Medium difficulty.", ai_neural),
    ("Chaos", "70% random, 30% perfect. Unpredictable.", ai_chaos),
    ("Mirror", "Copies your moves with symmetry. Falls back to random.", ai_mirror),
]


def main():
    print("\n=== Tic Tac Toe — AI Selector ===\n")
    for i, (name, desc, _) in enumerate(STRATEGIES):
        print(f"  {i}. {name}")
        print(f"     {desc}")
    print()

    # Select AI
    while True:
        try:
            choice = input(f"Pick an AI [0-{len(STRATEGIES)-1}]: ").strip()
            idx = int(choice)
            if 0 <= idx < len(STRATEGIES):
                break
            print("Out of range.")
        except EOFError:
            return
        except ValueError:
            print("Enter a number.")

    name, desc, ai_func = STRATEGIES[idx]
    print(f"\nPlaying against: {name}")
    print(f"  {desc}\n")

    board = Board()
    board.print_board()

    while True:
        # Human move (X)
        while True:
            try:
                move = input("Enter your move (row col, 0-indexed): ")
                parts = move.split()
                if len(parts) != 2:
                    raise ValueError
                row, col = int(parts[0]), int(parts[1])
                board.add_token(row, col, 'X')
                board.last_human_move = (row, col)
                break
            except EOFError:
                return
            except (ValueError, IndexError):
                print("Invalid move. Try again.")

        board.print_board()

        if board.check_winner('X'):
            print("You win!")
            break
        if board.is_full():
            print("It's a draw!")
            break

        # AI move
        r, c = ai_func(board)
        board.add_token(r, c, 'O')
        print(f"AI plays: {r} {c}")
        board.print_board()

        if board.check_winner('O'):
            print("AI wins!")
            break
        if board.is_full():
            print("It's a draw!")
            break


if __name__ == '__main__':
    main()
