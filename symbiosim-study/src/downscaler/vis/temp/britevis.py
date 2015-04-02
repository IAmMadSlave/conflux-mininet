#!/bin/python


from networkx.readwrite import json_graph

import networkx as nx
import fnss
import json
import sys

if __name__ == "__main__":
    graph = fnss.parse_brite( sys.argv[1] )    

    for n in graph:
        graph.node[n]['name'] = n

    d = json_graph.node_link_data( graph )
    json.dump( d, open( 'graph.json', 'w' ) )
