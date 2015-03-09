#!/bin/python

from itertools import combinations, permutations
from itertools import takewhile, dropwhile
from sets import Set
from copy import copy
import networkx as nx

class Downscaler():
    def __init__( self, emu_nodes, graph):
        self.emu_nodes = emu_nodes 
        self.graph = graph
        
        self.paths = []
        self.get_paths()

    def get_paths( self ):
        for flow in self.emu_nodes:
            path = nx.shortest_path( self.graph, flow['src'], flow['dest'] )

            node_types = nx.get_node_attributes( self.graph, 'type' )
            for p in path:
                if node_types.get( p ) != 'interface':
                    path.remove( p )
                    
            path1 = path[0:][::2]
            path2 = path[1:][::2]
            path2.reverse()
            
            path1id = int( flow['id'] )
            path2id = path1id + 1
 
            self.paths.append( {'id': path1id, 'path': path1} )
            self.paths.append( {'id': path2id, 'path': path2} )

        return self.paths

    def get_pipes( self ):
        pipes = []

        path_perms = []
        for path in self.paths:
            path_perms.append( set( path['path'] ) )

        intersections = []
        for p in permutations( path_perms, 2 ):
            temp = set( p[0] ) & set( p[1] )
            if len( temp ) != 0:
                try:
                    intersections.index( temp )
                except:
                    intersections.append( temp )
                    pipes.append( temp )

        for path in self.paths:
            for inter in intersections:
                temp = set( path['path'] ) - inter
                if len( temp ) != 0 and temp != set( path['path'] ):
                    try:
                        pipes.index( temp )
                    except:
                        pipes.append( temp )

        if len( pipes ) == 0:
            pipes = copy( path_perms )    

        i = 0
        for i in range( len( pipes ) ):
            pipes[i] = list( pipes[i] )

        return pipes
