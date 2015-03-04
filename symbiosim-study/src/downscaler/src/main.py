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

    print 'Enter a flow between two hosts (e.g., h1, h2)'
    i = 1
    for n in graph.nodes( data=True ):
        if n[1].get( 'type' ) == 'host':
            print str(i)+'. '+n[0]
            i = i + 1

    flows = []
    flow = 'default'
    while flow != '':
        flow = raw_input( 'Flow: ')
        if flow != '':
            flows.append( flow.split( ',' ) )
    # perhaps we should sanitize the list here?

    f = Flows(flows, graph)
    paths = f.get_path()

    print '\n'
    for p in paths:
        print p

    print '\n'
    f.get_flows()
