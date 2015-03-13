#!/usr/bin/python

"""
linuxrouter.py: Dumbbell Experiments using Mininet
 Routing entries can be added to the routing tables of the 
 hosts or router using the "ip route add" or "route add" command.
 See the man pages for more details.

"""

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
        # Dumbbell Topology 
        router = self.addNode( 'r0', cls=LinuxRouter, ip='192.168.1.1/24' )
        router2 = self.addNode( 'r1', cls=LinuxRouter, ip='192.168.1.2/24' )

        self.addLink( router, router2 )

	# hosts = double number of pairs
	hosts = range(4)
	a = 1
	for i in hosts:
		myhost = i + 1
		if(i % 2 == 0):
			hosts[i] = self.addHost( 'h%s' % myhost, 
				ip='10.10.%s.2/24' % myhost, defaultRoute='via 10.10.%s.1' % myhost)
			self.addLink( hosts[i], router, intfName2='r0-eth%s' % a, 
				params2={ 'ip' : '10.10.%s.1/24' % myhost } )
		else: 
			hosts[i] = self.addHost( 'h%s' % myhost, 
				ip='10.10.%s.2/24' % myhost, defaultRoute='via 10.10.%s.1' % myhost)
			self.addLink( hosts[i], router2, intfName2='r1-eth%s' % a, 
				params2={ 'ip' : '10.10.%s.1/24' % myhost } )
			a = a + 1

def run():
    topo = NetworkTopo()
    host = custom(CPULimitedHost, cpu=.15)
    link = custom(TCLink, bw=100, delay='1ms', max_queue_size=200)

    net = Mininet( topo=topo, host=host, link=link, controller=None ) # no controller needed
    net.start()

    # adding static routes
    # hosts = double number of pairs
    r0, r1 = net.getNodeByName('r0', 'r1')
    hosts = range(4)
    a = 1
    for i in hosts:
	myhost = i + 1
	if(i % 2 == 0):
    		r1.cmd('ip route add 10.10.%s.0/24 via 192.168.1.1' % myhost)
	else:
    		r0.cmd('ip route add 10.10.%s.0/24 via 192.168.1.2' % myhost)

    info( '*** Routing Table on Router 1\n' )
    print net[ 'r0' ].cmd( 'route' )
    info( '*** Routing Table on Router 2\n' )
    print net[ 'r1' ].cmd( 'route' )

    print "Firing all iperf servers"
    for i in hosts:
	myhost = i + 1
	if(i % 2 == 0):
		print "iperf server running in host", myhost
		net [ 'h%s' % myhost ].cmd('iperf -t 30 -s -i 1 > /tmp/rec%s_iperf &' % myhost)  
    
    sleep(10)
    print "Firing all iperf clients"
    for i in hosts:
	myhost = i + 1
	if(i % 2 != 0):
		print "iperf client running from host", myhost, " target ip 10.10.",(myhost-1),"2"
		net [ 'h%s' % myhost ].cmd('iperf -t 30 -c 10.10.%s.2 > /tmp/send%s_iperf &' % ((myhost-1), myhost))	
    		sleep(2)
    sleep(10)

    CLI( net )
    net.stop()
'''
#    h1, h2 = net.getNodeByName('h1', 'h2')
#    h3, h4 = net.getNodeByName('h3', 'h4')
#    h2.cmd('iperf -t 10 -s -i 1 > /tmp/rec2_iperf &')
#    h4.cmd('iperf -t 10 -s -i 1 > /tmp/rec3_iperf &')
#    sleep(2)
#    h1.cmd('iperf -t 10 -c 10.10.2.2 > /tmp/send1_iperf &')
#    sleep(2)
#    h3.cmd('iperf -t 10 -c 10.10.4.2 > /tmp/send2_iperf &')
'''
if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
