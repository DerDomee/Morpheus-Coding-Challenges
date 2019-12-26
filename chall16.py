"""
This solves Coding Challenge 16:
Calculate the longest consecutive subsequence of numbers in an array.
"""

import json


def solve(challenge):
    """Solving from json data to json token"""
    data = json.loads(challenge)
    nlist = data["list"]
    n = len(nlist)
    s = set(nlist)
    ans = 0
    for ele in nlist:
        s.add(ele)
    for i in range(n):
        if (nlist[i]-1) not in s:
            j = nlist[i]
            while j in s:
                j += 1
            ans = max(ans, j - nlist[i])
    payload = {"token": ans}
    payload = json.dumps(payload)
    return payload
