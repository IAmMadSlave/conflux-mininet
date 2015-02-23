#!/bin/python

try:
    import xml.etree.cElementTree as ET
    import networkx as nx
    import pprint
    import copy
except ImportError:
    import xml.etree.ElementTree as ET

net = {}

def getName( node ):
    return node.attrib.get( 'name' )

def getPath( node ):
    return node.attrib.get( 'path' )

def getType( node ):
    return node.attrib.get( 'type' )

def getTag( node ):
    return node.tag

def getValue( node ):
    return node.attrib.get( 'value' )

def parseModel( root, top ):
    for child in root:
        if getName( child ) == 'routing':
            top.update( {'routing': getType( child )} )
            continue

        if getType( child ) == 'Net':
            if top.has_key( 'subnets' ) == False:
                top.update( {'subnets': []} )

            newSubnet = {'name': getName( child )}
            top['subnets'].append( newSubnet )
            subnetIndex = top['subnets'].index( newSubnet )
            parseModel( child, top['subnets'][subnetIndex] )
            continue

        if getTag( child ) == 'replica':
            for i in range( len( top['subnets'] ) ):
                if top['subnets'][i].get( 'name' ) == getPath( child ):
                    break
                break
            top['subnets'].append( copy.deepcopy( top['subnets'][i] ) )
            top['subnets'][i+1].update( {'name': getName( child )} )
            continue

        if getType ( child ) == 'Host':
            if top.has_key( 'hosts' ) == False:
                top.update( {'hosts': []} )

            newHost = {'name': getName( child )} 
            newHost.update( {'interfaces': []} )

            for interface in child:
                newHost['interfaces'].append( {'name': getName( interface )} )
                hostIndex = newHost['interfaces'].index( {'name': getName( 
                    interface )} )

                for attribute in interface:
                    newHost['interfaces'][hostIndex].update( {getName( attribute ):
                        getValue( attribute )} )

            top['hosts'].append( newHost )
            continue

        if getType ( child ) == 'Router':
            if top.has_key( 'routers' ) == False:
                top.update( {'routers': []} )
            
            newRouter = {'name': getName( child )}
            newRouter.update( {'interfaces': []} )

            for interface in child:
                newRouter['interfaces'].append( {'name': getName( interface )} )
                routerIndex = newRouter['interfaces'].index( {'name': getName(
                    interface )} ) 

                for attribute in interface:
                    newRouter['interfaces'][routerIndex].update( {getName( 
                        attribute ): getValue( attribute )} )

            top['routers'].append( newRouter )
            continue

        if getType ( child ) == 'Link':
            if top.has_key( 'links' ) == False:
                top.update( {'links': []} )

            newLink = {'name': getName( child )}
            linkPath = ''

            for subchild in child:
                if getTag( subchild ) == 'attribute':
                    newLink.update( {getName( subchild ): getValue( subchild )} )

                if getTag( subchild ) == 'ref':
                    linkPath += getPath( subchild )

            newLink.update( {'path': linkPath} )

            top['links'].append( newLink )
            continue


#tree = ET.ElementTree(file='linear.xml')
#tree = ET.ElementTree(file='dumbbellwithreplica.xml')
tree = ET.ElementTree(file='dumbbellnoreplica.xml')

root = tree.getroot()

# add topNet to net{} -> { 'topNet': {} }
for child in root:
    net.update({child.attrib.get('name'): {}})
    root = child

topNet = net['topNet']

parseModel( root, topNet )

pprint.pprint( net )
