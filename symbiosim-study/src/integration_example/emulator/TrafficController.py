import re
import os
import sys
import time
import subprocess
import threading
from subprocess import Popen, PIPE
from Queue import Queue, Empty

from mininet.net import Mininet

ON_POSIX = 'posix' in sys.builtin_module_names

def enqueue_output( out, queue ):
    for line in iter( out.readline, b'' ):
            queue.put( line )
    out.close()

class TrafficController():
    
    def __init__( self, mn_pipes_file, tc_file, mn_ip, mn ):
        self.mn_ip = mn_ip
        self.mn = mn

        # read pipe info 
        pipes = []
        with open( mn_pipes_file, 'r') as openfile:
            for line in openfile:
                pipes.append( line )

        i = 0
        for i in range( len( pipes ) ):
            pipes[i] = pipes[i].split( ' ' )
           
        # setup pipes in memory 
        self.pipes_table = []
        for p in pipes:
            self.pipes_table.append( {'sim_dest': p[4].strip(), 'dest':
                p[3].strip(), 'sim_src': p[2].strip(), 'src': p[1].strip(),
                'nxt': 0, 'name':p[0].strip() } )

        self.run()

    def run( self ):
        env = os.environ.copy()
        env['LC_ALL'] = 'C'
        cat = Popen( ['cat', 'tc_file'], env=env, stdout=PIPE, bufsize=1,
            close_fds=ON_POSIX )

        q = Queue()
        t1 = threading.Thread( target=enqueue_output, args=(cat.stdout, q) )
        t1.daemon = True
        t1.start()

        t2 = threading.Thread( target=self.continous_update, args=(q,) )
        t2.daemon = True
        t2.start()

        cat.terminate()
        return

    def continous_update( self, q ):
        while True:
            try:
                line = q.get_nowait()
            except Empty:
                line = None
            else:
                lineparts = line.split( ' ' )
                for p in self.pipes_table:
                    if p['name'] == lineparts[0]:
                        for ip in self.mn_ip:
                            if ip.get( 'ip' ) == p['src']:
                                hostname = ip.get( 'name' )
                host = self.mn.getNodeByName( hostname )
                host.cmd( 'tc qdisc dev %s add netem rate %dbits', host.defaultIntf() , lineparts[2] )
                host.cmd( 'tc qdisc change dev %s root netemm loss %d', host.defaultIntf() , lineparts[1] )

                    
