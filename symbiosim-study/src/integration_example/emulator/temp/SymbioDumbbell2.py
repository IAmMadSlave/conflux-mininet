#!/bin/python

from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import CPULimitedHost
from mininet.cli import CLI
from mininet.node import OVSController

import os
import time
import datetime
import threading
import subprocess

log_file = open( 'tc_timestamps', 'w' )

def startMonitor( mn_pipes, demand_file ):
    tm = TrafficMonitor( mn_pipes, demand_file )

def startController( mn_pipes, tc_file, mn_ip, mn ):
    tc = TrafficController( mn_pipes, tc_file, mn_ip, mn )

def changeBW( host, bandwidth, interval ):
    time.sleep( interval )
    cmd = 'tc qdisc replace dev %s root handle 1:0 htb default 10' % (host.defaultIntf(),)
    host.popen( cmd )
    cmd = 'tc class replace dev %s parent 1:0 classid 1:10 htb rate %smbit' % (host.defaultIntf(), bandwidth,)
    host.popen( cmd )
    log_file.write( str(datetime.datetime.now()) + ' ' + str(bandwidth)  + '\n')

def autoBW( host, bandwidth_set, interval ):
    for bw in bandwidth_set:
        changeBW( host, bw, interval )

def SymbioTest():
    net = Mininet()

    h1 = net.addHost( 'h1' )
    h2 = net.addHost( 'h2' )

    #linkopts = dict( bw=10, delay='15ms' )
    #l1 = net.addLink( h1, h2, cls=TCLink, **linkopts )
    l1 = net.addLink( h1, h2, cls=TCLink )

    net.start()

    #t1 = threading.Thread( target=startMonitor, args=('mn_pipes_file', 'demand_file',) )
    #t1.daemon = True
    #t1.start()

    t0 = threading.Thread( target=changeBW, args=(h1, 10, 0,) )
    t0.start()
    t0.join()

    first_set = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 5]
    second_set = [10, 5, 50, 100, 20, 10, 5, 50, 100, 20]

    interval = 10
    iperf_time = len( first_set ) * interval

    h1test = open( 'h1_tcpdump.out', 'w' ) 
    h1tcpd = h1.popen( ['tcpdump'], stdout=h1test, stderr=h1test )

    h2iperfs = h2.popen( 'iperf -s' ) 

    t0 = threading.Thread( target=autoBW, args=(h1, first_set, interval,) )    
    t0.start()

    out, err, exitcode = h1.pexec( 'iperf -c %s -t %s -i %s' % (h2.IP(), iperf_time, interval) )

    print out

    #cli = CLI
    #cli( net )

    h2iperfs.terminate()

    net.stop

    h1tcpd.terminate() 
    h1test.close()
    log_file.close()

if __name__ == '__main__':
    SymbioTest()
