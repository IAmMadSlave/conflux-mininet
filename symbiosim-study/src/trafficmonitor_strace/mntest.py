#!/bin/python

from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI

def main():
    net = Mininet()

    h1 = net.addHost( 'h1' )
    h2 = net.addHost( 'h2' )

    l1 = net.addLink( h1, h2, cls=TCLink )

    net.start()

    cli = CLI
    cli( net )

    net.stop()

if __name__ == '__main__':
    main()
