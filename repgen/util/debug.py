import functools

# These are used to help trace where repgen is in the callstack
# They are not used in the code, and are used to help debug issues


def log_calls(func):
    """
    Decorator to log function calls.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The decorated function.
    
    Example:
        @log_calls
        def my_function(arg1, arg2):
            print(f'Calling my_function with args: {arg1} and {arg2}')
            result = arg1 + arg2
            print(f'my_function returned {result}')
            return result
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f'Calling {func.__name__} with args: {args} and kwargs: {kwargs}')
        result = func(*args, **kwargs)
        print(f'{func.__name__} returned {result}')
        return result
    return wrapper

def decorate_all_methods(cls):
    '''
    Decorate all methods of a class with the log_calls decorator.

    Args:
        cls (class): The class to be decorated.

    Returns:
        class: The decorated class.
    
    Example:
        @decorate_all_methods
        class MyClass:
            def my_method(self, arg1, arg2):
                print(f'Calling my_method with args: {arg1} and {arg2}')
                result = arg1 + arg2
                print(f'my_method returned {result}')
                return result
    '''
    for attribute_name in dir(cls):
        attribute = getattr(cls, attribute_name)
        if callable(attribute) and not attribute_name.startswith("__"):
            wrapped = log_calls(attribute)
            setattr(cls, attribute_name, wrapped)
    return cls