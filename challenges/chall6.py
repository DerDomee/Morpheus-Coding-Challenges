"""
This solves Coding Challenge 06:
Convert integer to binary string.
"""

import json


def solve(data):
    """Solving from plain text to json token"""
    i = int(data)
    s = ""
    while i:
        s = str(i % 2) + s
        i = i >> 1
    payload = {"token": s}
    payload = json.dumps(payload)
    return payload
