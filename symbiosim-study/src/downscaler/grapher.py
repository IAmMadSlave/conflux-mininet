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
    if top.has_key( 'subnets' ):
        for subnet in top['subnets']:
            json_to_networkx( g, subnet, s )

    if top.has_key( 'hosts' ):
        for host in top['hosts']:
            if s is not None:
                for i in range( len( s ) ):
                    if subnets[i]['name'] == top['name']:
                        nodename = top['name']+':'+host['name']
                        subnets[i]['nodes'].append( nodename )
                        break
                    else:
                        continue
                    break
            else:
                nodename = host['name']
            g.add_node( nodename, interfaces=len( host['interfaces'] ) )
            for interface in host['interfaces']:
                interfacename = nodename+':'+interface['name']
                if s is not None and nodename.find( top['name'] ) > -1:
                    subnets[i]['nodes'].append( interfacename )

                g.add_node( interfacename,
                    bit_rate=str_to_num( interface['bit_rate'] ), 
                    latency=str_to_num( interface['latency'] ))
                g.add_edge( interfacename, nodename )

    if top.has_key( 'routers' ):
        for router in top['routers']:
            if s is not None:
                for i in range( len( s ) ):
                    if subnets[i]['name'] == top['name']:
                        nodename = top['name']+':'+router['name']
                        subnets[i]['nodes'].append( nodename )
                        break
                    else:
                        continue
                    break
            else:
                nodename = router['name']
            g.add_node( nodename )
            for interface in router['interfaces']:
                interfacename = nodename+':'+interface['name']
                if s is not None and nodename.find( top['name'] ) > -1:
                    subnets[i]['nodes'].append( interfacename )
                    
                g.add_node( interfacename,
                    bit_rate=str_to_num( interface['bit_rate'] ),
                    latency=str_to_num( interface['latency'] ) )
                g.add_edge( interfacename, nodename )

    if top.has_key( 'links' ):
        for link in top['links']:
            path = link['path']
            path = path.replace( '..', '', 1 )
            path = path.split( '..' )

            if top != net['topNet'] and s is not None:
                for i in range( len( s ) ):
                    if subnets[i]['name'] == top['name']:
                        for i in range( len( path ) ):
                            path[i] = top['name']+':'+path[i]
                        break
                    else:
                        continue
                    break
            else:
                for i in range( len( path ) ):
                    path[i] = path[i].replace( ':', '', 1)
'''
            g.add_edge( path[0], path[1],
                bandwidth=str_to_num( link['bandwidth'] ), 
                delay=str_to_num( link['delay'] ),
                name=link['name'],)
'''
jsontopology = open( sys.argv[1] )
net = json.load( jsontopology )
net = ast.literal_eval( json.dumps(net) )

g = nx.Graph( routing=routing_type( net['topNet'] ) )

subnets = has_subnets( net['topNet'] )

if subnets is None:
    json_to_networkx(g, net['topNet'])
else:
    json_to_networkx(g, net['topNet'], subnets)


print 'SUBNETS...'
print subnets

# shortest path calculation
#print nx.shortest_path( g, 'h1', 'h2', 'delay' )

# test
print '\nNODES...'
print g.nodes()
print '\nEDGES...'
print g.edges()

pos = nx.random_layout(g)
nx.draw_networkx_nodes(g,pos,node_size=700)
nx.draw_networkx_edges(g,pos,width=3)
nx.draw_networkx_labels(g,pos,font_size=10)

plt.axis('off')
plt.savefig("test.png")
