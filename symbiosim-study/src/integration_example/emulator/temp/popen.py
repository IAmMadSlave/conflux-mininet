#!/usr/bin/python

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.node import OVSController

import os
import time
import threading
import subprocess

net = Mininet()

h1 = net.addHost( 'h1' )
h2 = net.addHost( 'h2' )

l1 = net.addLink( h1, h2, cls=TCLink )

net.start()

h1tcpd = open( 'h1_tcpdump.out', 'w' )
tcpd = h1.popen( ['tcpdump'], stdout=h1tcpd, stderr=h1tcpd )

cli = CLI
cli( net )

h1tcpd.close()
tcpd.terminate()

net.stop()
