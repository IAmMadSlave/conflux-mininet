#!/usr/bin/python

import re
import os
import sys
import logging
import threading
from subprocess import PIPE
from Queue import Queue, Empty
from time import sleep
from datetime import datetime

from mininet.net import Mininet
from proc import procinfofactory, procinfo

ON_POSIX = 'posix' in sys.builtin_module_names
logging.basicConfig( filename='log_file', level=logging.DEBUG, format='%(levelname)s - %(message)s' )

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
            logging.debug( 'Add {} to host set'.format( emu_src ) )

            self.mn_pipes_table.append( { 'name': name,
                                          'emu_src': emu_src,
                                          'sim_src': sim_src,
                                          'emu_dest': emu_dest,
                                          'sim_dest': sim_dest,
                                          'tcp_demand': 0,
                                          'udp_demand': 0 } )
            logging.debug( 'Add {} to pipes table'.format( name ) )

        self.run()

    def run( self ):
        self.monitors = []
        for host in self.host_set:
            host_real = self.get_host_by_ip( host )
            pif = procinfofactory( host_real, self.mn_pipes_table, logging )
            logging.debug( 'ProcInfoFactory for {}'.format( host_real ) )
            out = self.strace_monitor( host )
            logging.debug( 'Start strace on {}'.format( host ) )
            q = Queue()
            t = threading.Thread( target=self.enqueue_output, args=(out.stderr, q,) )
            logging.debug( 'Start stdout processing for {}'.format( host ) )
            t.daemon = True
            t.start()
            self.monitors.append( (pif, q) )

        t0 = threading.Thread( target=self.timed_update )
        t0.daemon = True
        t0.start()
        logging.debug( 'Start timed updating' )

        t1 = threading.Thread( target=self.strace_listener )
        t1.daemon = True
        t1.start()
        logging.debug( 'Start strace listener' )

    def strace_listener( self ):
        strace = open( 'strace.out', 'w' )
        while True:
            for pif, q in self.monitors:
                try:
                    line = q.get_nowait()
                    #logging.debug( 'Attempting to get line from ProcInfoFactory.{}'.format( pif.host ) )
                except:
                    line = None
                    #logging.debug( 'No line from ProcInfoFactory.{}'.format( pif.host ) )
                    sleep( 0.001 )
                else:
                    #logging.debug( 'Line found from ProcInfoFactory.{}'.format( pif.host ) )
                    if re.search( 'pid', line ):
                        if re.search( 'connect', line ):
                            logging.debug( 'Line is of type CONNECT' )
                            line = line.split( ' ' )
                            strace.write(str(line)+'\n')
                            temp_pid = line[1].strip( '\n' )
                            temp_pid = temp_pid.translate( None, '[]' )
                            # add pid
                            proc = pif.add_proc( temp_pid )
                            temp_fd = ''.join( x for x in line[2] if x.isdigit() )
                            # add fd
                            temp_pipe = proc.add_fd( temp_fd )
                            logging.debug( 'PID:{} FD:{} PIPE:{}'.format( temp_pid, temp_fd, temp_pipe ) )
                            #temp_pipe['tcp_demand'] += int(line[-1])
                        elif re.search( 'write', line ):
                            logging.debug( 'Line is of type WRITE' )
                            line = line.split( ' ' )
                            strace.write(str(line)+'\n')
                            temp_pid = line[1].strip( '\n' )
                            temp_pid = temp_pid.translate( None, '[]' )
                            # add pid
                            proc = pif.add_proc( str(temp_pid) )
                            temp_fd = ''.join( x for x in line[2] if x.isdigit() )
                            # add fd
                            temp_pipe = proc.add_fd( temp_fd )
                            logging.debug( 'PID:{} FD:{} PIPE:{}'.format( temp_pid, temp_fd, temp_pipe ) )
                            if temp_pipe:
                                temp_pipe = self.get_pipe_by_name( temp_pipe )
                                for pipe in self.mn_pipes_table:
                                    if temp_pipe['name'] == pipe['name']:
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
                    logging.debug( 'Demand of {} on {}'.format( pipe['tcp_demand'], pipe['name'] ) )
                    demand.flush()
                    pipe['tcp_demand'] = 0
                    logging.debug( 'Demand is now 0 on {}'.format( pipe['name'] ) )
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

    def get_pipe_by_name( self, pipe_name ):
        for pipe in self.mn_pipes_table:
            if pipe['name'] == pipe_name:
                return pipe
        else:
            raise LookupError
