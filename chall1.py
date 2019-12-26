"""
This solves Coding Challenge 01:
Read the contents of the challenge interface. Return the content back in json.
"""

import json


def solve(challenge):
    """Solving Challenge"""
    payload = {"token": challenge}
    payload = json.dumps(payload)
    return payload
