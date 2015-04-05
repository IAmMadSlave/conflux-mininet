#!/bin/python

from itertools import combinations, permutations
from itertools import takewhile, dropwhile
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
        
        print 'UNIVERSE...'
        for u in universe:
            print u

        intersections = []

        for c in combinations( self.paths, 2 ):
            intersect = set( c[0] ) & set( c[1] )
            if len( intersect ) != 0:
                intersections.append( intersect )

        if len( intersections) == 0:
            print 'NO INTERSECTIONS...'
        else:
            for i in range( len( self.paths ) ):
                for intersect in intersections:
                    flag = False
                    for element in intersect:
                        ind = self.paths[i].index( element )
                        self.paths[i].remove( element )
                        if flag == False:
                            self.paths[i].insert( ind, '' )
                            flag = True


        for p in self.paths:
        # do something here

            self.flows.append( p )

        for i in intersections:
            self.flows.append( list( i ) )

            '''
            print 'INTERSECTIONS...'
            for i in intersections:
                universe -= i
                print i

            universe = list( universe )
            print 'UNIVERSE-INTERSECTIONS...'
            for u in universe:
                print u

            for i in range( len( universe ) ):
                universe[i] = [ universe[i] ]

            for i in intersections:
                try:
                    universe.index( list( i ) )
                except Exception:
                    universe.append( list( i ) )

            self.flows = universe
            '''

        print 'FLOWS...'
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
