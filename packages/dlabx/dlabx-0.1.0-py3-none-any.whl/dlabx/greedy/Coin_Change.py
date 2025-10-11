# ----------- Greedy Coin Change -----------

def Coin_Change(coins, amount):
    # Sort coins in descending order
    coins = sorted(coins, reverse=True)
    count = 0
    remaining = amount

    for coin in coins:
        if remaining == 0:
            break
        num = remaining // coin  # Number of this coin used
        count += num
        remaining -= num * coin

    if remaining != 0:
        return None  # No exact solution possible
    return count
