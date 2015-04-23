#!/usr/bin/python

import threading
import subprocess

from time import sleep
from subprocess import PIPE
from datetime import datetime
from mininet.net import Mininet

class trafficmonitor():
    def __init__( self, mn, mn_pipes_file ):
        self.mn = mn

        # read in pipes info from file
        mn_pipes = []
        with open( mn_pipes_file, 'r' ) as openfile:
            for line in openfile:
                mn_pipes.append( line )

        # setup pipes table
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
                                          'drop_prob': 0.0,
                                          'delay': 0.0 } )

        self.run()

    def run( self ):
        # setup tc for each pipe
        for pipe in self.mn_pipes_table:
            host = self.get_host_by_ip( pipe['emu_src'] )
            self.setup_tc( host, pipe, None, None, None )
            
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

                for line in data.splitlines():
                    line = line.split()
                    pipe = self.get_pipe_table_by_name( line[0] )
                    host = self.get_host_by_ip( pipe['emu_src'] )
                    self.tc_change_bandwidth( line[2], host, pipe )
                    self.tc_change_drop_prob( line[1], None, host, pipe )
                    time.sleep( 1 )

    def setup_tc( self, host, pipe=None, interface=None, bandwidth=None, delay=None ):
        if interface is None:
            interface = host.defaultIntf()

        cmd = 'tc qdisc add dev {} root handle 1:0 htb default 10'.format(
                interface )
        tc_cmd = host.popen( cmd )
        tc_cmd.wait()

        if bandwidth is not None:
            self.tc_change_bandwidth( bandwidth, host, pipe, interface )

        if delay is not None:
            self.tc_change_drop_prob( 0.0, delay, host, pipe, interface )

    def tc_change_bandwidth( self, bandwidth, host, pipe=None, interface=None ):
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

    def tc_change_drop_prob( self, drop_prob, delay, host, pipe=None, interface=None ):
        if interface is None:
            interface = host.defaultIntf()

        if pipe['drop_prob'] == float( drop_prob )*100:
            return
        else:
            if delay is None:
                delay = pipe['delay']
            cmd = 'tc qdisc replace dev {} parent 1:10 handle 10 netem loss
            {}% delay {}ms'.format( interface, drop_prob*100, delay )
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
