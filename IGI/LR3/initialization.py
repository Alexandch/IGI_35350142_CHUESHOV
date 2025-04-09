# Module: initialization.py
import random

def get_series_input():
    """Get x and eps from user with validation.
    
    Returns:
        tuple: (x, eps)
    
    Raises:
        ValueError: If input cannot be converted to float or eps is not positive.
    """
    while True:
        try:
            x = float(input("Enter x: "))
            eps = float(input("Enter eps (e.g., 0.0001): "))
            if eps <= 0:
                raise ValueError("eps must be positive")
            return x, eps
        except ValueError as e:
            print(f"Invalid input: {e}. Try again.")

def generate_sequence(size, start=-10, end=10):
    """Generate a sequence of random numbers.
    
    Args:
        size (int): Number of elements to generate.
        start (float): Lower bound of random numbers (default -10).
        end (float): Upper bound of random numbers (default 10).
    
    Yields:
        float: Random number in the specified range.
    
    Raises:
        ValueError: If size is not positive or start is greater than end.
        TypeError: If arguments are of incorrect type.
    """
    try:
        if not isinstance(size, int):
            raise TypeError("size must be an integer")
        if size <= 0:
            raise ValueError("size must be positive")
        if start > end:
            raise ValueError("start must be less than or equal to end")
        
        for _ in range(size):
            yield random.uniform(start, end)
    except TypeError as e:
        print(f"TypeError in generate_sequence: {e}")
        raise
    except ValueError as e:
        print(f"ValueError in generate_sequence: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error in generate_sequence: {e}")
        raise