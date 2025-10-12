"""
PyHanNom: Vietnamese Latin ↔ Han-Nom converter and lookup tool
"""

from .load_syllable_char_table import load_syllable_char_table
from .get_chuhannom_from_latin import (
    get_chuhannom_from_latin,
    get_chuhannom_unicode_from_latin,
)
from .get_latin_from_chuhannom import get_latin_from_chuhannom

from .load_word_table import load_word_table
from .get_chuhannom_word_from_latin import get_chuhannom_word_from_latin
from .get_latin_word_from_chuhannom import get_latin_word_from_chuhannom

__version__ = "0.1.0"

__all__ = [
    "load_syllable_char_table",
    "get_chuhannom_from_latin",
    "get_chuhannom_unicode_from_latin",
    "get_latin_from_chuhannom",
    "load_word_table",
    "get_chuhannom_word_from_latin",
    "get_latin_word_from_chuhannom",
]
