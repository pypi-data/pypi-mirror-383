"""
Utility functions for the corebrum package.
"""

import random
import string


def generate_random_string(length=10):
    """
    Generate a random string of specified length.
    
    Args:
        length (int): Length of the random string to generate
        
    Returns:
        str: Random string containing letters and digits
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def is_even(number):
    """
    Check if a number is even.
    
    Args:
        number (int): Number to check
        
    Returns:
        bool: True if number is even, False otherwise
    """
    return number % 2 == 0


def factorial(n):
    """
    Calculate the factorial of a number.
    
    Args:
        n (int): Number to calculate factorial for
        
    Returns:
        int: Factorial of n
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
