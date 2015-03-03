#!/bin/python

import sys
from Parser import Parser
from Grapher import Grapher
from Flows import Flows

import networkx as nx

if __name__ == "__main__":
    p = Parser( sys.argv[1] )
    net = p.xml_to_json()

    g = Grapher( net )
    graph = g.json_to_graph()

    print 'Please select nodes to be emulated (e.g., h1, h2, h3)..'
    i = 1
    for n in graph.nodes( data=True ):
        if n[1].get( 'type' ) == 'host':
            print str(i)+'. '+n[0]
            i = i + 1

    emu_nodes = raw_input( 'Emulated nodes: ')
    emu_nodes = emu_nodes.split( ',' )
    # perhaps we should sanitize the list here?

    f = Flows(emu_nodes, graph)
    f.get_path()
    f.get_flows()
