# Module: list_processing.py
def process_list(numbers):
    """Process list to find min by abs value and sum between first/last positive elements.
    
    Args:
        numbers (list): List of real numbers.
    
    Returns:
        tuple: (min by abs value, sum between positives)
    """
    if not numbers:
        return None, 0
    
    # Minimal by absolute value
    min_abs = min(numbers, key=abs)
    
    # Sum between first and last positive
    positive_indices = [i for i, num in enumerate(numbers) if num > 0]
    if len(positive_indices) < 2:
        sum_between = 0
    else:
        sum_between = sum(numbers[positive_indices[0] + 1:positive_indices[-1]])
    
    return min_abs, sum_between

def get_user_list():
    """Get list of real numbers from user.
    
    Returns:
        list: List of real numbers.
    """
    while True:
        try:
            n = int(input("Enter number of elements: "))
            if n <= 0:
                raise ValueError("Number must be positive")
            return [float(input(f"Enter element {i+1}: ")) for i in range(n)]
        except ValueError as e:
            print(f"Invalid input: {e}. Try again.")