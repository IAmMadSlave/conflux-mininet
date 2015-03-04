#!/bin/python

from Parser import Parser
from Grapher import Grapher

import networkx as nx
import http_server
import json
import sys

if __name__ == "__main__":
    p = Parser( sys.argv[1] )
    g = Grapher ( p.xml_to_json() )
    graph = g.json_to_graph()

    for n in graph:
        graph.node[n]['name'] = n

    d = json_graph.node_link_data( graph )
    json.dump( d, open( 'graph.json', 'w' ) )
    http_server.load_url( 'temp.html' )
