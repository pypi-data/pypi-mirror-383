import secrets
import math
import matplotlib.pyplot as plt

def uniform(a: float = 0.0, b: float = 1.0) -> float:
    u = secrets.randbits(53) / (1 << 53)
    return a + (b - a) * u

def exponentialdist(l: float = 0.5) -> float:
    
    x = uniform(0, 1)
    return (-1.0/l) * math.log(x)

def poissiondist(l: float = 0.5) -> float:

    u = uniform(0.0, 1.0)
    p = math.exp(-l) # p0
    F = p
    k = 0

    while u > F:
        k += 1
        p *= l/k
        F += p

    return k 

if __name__ == "__main__":
    #Testing code

    #Test exponentialdist
    y = []
    for i in range(1000):
        y.append(exponentialdist(0.5))

    plt.hist(y, bins=50, edgecolor='black', density=True)
    plt.title("Histogram of 1000 Exponential Samples")
    plt.xlabel("Value")
    plt.ylabel("Density")
    plt.grid(True)
    #plt.savefig("hw2_q9_inverse_histogram.png")
    plt.show()

    #Test poissiondist
    y = []
    for i in range(1000):
        y.append(poissiondist(0.5))

    plt.hist(y, bins=range(min(y), max(y) + 2), edgecolor='black', density=True)
    plt.title("Histogram of 1000 Poission Samples")
    plt.xlabel("Value")
    plt.ylabel("Density")
    plt.grid(True)
    plt.show()


