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

        self.emuhosts = []
    
    def parse_model( self, root, top ):
        for child in root:
            if self.get_name( child ) == 'routing':
                top.update( {'routing': self.get_type( child )} )
                continue

            if self.get_type( child ) == 'Net':
                if top.has_key( 'subnets' ) == False:
                    top.update( {'subnets': []} )

                fullname = 'topnet:'
                if self.get_name( root ) != 'topnet':
                    fullname = fullname + self.get_name( root ) + ':'
                
                newsubnet = {'name': fullname + self.get_name( child )}
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

                fullname = 'topnet:'
                if self.get_name( root ) != 'topnet':
                    fullname = fullname + self.get_name( root ) + ':'

                fullname = fullname + self.get_name( child )

                newhost = {'name': fullname } 
                newhost.update( {'interfaces': []} )

                for interface in child:
                    if self.get_type( interface ) == 'Sender':
                        for attribute in interface:
                            found = False
                            for e in self.emuhosts:
                                if e.get( 'id') == self.get_value( attribute ):
                                    e.update( {'src': fullname} )
                                    found = True
                            if not found:
                                self.emuhosts.append( {'id': self.get_value(
                                    attribute ), 'src': fullname} )

                    if self.get_type( interface ) == 'Receiver':
                        for attribute in interface:
                            found = False
                            for e in self.emuhosts:
                                if e.get( 'id' ) == self.get_value( attribute ):
                                    e.update( {'dest': fullname} )
                                    found = True
                            if not found:
                                self.emuhosts.append( {'id': self.get_value(
                                    attribute ), 'dest': fullname} )

                    if self.get_type( interface ) == 'Interface':
                        intfullname = fullname + ':' + self.get_name( interface )
                        newhost['interfaces'].append( {'name': intfullname} )
                        hostindex = newhost['interfaces'].index( {'name':
                            intfullname} )

                        for attribute in interface:
                            newhost['interfaces'][hostindex].update( {self.get_name( attribute ):
                                self.get_value( attribute )} )

                top['hosts'].append( newhost )
                continue

            if self.get_type ( child ) == 'Router':
                if top.has_key( 'routers' ) == False:
                    top.update( {'routers': []} )

                fullname = 'topnet:'
                if self.get_name( root ) != 'topnet':
                    fullname = fullname + self.get_name( root ) + ':'

                fullname = fullname + self.get_name( child )
            
                newrouter = {'name':  fullname}
                newrouter.update( {'interfaces': []} )

                for interface in child:
                    intfullname = fullname + ':' + self.get_name( interface )
                    newrouter['interfaces'].append( {'name': intfullname} )
                    routerindex = newrouter['interfaces'].index( {'name':
                        intfullname} ) 

                    for attribute in interface:
                        newrouter['interfaces'][routerindex].update( {self.get_name( 
                            attribute ): self.get_value( attribute )} )

                top['routers'].append( newrouter )
                continue

            if self.get_type ( child ) == 'Link':
                fullname = 'topnet:'
                if self.get_name( root ) != 'topnet':
                    fullname = fullname + self.get_name( root ) + ':'

                if top.has_key( 'links' ) == False:
                    top.update( {'links': []} )

                newlink = {'name': fullname + self.get_name( child )}
                linkpath = ''

                for subchild in child:
                    if self.get_tag( subchild ) == 'attribute':
                        newlink.update( {self.get_name( subchild ): self.get_value( subchild )} )

                    if self.get_tag( subchild ) == 'ref':
                        link = self.get_path( subchild )
                        link = link.replace( '..', '', 1 )
                        link = link.replace( ':', '', 1 )
                        link = fullname + link
                        link = '..' +  link
                        linkpath += link

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

    def emuflows( self ):
        return self.emuhosts
