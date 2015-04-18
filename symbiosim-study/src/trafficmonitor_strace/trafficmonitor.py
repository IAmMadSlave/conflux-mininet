#!/bin/python

import re
import os
import sys
import threading
from mininet.net import Mininet
from subprocess import PIPE
from Queue import Queue, Empty
from time import sleep
from datetime import datetime

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

            self.mn_pipes_table.append( { 'name': name,
                                          'emu_src': emu_src,
                                          'sim_src': sim_src,
                                          'emu_dest': emu_dest,
                                          'sim_dest': sim_dest,
                                          'demand': 0 } )
            self.run()
    
    def run( self ):
        out = self.monitorhost()
        q = Queue()

        t0 = threading.Thread( target=self.enqueue_output, args=(out.stderr, q,) )
        t0.daemon = True
        t0.start()

        t1 = threading.Thread( target=self.timed_update )
        t1.daemon = True
        t1.start()

        fds = []
        while True:
            try:
                line = q.get_nowait()
            except:
                line = None
                sleep( 0.001 )
            else:
                if re.search( 'connect', line ) and re.search( '10.0.0.2', line ): 
                    line = line.split( ' ' )
                    fd = ''.join( x for x in line[2] if x.isdigit() ) + '\n'
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
                                    self.mn_pipes_table[0]['demand'] +=
                                    new_demand

    def timed_update( self ):
        with open( self.demand_file, 'w' ) as demand:
            while True:
                demand.write( '{} {} \n'.format( self.mn_pipes_table[0]['name'], 
                                                 self.mn_pipes_table[0]['demand']
                                                 ) )
                demand.flush()
                self.mn_pipes_table[0]['demand'] = 0
                sleep( 1 )

    def monitorhost( self ):
        host = self.mn.get( 'h1' )
        env = os.environ.copy()
        cmd = ['strace', '-f', '-e', 'trace=connect,write,send,sendto,sendmsg', '-p', str(host.pid) ]
        proc = host.popen( cmd, env=env, stdout=PIPE, stderr=PIPE, bufsize=1,
                close_fds=ON_POSIX )
        return proc

    def enqueue_output( self, output, queue ):
        for line in iter( output.readline, b'' ):
            queue.put( line )
        output.close()
