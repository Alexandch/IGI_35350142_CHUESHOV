# Module: series_expansion.py
import math
import time

def timing_decorator(func):
    """Decorator to measure execution time of a function."""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

@timing_decorator
def compute_exp_series(x, eps, max_iter=500):
    """Compute e^x using Taylor series expansion with specified precision.
    
    Args:
        x (float): The argument of the function.
        eps (float): Desired precision.
        max_iter (int): Maximum number of iterations (default 500).
    
    Returns:
        tuple: (computed value, number of terms used)
    """
    sum_exp = 0.0
    term = 1.0  # Initial term (n=0)
    n = 0
    while abs(term) >= eps and n < max_iter:
        sum_exp += term
        n += 1
        term = term * x / n  # Compute next term iteratively
    return sum_exp, n