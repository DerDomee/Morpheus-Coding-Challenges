"""
This solves Coding Challenge 11:
Validate brackets in mathematical formulas
"""

import json


def solve(data):
    """Solving from plaintext data to json token"""

    valid = True
    brackets = 0
    for character in data:
        if character == "(":
            brackets += 1
        elif character == ")":
            brackets -= 1
        if brackets < 0:
            valid = False
            break

    if brackets != 0:
        valid = False

    payload = {
        "token": valid}
    return payload
