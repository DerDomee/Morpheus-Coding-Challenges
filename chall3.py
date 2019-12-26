"""
This solves Coding Challenge 03:
Find the k-largest element in a list.
"""

import json


def solve(data):
    """Solving from json data to json token"""
    challenge = json.loads(data)
    k = challenge['k']
    nlist = sorted(challenge['list'], reverse=True)
    retval = nlist[k-1]
    payload = {"token": retval}
    payload = json.dumps(payload)
    return payload
