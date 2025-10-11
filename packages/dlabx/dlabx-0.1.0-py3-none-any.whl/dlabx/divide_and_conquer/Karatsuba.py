
# ----------- Karatsuba Multiplication -----------

def Karatsuba(x, y):
    """Karatsuba multiplication"""
    str_x = str(x)
    str_y = str(y)
    n = max(len(str_x), len(str_y))
    if n == 1:
        return x * y
    m = n // 2
    high1, low1 = divmod(x, 10 ** m)
    high2, low2 = divmod(y, 10 ** m)

    z0 = Karatsuba(low1, low2)
    z1 = Karatsuba(low1 + high1, low2 + high2)
    z2 = Karatsuba(high1, high2)

    return (z2 * 10 ** (2 * m)) + ((z1 - z2 - z0) * 10 ** m) + z0
