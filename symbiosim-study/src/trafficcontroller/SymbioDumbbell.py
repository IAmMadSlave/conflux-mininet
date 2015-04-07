#!/bin/python

import time
import threading

from mininet.net  import Mininet
from mininet.link import TCLink
from mininet.cli  import CLI

from TrafficMonitor import TrafficMonitor

lock = threading.Lock()

# function for long single async wget
def wget_short():
    return

# function for short single async wget
def wget_long():
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
            lock.acquire()
            tc_file = open( 'tc_changes_file', 'r' )
        except:
            lock.release()
            time.sleep(1)
            continue
        else:
            lines = tc_file.readlines()
            tc_changes = []
            for line in lines:
                tc_changes.append( line.split() )

            for h in hosts:
                for t in tc_changes:
                    tc_change( h, t[1], t[2] )

            tc_file.close()
            lock.release()
            time.sleep(1)
        return

def start_tc_listener( hosts ):
    t = threading.Thread( target=tc_listener, args=(hosts,) )
    t.daemon = True
    t.start()
    return

def fake_sim():
    i = 0
    for i in range(10):
        lock.acquire()
        tc = open('tc_changes_file', 'w' )
        cmd = 'pipe1 %s 0.0' % (str(i+1),)
        tc.write( cmd )
        tc.close()
        lock.release()

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

    t0 = threading.Thread( target=fake_sim )
    t0.start()

    # start traffic monitor here
    start_traffic_monitor()

    cli = CLI
    cli( net )

    net.stop

if __name__ == '__main__':
    main()
