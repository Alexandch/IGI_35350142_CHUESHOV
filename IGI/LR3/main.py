# Lab Work #3: Standard Data Types, Collections, Functions, and Modules
# Purpose: Compute e^x using Taylor series and perform other data processing tasks
# Version: 3.0
# Developer: Aleksandr Chueshov
# Date: 31/03/2025

from series_expansion import compute_exp_series
from initialization import get_series_input
from text_analysis import count_consonant_words, analyze_string
from list_processing import process_list, get_user_list
import math


def print_table(headers, data):
    """Print a table with given headers and data.
    
    Args:
        headers (list): List of column headers.
        data (list): List of rows, where each row is a list of values.
    
    Raises:
        TypeError: If headers or data are not lists.
    """
    try:
        if not isinstance(headers, list) or not isinstance(data, list):
            raise TypeError("headers and data must be lists")
        
        # Вычисляем ширину каждого столбца
        column_widths = [max(len(str(item)) for item in column) for column in zip(*([headers] + data))]
        
        # Форматируем и выводим заголовки
        header_line = " | ".join(f"{header:<{width}}" for header, width in zip(headers, column_widths))
        separator_line = "-+-".join("-" * width for width in column_widths)
        
        print(header_line)
        print(separator_line)
    
    # Выводим строки данных
        for row in data:
            row_line = " | ".join(f"{str(item):<{width}}" for item, width in zip(row, column_widths))
            print(row_line)
    except TypeError as e:
        print(f"TypeError in print_table: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error in print_table: {e}")
        raise

def task1():
    """Execute Task 1: Compute e^x using power series."""
    try:
        print("\nTask 1: Compute e^x using Taylor series")
        while True:
            x, eps = get_series_input()
            computed_value, n_terms = compute_exp_series(x, eps)
            exact_value = math.exp(x)
            results = [[x, computed_value, n_terms, exact_value, eps]]
            headers = ["x", "F(x)", "n", "Math F(x)", "eps"]
            print_table(headers, results)
            choice = input("Try another? (y/n): ").lower()
            if choice != 'y':
                break
    except ValueError as e:
        print(f"ValueError in task1: {e}")
    except Exception as e:
        print(f"Unexpected error in task1: {e}")
    pass

def sum_every_second():
    """Sum every second integer until 1 is entered.
    
    Returns:
        int: Sum of every second integer.
    """
    total = 0
    count = 0
    while True:
        try:
            num = int(input("Enter an integer (1 to stop): "))
            if num == 1:
                break
            count += 1
            if count % 2 == 0:
                total += num
        except ValueError:
            print("Please enter a valid integer.")
    return total

def task2():
    """Execute Task 2: Sum every second integer."""
    try:
        print("\nTask 2: Sum every second integer until 1")
        total = 0
        count = 0
        while True:
            try:
                num = int(input("Enter an integer (1 to stop): "))
                if num == 1:
                    break
                count += 1
                if count % 2 == 0:
                    total += num
            except ValueError as e:
                print(f"Invalid input: {e}. Please enter a valid integer.")
        print(f"Sum of every second integer: {total}")
    except Exception as e:
        print(f"Unexpected error in task2: {e}")
    pass

def task3():
    """Execute Task 3: Count words starting with lowercase consonant."""
    try:
        print("\nTask 3: Count words starting with lowercase consonant")
        while True:
            text = input("Enter a string: ")
            if not text.strip():
                print("String cannot be empty. Try again.")
                continue
            result = count_consonant_words(text)
            print(f"Words starting with lowercase consonant: {result}")
            choice = input("Try another? (y/n): ").lower()
            if choice != 'y':
                break
    except Exception as e:
        print(f"Unexpected error in task3: {e}")
    pass

def task4():
    """Execute Task 4: Analyze given string."""
    try:
        text = ("So she was considering in her own mind, as well as she could, for the hot day made her "
                "feel very sleepy and stupid, whether the pleasure of making a daisy-chain would be worth "
                "the trouble of getting up and picking the daisies, when suddenly a White Rabbit with "
                "pink eyes ran close by her.")
        print("\nTask 4: Analyze the given string")
        count_min, words_period, longest_r = analyze_string(text)
        print(f"a) Number of words with minimal length: {count_min}")
        print(f"b) Words followed by a period: {words_period}")
        print(f"c) Longest word ending with 'r': {longest_r}")
    except Exception as e:
        print(f"Unexpected error in task4: {e}")
    pass

def task5():
    """Execute Task 5: Process list of real numbers."""
    try:
        print("\nTask 5: Process list of real numbers")
        numbers = get_user_list()
        print(f"List: {numbers}")
        min_abs, sum_between = process_list(numbers)
        print(f"Minimal element by absolute value: {min_abs}")
        print(f"Sum between first and last positive elements: {sum_between}")
    except ValueError as e:
        print(f"ValueError in task5: {e}")
    except Exception as e:
        print(f"Unexpected error in task5: {e}")
    pass

def main():
    tasks = {
        '1': task1,
        '2': task2,
        '3': task3,
        '4': task4,
        '5': task5
    }
    while True:
        try:
            print("\nAvailable tasks:")
            print("1: Compute e^x using Taylor series")
            print("2: Sum every second integer")
            print("3: Count words starting with lowercase consonant")
            print("4: Analyze given string")
            print("5: Process list of real numbers")
            print("0: Exit")
            choice = input("Choose a task (0-5): ")
            if choice == '0':
                print("Goodbye!")
                break
            elif choice in tasks:
                tasks[choice]()
            else:
                print("Invalid choice. Try again.")
        except KeyboardInterrupt:
            print("\nProgram interrupted by user. Exiting...")
            break
        except Exception as e:
            print(f"Unexpected error in main: {e}")
            continue

if __name__ == "__main__":
    main()