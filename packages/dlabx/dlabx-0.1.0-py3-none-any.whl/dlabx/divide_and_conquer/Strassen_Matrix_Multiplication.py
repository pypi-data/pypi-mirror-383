
# ----------- Matrix Multiplication -----------

def Strassen_Matrix_Multiplication(A, B):
    """Strassen's Matrix Multiplication"""
    n = len(A)
    # Assumes square matrices of size 2^n
    if n == 1:
        return [[A[0][0] * B[0][0]]]

    def add_matrix(X, Y):
        return [[X[i][j] + Y[i][j] for j in range(len(X))] for i in range(len(X))]

    def subtract_matrix(X, Y):
        return [[X[i][j] - Y[i][j] for j in range(len(X))] for i in range(len(X))]

    def split(matrix):
        row = len(matrix)
        mid = row // 2
        A11 = [row[:mid] for row in matrix[:mid]]
        A12 = [row[mid:] for row in matrix[:mid]]
        A21 = [row[:mid] for row in matrix[mid:]]
        A22 = [row[mid:] for row in matrix[mid:]]
        return A11, A12, A21, A22

    A11, A12, A21, A22 = split(A)
    B11, B12, B21, B22 = split(B)

    M1 = Strassen_Matrix_Multiplication(add_matrix(A11, A22), add_matrix(B11, B22))
    M2 = Strassen_Matrix_Multiplication(add_matrix(A21, A22), B11)
    M3 = Strassen_Matrix_Multiplication(A11, subtract_matrix(B12, B22))
    M4 = Strassen_Matrix_Multiplication(A22, subtract_matrix(B21, B11))
    M5 = Strassen_Matrix_Multiplication(add_matrix(A11, A12), B22)
    M6 = Strassen_Matrix_Multiplication(subtract_matrix(A21, A11), add_matrix(B11, B12))
    M7 = Strassen_Matrix_Multiplication(subtract_matrix(A12, A22), add_matrix(B21, B22))

    def join(C11, C12, C21, C22):
        top = [c11 + c12 for c11, c12 in zip(C11, C12)]
        bottom = [c21 + c22 for c21, c22 in zip(C21, C22)]
        return top + bottom

    C11 = add_matrix(subtract_matrix(add_matrix(M1, M4), M5), M7)
    C12 = add_matrix(M3, M5)
    C21 = add_matrix(M2, M4)
    C22 = add_matrix(subtract_matrix(add_matrix(M1, M3), M2), M6)

    return join(C11, C12, C21, C22)