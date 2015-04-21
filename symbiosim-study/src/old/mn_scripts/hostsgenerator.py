#!/usr/bin/python

from mininet.net import Mininet
from mininet.topo import SingleSwitchTopo
from mininet.util import pmonitor
import time

if __name__ == '__main__':
    mytopo = SingleSwitchTopo(3)
    net = Mininet(topo=mytopo)

    net.start()

    h1, h2, h3 = net.getNodeByName('h1', 'h2', 'h3')

    for host in net.hosts:
        if host.IP() == '10.0.0.1':
            print host.IP()


    net.stop() 
