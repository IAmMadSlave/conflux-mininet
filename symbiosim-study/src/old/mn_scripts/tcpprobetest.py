#!/usr/bin/python

"""Start logging before executing script """
from mininet.net  import Mininet
from mininet.topo import SingleSwitchTopo
from mininet.cli  import CLI

import threading
import time
import sys
        
def tcpprobe_log( tid, net ):
    hosts = {}
    h1, h2, h3 = net.getNodeByName( 'h1', 'h2', 'h3' )

    popens = {}

    popens[1] = h1.popen( 'iperf -s' )

    popens[2] = h2.popen( 'iperf -c %s -t 10' % h1.IP() )
    popens[3] = h3.popen( 'iperf -c %s -t 10' % h1.IP() )

    time.sleep(15)

    popens[1].terminate()
    popens[2].terminate()
    popens[3].terminate()

if __name__ == '__main__':
    mytopo = SingleSwitchTopo( 3 )
    net = Mininet( topo=mytopo )

    net.start()

    t1 = threading.Thread( target=tcpprobe_log, args=( 1, net ) )
    t1.start()
    
    cli = CLI
    cli( net )
    sys.stdout = sys.__stdout__
    sys.stdin  = sys.__stdin__
   
    t1.join()

    net.stop()
