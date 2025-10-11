# ----------- Distance function for TSP (Euclidean distance) -----------

# ----------- Generalized Euclidean Distance Function -----------

def Distance(point1, point2):

    # Validate input dimensions
    if len(point1) != len(point2):
        raise ValueError("Both points must have the same number of dimensions")

    # Compute squared distance
    dist_squared = 0
    for a, b in zip(point1, point2):
        diff = a - b
        dist_squared += diff * diff

    # Newton's method for square root
    def sqrt_newton(n, guess=1.0):
        if n == 0:
            return 0.0
        for _ in range(25):  # more iterations for better precision
            guess = 0.5 * (guess + n / guess)
        return guess

    return sqrt_newton(dist_squared)
