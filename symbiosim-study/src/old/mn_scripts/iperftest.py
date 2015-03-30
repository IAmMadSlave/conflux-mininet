#!/usr/bin/python

from mininet.net  import Mininet
from mininet.topo import SingleSwitchTopo
from mininet.cli  import CLI

import threading
import time
import sys

def startConsole( tid, net ):
    cli = CLI
    cli( net )
    sys.stdout = sys.__stdout__
    sys.stdin  = sys.__stdin__

if __name__ == '__main__':
    mytopo = SingleSwitchTopo( 2 )
    net = Mininet( topo=mytopo )

    net.start()
    
    thread1 = threading.Thread( target=startConsole, args=( 1, net ) )
    thread1.start()

    h1, h2 = net.getNodeByName( 'h1', 'h2' )
    
    h1log = open( 'h1.log', 'w' )
    h2log = open( 'h2.log', 'w' )

    popens = {}
    popens[1] = h1.popen( "iperf -s" )
    popens[2] = h2.popen( "iperf -c %s -t 10" % h1.IP() )

    popens[3] = h1.popen( ["./ss_test.sh"], stdout=h1log )
    popens[4] = h2.popen( ["./ss_test.sh"], stdout=h2log )

    #out = popens[4].communicate()

    time.sleep( 10 )

    popens[1].terminate()
    popens[2].terminate()

    ret1 = popens[3].wait()
    ret2 = popens[4].wait()

    h1log.flush()
    h2log.flush()
    
    thread1.join()

    net.stop() 
