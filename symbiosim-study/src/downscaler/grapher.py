#!/bin/python

import ast
import sys
import json
import networkx as nx

import matplotlib.pyplot as plt

def str_to_num( str ):
    try:
        return int( str )
    except ValueError:
        return float( str )

jsontopology = open( sys.argv[1] )
net = json.load( jsontopology )
net = ast.literal_eval( json.dumps(net) )

g = nx.Graph()

if net['topNet'].has_key( 'hosts' ):
    for host in net['topNet']['hosts']:
        g.add_node( host['name'], interfaces=len( host['interfaces'] ) )
        for interface in host['interfaces']:
            g.add_node( (host['name'], interface['name']),
                    bit_rate=str_to_num( interface['bit_rate'] ), 
                    latency=str_to_num( interface['latency'] ))
            g.add_edge( (host['name'], interface['name']), host['name'] )

if net['topNet'].has_key( 'routers' ):
    for router in net['topNet']['routers']:
        g.add_node( router['name'] )
        for interface in router['interfaces']:
            g.add_node( (router['name'], interface['name']),
                    bit_rate=str_to_num( interface['bit_rate'] ),
                    latency=str_to_num( interface['latency'] ) )
            g.add_edge( (router['name'], interface['name']), router['name'] )

if net['topNet'].has_key( 'links' ):
    for link in net['topNet']['links']:
        path = link['path']
        path = path.replace( '..', '', 1 )
        path = path.split( '..' )
        for i in range( len( path ) ):
            path[i] = path[i].replace( ':', '', 1 )
            path[i] = path[i].split( ':' )
        g.add_edge( tuple( path[0] ), tuple( path[1] ),
        bandwidth=str_to_num( link['bandwidth'] ), 
        delay=str_to_num( link['delay'] ),
        name=link['name'],)

#print '\n\n'
#print 'NODES...'
#for n in g.nodes(data=True):
#    print n

#print 'EDGES...'
#print g.edges(data=True)

print 'SHORTEST PATH FROM H1 TO H2...'
print nx.shortest_path( g, 'h1', 'h2', 'delay' )

pos = nx.spectral_layout(g)
nx.draw_networkx_nodes(g,pos,node_size=350)
nx.draw_networkx_edges(g,pos,width=3)
nx.draw_networkx_labels(g,pos,font_size=10)

plt.axis('off')
plt.savefig("test.png")
plt.show()
