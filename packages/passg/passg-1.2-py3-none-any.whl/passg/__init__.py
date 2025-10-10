"""
passg - A simple, secure, and customizable password generator.

This package provides a single function, `generate_password`, which creates
random passwords of a specified length. The passwords are guaranteed to include
at least one lowercase letter, one uppercase letter, one digit, and one special character.

Example:
    >>> from passg import generate_password
    >>> password = generate_password(20)
    >>> print(password)
"""

from .passg import generate_password
__all__ = ['generate_password']