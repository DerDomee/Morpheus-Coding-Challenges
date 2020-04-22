"""
This solves Coding Challenge 07:
Given a number k, find two numbers in a list that add to k.
"""

import json


def solve(data):
    """Solving from json data to json token"""
    challenge = json.loads(data)
    k = challenge['k']
    nlist = challenge['list']
    solution = []
    for i in range(len(nlist)):
        for j in range(len(nlist)):
            if nlist[i] + nlist[j] == k:
                solution.append(i)
                solution.append(j)
        if not len(solution) == 0:
            break
    payload = {"token": solution}
    payload = json.dumps(payload)
    return payload
