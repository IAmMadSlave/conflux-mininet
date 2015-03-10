#!/bin/python

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.cli import CLI

from TrafficMonitor import TrafficMonitor
from TrafficController import TrafficController

import threading

def startMonitor( mn_pipes, demand_file ):
    tm = TrafficMonitor( mn_pipes, demand_file )

def startController( mn_pipes, tc_file, mn_ip, mn ):
    tc = TrafficController( mn_pipes, tc_file, mn_ip, mn )

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

    mn_ip = []
    mn_ip.append( {'name': 'h1', 'ip': leftIP} )
    mn_ip.append( {'name': 'h2', 'ip': rightIP} )

    t1 = threading.Thread( target=startMonitor, args=('mn_pipes_file',
    'demand_file' ) )
    t1.daemon = True

    t2 = threading.Thread( target=startController, args=('mn_pipes_file', 'tc_file',
        mn_ip, net,) )
    t2.daemon = True
    
    t1.start()
    t2.start()

    cli = CLI
    cli( net )

    net.stop

if __name__ == '__main__':
    SymbioTest()
