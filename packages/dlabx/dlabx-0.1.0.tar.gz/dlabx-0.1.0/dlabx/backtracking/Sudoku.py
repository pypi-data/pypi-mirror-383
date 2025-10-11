# ----------- Generalized Sudoku Solver (No math import) -----------
def Sudoku(board):
    n = len(board)

    # Compute subgrid size manually
    subgrid_size = 1
    while subgrid_size * subgrid_size < n:
        subgrid_size += 1

    def is_valid(r, c, val):
        # Check row and column
        for i in range(n):
            if board[r][i] == val or board[i][c] == val:
                return False
        # Check subgrid
        start_row, start_col = r - r % subgrid_size, c - c % subgrid_size
        for i in range(start_row, start_row + subgrid_size):
            for j in range(start_col, start_col + subgrid_size):
                if board[i][j] == val:
                    return False
        return True

    def dfs():
        for r in range(n):
            for c in range(n):
                if board[r][c] == 0:
                    for num in range(1, n + 1):
                        if is_valid(r, c, num):
                            board[r][c] = num
                            if dfs():
                                return True
                            board[r][c] = 0
                    return False
        return True

    dfs()
    return board
