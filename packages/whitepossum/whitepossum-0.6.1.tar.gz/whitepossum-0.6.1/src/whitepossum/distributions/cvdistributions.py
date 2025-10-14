import secrets
import numpy as np
import math
def uniform(a: float = 0.0, b: float = 1.0) -> float:
    """Cryptographically secure uniform sample."""
    # 53 random bits gives 53-bit precision double
    u = secrets.randbits(53) / (1 << 53)
    # in [0, 1)
    return a + (b - a) * u


def exponentialdist(l):
    """
    This uses uniform() to generate a sample for the exponential distribution.

    x = - ( ln(y) / alpha) 

    Arguments:
    l
      Lamda value to pass to the function.
    """
    if  l < 0:
       raise ValueError("Lamda must be greater than 0")


    # get one y-value
    y = uniform()
    x = -( np.log(y) / l)
    return x

def poissondist(l):
    """
    Generate Poisson distributed random sample using inverse transform sampling.
    """
    if l <= 0:
        raise ValueError("Lambda must be greater than 0")

    u = uniform()
    p = math.exp(-l)   # P(X=0)
    F = p              # cumulative probability
    k = 0

    while u > F:
        k += 1
        p *= l / k     # recursive relation for P(X=k)
        F += p

    return k


# Example
if __name__ == '__main__':
    lam = 10
    print("Exponential:", exponentialdist(lam))
    print("Poisson:", poissondist(lam))
