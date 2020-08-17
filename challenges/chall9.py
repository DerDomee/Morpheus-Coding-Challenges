"""
This solves Coding Challenge 07:
Given a number k, find two numbers in a list that add to k.
"""

import json
import sys


def solve(data):
    """Solving from json data to json token"""
    challenge = json.loads(data)
    k = challenge['k']
    nlist = challenge['list']
    solution = []
    shortest_distance = sys.maxsize

    for i_key, i_val in enumerate(nlist):
        for j_key, j_val in enumerate(nlist):
            if i_val + j_val == k:
                current_distance = abs(i_key - j_key)
                if current_distance < distance:
                    solution = [i_key, j_key]
                    shortest_distance = current_distance

    payload = {"token": solution}
    payload = json.dumps(payload)
    return payload
