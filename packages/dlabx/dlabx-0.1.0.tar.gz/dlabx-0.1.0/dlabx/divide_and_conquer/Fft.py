# Euclidean distance
def euclidean_distance(p1, p2):
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2) ** 0.5

# Constants
_PI = 3.141592653589793

# Approximate sine using Taylor series
def _sin_taylor(x):
    x = x % (2*_PI)  # reduce for better accuracy
    return x - x**3 / 6 + x**5 / 120 - x**7 / 5040

# Approximate cosine using Taylor series
def _cos_taylor(x):
    x = x % (2*_PI)
    return 1 - x**2 / 2 + x**4 / 24 - x**6 / 720

# Complex exponential
def complex_exp(theta):
    return complex(_cos_taylor(theta), _sin_taylor(theta))

# FFT implementation
def Fft(arr):
    n = len(arr)
    if n <= 1:
        return arr
    even = Fft(arr[0::2])
    odd = Fft(arr[1::2])
    T = [0] * n
    for k in range(n // 2):
        angle = -2 * _PI * k / n
        t = complex_exp(angle) * odd[k]
        T[k] = even[k] + t
        T[k + n // 2] = even[k] - t
    return T

# Inverse FFT
def Ifft(arr):
    n = len(arr)
    conjugated = [x.conjugate() for x in arr]
    y = Fft(conjugated)
    return [x.conjugate()/n for x in y]
