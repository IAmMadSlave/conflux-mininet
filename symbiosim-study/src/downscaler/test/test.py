#!/bin/python

import fuckit
import itertools
from sets import Set

f1 = Set(['A', 'C', 'D', 'E'])
f2 = Set(['B', 'C', 'D', 'E'])
f3 = Set(['B', 'G'])

flows = [f1, f2, f3]

universe = f1 | f2 | f3


intersects = []

for i in range( len( flows ) ):
    for j in range( len( flows ) -1 ):
        if i != j:
            intersects.append( flows[i] & flows[j] )

for i in intersects:
    if len(i) == 0:
        intersects.remove(i)

for i in intersects:
    universe -= i

universe = list(universe)

for i in intersects:
    i = list(i)
    try:
        if universe.index(i) != -1:
            universe.append(i)
    except Exception:
        pass

print universe

