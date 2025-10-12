"""
This module defines tests for module integer_to_roman - use pytest to run them.
"""

from idroman.roman import *


def test_integer_to_roman() -> None:
    assert integer_to_roman(0) == ""
    assert integer_to_roman(1) == "I"
    assert integer_to_roman(2) == "II"
    assert integer_to_roman(3) == "III"
    assert integer_to_roman(4) == "IV"
    assert integer_to_roman(5) == "V"
    assert integer_to_roman(6) == "VI"
    assert integer_to_roman(7) == "VII"
    assert integer_to_roman(8) == "VIII"
    assert integer_to_roman(9) == "IX"
    assert integer_to_roman(10) == "X"

    assert integer_to_roman(20) == "XX"
    assert integer_to_roman(24) == "XXIV"
    assert integer_to_roman(26) == "XXVI"
    assert integer_to_roman(29) == "XXIX"

    assert integer_to_roman(41) == "XLI"
    assert integer_to_roman(92) == "XCII"
    assert integer_to_roman(433) == "CDXXXIII"
    assert integer_to_roman(675) == "DCLXXV"
    assert integer_to_roman(999) == "CMXCIX"
    assert integer_to_roman(2025) == "MMXXV"


def test_integer_to_roman_lover_case() -> None:
    assert integer_to_roman(1, "lower") == "i"
    assert integer_to_roman(2, "lower") == "ii"
    assert integer_to_roman(3, "lower") == "iii"
    assert integer_to_roman(4, "lower") == "iv"
    assert integer_to_roman(5, "lower") == "v"
    assert integer_to_roman(6, "lower") == "vi"
    assert integer_to_roman(7, "lower") == "vii"
    assert integer_to_roman(8, "lower") == "viii"
    assert integer_to_roman(9, "lower") == "ix"
    assert integer_to_roman(10, "lower") == "x"


def test_roman_to_integer() -> None:
    assert roman_to_integer("IV") == 4
    assert roman_to_integer("xl") == 40
    assert roman_to_integer("XC") == 90
    assert roman_to_integer("mmxxv") == 2025
    assert roman_to_integer("CDXLIV") == 444


if __name__ == "__main__":
    print(__file__)
    import pytest
    pytest.main()