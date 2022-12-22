# pylint: disable=invalid-name
from functools import wraps
from typing import Any, Callable

VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def check_roman_numeral(numeral: str) -> bool:
    """Controls that the userinput only contains valid roman numerals"""
    numeral = numeral.upper()
    validRomanNumerals = ["M", "D", "C", "L", "X", "V", "I"]
    for letters in numeral:
        if letters not in validRomanNumerals:
            return False
    return True


def roman_to_int(s: str) -> int:

    s = s.replace("IV", "IIII").replace("IX", "VIIII")
    s = s.replace("XL", "XXXX").replace("XC", "LXXXX")
    s = s.replace("CD", "CCCC").replace("CM", "DCCCC")

    return sum(map(lambda x: VALUES[x], s))


def roman_num_handler(func: Callable[..., str | None]) -> Callable[..., int | None]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> int | None:
        volume = func(*args, **kwargs)
        if volume is None:
            return volume
        return roman_to_int(volume) if check_roman_numeral(volume) else int(volume)

    return wrapper
