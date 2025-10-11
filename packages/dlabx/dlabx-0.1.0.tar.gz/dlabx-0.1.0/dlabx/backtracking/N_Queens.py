# ----------- N-Queens Problem -----------

def N_Queens(n):
    def is_safe(row, col):
        for r in range(row):
            if cols[r] == col or abs(cols[r] - col) == abs(r - row):
                return False
        return True

    def backtrack(row):
        if row == n:
            solution = []
            for r in range(n):
                row_str = ['.'] * n
                row_str[cols[r]] = 'Q'
                solution.append(''.join(row_str))
            solutions.append(solution)
            return
        for col in range(n):
            if is_safe(row, col):
                cols[row] = col
                backtrack(row + 1)

    solutions = []
    cols = [-1] * n
    backtrack(0)
    return solutions