#!/bin/python

try:
    import xml.etree.cElementTree as ET
    import networkx as nx
    import pprint
except ImportError:
    import xml.etree.ElementTree as ET


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

net = {}

# parse <model>
tree = ET.ElementTree(file='linear.xml')
root = tree.getroot()

# add topNet to net{} -> { 'topNet': {} }
for child in root:
    net.update({child.attrib.get('name'): {}})
    root = child

# for each net in topNet update net{} -> { 'topNet': {'sub1': {}, 'sub2': {} } }
'''
for child in root:
    if child.attrib.get('type') == 'Net':
        net['topNet'].update({child.attrib.get('name'): {}})
        for subchild in child:
            if subchild.attrib.get('type') == 'Host':
                net['topNet'][child.attrib.get('name')].update( {'Host':
                    {'name': subchild.attrib.get('name'), 'interfaces': {} }} )
                for subsubchild in subchild:
                    if subsubchild.attrib.get('type') == 'Interface':
                        net['topNet'][child.attrib.get('name')][subchild.attrib.get('type')]['interfaces'].update(
                                {'name': subsubchild.attrib.get('name')} )

            if subchild.attrib.get('type') == 'Router':
                break; 

            if subchild.attrib.get('type') == 'Link':
                break;

    if child.tag == 'replica':
        net['topNet'].update({child.attrib.get('name'): {}})
'''

#net['topNet'].update( {'subnets': [{}] }  )
topNet = net['topNet']
hasSubnets = False
subnets = []
hasReplicas = False
replicas = []

hosts = []
routers = []
links = []

for child in root:
    if getName( child ) == 'routing':
        topNet.update( {'routing': getType( child )} )

    if hasSubnets == False and getType( child ) == 'Net':
        topNet.update( {'subnets': [{}]} )
        hasSubnets = True

    if getTag( child ) == 'replica':
        replicas.append( (getPath( child ), getName( child )) ) 
        hasReplicas = True

    if getType ( child ) == 'Host':
        newHost = {'name': getName( child )} 
        newHost.update( {'interfaces': []} )
        for interface in child:
            newHost['interfaces'].append( {'name': getName( interface )} )
        hosts.append( newHost )    

    if getType ( child ) == 'Router':
        newRouter = {'name': getName( child )}
        newRouter.update( {'interfaces': []} )
        for interface in child:
            newRouter['interfaces'].append( {'name': getName( interface )} )
        routers.append( newRouter )

    if getType ( child ) == 'Link':
        newLink = {'name': getName( child )}
        linkPath = ''
        for subchild in child:
            if getTag( subchild ) == 'attribute':
                newLink.update( {getName( subchild ): getValue( subchild )} )

            if getTag( subchild ) == 'ref':
                linkPath += getPath( subchild )

        newLink.update( {'path': linkPath} )
        links.append( newLink)


#print net
pprint.pprint( hosts )
pprint.pprint( routers )
pprint.pprint( links )
