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

        mn_pipes = []
        with open( mn_pipes_file, 'r') as openfile:
            for line in openfile:
                mn_pipes.append( line )

        self.mn_pipes_table = []
        for i,_ in enumerate( mn_pipes ):
            mn_pipes[i] = mn_pipes[i].rstrip( '\n' ).split( ' ' )

            name = mn_pipes[i][0]
            emu_src = mn_pipes[i][1]
            sim_src = mn_pipes[i][2]
            emu_dest = mn_pipes[i][3]
            sim_dest = mn_pipes[i][4]

            proc_info = procinfofactory()

            self.mn_pipes_table.append( { 'name': name,
                                          'emu_src': emu_src,
                                          'sim_src': sim_src,
                                          'emu_dest': emu_dest,
                                          'sim_dest': sim_dest,
                                          'tcp_demand': 0,
                                          'udp_demand': 0,
                                          'proc_info': proc_info,
                                          'demand': 0 } )
        self.run()

    def run( self ):
        self.monitors = []
        for pipe in  self.mn_pipes_table:
            out = self.strace_monitor( pipe['emu_src'] )
            q = Queue()
            t = threading.Thread( target=self.enqueue_output, args=(out.stderr, q,))
            t.daemon = True
            t.start()
            self.monitors.append( (out, q, t, pipe ) )

        t0 = threading.Thread( target=self.timed_update )
        t0.daemon = True
        t0.start()

        t1 = threading.Thread( target=self.strace_listener )
        t1.daemon = True
        t1.start()

    def strace_listener( self ):
        fds = []
        while True:
            for proc, q, t, pipe in self.monitors:
                try:
                    line = q.get_nowait()
                except:
                    line = None
                    sleep( 0.001 )
                else:
                    emu_dest = pipe['emu_dest']
                    if re.search( 'connect', line ) and re.search( emu_dest, line ):
                        line = line.split( ' ' )
                        temp_proc = pipe['proc_info'].get_proc( line[0].strip() )
                        fd = ''.join( x for x in line[2] if x.isdigit() ) + '\n'
                        temp_proc.add_fd( fd, )
                        fds.append( fd )
                    else:
                        if re.search( 'write', line ):
                            line = line.split( ' ' )
                            fd_temp = ''.join( x for x in line[2] if x.isdigit() ) + '\n'
                            for fd in fds:
                                if fd == fd_temp:
                                    try:
                                        new_demand = int( line[-1] )
                                    except:
                                        continue
                                    else:
                                        pipe['demand'] += new_demand

    def timed_update( self ):
        with open( self.demand_file, 'w' ) as demand:
            while True:
                for pipe in self.mn_pipes_table:
                    demand.write( '{} {} \n'.format( pipe['name'],
                                                     pipe['demand']
                                                   ) )
                    demand.flush()
                    pipe['demand'] = 0
                    sleep( 1 )

    def strace_monitor( self, host ):
        host = self.get_host_by_ip( host )
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
        return None

    def get_pipe_table_by_name( self, name ):
        for pipe in self.mn_pipes_table:
            if pipe['name'] == name:
                return pipe
