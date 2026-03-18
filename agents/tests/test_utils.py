"""
Unit tests for mypackage.utils module.
"""

import pytest
from mypackage.utils import (
    add_numbers,
    multiply_numbers,
    string_reverse,
    is_palindrome,
    calculate_factorial,
    average,
    find_max,
    find_min,
    count_vowels,
    is_prime
)


class TestAddNumbers:
    """Test cases for add_numbers function."""
    
    def test_add_integers(self):
        """Test adding two integers."""
        assert add_numbers(2, 3) == 5
        assert add_numbers(-5, 10) == 5
        assert add_numbers(0, 0) == 0
        
    def test_add_floats(self):
        """Test adding two floats."""
        assert add_numbers(2.5, 3.5) == 6.0
        assert add_numbers(-1.5, 2.5) == 1.0
        
    def test_add_mixed(self):
        """Test adding integer and float."""
        assert add_numbers(2, 3.5) == 5.5
        assert add_numbers(5.5, 2) == 7.5


class TestMultiplyNumbers:
    """Test cases for multiply_numbers function."""
    
    def test_multiply_integers(self):
        """Test multiplying two integers."""
        assert multiply_numbers(2, 3) == 6
        assert multiply_numbers(-5, 4) == -20
        assert multiply_numbers(0, 10) == 0
        
    def test_multiply_floats(self):
        """Test multiplying two floats."""
        assert multiply_numbers(2.5, 4.0) == 10.0
        assert multiply_numbers(-1.5, 2.0) == -3.0


class TestStringReverse:
    """Test cases for string_reverse function."""
    
    def test_reverse_normal_string(self):
        """Test reversing a normal string."""
        assert string_reverse("hello") == "olleh"
        assert string_reverse("Python") == "nohtyP"
        
    def test_reverse_empty_string(self):
        """Test reversing an empty string."""
        assert string_reverse("") == ""
        
    def test_reverse_single_character(self):
        """Test reversing a single character string."""
        assert string_reverse("a") == "a"


class TestIsPalindrome:
    """Test cases for is_palindrome function."""
    
    def test_palindrome_true(self):
        """Test strings that are palindromes."""
        assert is_palindrome("racecar") == True
        assert is_palindrome("A man a plan a canal Panama") == True
        assert is_palindrome("") == True
        assert is_palindrome("a") == True
        
    def test_palindrome_false(self):
        """Test strings that are not palindromes."""
        assert is_palindrome("hello") == False
        assert is_palindrome("Python") == False
        
    def test_palindrome_case_insensitive(self):
        """Test that palindrome check is case insensitive."""
        assert is_palindrome("Racecar") == True
        assert is_palindrome("RaceCar") == True


class TestCalculateFactorial:
    """Test cases for calculate_factorial function."""
    
    def test_factorial_zero(self):
        """Test factorial of 0."""
        assert calculate_factorial(0) == 1
        
    def test_factorial_positive(self):
        """Test factorial of positive numbers."""
        assert calculate_factorial(1) == 1
        assert calculate_factorial(5) == 120
        assert calculate_factorial(7) == 5040
        
    def test_factorial_negative(self):
        """Test factorial of negative number raises ValueError."""
        with pytest.raises(ValueError, match="Factorial is not defined for negative numbers"):
            calculate_factorial(-5)


class TestAverage:
    """Test cases for average function."""
    
    def test_average_integers(self):
        """Test average of integers."""
        assert average([1, 2, 3, 4, 5]) == 3.0
        assert average([10, 20, 30]) == 20.0
        
    def test_average_floats(self):
        """Test average of floats."""
        assert average([1.5, 2.5, 3.5]) == 2.5
        
    def test_average_single_element(self):
        """Test average of single element list."""
        assert average([5]) == 5.0
        
    def test_average_empty_list(self):
        """Test average of empty list raises ValueError."""
        with pytest.raises(ValueError, match="Cannot calculate average of empty list"):
            average([])


class TestFindMax:
    """Test cases for find_max function."""
    
    def test_find_max_integers(self):
        """Test finding max of integers."""
        assert find_max([1, 5, 3, 9, 2]) == 9
        assert find_max([-5, -1, -10]) == -1
        
    def test_find_max_floats(self):
        """Test finding max of floats."""
        assert find_max([1.5, 3.2, 2.1]) == 3.2
        
    def test_find_max_single_element(self):
        """Test finding max of single element list."""
        assert find_max([7]) == 7
        
    def test_find_max_empty_list(self):
        """Test finding max of empty list raises ValueError."""
        with pytest.raises(ValueError, match="Cannot find max of empty list"):
            find_max([])


class TestFindMin:
    """Test cases for find_min function."""
    
    def test_find_min_integers(self):
        """Test finding min of integers."""
        assert find_min([1, 5, 3, 9, 2]) == 1
        assert find_min([-5, -1, -10]) == -10
        
    def test_find_min_floats(self):
        """Test finding min of floats."""
        assert find_min([1.5, 3.2, 2.1]) == 1.5
        
    def test_find_min_single_element(self):
        """Test finding min of single element list."""
        assert find_min([7]) == 7
        
    def test_find_min_empty_list(self):
        """Test finding min of empty list raises ValueError."""
        with pytest.raises(ValueError, match="Cannot find min of empty list"):
            find_min([])


class TestCountVowels:
    """Test cases for count_vowels function."""
    
    def test_count_vowels_normal(self):
        """Test counting vowels in normal strings."""
        assert count_vowels("hello") == 2
        assert count_vowels("Python") == 1
        assert count_vowels("AEIOU") == 5
        
    def test_count_vowels_empty(self):
        """Test counting vowels in empty string."""
        assert count_vowels("") == 0
        
    def test_count_vowels_no_vowels(self):
        """Test counting vowels in string with no vowels."""
        assert count_vowels("xyz") == 0
        assert count_vowels("123") == 0
        
    def test_count_vowels_mixed_case(self):
        """Test counting vowels with mixed case."""
        assert count_vowels("Hello World") == 3


class TestIsPrime:
    """Test cases for is_prime function."""
    
    def test_prime_true(self):
        """Test numbers that are prime."""
        assert is_prime(2) == True
        assert is_prime(3) == True
        assert is_prime(17) == True
        assert is_prime(97) == True
        
    def test_prime_false(self):
        """Test numbers that are not prime."""
        assert is_prime(1) == False
        assert is_prime(4) == False
        assert is_prime(15) == False
        assert is_prime(100) == False
        
    def test_prime_negative(self):
        """Test negative number raises ValueError."""
        with pytest.raises(ValueError, match="Prime numbers are defined for integers >= 2"):
            is_prime(-5)
            
    def test_prime_zero(self):
        """Test 0 raises ValueError."""
        with pytest.raises(ValueError, match="Prime numbers are defined for integers >= 2"):
            is_prime(0)
            
    def test_prime_one(self):
        """Test 1 raises ValueError."""
        with pytest.raises(ValueError, match="Prime numbers are defined for integers >= 2"):
            is_prime(1)