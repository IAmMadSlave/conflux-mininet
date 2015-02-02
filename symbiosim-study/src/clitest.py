#!/usr/bin/python

from mininet.net import Mininet
from mininet.topo import SingleSwitchTopo
from mininet.cli import CLI

import threading
import time
import sys

def startConsole( threadId, net ):
    cli = CLI
    cli( net )
    sys.stdout = sys.__stdout__
    sys.stdin  = sys.__stdin__

if __name__ == '__main__':
    mytopo = SingleSwitchTopo( 2 )
    net = Mininet( topo=mytopo )

    net.start()

    t1 = threading.Thread( target=startConsole, args=( 1, net))
    t1.start()

    h1, h2 = net.getNodeByName( 'h1', 'h2' )

    popens = {}
    popens[1] = h1.popen( "ping -c4 -D %s" % h2.IP() )
    popens[2] = h2.popen( "ping -c4 -D %s" % h1.IP() )
    
    t1.join()

    net.stop() 
