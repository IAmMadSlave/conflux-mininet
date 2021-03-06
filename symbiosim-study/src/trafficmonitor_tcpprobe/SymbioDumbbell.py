#!/bin/python

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.node import CPULimitedHost
from mininet.cli import CLI
from mininet.node import OVSController

from TrafficMonitor import TrafficMonitor
#from TrafficController import TrafficController

import threading
import subprocess

def startMonitor( mn_pipes, demand_file ):
    tm = TrafficMonitor( mn_pipes, demand_file )

def startController( mn_pipes, tc_file, mn_ip, mn ):
    tc = TrafficController( mn_pipes, tc_file, mn_ip, mn )

class SymbioTopo( Topo ):
    def __init__( self ):
        Topo.__init__( self )

        leftHost = self.addHost( 'h1' )
        #leftHost = self.addHost( 'h1', cls=CPULimitedHost, cpu=.5 )

        rightHost = self.addHost( 'h2' )
        #rightHost = self.addHost( 'h2', cls=CPULimitedHost, cpu=.5 )

        linkopts = dict( bw=10, delay='15ms' )
        self.addLink( leftHost, rightHost, cls=TCLink, **linkopts )
        
def SymbioTest():
    topo = SymbioTopo()
    net = Mininet( topo=topo, controller=OVSController, link=TCLink )
    #net = Mininet( topo=topo, host=CPULimitedHost, controller=OVSController, link=TCLink )

    net.start()
  
    t1 = threading.Thread( target=startMonitor, args=('mn_pipes_file', 'demand_file',) )
    t1.daemon = True
    t1.start()

    cli = CLI
    cli( net )

    subprocess.call( ['sudo', 'killall', 'cat'] )
    subprocess.call( ['sudo', 'killall', 'ovs-controller'] )

    net.stop

if __name__ == '__main__':
    SymbioTest()
