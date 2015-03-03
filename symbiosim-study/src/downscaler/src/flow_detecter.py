#!/bin/python

from pprint import pprint
from itertools import combinations
from sets import Set

f1 = Set(['A', 'C', 'D', 'E'])
f2 = Set(['B', 'C', 'D', 'E'])
f3 = Set(['B', 'G'])

flows = [f1, f2, f3]

universe = f1 | f2 | f3

intersections = []

for c in combinations( flows, 2 ):
    intersect = c[0] & c[1]    
    if len( intersect ) != 0:
        intersections.append( intersect )

for i in intersections:
    universe -= i

universe = list( universe )

for i in range( len( universe ) ):
    universe[i] = [ universe[i] ]

for i in intersections:
    try:
        universe.index( list( i ) )
    except Exception:
        universe.append( list( i ) )

i = 0
for u in universe:
    print 'flow', str( i ) + ': ' + '%s' % ', '.join( map( str, u ) )
    i = i + 1
