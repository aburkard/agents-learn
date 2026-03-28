class Board:
    def __init__(self):
        self.grid = [['–'] * 3 for _ in range(3)]

    def add_token(self, row, col, token):
        if not (0 <= row < 3 and 0 <= col < 3):
            raise ValueError("Position out of bounds")
        if self.grid[row][col] != '–':
            raise ValueError("Position already occupied")
        self.grid[row][col] = token

    def print_board(self):
        for row in self.grid:
            print('|'.join(row))

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


def ai_move(board):
    empty = board.get_empty_cells()
    if not empty:
        raise RuntimeError("No legal move exists")

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


def main():
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

        # AI move (O)
        r, c = ai_move(board)
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
