"""
Extra operators not in the standard Python 'operators' module.

"""

# This is needed to implement subtracting a Value from a simple number (e.g., 0-STOR)
def rsub(a, b):
    "Same as b - a."
    return b - a