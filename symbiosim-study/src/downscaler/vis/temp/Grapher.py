#!/bin/python

import ast
import sys
import json
import networkx as nx

from networkx.readwrite import json_graph

class Grapher():
    def routing_type( self, top ):
        return top['routing']
    
    def str_to_num( self, str ):
        try:
            return int( str )
        except ValueError:
            return float( str )

    def has_subnets( self, top ):
        subnets = None
        if top.has_key( 'subnets' ):
            subnets = []
            for subnet in top['subnets']:
                subnets.append( {'name': subnet['name'], 'nodes': []} )
        return subnets

    def __init__( self, net ):
        #net = ast.literal_eval( json.dumps(net) )
        self.net = net

        #self.g = nx.Graph( routing=self.routing_type( self.net['topnet'] ) )
        self.g = nx.Graph()

        self.subnets = self.has_subnets( self.net['topnet'] )

        if self.subnets is None:
            self.json_to_networkx(self.g, self.net['topnet'])
        else:
            self.json_to_networkx(self.g, self.net['topnet'], self.subnets)

    def json_to_networkx( self, g, top, s=None ):
        if top.has_key( 'subnets' ):
            for subnet in top['subnets']:
                self.json_to_networkx( g, subnet, s )

        if top.has_key( 'hosts' ):
            for host in top['hosts']:
                if s is not None:
                    for i in range( len( s ) ):
                        if self.subnets[i]['name'] == top['name']:
                            nodename = top['name']+':'+host['name']
                            self.subnets[i]['nodes'].append( nodename )
                            break
                        else:
                            continue
                        break
                else:
                    nodename = host['name']
                g.add_node( nodename, type='host',
                        interfaces=len( host['interfaces'] ) )
                for interface in host['interfaces']:
                    interfacename = nodename+':'+interface['name']
                    if s is not None and nodename.find( top['name'] ) > -1:
                        self.subnets[i]['nodes'].append( interfacename )

                    g.add_node( interfacename, type='interface',
                        bit_rate=interface['bit_rate'], 
                        latency=self.str_to_num( interface['latency'] ))
                    g.add_edge( interfacename, nodename )

        if top.has_key( 'routers' ):
            for router in top['routers']:
                if s is not None:
                    for i in range( len( s ) ):
                        if self.subnets[i]['name'] == top['name']:
                            nodename = top['name']+':'+router['name']
                            self.subnets[i]['nodes'].append( nodename )
                            break
                        else:
                            continue
                        break
                else:
                    nodename = router['name']
                g.add_node( nodename, type='router', 
                        interfaces=len( router['interfaces'] ) )
                for interface in router['interfaces']:
                    interfacename = nodename+':'+interface['name']
                    if s is not None and nodename.find( top['name'] ) > -1:
                        self.subnets[i]['nodes'].append( interfacename )
                    
                    g.add_node( interfacename, type='interface',
                        bit_rate=interface['bit_rate'],
                        latency=self.str_to_num( interface['latency'] ) )
                    g.add_edge( interfacename, nodename )

        if top.has_key( 'links' ):
            for link in top['links']:
                path = link['path']
                path = path.replace( '..', '', 1 )
                path = path.split( '..' )

                if top != self.net['topnet'] and s is not None:
                    for i in range( len( s ) ):
                        if self.subnets[i]['name'] == top['name']:
                            for i in range( len( path ) ):
                                path[i] = top['name']+path[i]
                            break
                        else:
                            continue
                        break
                else:
                    for i in range( len( path ) ):
                        path[i] = path[i].replace( ':', '', 1 )
                g.add_edge( path[0], path[1],
                    bandwidth=link['bandwidth'], 
                    delay=self.str_to_num( link['delay'] ),
                    name=link['name'],)

    def get_subnets( self, top ):
        subnets = []
        if top.has_key( 'subnets'):
            for s in top['subnets']:
                subnets.append( s['name'] )
        return subnets

    def json_to_graph( self ):

        return self.g

    
