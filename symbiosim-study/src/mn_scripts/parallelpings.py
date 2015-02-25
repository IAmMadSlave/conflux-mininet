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

    popens = {}
    popens[1] = h1.popen("ping -c4 -D %s" % h3.IP())
    popens[2] = h2.popen("ping -c4 -D %s" % h1.IP())
    popens[3] = h3.popen("ping -c4 -D %s" % h2.IP())

    time.sleep(5)

    for h, line in pmonitor(popens):
        if h:
            print '%s' % (line)

    net.stop() 
