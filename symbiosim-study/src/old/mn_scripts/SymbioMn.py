#!/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI

from mininet.link import Intf
from mininet.link import Link
from mininet.node import Host, Switch

class SymbioTopo( Topo ):
    def __init__( self ):
        Topo.__init__( self )

        h1 = self.addHost( 'h1' )
        h2 = self.addHost( 'h2' )
        s1 = self.addSwitch( 's1' )

        h3 = self.addHost( 'h3' )
        h4 = self.addHost( 'h4' )
        s2 = self.addSwitch( 's2' )

        self.addLink( h1, s1 )
        self.addLink( h2, s1 )

        self.addLink( s1, s2 )

        self.addLink( h3, s2 )
        self.addLink( h4, s2 )

    def build( self ):

if __name__ == '__main__':
    mytopo = SymbioTopo()

    net = Mininet( topo=mytopo )
    net.start()

    cli = CLI
    cli( net )

    net.stop()
