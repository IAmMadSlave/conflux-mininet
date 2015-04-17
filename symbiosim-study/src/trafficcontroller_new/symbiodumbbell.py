#!/bin/python

import threading

from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI

from trafficmonitor import trafficmonitor

def traffic_monitor( net, mn_pipes_file, demand_file ):
    trafficmonitor( net, mn_pipes_file, demand_file )

def start_traffic_monitor( net, mn_pipes_file, demand_file ):
    t = threading.Thread( target=traffic_monitor, args=(net, 
        mn_pipes_file, demand_file,) )
    t.daemon = True
    t.start()

def main():
    net = Mininet()

    h1 = net.addHost( 'h1' )
    h2 = net.addHost( 'h2' )

    linkopts = dict( bw=10, delay='15ms' )
    l1 = net.addLink( h1, h2, cls=TCLink, **linkopts )

    net.start()

    h1tcpdump = h1.popen( ['tcpdump', '-w', 'h1_tcpdump.pcap'] )

    #start_traffic_monitor( net, 'mn_pipes_file', 'demand_file' )
    #start_traffic_monitor( net, 'mn_pipes_file', 'demand_file' )

    cli = CLI
    cli( net )

    h1tcpdump.terminate()

    net.stop()

if __name__ == '__main__':
    main()
