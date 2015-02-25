#!/bin/python

import ast
import sys
import json
import networkx as nx

import matplotlib.pyplot as plt

def routing_type( top ):
    return top['routing']
    
def str_to_num( str ):
    try:
        return int( str )
    except ValueError:
        return float( str )

def has_subnets( top ):
    subnets = None
    if top.has_key( 'subnets' ):
        subnets = []
        for subnet in top['subnets']:
            subnets.append( {'name': subnet['name'], 'nodes': []} )
    return subnets

def json_to_networkx( g, top, s=None ):
    if top.has_key( 'hosts' ):
        for host in top['hosts']:
            g.add_node( host['name'], interfaces=len( host['interfaces'] ) )
            for interface in host['interfaces']:
                g.add_node( (host['name'], interface['name']),
                    bit_rate=str_to_num( interface['bit_rate'] ), 
                    latency=str_to_num( interface['latency'] ))
                g.add_edge( (host['name'], interface['name']), host['name'] )

    if top.has_key( 'routers' ):
        for router in top['routers']:
            g.add_node( router['name'] )
            for interface in router['interfaces']:
                g.add_node( (router['name'], interface['name']),
                    bit_rate=str_to_num( interface['bit_rate'] ),
                    latency=str_to_num( interface['latency'] ) )
                g.add_edge( (router['name'], interface['name']), router['name'] )

    if top.has_key( 'links' ):
        for link in top['links']:
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

jsontopology = open( sys.argv[1] )
net = json.load( jsontopology )
net = ast.literal_eval( json.dumps(net) )

g = nx.Graph( routing=routing_type( net['topNet'] ) )

subnets = has_subnets( net['topNet'] )

if subnets is None:
    json_to_networkx(g, net['topNet'])
else:
    json_to_networkx(g, net['topNet'], subnets)


# adding nodes to subnets
'''
print 'BEFORE...'
print subnets

for i in range( len( subnets ) ):
    if subnets[i]['name'] == 'sub1':
        subnets[i][''].append('h1')

print '\nAFTER...'
print subnets
'''

# shortest path calculation
#print nx.shortest_path( g, 'h1', 'h2', 'delay' )

# test
print 'NODES...'
print g.nodes()
print '\nEDGES...'
print g.edges()

pos = nx.spectral_layout(g)
nx.draw_networkx_nodes(g,pos,node_size=350)
nx.draw_networkx_edges(g,pos,width=3)
nx.draw_networkx_labels(g,pos,font_size=10)

plt.axis('off')
plt.savefig("test.png")
