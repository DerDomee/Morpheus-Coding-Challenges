"""
This solves Coding Challenge 08:
Given a number k, find four numbers in a list that add to k.
"""

import json


def solve(data):
    """Solving from json data to json token"""
    challenge = json.loads(data)
    k = challenge['k']
    nlist = challenge['list']

    def evalsum(nlist, k):
        slist = sorted(nlist)
        for i in range(len(slist) - 3):
            for j in range(i + 1, len(slist) - 2):
                n = j + 1
                m = len(slist) - 1
                while n < m:
                    if slist[i] + slist[j] + slist[n] + slist[m] < k:
                        n += 1
                    elif slist[i] + slist[j] + slist[n] + slist[m] > k:
                        m -= 1
                    else:
                        solution = [nlist.index(
                            slist[i]),
                            nlist.index(slist[j]),
                            nlist.index(slist[n]),
                            nlist.index(slist[m])]
                        return solution
    # enddef evalsum

    payload = {"token": evalsum(nlist, k)}
    payload = json.dumps(payload)
    return payload
