#!/bin/python

import time
import datetime
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
#print ('SymbioDumbell: socket is %s' % sock)

log_file = open( 'tc_changes.out', 'w' )
python_server = None
server_on = False

# python server
def set_server( host ):
    if server_on:
        return True
    else:
        python_server = host.popen( 'python -m SimpleHTTPServer' )
        server_on = True
    return True

def kill_server():
    python_server.terminate()

# function for long single async wget
def wget_short( src, dest ):
    dest_ip = dest.IP()
    dest_ip = dest_ip + ':8000/two_m.dat'
    src.popen( ['wget', dest_ip] )
    return

# function for short single async wget
def wget_long( src, dest ):
    dest_ip = dest.IP()
    dest_ip = dest_ip + ':8000/ten_m.dat' 
    src.popen( ['wget', dest_ip] )
    return

# iperf2
def iperf( src, dest, duration, interval ):
    iperf_server = dest.popen( 'iperf -s' )
    out, err, exitcode = src.pexec( 'iperf -c %s -t %s -i %s' % ( dest.IP(),
        duration, interval) )
    return out

# iperf3
def iperf3( src, dest, duration, interval ):
    iperf_server = dest.popen( 'iperf3 -s' )
    out, err, exitcode = src.pexec( 'iperf3 -c %s -t %s -i %s' % ( dest.IP(),
        duration, interval) )
    return out


# functions for test_file (tcpprobe)
def call_traffic_monitor():
    TrafficMonitor( 'mn_pipes_file' )

def start_traffic_monitor():
    t = threading.Thread( target=call_traffic_monitor )
    t.daemon = True
    t.start()
    return

# functions for tc changes
def setup_tc( host ):
    cmd = 'tc -s qdisc ls dev %s' % ( host.defaultIntf(), )
    out, err, exitcode = host.pexec( cmd )
    if out.find( 'htb' ) < 0:
        cmd = 'tc qdisc add dev %s handle 1:0 root htb default 10' % ( host.defaultIntf(), )
        host.popen( cmd )
        return True
    else:
        return True

def tc_change( host, bandwidth, drop_prob ):
#    cmd = 'tc qdisc replace dev %s root handle 1:0 htb default 10' % (host.defaultIntf(),)
#    host.popen( cmd )
#    cmd = 'tc class replace dev %s parent 1:0 classid 1:10 htb rate %smbit' % (host.defaultIntf(), bandwidth, )
#    host.popen( cmd )
#    if float( drop_prob ) > 0:
#        cmd = 'tc qdisc replace dev %s root netem loss %s%' %(host.defaultIntf(), drop_prob,)
#        host.popen( cmd )
    setup_tc( host )
    cmd = 'tc class replace dev %s parent 1:0 classid 1:10 htb rate %smbit' % ( host.defaultIntf(), bandwidth, )
    host.popen( cmd )
    if float( drop_prob ) > 0.0:
        drop_prob = float( drop_prob ) / 100.0
        drop_prob = str( drop_prob )
        cmd = 'tc qdisc replace dev %s parent 1:10 handle 10 netem loss %s%% delay 1ms' % ( host.defaultIntf(), drop_prob, )
        host.popen( cmd )
    log_file.write( str( datetime.now() ) + ' ' + str( bandwidth ) + ' ' + str( drop_prob ) +'\n' )
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
               tc_changes.append( line.split() )

            for h in hosts:
                for t in tc_changes:
                    tc_change( h, t[2], t[1] )

            #tc_file.close()
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
    tc_change( h1, '10', '0.0' )

    # start tc lister here
    start_tc_listener( hosts )


    # start traffic monitor here
    start_traffic_monitor()

    # add iperf 20s 1s interval
    #out = iperf( h1, h2, 20, 1 )
    out = iperf3( h1, h2, 20, 1 )
    print out
    
    out, err, exitcode = h1.pexec( 'ping -c 5 10.0.0.2' )
    print out

    #set_server( h2 )
    #wget_short( h1, h2 )
    #wget_long( h1, h2 )
    #kill_server()

    #cli = CLI
    #cli( net )

    net.stop

if __name__ == '__main__':
    main()
