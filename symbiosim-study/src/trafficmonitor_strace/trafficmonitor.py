#!/usr/bin/python

import re
import os
import sys
import threading
from subprocess import PIPE
from Queue import Queue, Empty
from time import sleep
from datetime import datetime

from mininet.net import Mininet
from proc import procinfofactory, procinfo

ON_POSIX = 'posix' in sys.builtin_module_names

class trafficmonitor():
    def __init__( self, mn, mn_pipes_file, demand_file ):
        self.mn = mn
        self.demand_file = demand_file

        with open( mn_pipes_file, 'r') as openfile:
            mn_pipes = [ line.rstrip( '\n' ) for line in openfile ]

        self.host_set = set()
        self.mn_pipes_table = []
        for i,_ in enumerate( mn_pipes ):
            mn_pipes[i] = mn_pipes[i].rstrip( '\n' ).split( ' ' )

            name = mn_pipes[i][0]
            emu_src = mn_pipes[i][1]
            sim_src = mn_pipes[i][2]
            emu_dest = mn_pipes[i][3]
            sim_dest = mn_pipes[i][4]

            self.host_set.add( emu_src )

            self.mn_pipes_table.append( { 'name': name,
                                          'emu_src': emu_src,
                                          'sim_src': sim_src,
                                          'emu_dest': emu_dest,
                                          'sim_dest': sim_dest,
                                          'tcp_demand': 0,
                                          'udp_demand': 0 } )

        self.run()

    def run( self ):
        self.monitors = []
        for host in self.host_set:
            pif = procinfofactory( host, self.mn_pipes_table )
            out = self.strace_monitor( host )
            q = Queue()
            t = threading.Thread( target=self.enqueue_output, args=(out.stderr, q,) )
            t.daemon = True
            t.start()
            self.monitors.append( (pif, q) )

        t0 = threading.Thread( target=self.timed_update )
        t0.daemon = True
        t0.start()

        t1 = threading.Thread( target=self.strace_listener )
        t1.daemon = True
        t1.start()

    def strace_listener( self ):
        while True:
            for pif, q in self.monitors:
                try:
                    line = q.get_nowait()
                except:
                    line = None
                    sleep( 0.001 )
                else:
                    if re.search( 'connect', line ):
                        line = line.split( ' ' )
                        temp_pid = line[0].strip( '\n' )
                        # add pid
                        proc = pif.add_proc( temp_pid )
                        temp_fd = ''.join( x for x in line[2] if x.isdigit() )
                        # add fd
                        temp_pipe = proc.add_fd( temp_fd )
                        #temp_pipe['tcp_demand'] += int(line[-1])
                    if re.search( 'write', line ):
                        line = line.split( ' ' )
                        temp_pid = line[0].strip( '\n' )
                        # add pid
                        proc = pif.add_proc( temp_pid )
                        temp_fd = ''.join( x for x in line[2] if x.isdigit() )
                        # add fd
                        temp_pipe = proc.add_fd( temp_fd )
                        if temp_pipe:
                            for pipe in self.mn_pipes_table:
                                if temp_pipe == pipe['name']:
                                    try:
                                        new_demand = int(line[-1])
                                    except:
                                        continue
                                    else:
                                        temp_pipe['tcp_demand'] += new_demand

    def timed_update( self ):
        with open( self.demand_file, 'w' ) as demand:
            while True:
                for pipe in self.mn_pipes_table:
                    demand.write( '{} {} \n'.format( pipe['name'],
                                                     pipe['tcp_demand']
                                                   ) )
                    demand.flush()
                    pipe['tcp_demand'] = 0
                    sleep( 1 )

    def strace_monitor( self, host ):
        try:
            host = self.get_host_by_ip( host )
        except LookupError:
            print 'Invalid host name!'
        else:
            env = os.environ.copy()
            cmd = ['strace', '-f', '-e', 'trace=connect,write,send,sendto,sendmsg', '-p', str(host.pid) ]
            proc = host.popen( cmd, env=env, stdout=PIPE, stderr=PIPE, bufsize=1,
                close_fds=ON_POSIX )
            return proc

    def enqueue_output( self, output, queue ):
        for line in iter( output.readline, b'' ):
            queue.put( line )
        output.close()

    def get_host_by_ip( self, ip ):
        for host in self.mn.hosts:
            if host.IP() == ip:
                return host
        else:
            raise LookupError
