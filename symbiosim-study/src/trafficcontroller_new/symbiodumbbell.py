#!/bin/python

import threading

from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI

#from trafficmonitor import trafficmonitor
from trafficcontroller import trafficcontroller

def traffic_monitor( net, mn_pipes_file, demand_file ):
    trafficmonitor( net, mn_pipes_file, demand_file )

def start_traffic_monitor( net, mn_pipes_file, demand_file ):
    t = threading.Thread( target=traffic_monitor, args=(net, 
        mn_pipes_file, demand_file,) )
    t.daemon = True
    t.start()

def traffic_controller():
    return

def start_traffic_controller():
    return

def main():
    net = Mininet()

    h1 = net.addHost( 'h1' )
    h2 = net.addHost( 'h2' )

    linkopts = dict( bw=10, delay='15ms' )
    l1 = net.addLink( h1, h2, cls=TCLink, **linkopts )

    net.start()

    #start_traffic_monitor( net, 'mn_pipes_file', 'demand_file' )

    cli = CLI
    cli( net )

    net.stop()

if __name__ == '__main__':
    main()
