#!/bin/python

from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI

from trafficmonitor import trafficmonitor

def main():
    net = Mininet()

    h1 = net.addHost( 'h1' )
    h2 = net.addHost( 'h2' )

    l1 = net.addLink( h1, h2, cls=TCLink )

    net.start()

    hosts_map = []
    hosts_map.append( (h1.IP(), h1.name) )
    hosts_map.append( (h2.IP(), h2.name) )


    trafficmonitor( net, hosts_map, 'mn_pipes_file', 'demand_file' )

    cli - CLI
    cli( net )

    net.stop()

if __name__ == '__main__':
    main()
