"""
This solves Coding Challenge 10:
From a plaintext string containing a float, convert that string
to a float data type
"""

import json
import sys


def solve(data):
    """Solving from plaintext data to json token"""
    # Lol ik this is the dumb hacky way.
    solution = float(data)

    payload = {"token": solution}
    payload = json.dumps(payload)
    return payload
