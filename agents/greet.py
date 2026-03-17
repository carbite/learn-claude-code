def greet(name):
    """Greet a person by name.
    
    This function generates a friendly greeting message for the given name.
    
    Args:
        name (str): The name of the person to greet. Can be any string.
    
    Returns:
        str: A greeting message in the format "Hello, {name}!".
    
    Examples:
        >>> greet("Alice")
        'Hello, Alice!'
        >>> greet("Bob")
        'Hello, Bob!'
    """
    return f"Hello, {name}!"