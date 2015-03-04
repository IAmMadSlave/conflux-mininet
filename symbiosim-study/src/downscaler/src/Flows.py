#!/bin/python

from pprint import pprint
from itertools import combinations
from itertools import permutations
from sets import Set
import networkx as nx

class Flows():
    def __init__( self, emu_nodes, graph):
        self.flows = []
        self.paths = []
        self.emu_nodes = emu_nodes 
        self.graph = graph

    def get_path( self ):
        #for p in permutations( self.emu_nodes, 2 ):
        for p in self.emu_nodes:
            path = nx.shortest_path( self.graph, p[0].strip(), p[1].strip() )
            self.paths.append( path )

        return self.paths

    def get_flows( self ):
        universe = set().union( *self.paths )

        intersections = []

        for c in combinations( self.paths, 2 ):
            intersect = set( c[0] ) & set( c[1] )

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

        self.flows = universe

        for f in self.flows:
            print f
'''
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
'''
