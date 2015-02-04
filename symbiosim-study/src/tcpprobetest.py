#!/usr/bin/python

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

#    h1log = open( 'h1.log', 'w' )
#    h2log = open( 'h2.log', 'w' )
#    h3log = open( 'h3.log', 'w' )

#    popens[1] = h1.popen( ['cat /proc/net/tcpprobe'], stdout=h1log )
#    popens[2] = h2.popen( ['cat /proc/net/tcpprobe'], stdout=h2log )
#    popens[3] = h3.popen( ['cat /proc/net/tcpprobe'], stdout=h3log )

    popens[4] = h1.popen( 'iperf -s' )

    popens[5] = h2.popen( 'iperf -c %s -t 10' % h1.IP() )
    popens[6] = h3.popen( 'iperf -c %s -t 10' % h1.IP() )

    time.sleep(15)

#    h1log.flush()
#    h2log.flush()
#    h3log.flush()

#    popens[1].terminate()
#    popens[2].terminate()
#    popens[3].terminate()
    popens[4].terminate()
    popens[5].terminate()
    popens[6].terminate()

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
