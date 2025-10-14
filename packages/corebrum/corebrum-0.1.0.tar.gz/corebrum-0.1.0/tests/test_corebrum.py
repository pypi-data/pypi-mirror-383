"""
Tests for the corebrum package.
"""

import pytest
import corebrum


def test_hello_world():
    """Test the hello_world function."""
    result = corebrum.hello_world()
    assert result == "Hello from Corebrum!"


def test_add_numbers():
    """Test the add_numbers function."""
    assert corebrum.add_numbers(2, 3) == 5
    assert corebrum.add_numbers(-1, 1) == 0
    assert corebrum.add_numbers(0, 0) == 0


def test_get_version():
    """Test the get_version function."""
    version = corebrum.get_version()
    assert isinstance(version, str)
    assert version == "0.1.0"


def test_generate_random_string():
    """Test the generate_random_string function."""
    result = corebrum.generate_random_string(10)
    assert len(result) == 10
    assert isinstance(result, str)
    
    # Test with different length
    result2 = corebrum.generate_random_string(5)
    assert len(result2) == 5


def test_is_even():
    """Test the is_even function."""
    assert corebrum.is_even(2) is True
    assert corebrum.is_even(3) is False
    assert corebrum.is_even(0) is True
    assert corebrum.is_even(-2) is True
    assert corebrum.is_even(-3) is False


def test_factorial():
    """Test the factorial function."""
    assert corebrum.factorial(0) == 1
    assert corebrum.factorial(1) == 1
    assert corebrum.factorial(5) == 120
    assert corebrum.factorial(3) == 6
    
    # Test negative number raises ValueError
    with pytest.raises(ValueError):
        corebrum.factorial(-1)
