#!/bin/python

try:
    import xml.etree.cElementTree as ET
    #import pprint
    import copy
    import sys
    import json
except ImportError:
    import xml.etree.ElementTree as ET

net = {}

def get_name( node ):
    return node.attrib.get( 'name' )

def get_path( node ):
    return node.attrib.get( 'path' )

def get_type( node ):
    return node.attrib.get( 'type' )

def get_tag( node ):
    return node.tag

def get_value( node ):
    return node.attrib.get( 'value' )

def parse_model( root, top ):
    for child in root:
        if get_name( child ) == 'routing':
            top.update( {'routing': get_type( child )} )
            continue

        if get_type( child ) == 'Net':
            if top.has_key( 'subnets' ) == False:
                top.update( {'subnets': []} )

            newsubnet = {'name': get_name( child )}
            top['subnets'].append( newsubnet )
            subnetindex = top['subnets'].index( newsubnet )
            parse_model( child, top['subnets'][subnetindex] )
            continue

        if get_tag( child ) == 'replica':
            for i in range( len( top['subnets'] ) ):
                if top['subnets'][i].get( 'name' ) == get_path( child ):
                    break
                break
            top['subnets'].append( copy.deepcopy( top['subnets'][i] ) )
            top['subnets'][i+1].update( {'name': get_name( child )} )
            continue

        if get_type ( child ) == 'Host':
            if top.has_key( 'hosts' ) == False:
                top.update( {'hosts': []} )

            newhost = {'name': get_name( child )} 
            newhost.update( {'interfaces': []} )

            for interface in child:
                newhost['interfaces'].append( {'name': get_name( interface )} )
                hostindex = newhost['interfaces'].index( {'name': get_name( 
                    interface )} )

                for attribute in interface:
                    newhost['interfaces'][hostindex].update( {get_name( attribute ):
                        get_value( attribute )} )

            top['hosts'].append( newhost )
            continue

        if get_type ( child ) == 'Router':
            if top.has_key( 'routers' ) == False:
                top.update( {'routers': []} )
            
            newrouter = {'name': get_name( child )}
            newrouter.update( {'interfaces': []} )

            for interface in child:
                newrouter['interfaces'].append( {'name': get_name( interface )} )
                routerindex = newrouter['interfaces'].index( {'name': get_name(
                    interface )} ) 

                for attribute in interface:
                    newrouter['interfaces'][routerindex].update( {get_name( 
                        attribute ): get_value( attribute )} )

            top['routers'].append( newrouter )
            continue

        if get_type ( child ) == 'Link':
            if top.has_key( 'links' ) == False:
                top.update( {'links': []} )

            newlink = {'name': get_name( child )}
            linkpath = ''

            for subchild in child:
                if get_tag( subchild ) == 'attribute':
                    newlink.update( {get_name( subchild ): get_value( subchild )} )

                if get_tag( subchild ) == 'ref':
                    linkpath += get_path( subchild )

            newlink.update( {'path': linkpath} )

            top['links'].append( newlink )
            continue

xmltopology = sys.argv[1]
tree = ET.ElementTree( file=xmltopology )

root = tree.getroot()

for child in root:
    net.update( {get_name( child ): {}} )
    root = child

topnet = net['topNet']

parse_model( root, topnet )

#pprint.pprint( net )

jsontopology = xmltopology.replace( '.xml', '.json' )
jsonfile = open( jsontopology, 'wb' )
json.dump( net, jsonfile, sort_keys=True, indent=4, separators=(',', ': '))
jsonfile.close()
