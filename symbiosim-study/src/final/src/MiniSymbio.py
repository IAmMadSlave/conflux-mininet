#!/bin/python

import sys
from Parser import Parser
from Grapher import Grapher
from Downscaler import Downscaler

from TrafficMonitor import TrafficMonitor

import networkx as nx

if __name__ == "__main__":
    # start parser with command line arg
    p = Parser( sys.argv[1] )

    # this is the topology in json
    net = p.xml_to_json()

    # list of emulated flows
    emuflows = p.emuflows()

    from pprint import pprint
    pprint( net, width=1 )
   
    print '\n' 

    # translate to networkx 
    graph = Grapher( net )
    
    g = graph.json_to_graph()
  
    for n in g.nodes():
        print n
    '''
    d = Downscaler( emuflows, g ) 
    paths = d.get_paths()

    for p in paths:
        print p

    print '\n'

    d.get_flows()
    '''
