"""
This solves Coding Challenge 18:
Check if a list contains duplicates with distance of k to checked object.
"""

import json


def solve(challenge):
    """Solving from json data to json token"""
    jsonobj = json.loads(challenge)
    list = jsonobj['list']
    k = jsonobj['k']
    checklist = []
    solution = False
    for item in list:
        for i in range(item-k, item+k+1):
            if i in checklist:
                solution = True
                break
        if solution:
            break
        checklist.append(item)

    payload = {"token": solution}
    payload = json.dumps(payload)
    return payload
