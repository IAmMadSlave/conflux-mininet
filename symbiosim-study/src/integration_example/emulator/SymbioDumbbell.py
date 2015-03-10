#!/bin/python

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import TCLink

class SingleSwitchTopo( Topo ):
    def build( self, n=2 ):
        switch = self.addSwitch( 's1' )

        leftHost = self.addHost( 'h1' )
        rightHost = self.addHost( 'h2' )

        self.addLink( leftHost, switch, 
                bw=1000, delay='0.001s' )
        
        self.addLink( rightHost, switch,
                bw=1000, delay='1s' )
                
def SymbioTest():
    topo = SingleSwitchTopo()
    net = Mininet( topo=topo, link=TCLink )

    net.start()

    left = net.getNodeByName( 'h1' )
    leftIP = left.IP()

    right = net.getNodeByName( 'h2' )
    rightIP = right.IP()

    
