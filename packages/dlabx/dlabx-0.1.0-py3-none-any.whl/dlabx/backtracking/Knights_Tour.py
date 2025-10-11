def Knights_Tour(n):
    board = [[-1]*n for _ in range(n)]
    moves = [(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2),(2,-1)]

    def is_valid(x, y):
        return 0 <= x < n and 0 <= y < n and board[x][y] == -1

    def backtrack(x, y, move_i):
        if move_i == n*n:
            return True
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if is_valid(nx, ny):
                board[nx][ny] = move_i
                if backtrack(nx, ny, move_i + 1):
                    return True
                board[nx][ny] = -1
        return False

    # Try all starting positions
    for i in range(n):
        for j in range(n):
            board[i][j] = 0
            if backtrack(i, j, 1):
                return board
            board[i][j] = -1
    return []