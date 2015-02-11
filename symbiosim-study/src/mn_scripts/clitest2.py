#!/usr/bin/python

from mininet.net import Mininet
from mininet.topo import SingleSwitchTopo
from mininet.cli import CLI

import threading
import time
import sys

def startMn( threadId, net ):
    net.start()
    
    h1, h2 = net.getNodeByName( 'h1', 'h2' )

    popens = {}
    popens[1] = h1.popen( "ping -c4 -D %s" % h2.IP() )
    popens[2] = h2.popen( "ping -c4 -D %s" % h1.IP() )
    
    popens[1].wait()
    popens[2].wait()
   

if __name__ == '__main__':
    mytopo = SingleSwitchTopo( 3 )
    net = Mininet( topo=mytopo )

    t1 = threading.Thread( target=startMn, args=( 1, net))
    t1.start()

    cli = CLI
    cli( net )
    sys.stdout = sys.__stdout__
    sys.stdin  = sys.__stdin__
    
    t1.join()

    net.stop() 
