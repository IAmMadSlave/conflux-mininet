#!/bin/python

import time
import threading

import socket
from datetime import datetime

from mininet.net  import Mininet
from mininet.link import TCLink
from mininet.cli  import CLI

from TrafficMonitor import TrafficMonitor

sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
server_address = ( 'localhost', 51717 )
sock.connect( server_address )
print ('SymbioDumbell: socket is %s' % sock)

# function for long single async wget
def wget_short( src, dest ):
    dest_ip = dest.IP()
    src.popen( [] )
    return

# function for short single async wget
def wget_long( src, dest ):
    dest_ip = dest.IP()
    src.popen( [] )
    return

# functions for test_file (tcpprobe)
def call_traffic_monitor():
    TrafficMonitor( 'mn_pipes_file' )

def start_traffic_monitor():
    t = threading.Thread( target=call_traffic_monitor )
    t.daemon = True
    t.start()
    return

# functions for tc changes
def tc_change( host, bandwidth, drop_prob ):
    cmd = 'tc qdisc replace dev %s root handle 1:0 htb default 10' % (host.defaultIntf(),)
    host.popen( cmd )
    cmd = 'tc class replace dev %s parent 1:0 classid 1:10 htb rate %smbit' % (host.defaultIntf(), bandwidth, )
    host.popen( cmd )
    if float( drop_prob ) > 0:
        cmd = 'tc qdisc replace dev %s root netem loss %s%' %(drop_prob,)
        host.popen( cmd )
    return

def tc_listener( hosts ):
    while True:
        try:
            #tc_file = open( 'tc_changes_file', 'r' )
            data = sock.recv(256)
        except:
            time.sleep(0.001)
            continue
        else:
            received = len(data)
            if received == 0:
                break
            #print('msg: %s at: %s size: of %s'%(data, str(datetime.now()),str(received)))
            #lines = tc_file.readlines()
            tc_changes = []
            for line in data.splitlines():
               tc_changes.append( line.split())

            for h in hosts:
                for t in tc_changes:
                    #tc_change( h, t[1], t[2] )

            #tc_file.close()
            time.sleep(0.001)
            continue
        #time.sleep(1)
    return

def start_tc_listener( hosts ):
    t = threading.Thread( target=tc_listener, args=(hosts,) )
    t.daemon = True
    t.start()
    return

def main():
    net = Mininet()

    h1 = net.addHost( 'h1' )
    h2 = net.addHost( 'h2' )

    hosts = []
    hosts.append( h1 )
    hosts.append( h2 )

    l1 = net.addLink( h1, h2, cls=TCLink )

    net.start()

    # start tc lister here
    start_tc_listener( hosts )


    # start traffic monitor here
    start_traffic_monitor()

    cli = CLI
    cli( net )

    net.stop

if __name__ == '__main__':
    main()
