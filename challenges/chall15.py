"""
This solves Coding Challenge 15:
Check if a string is a palindrome. Ignore all punctuation.#
Only A-Za-z are relevant for the check.
"""

import json


def solve(challenge):
    """Solving from json data to json token"""
    data = json.loads(challenge)
    text = data["word"].lower()
    for character in " ,;'?!.:-_`´\"§$%&/()=#\n":
        text = text.replace(character, '')
    solution = False
    if text == text[::-1]:
        solution = True
    payload = {"token": solution}
    payload = json.dumps(payload)
    return payload
