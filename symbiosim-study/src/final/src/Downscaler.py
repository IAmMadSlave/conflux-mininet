#!/bin/python

from itertools import combinations, permutations
from itertools import takewhile, dropwhile
from sets import Set
import networkx as nx

class Downscaler():
    def __init__( self, emu_nodes, graph):
        self.emu_nodes = emu_nodes 
        self.graph = graph
        
        self.paths = []

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

    def get_flows( self ):
        universe = set()

        for path in self.paths:
            universe = universe | set( path['path'] )
        
        print 'UNIVERSE...'
        for u in universe:
            print u

