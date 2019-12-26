"""
This solves Coding Challenge 04:
Rotate a list by k elements to the right.
"""

import json


def solve(data):
    """Solving from json data to json token"""
    challenge = json.loads(data)
    k = challenge['k']
    wlist = challenge['list']
    wlist = wlist[(-k % len(wlist)):] + wlist[:(-k % len(wlist))]
    payload = {"token": wlist}
    payload = json.dumps(payload)
    return payload
