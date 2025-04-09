# Module: series_expansion.py
import math
import time

def timing_decorator(func):
    """Decorator to measure execution time of a function."""
    def wrapper(*args, **kwargs):
        try:
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            print(f"{func.__name__} took {end - start:.4f} seconds")
            return result
        except Exception as e:
            print(f"Error in {func.__name__}: {e}")
            raise
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
    
    Raises:
        ValueError: If eps is not positive or max_iter is not positive.
    """
    try:
        if eps <= 0:
            raise ValueError("eps must be positive")
        if max_iter <= 0:
            raise ValueError("max_iter must be positive")
        
        sum_exp = 0.0
        term = 1.0  # Initial term (n=0)
        n = 0
        while abs(term) >= eps and n < max_iter:
            sum_exp += term
            n += 1
            term = term * x / n  # Compute next term iteratively
        return sum_exp, n
    except TypeError as e:
        print(f"TypeError in compute_exp_series: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error in compute_exp_series: {e}")
        raise