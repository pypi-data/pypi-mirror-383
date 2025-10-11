# ----------- Fractional Knapsack -----------

def Fractional_Knapsack(weights, values, capacity):


    # Create list of tuples: (value/weight ratio, weight, value, index)
    ratio = [(v / w, w, v, i) for i, (w, v) in enumerate(zip(weights, values))]
    # Sort items by value/weight ratio in descending order
    ratio.sort(key=lambda x: x[0], reverse=True)

    total_value = 0.0
    fractions = [0.0] * len(weights)

    for r, w, v, i in ratio:
        if capacity == 0:
            break

        if w <= capacity:
            # Take the whole item
            total_value += v
            capacity -= w
            fractions[i] = 1.0
        else:
            # Take fractional part
            fraction = capacity / w
            total_value += v * fraction
            fractions[i] = fraction
            capacity = 0
            break

    return total_value, fractions
