"""
Module for converting integers to roman numerals.
"""


__author__ = "https://codeberg.org/decoherence"


_ROMAN_NUMERALS = {1: "I", 4: "IV", 5: "V", 9: "IX", 
                   10: "X", 40: "XL", 50: "L", 90: "XC", 
                   100: "C", 400: "CD", 500: "D", 900: "CM",
                   1000: "M"}


def integer_to_roman(integer: int, case="upper") -> str:
    """Converts an integer to corresponding Roman numeral.
    
    Args:
        integer: Positive integer to be converted.
        case (optional): 'upper' or 'lower'; defines if the
          roman numerals shall be uppercase or lowercase.

    Raises:
        ValueError: If the input is negative.
    
    """
    if integer < 0:
        raise ValueError(f"Cannot handle negative or zero values")


    roman = str()

    for base in reversed(_ROMAN_NUMERALS.keys()):
        div = integer // base
        integer = integer % base
        roman = roman + (_ROMAN_NUMERALS[base] * div)

    if case == "upper":
        return roman
    else:
        return roman.lower()


def roman_to_integer(roman: str) -> int:
    """Converts a Roman numeral to an integer.
    
    Args:
        roman: A string containing a valid Roman numeral
               (case-insensitive).
    
    Returns:
        The integer value of the Roman numeral.
    
    Raises:
        ValueError: If the input is not a valid Roman numeral.
    """
    roman = roman.upper()
    roman_map = {v: k for k, v in _ROMAN_NUMERALS.items()}
    i = 0
    value = 0
    n = len(roman)

    while i < n:
        # Try two-character numerals first (IV, IX, etc.)
        if i + 1 < n and roman[i:i+2] in roman_map:
            value += roman_map[roman[i:i+2]]
            i += 2
        elif roman[i] in roman_map:
            value += roman_map[roman[i]]
            i += 1
        else:
            raise ValueError(f"Invalid Roman numeral sequence: {roman}")

    # Optional sanity check: ensure it round-trips correctly
    if integer_to_roman(value) != roman:
        raise ValueError(f"Invalid or non-canonical Roman numeral: {roman}")

    return value