#!/bin/python

import threading
import subprocess

from time import sleep
from subprocess import PIPE
from datetime import datetime
from mininet.net import Mininet

class trafficmonitor():
    def __init__( self, mn, mn_pipes_file ):
        self.mn = mn

        mn_pipes = []
        with open( mn_pipes_file, 'r' ) as openfile:
            for line in openfile:
                mn_pipes.append( line )

        self.mn_pipes_table = []
        for i,_ in enumerate( mn_pipes ):
            mn_pipes[i] = mn_pipes[i].rstrip( '\n' ).split( ' ' )

            name = mn_pipes[i][0]
            emu_src = mn_pipes[i][1]
            sim_src = mn_pipes[i][2]
            emu_dest = mn_pipes[i][3]
            sim_dest = mn_pipes]i][4]

            self.mn_pipes_table.append( { 'name': name,
                                          'emu_src': emu_src,
                                          'sim_src': sim_src,
                                          'emu_dest': emu_dest,
                                          'sim_dest': sim_dest,
                                          'bandwidth': 0.0,
                                          'drop_prob': 0.0 } )

        self.run()

    def run( self ):
        # setup tc for each pipe
        for pipe in self.mn_pipes_table:
            host = self.get_host_by_ip( pipe['emu_src'] )
            self.setup_tc( host )
            
        # start tc_listener
        t = threading.Thread( target=self.tc_listener )
        t.daemon = True
        t.start()

    def tc_listener( self ):
        while True:
            try:
                # get from socket
                data = sock.recv( 256 )
            except:
                # nothing in socket
                sleep( 0.001 )
            else:
                # process for pipe
                received = len( data )
                if received == 0:
                    break

                #print 'msg: {} at: {}\nsize: of {}'.format( data,
                #        datetime.now(), received )

                tc_changes = []
                for line in data.splitlines():
                    tc_changes.append( line.split() )

                # for each tc change
                # find the table entry for the pipe
                # check table for same values
                # if different
                # apply the tc changes to the emu_src host
                # update table

    def setup_tc( self, host, interface=None ):
        if interface is None:
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

    def tc_change_bandwidth( self, pipe, host, interface=None, bandwidth ):
        if interface is None:
            interface = host.defaultIntf()

        if pipe['bandwidth'] == float( bandwidth ):
            return
        else:
            cmd = 'tc class replace dev {} parent 1:0 classid 1:10 htb rate
            {}mbit'.format( interface, bandwidth )
            tc_cmd = host.popen( cmd )
            tc_cmd.wait()
        return

    def tc_change_drop_prob( self, pipe, host, interface=None, drop_prob ):
        if interface is None:
            interface = host.defaultIntf()

        if pipe['drop_prob'] == float( drop_prob )*100:
            return
        else:
            cmd = 'tc qdisc replace dev {} parent 1:10 handle 10 netem loss
            {}% delay 15 ms'.format( interface, drop_prob*100 )
            tc_cmd = host.popen( cmd )
            tc_cmd.wait()
        return

    def get_host_by_ip( self, ip ):
        for host in self.mn.hosts:
            if host.IP() == ip:
                return host
        return null

    def get_pipe_table_by_name( self, name ):
        for pipe in self.mn_pipes_table:
            if pipe['name'] == name:
                return pipe
        return null
