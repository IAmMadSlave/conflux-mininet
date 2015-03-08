#!/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI

#from mininet.link import Intf
#from mininet.link import Link
#from mininet.node import Host, Switch

class SymbioTopo( Topo ):
    def __init__( self, topo, pipes ):
        #Topo.__init__( self )
        
        self.topo = topo
        self.topo = self.topo['topnet']

        self.pipes = pipes

        self.hosts = []
        self.switches = []

    def getHosts( self ):
        if self.topo.has_key( 'subnets' ):
            for subnet in self.topo['subnets']:
                if subnet.has_key( 'hosts' ):
                    for host in subnet['hosts']:
                        if host.has_key( 'interfaces' ):
                            for interface in host['interfaces']:
                                for pipe in self.pipes:
                                    for p in pipe:
                                        if interface['name'] == p:
                                            hostname = host.get( 'name' )
                                            try:
                                                self.hosts.index( hostname )
                                            except:
                                                self.hosts.append( hostname )
                if subnet.has_key( 'routers' ):
                    for router in subnet['routers']:
                        if router.has_key( 'interfaces' ):
                            for interface in router['interfaces']:
                                for pipe in self.pipes:
                                    for p in pipe:
                                        if interface['name'] == p:
                                            routername = router.get( 'name' ) 
                                            try:
                                                self.switches.index( routername )
                                            except:
                                                self.switches.append( routername )
                        
        for h in self.hosts:
            print h

        for s in self.switches:
            print s

'''
if __name__ == '__main__':
    mytopo = SymbioTopo()

    net = Mininet( topo=mytopo )
    net.start()

    cli = CLI
    cli( net )

    net.stop()
'''
