# Lab Work #3: Standard Data Types, Collections, Functions, and Modules
# Purpose: Compute e^x using Taylor series and perform other data processing tasks
# Version: 1.0
# Developer: Aleksandr Chueshov
# Date: 31/03/2025

from series_expansion import compute_exp_series
from initialization import get_series_input
from text_analysis import count_consonant_words, analyze_string
from list_processing import process_list, get_user_list
import math

def task1():
    """Execute Task 1: Compute e^x using power series."""
    print("\nTask 1: Compute e^x using Taylor series")
    while True:
        x, eps = get_series_input()
        computed_value, n_terms = compute_exp_series(x, eps)
        exact_value = math.exp(x)
        results = [[x, computed_value, n_terms, exact_value, eps]]
        #headers = ["x", "F(x)", "n", "Math F(x)", "eps"]
        print(results)
        if input("Try another? (y/n): ").lower() != 'y':
            break
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
    print("\nTask 2: Sum every second integer until 1")
    result = sum_every_second()
    print(f"Sum of every second integer: {result}")
    pass

def task3():
    """Execute Task 3: Count words starting with lowercase consonant."""
    print("\nTask 3: Count words starting with lowercase consonant")
    while True:
        text = input("Enter a string: ")
        if not text.strip():
            print("String cannot be empty. Try again.")
            continue
        result = count_consonant_words(text)
        print(f"Words starting with lowercase consonant: {result}")
        if input("Try another? (y/n): ").lower() != 'y':
            break
    pass

def task4():
    """Execute Task 4: Analyze given string."""
    text = ("So she was considering in her own mind, as well as she could, for the hot day made her "
            "feel very sleepy and stupid, whether the pleasure of making a daisy-chain would be worth "
            "the trouble of getting up and picking the daisies, when suddenly a White Rabbit with "
            "pink eyes ran close by her.")
    print("\nTask 4: Analyze the given string")
    count_min, words_period, longest_r = analyze_string(text)
    print(f"a) Number of words with minimal length: {count_min}")
    print(f"b) Words followed by a period: {words_period}")
    print(f"c) Longest word ending with 'r': {longest_r}")
    pass

def task5():
    """Execute Task 5: Process list of real numbers."""
    print("\nTask 5: Process list of real numbers")
    numbers = get_user_list()
    print(f"List: {numbers}")
    min_abs, sum_between = process_list(numbers)
    print(f"Minimal element by absolute value: {min_abs}")
    print(f"Sum between first and last positive elements: {sum_between}")
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

if __name__ == "__main__":
    main()