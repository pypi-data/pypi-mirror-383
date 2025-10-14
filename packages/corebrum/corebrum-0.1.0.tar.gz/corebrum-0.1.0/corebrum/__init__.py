"""
Corebrum - A basic Python package for demonstration purposes.
"""

__version__ = "0.1.0"
__author__ = "Corebrum"
__email__ = "hello@corebrum.com"

def hello_world():
    """Return a simple greeting message."""
    return "Hello from Corebrum!"

def add_numbers(a, b):
    """Add two numbers together."""
    return a + b

def get_version():
    """Get the current version of the package."""
    return __version__

# Import utility functions
from .utils import generate_random_string, is_even, factorial

__all__ = [
    'hello_world',
    'add_numbers', 
    'get_version',
    'generate_random_string',
    'is_even',
    'factorial'
]
