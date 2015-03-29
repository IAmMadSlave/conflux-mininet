#!/bin/python

from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import CPULimitedHost
from mininet.cli import CLI
from mininet.node import OVSController

from TrafficMonitor import TrafficMonitor
#from TrafficController import TrafficController

import os
import time
import threading
import subprocess

def startMonitor( mn_pipes, demand_file ):
    tm = TrafficMonitor( mn_pipes, demand_file )

def startController( mn_pipes, tc_file, mn_ip, mn ):
    tc = TrafficController( mn_pipes, tc_file, mn_ip, mn )

def changeBW( host, bandwidth ):
    time.sleep(3)

def SymbioTest():
    net = Mininet()

    h1 = net.addHost( 'h1' )
    h2 = net.addHost( 'h2' )

    linkopts = dict( bw=10, delay='15ms' )
    l1 = net.addLink( h1, h2, cls=TCLink, **linkopts )

    net.start()
    
    t1 = threading.Thread( target=startMonitor, args=('mn_pipes_file', 'demand_file',) )
    t1.daemon = True
    t1.start()

    net.iperf()
    bws = h1.defaultIntf().bwCmds( bw=5 )
    h1.defaultIntf().tc( bws )
    net.iperf()
    bws = h1.defaultIntf().bwCmds( bw=2 )
    h1.defaultIntf().tc( bws )
    net.iperf()

    #cli = CLI
    #cli( net )

    with open( os.devnull, 'w' ) as fnull:
        subprocess.call( ['sudo', 'killall', 'cat'], stdout=fnull, stderr=fnull )
        subprocess.call( ['sudo', 'killall', 'ovs-controller'], stdout=fnull, stderr=fnull )

    net.stop

if __name__ == '__main__':
    SymbioTest()
