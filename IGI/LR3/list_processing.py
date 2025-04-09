# Module: list_processing.py
from initialization import generate_sequence

def process_list(numbers):
    """Process list to find min by abs value and sum between first/last positive elements.
    
    Args:
        numbers (list): List of real numbers.
    
    Returns:
        tuple: (min by abs value, sum between positives)
    
    Raises:
        TypeError: If numbers is not a list or contains non-numeric elements.
        ValueError: If the list is empty.
    """
    try:
        if not isinstance(numbers, list):
            raise TypeError("numbers must be a list")
        if not numbers:
            raise ValueError("list cannot be empty")
        if not all(isinstance(x, (int, float)) for x in numbers):
            raise TypeError("all elements must be numbers")
        
        # Minimal by absolute value
        min_abs = min(numbers, key=abs)
        
        # Sum between first and last positive
        positive_indices = [i for i, num in enumerate(numbers) if num > 0]
        if len(positive_indices) < 2:
            sum_between = 0
        else:
            sum_between = sum(numbers[positive_indices[0] + 1:positive_indices[-1]])
        
        return min_abs, sum_between
    except TypeError as e:
        print(f"TypeError in process_list: {e}")
        raise
    except ValueError as e:
        print(f"ValueError in process_list: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error in process_list: {e}")
        raise

def get_user_list():
    """Get list of real numbers from user or generate it.
    
    Returns:
        list: List of real numbers.
    
    Raises:
        ValueError: If input is invalid.
    """
    while True:
        try:
            method = input("Choose input method (1 for manual, 2 for generated): ")
            if method not in ['1', '2']:
                raise ValueError("Choose 1 or 2")
            n = int(input("Enter number of elements: "))
            if n <= 0:
                raise ValueError("Number must be positive")
            
            if method == '1':
                # Manual input
                numbers = []
                for i in range(n):
                    num = float(input(f"Enter element {i+1}: "))
                    numbers.append(num)
                return numbers
            else:
                # Generated sequence
                return list(generate_sequence(n, start=-10, end=10))
        except ValueError as e:
            print(f"Invalid input: {e}. Try again.")
        except Exception as e:
            print(f"Unexpected error in get_user_list: {e}")
            raise