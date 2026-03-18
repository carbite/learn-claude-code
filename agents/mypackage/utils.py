"""
Utility functions for MyPackage.
"""

import math
from typing import Union


def add_numbers(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Add two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of a and b
    """
    return a + b


def multiply_numbers(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Multiply two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Product of a and b
    """
    return a * b


def string_reverse(s: str) -> str:
    """Reverse a string.
    
    Args:
        s: Input string
        
    Returns:
        Reversed string
    """
    return s[::-1]


def is_palindrome(s: str) -> bool:
    """Check if a string is a palindrome.
    
    Args:
        s: Input string
        
    Returns:
        True if string is palindrome, False otherwise
    """
    s = s.lower().replace(" ", "")
    return s == s[::-1]


def calculate_factorial(n: int) -> int:
    """Calculate factorial of a number.
    
    Args:
        n: Non-negative integer
        
    Returns:
        Factorial of n
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0:
        return 1
    return math.prod(range(1, n + 1))


def average(numbers: list[int | float]) -> float:
    """Calculate average of a list of numbers.
    
    Args:
        numbers: List of numbers
        
    Returns:
        Average of the numbers
        
    Raises:
        ValueError: If list is empty
    """
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)


def find_max(numbers: list[int | float]) -> int | float:
    """Find maximum value in a list.
    
    Args:
        numbers: List of numbers
        
    Returns:
        Maximum value
        
    Raises:
        ValueError: If list is empty
    """
    if not numbers:
        raise ValueError("Cannot find max of empty list")
    return max(numbers)


def find_min(numbers: list[int | float]) -> int | float:
    """Find minimum value in a list.
    
    Args:
        numbers: List of numbers
        
    Returns:
        Minimum value
        
    Raises:
        ValueError: If list is empty
    """
    if not numbers:
        raise ValueError("Cannot find min of empty list")
    return min(numbers)


def count_vowels(s: str) -> int:
    """Count vowels in a string.
    
    Args:
        s: Input string
        
    Returns:
        Number of vowels (a, e, i, o, u) in the string
    """
    vowels = "aeiouAEIOU"
    return sum(1 for char in s if char in vowels)


def is_prime(n: int) -> bool:
    """Check if a number is prime.
    
    Args:
        n: Positive integer
        
    Returns:
        True if number is prime, False otherwise
        
    Raises:
        ValueError: If n is less than 2
    """
    if n < 2:
        raise ValueError("Prime numbers are defined for integers >= 2")
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True