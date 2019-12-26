"""
This solves Coding Challenge 02:
Find an element in a list. Return the index of this element.
"""

import json


def solve(data):
    """Solving from json data to json token"""
    challenge = json.loads(data)
    number = challenge["k"]
    liste = challenge["list"]
    index = -1
    for i in liste:
        if i == number:
            index = liste.index(i)
            break
    retval = {"token": index}
    retval = json.dumps(retval)
    return retval
