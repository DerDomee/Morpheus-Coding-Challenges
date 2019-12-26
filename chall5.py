"""
This solves Coding Challenge 04:
Evaluate a postfix notation string
"""

import json


def solve(data):
    """Solving from plain text to json token"""
    ops = {
        "+": (lambda a, b: a + b),
        "-": (lambda a, b: a - b),
        "*": (lambda a, b: a * b),
        "/": (lambda a, b: a / b),
    }
    tokens = data.split(" ")
    stack = []
    for token in tokens:
        if token in ops:
            arg2 = stack.pop()
            arg1 = stack.pop()
            result = ops[token](arg1, arg2)
            stack.append(result)
        else:
            stack.append(int(token))
    solution = int(stack.pop())
    payload = {"token": solution}
    payload = json.dumps(payload)
    return payload
