#!/bin/python

import threading
import subprocess

from time import sleep
from subprocess import PIPE
from datetime import datetime
from mininet.net import Mininet

class trafficmonitor():

    def __init__( self, mn ):
        self.mn = mn
        self.run()
   
    # tc listener
    def run( self ):

        return

    def setup_tc( self, host, interface='default' ):
        if interface == 'default':
            interface = host.defaultIntf()

        cmd = 'tc qdisc del dev {} root'.format( interface )
        tc_cmd = host.popen( cmd )
        tc_cmd.wait()

        cmd = 'tc qdisc add dev {} handle 1:0 root htb default 10'.format(
                interface )
        tc_cmd = host.popen( cmd )
        tc_cmd.wait()

        cmd = 'tc class add dev {} parent 1:0 classid 1:10 htb rate
        {}mbit'.format( interface, 100 )
        tc_cmd = host.popen( cmd )
        tc_cmd.wait()

    def tc_change( self, host, interface='default', bandwidth, drop_prob ):
        if interface == 'default':
            interface = host.defaultIntf()

        # list tc classes
        cmd = 'tc class ls dev {}'.format( interface )
        tc_cmd = host.popen( cmd, stdout=PIPE, stderr=PIPE )
        out, err = tc_cmd.communicate() 

        # update tc classes if necessary
        rate_str = 'rate {}Kbit'.format( bandwidth * 1000 )
        if out.find( rate_str ) < 0:
            cmd = 'tc class replace dev {} parent 1:0 classid 1:10 htb rate
                   {}mbit'.format( interface, bandwidth )
            tc_cmd = host.popen( cmd )
            tc_cmd.wait()

        # list tc qdiscs
        cmd = 'tc qdisc ls dev {}'.format( interface )
        tc_cmd = host.popen( cmd, stdout=PIPE, stderr=PIPE )
        out, err = tc_cmd.communicate()

        # update tc qdisc if necessary
        loss_str = 'loss {}%'.format( drop_prob * 100 )
        if out.find( loss_str ) < 0:
            cmd = 'tc qdisc replace dev {} parent 1:10 handle 10 netem loss
                   {}% delay 15ms'.format( interface, drop_prob*100 )
            tc_cmd = host.popen( cmd )
            tc_cmd.wait()
