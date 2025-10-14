"""
JAN Code Generator

This module provides functions to generate random JAN (Japanese Article Number) codes,
including GTIN-13, GTIN-8, GTIN-14, UPC-12, and SSCC-18 formats.
All generated codes include valid check digits calculated using the standard algorithm.
"""

import random

def _get_last_jan_digit(jan_code: str) -> int:
    """
    Calculate the check digit for a JAN code using the standard algorithm.
    
    Args:
        jan_code (str): The JAN code digits without the check digit.
    
    Returns:
        int: The calculated check digit (0-9).
    """
    i = len(jan_code) + 1
    sum = 0
    for digit in jan_code:
        if i % 2 == 0:
            sum += int(digit) * 3
        else:
            sum += int(digit)
        i -= 1
    last_digit = 10 - int(str(sum)[-1])
    if last_digit == 10:
        last_digit = 0
    return last_digit

def random_gtin_13() -> str:
    """
    Generate a random GTIN-13 (Global Trade Item Number) code.
    
    Returns:
        str: A 13-digit GTIN-13 code with a valid check digit.
    """
    random_jan = ''.join(random.choices('0123456789', k=12))
    last_digit = _get_last_jan_digit(random_jan)
    return random_jan + str(last_digit)

def random_gtin_8() -> str:
    """
    Generate a random GTIN-8 (Global Trade Item Number) code.
    
    Returns:
        str: An 8-digit GTIN-8 code with a valid check digit.
    """
    random_jan = ''.join(random.choices('0123456789', k=7))
    last_digit = _get_last_jan_digit(random_jan)
    return random_jan + str(last_digit)

def random_gtin_14() -> str:
    """
    Generate a random GTIN-14 (Global Trade Item Number) code.
    
    Returns:
        str: A 14-digit GTIN-14 code with a valid check digit, starting with '1'.
    """
    random_jan = '1' + ''.join(random.choices('0123456789', k=12))
    last_digit = _get_last_jan_digit(random_jan)
    return random_jan + str(last_digit)

def random_upc_12() -> str:
    """
    Generate a random UPC-12 (Universal Product Code) code.
    
    Returns:
        str: A 12-digit UPC-12 code with a valid check digit.
    """
    random_jan = ''.join(random.choices('0123456789', k=11))
    last_digit = _get_last_jan_digit(random_jan)
    return random_jan + str(last_digit)

def random_sscc_18() -> str:
    """
    Generate a random SSCC-18 (Serial Shipping Container Code) code.
    
    Returns:
        str: An 18-digit SSCC-18 code with a valid check digit, starting with '0'.
    """
    random_jan = '0' + ''.join(random.choices('0123456789', k=16))
    last_digit = _get_last_jan_digit(random_jan)
    return random_jan + str(last_digit)

def random_grai_14() -> str:
    """
    Generate a random GRAI-14 (Global Returnable Asset Identifier) code.
    
    Returns:
        str: A 14-digit GRAI-14 code with a valid check digit, starting with '0'.
    """
    random_jan = '0' + ''.join(random.choices('0123456789', k=12))
    last_digit = _get_last_jan_digit(random_jan)
    return random_jan + str(last_digit)
