#!/bin/python

try:
    import copy
    import json
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

class Parser():
    def get_name( self, node ):
        return node.attrib.get( 'name' )

    def get_path( self, node ):
        return node.attrib.get( 'path' )

    def get_type( self, node ):
        return node.attrib.get( 'type' )

    def get_tag( self, node ):
        return node.tag

    def get_value( self, node ):
        return node.attrib.get( 'value' )

    def __init__( self, xmlfile ):
        self.net = {}

        self.xmltopology = xmlfile
        tree = ET.ElementTree( file=self.xmltopology )

        self.root = tree.getroot()

        for child in self.root:
            self.net.update( { self.get_name( child ): {}} )
            self.root = child

        self.topnet = self.net['topnet']
    
    def parse_model( self, root, top ):
        for child in root:
            if self.get_name( child ) == 'routing':
                top.update( {'routing': self.get_type( child )} )
                continue

            if self.get_type( child ) == 'Net':
                if top.has_key( 'subnets' ) == False:
                    top.update( {'subnets': []} )

                newsubnet = {'name': self.get_name( child )}
                top['subnets'].append( newsubnet )
                subnetindex = top['subnets'].index( newsubnet )
                self.parse_model( child, top['subnets'][subnetindex] )
                continue

            if self.get_tag( child ) == 'replica':
                for i in range( len( top['subnets'] ) ):
                    if top['subnets'][i].get( 'name' ) == self.get_path( child ):
                        break
                    break
                top['subnets'].append( copy.deepcopy( top['subnets'][i] ) )
                top['subnets'][i+1].update( {'name': self.get_name( child )} )
                continue

            if self.get_type ( child ) == 'Host':
                if top.has_key( 'hosts' ) == False:
                    top.update( {'hosts': []} )

                newhost = {'name': self.get_name( child )} 
                newhost.update( {'interfaces': []} )

                for interface in child:
                    if self.get_type( interface ) == 'Interface':
                        newhost['interfaces'].append( {'name': self.get_name( interface )} )
                        hostindex = newhost['interfaces'].index( {'name': self.get_name( 
                            interface )} )

                        for attribute in interface:
                            if self.get_name( attribute ) == 'latency' or 'bit_rate' or 'emu':
                                newhost['interfaces'][hostindex].update( {self.get_name( attribute ):
                                    self.get_value( attribute )} )

                top['hosts'].append( newhost )
                continue

            if self.get_type ( child ) == 'Router':
                if top.has_key( 'routers' ) == False:
                    top.update( {'routers': []} )
            
                newrouter = {'name': self.get_name( child )}
                newrouter.update( {'interfaces': []} )

                for interface in child:
                    newrouter['interfaces'].append( {'name': self.get_name( interface )} )
                    routerindex = newrouter['interfaces'].index( {'name': self.get_name(
                        interface )} ) 

                    for attribute in interface:
                        if self.get_name( attribute ) == 'latency' or 'bit_rate' or 'emu':
                            newrouter['interfaces'][routerindex].update( {self.get_name( 
                                attribute ): self.get_value( attribute )} )

                top['routers'].append( newrouter )
                continue

            if self.get_type ( child ) == 'Link':
                if top.has_key( 'links' ) == False:
                    top.update( {'links': []} )

                newlink = {'name': self.get_name( child )}
                linkpath = ''

                for subchild in child:
                    if self.get_tag( subchild ) == 'attribute':
                        newlink.update( {self.get_name( subchild ): self.get_value( subchild )} )

                    if self.get_tag( subchild ) == 'ref':
                        linkpath += self.get_path( subchild )

                newlink.update( {'path': linkpath} )

                top['links'].append( newlink )
                continue

    def xml_to_json( self ):
        self.parse_model( self.root, self.topnet )
        
        return self.net

    def write_json( self ):
        jsonfile = self.xmltopology.replace( 'xml', 'json' )

        with open( jsonfile, 'w') as jsonout:
            json.dump( self.net, jsonout )
