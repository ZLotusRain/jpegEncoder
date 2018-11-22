
import math

def calculate(x):
    if x == 0:
        return math.sqrt(2)/2
    else:
        return 1

def makeEmptyList(m,n):
    l = []
    for i in range(m):
        sublist = []
        for j in range(n):
            sublist.append(0)
        l.append(sublist)
    return l