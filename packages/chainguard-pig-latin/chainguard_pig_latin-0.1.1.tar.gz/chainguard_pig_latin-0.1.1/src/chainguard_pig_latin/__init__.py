"""
Chainguard Pig Latin - A Python package for converting text to Pig Latin.

This package provides functions to convert English text to Pig Latin,
following standard Pig Latin rules.
"""

from .converter import to_pig_latin, word_to_pig_latin

__version__ = "0.1.1"
__all__ = ["to_pig_latin", "word_to_pig_latin"]
