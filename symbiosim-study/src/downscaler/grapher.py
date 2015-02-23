#!/bin/python

import sys
import json
import networkx as nx

def string_to_number( string ):
    try:
        return int( string )
    except ValueError:
        return float( string )

jsontopology = open( sys.argv[1] )
net = json.load( jsontopology )

g = nx.Graph()

if net['topNet'].has_key( 'hosts' ):
    for host in net['topNet']['hosts']:
        g.add_node( host['name'], interfaces=len( host['interfaces'] ) )
        for interface in host['interfaces']:
            g.add_node( (host['name'], interface['name']),
                    bit_rate=string_to_number( interface['bit_rate'] ), 
                    latency=string_to_number( interface['latency'] ))
            g.add_edge( (host['name'], interface['name']), host['name'] )

if net['topNet'].has_key( 'routers' ):
    for router in net['topNet']['routers']:
        g.add_node( router['name'] )
        for interface in router['interfaces']:
            g.add_node( (router['name'], interface['name']),
                    bit_rate=string_to_number( interface['bit_rate'] ),
                    latency=string_to_number( interface['latency'] ) )
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
        bandwidth=string_to_number( link['bandwidth'] ), 
        delay=string_to_number( link['delay'] ),
        name=link['name'],)

#print '\n\n'
#print 'NODES...'
#for n in g.nodes(data=True):
#    print n

#print 'EDGES...'
#print g.edges(data=True)

print 'SHORTEST PATH FROM H1 TO H2...'
print nx.shortest_path( g, 'h1', 'h2', 'delay' )
