"""
Calculator module providing basic arithmetic operations and expression evaluation.
"""

import math
from typing import Union, Optional


class Calculator:
    """A class for performing basic arithmetic operations."""
    
    def __init__(self):
        """Initialize the Calculator."""
        pass
    
    def add(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Add two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Sum of a and b
        """
        return a + b
    
    def subtract(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Subtract b from a.
        
        Args:
            a: First number
            b: Second number to subtract
            
        Returns:
            Result of a - b
        """
        return a - b
    
    def multiply(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Multiply two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Product of a and b
        """
        return a * b
    
    def divide(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Divide a by b.
        
        Args:
            a: Numerator
            b: Denominator
            
        Returns:
            Result of a / b
            
        Raises:
            ZeroDivisionError: If b is zero
        """
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return a / b
    
    def power(self, base: Union[int, float], exponent: Union[int, float]) -> Union[int, float]:
        """
        Raise base to the power of exponent.
        
        Args:
            base: Base number
            exponent: Exponent
            
        Returns:
            base raised to the power of exponent
        """
        return base ** exponent
    
    def square_root(self, x: Union[int, float]) -> float:
        """
        Calculate the square root of x.
        
        Args:
            x: Number to find square root of
            
        Returns:
            Square root of x
            
        Raises:
            ValueError: If x is negative
        """
        if x < 0:
            raise ValueError("Cannot calculate square root of negative number")
        return math.sqrt(x)


def calculate_expression(expression: str) -> Optional[Union[int, float]]:
    """
    Parse and evaluate a simple mathematical expression.
    
    Supports basic operations: +, -, *, /, ^ (power)
    Follows standard operator precedence.
    
    Args:
        expression: Mathematical expression as a string
        
    Returns:
        Result of the expression evaluation
        
    Raises:
        ValueError: If expression is invalid or contains unsupported operations
    """
    # Remove whitespace
    expression = expression.replace(" ", "")
    
    if not expression:
        raise ValueError("Empty expression")
    
    # Validate expression contains only allowed characters
    allowed_chars = set("0123456789.+-*/^()")
    for char in expression:
        if char not in allowed_chars:
            raise ValueError(f"Invalid character in expression: {char}")
    
    # Replace ^ with ** for Python's power operator
    expression = expression.replace("^", "**")
    
    # Create calculator instance
    calc = Calculator()
    
    # Define operation mapping
    operations = {
        '+': calc.add,
        '-': calc.subtract,
        '*': calc.multiply,
        '/': calc.divide,
        '**': calc.power,
    }
    
    # For simple expressions, we can use eval with safe operations
    # In a production environment, you'd want a proper parser
    try:
        # Create a safe evaluation environment
        safe_globals = {
            '__builtins__': {},
            'math': math,
        }
        
        # Add calculator operations to the safe environment
        for op_name, op_func in operations.items():
            if op_name == '**':
                # Python already has ** operator
                continue
            # Create wrapper functions
            safe_globals[f'calc_{op_name}'] = op_func
        
        # Replace operators with function calls for safer evaluation
        # This is a simplified approach - a proper parser would be better
        result = eval(expression, safe_globals)
        return result
        
    except ZeroDivisionError as e:
        raise ValueError(f"Division by zero in expression: {expression}") from e
    except Exception as e:
        raise ValueError(f"Error evaluating expression '{expression}': {str(e)}") from e


def main() -> None:
    """Demonstrate the usage of Calculator class and calculate_expression function."""
    print("Calculator Module Demo")
    print("=" * 50)
    
    # Create calculator instance
    calc = Calculator()
    
    # Test basic operations
    print("\n1. Testing basic operations:")
    print(f"   5 + 3 = {calc.add(5, 3)}")
    print(f"   10 - 4 = {calc.subtract(10, 4)}")
    print(f"   6 * 7 = {calc.multiply(6, 7)}")
    print(f"   15 / 3 = {calc.divide(15, 3)}")
    print(f"   2 ^ 8 = {calc.power(2, 8)}")
    print(f"   sqrt(25) = {calc.square_root(25)}")
    
    # Test error handling
    print("\n2. Testing error handling:")
    try:
        calc.divide(10, 0)
    except ZeroDivisionError as e:
        print(f"   Division by zero: {e}")
    
    try:
        calc.square_root(-9)
    except ValueError as e:
        print(f"   Square root of negative: {e}")
    
    # Test expression evaluation
    print("\n3. Testing expression evaluation:")
    expressions = [
        "2 + 3",
        "10 - 4 * 2",
        "(10 - 4) * 2",
        "2 * 3 + 4 / 2",
        "2 ^ 3 + 1",
        "sqrt(16) + 2 * 3",
    ]
    
    for expr in expressions:
        try:
            result = calculate_expression(expr)
            print(f"   {expr} = {result}")
        except ValueError as e:
            print(f"   Error evaluating '{expr}': {e}")
    
    # Interactive demo
    print("\n4. Interactive demo (enter 'quit' to exit):")
    while True:
        try:
            user_input = input("\nEnter an expression: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            result = calculate_expression(user_input)
            print(f"Result: {result}")
            
        except ValueError as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
    
    print("\nDemo completed!")


if __name__ == "__main__":
    main()