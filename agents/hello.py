#!/usr/bin/env python3
"""A simple hello world program with type hints and documentation."""


def say_hello(name: str = "World") -> str:
    """
    Return a greeting message.
    
    Args:
        name: The name to greet. Defaults to "World".
        
    Returns:
        A greeting string in the format "Hello, {name}!"
    """
    return f"Hello, {name}!"


def main() -> None:
    """Main function that runs the program."""
    greeting = say_hello()
    print(greeting)


if __name__ == "__main__":
    main()