# Module: initialization.py
def get_series_input():
    """Get x and eps from user with validation.
    
    Returns:
        tuple: (x, eps)
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