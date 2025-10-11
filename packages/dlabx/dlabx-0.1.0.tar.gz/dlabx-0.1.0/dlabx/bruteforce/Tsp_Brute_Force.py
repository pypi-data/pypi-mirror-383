# ----------- Traveling Salesman Problem (TSP) - Brute Force -----------

def Tsp_Brute_Force(cities):
    n = len(cities)
    min_path = None
    min_cost = float('inf')

    def permute(arr, l, r):
        if l == r:
            nonlocal min_cost, min_path
            total_distance = 0
            for i in range(len(arr) - 1):
                total_distance += distance(cities[arr[i]], cities[arr[i + 1]])
            total_distance += distance(cities[arr[-1]], cities[0])  # Return to start
            if total_distance < min_cost:
                min_cost = total_distance
                min_path = [0] + arr[:] + [0]
        else:
            for i in range(l, r + 1):
                arr[l], arr[i] = arr[i], arr[l]
                permute(arr, l + 1, r)
                arr[l], arr[i] = arr[i], arr[l]

    permute(list(range(1, n)), 0, n - 2)
    return min_path, min_cost


# ----------- Distance function for TSP (Euclidean distance) -----------

def distance(city1, city2):
    # city1 and city2 are tuples like (x, y)
    dx = city1[0] - city2[0]
    dy = city1[1] - city2[1]
    # Manual hypotenuse calculation (without math.sqrt)
    dist_squared = dx * dx + dy * dy
    
    # Implement square root using Newton's method
    def sqrt_newton(n, guess=1.0):
        for _ in range(20):  # 20 iterations for sufficient accuracy
            guess = 0.5 * (guess + n / guess)
        return guess

    return sqrt_newton(dist_squared)