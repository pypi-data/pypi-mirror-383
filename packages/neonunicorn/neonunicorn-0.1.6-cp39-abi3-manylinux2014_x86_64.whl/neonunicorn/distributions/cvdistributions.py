# distributions/cvdistributions.py
"""Cryptographically secure distributions utilities."""

import secrets
from typing import Optional

def uniform(a: float = 0.0, b: float = 1.0) -> float:
    """
    Cryptographically secure uniform random sample in [a, b).
    Uses 53 random bits to match double-precision mantissa precision.
    """
    u = secrets.randbits(53) / (1 << 53)  # in [0, 1)
    return a + (b - a) * u


if __name__ == "__main__":
    # Quick demo when module run as script
    samples = [uniform() for _ in range(10)]
    print("Example samples:", samples)
    import random
import math

def uniform():
    """Return a single random sample uniformly distributed between 0 and 1."""
    return random.random()

def exponentialdist(lmbda: float):
    """Return a single random sample from exponential distribution with rate lmbda."""
    y = random.random()  # U(0,1)
    x = -1 / lmbda * math.log(y)  # Inverse CDF method
    return x

