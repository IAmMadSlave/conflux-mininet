#!/usr/bin/python

"""
This example shows how to create an empty Mininet object
(without a topology object) and add nodes to it manually.
"""

from mininet.net import Mininet
from mininet.node import Controller
from mininet.node import Node
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def emptyNet():

    "Create an empty network and add nodes to it."

    net = Mininet( controller=Controller )

    info( '*** Adding hosts\n' )
    primex = net.addHost( 'primex', ip='10.10.1.1/24' )
    h1 = net.addHost( 'h1', ip='10.10.1.2', defaultRoute='via 10.10.1.1' )
    h2 = net.addHost( 'h2', ip='10.10.3.1', defaultRoute='via 10.10.3.2' )
    
    info( '*** Creating links\n' )
    net.addLink( h1, primex, intfName2='r0-eth1', params2={ 'ip' : '10.10.1.1/24' } )
    net.addLink( h2, primex, intfName2='r0-eth2', params2={ 'ip' : '10.10.3.2/24' } )

    info( '*** Running primex\n' )
    cmd = '/home/cesar/primogeni/netsim/primex -tp 10.10.3.2 166 -tp 10.10.1.1 605 600 /home/cesar/PortalsExogeni_part_1.tlv 2>test.out &'
    primex.cmd( cmd )

    info( '*** Starting network\n')
    net.start()

    info( '*** Running CLI\n' )
    CLI( net )

    info( '*** Stopping network' )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    emptyNet()
