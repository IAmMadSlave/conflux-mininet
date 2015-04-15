#!/bin/python

import sys
from mininet.net import Mininet
from subprocess import PIPE
from Queue import Queue, Empty
from time import sleep

ON_POSIX = 'posix' in sys.builtin_module_names

class trafficmonitor():

    def __init__( self, mn, hosts_map, mn_pipes_file, demand_file ):
        self.mn = mn
        self.hosts_map = hosts_map
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
        
        while True:
            try:
                line = q.get_nowait()
            except:
                line = None
                sleep( 0.001 )
            else:
                print line
        

    def monitorhost( self ):
        host = None
        hostip = self.mn_pipes_table[0].get( 'emu_src' )
        for ip, name in self.hosts_map:
            if ip == hostip:
                host = name

        host = self.mn.get( name )
        cmd = 'strace -f -e trace=network -p %s', ( host.pid, )
        proc = host.popen( cmd, env=env, stdout=PIPE, bufsize=1,
                close_fds=ONPOSIX )
        return proc.stdout

    def enqueue_output( output, queue ):
        for line in iter( output.readline, b'' ):
            queue.put( line )
        output.close()
