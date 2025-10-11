# knapsack_bruteforce.py
def Knapsack_Bruteforce(weights, values, capacity):
    max_value = 0
    best_combination = []
    n = len(weights)
    
    for i in range(1, 2**n):
        total_weight = 0
        total_value = 0
        current_combination = []
        for j in range(n):
            if (i >> j) & 1:
                total_weight += weights[j]
                total_value += values[j]
                current_combination.append(j)
        if total_weight <= capacity and total_value > max_value:
            max_value = total_value
            best_combination = current_combination
    return max_value, best_combination