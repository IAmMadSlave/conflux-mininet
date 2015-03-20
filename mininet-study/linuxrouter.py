#!/usr/bin/python

"""
linuxrouter.py: Dumbbell Experiments using Mininet
 Routing entries can be added to the routing tables of the 
 hosts or router using the "ip route add" or "route add" command.
 See the man pages for more details.

"""
import sys
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.util import irange
from mininet.util import custom
from mininet.node import CPULimitedHost
from mininet.link import TCLink

from time import sleep, time

class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()

class NetworkTopo( Topo ):
    "A simple topology of a router with three subnets (one host in each)."

    def build( self, n=2, h=1, **opts ):
	lconfig_bottleneck = {'show_commands': False}  # unlimited
	lconfig_access = {'bw': 100, 'show_commands': False}

        # Dumbbell Topology 
        router = self.addNode( 'r0', cls=LinuxRouter, ip='192.168.1.1/24' )
        router2 = self.addNode( 'r1', cls=LinuxRouter, ip='192.168.1.2/24' )

        self.addLink( router, router2 , **lconfig_bottleneck)

	# hosts = double number of pairs
	hosts = range(numnodes)
	a = 1
	for i in hosts:
		myhost = i + 1
		if(i % 2 == 0):
			hosts[i] = self.addHost( 'h%s' % myhost, 
				ip='10.10.%s.2/24' % myhost, defaultRoute='via 10.10.%s.1' % myhost)
			self.addLink( hosts[i], router, intfName2='r0-eth%s' % a, **lconfig_access)
#			self.addLink( hosts[i], router, intfName2='r0-eth%s' % a, 
#				params2={ 'ip' : '10.10.%s.1/24' % myhost } )
		else: 
			hosts[i] = self.addHost( 'h%s' % myhost, 
				ip='10.10.%s.2/24' % myhost, defaultRoute='via 10.10.%s.1' % myhost)
			self.addLink( hosts[i], router2, intfName2='r1-eth%s' % a, **lconfig_access) 
#				params2={ 'ip' : '10.10.%s.1/24' % myhost } )
			a = a + 1

def run():
    topo = NetworkTopo()
    host = custom(CPULimitedHost, cpu=.15)
    #link = custom(TCLink, bw=100)

    net = Mininet( topo=topo, host=host, link=TCLink, controller=None ) # no controller needed
    #net = Mininet( topo=topo, controller=None ) # no controller needed
    net.start()

    # adding static routes
    # hosts = double number of pairs
    r0, r1 = net.getNodeByName('r0', 'r1')
    hosts = range(numnodes)
    a = 1
    for i in hosts:
	myhost = i + 1
	if(i % 2 == 0):
		r0.cmd('ifconfig r0-eth%s 10.10.%s.1/24' % (a, myhost))
    		r1.cmd('ip route add 10.10.%s.0/24 via 192.168.1.1' % myhost)
	else:
		r1.cmd('ifconfig r1-eth%s 10.10.%s.1/24' % (a, myhost))
    		r0.cmd('ip route add 10.10.%s.0/24 via 192.168.1.2' % myhost)
		a = a + 1

    info( '*** Routing Table on Router 1\n' )
    print net[ 'r0' ].cmd( 'route' )
    info( '*** Routing Table on Router 2\n' )
    print net[ 'r1' ].cmd( 'route' )

    print "Firing all iperf servers"
    maxtime = 50 + 2 * numnodes
    for i in hosts:
	myhost = i + 1
	if(i % 2 == 0):
		print "iperf server running in host", myhost
		net [ 'h%s' % myhost ].cmd('iperf -t %s -s > /tmp/rec%s_iperf &' % (maxtime, myhost))  
		sleep(1)
    sleep(10)
    
    print "Firing all iperf clients"
    maxtime = 30 + 2 * numnodes
    for i in hosts:
	myhost = i + 1
	if(i % 2 != 0):
		print "iperf client running from host", myhost, " target ip 10.10.",(myhost-1),"2"
		net [ 'h%s' % myhost ].cmd('iperf -t %s -c 10.10.%s.2 > /tmp/send%s_iperf &' % (maxtime, (myhost-1), myhost))	
    		sleep(2)
    sleep(maxtime)

    #CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    numnodes = 2 * int(sys.argv[1])
    run()
