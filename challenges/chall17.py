"""
This solves Coding Challenge 16:
Calculate the longest consecutive subsequence of numbers in an array.
"""

import json


def solve(challenge):
    """Solving from json data to json token"""
    list = json.loads(challenge)['list']
    checklist = []
    solution = False
    for item in list:
        if item in checklist:
            solution = True
            break
        checklist.append(item)

    payload = {"token": solution}
    payload = json.dumps(payload)
    return payload
