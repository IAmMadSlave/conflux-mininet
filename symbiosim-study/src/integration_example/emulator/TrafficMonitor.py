import re
import os
import sys
import time
import subprocess
import threading
from subprocess import Popen, PIPE
from Queue import Queue, Empty

ON_POSIX = 'posix' in sys.builtin_module_names

def enqueue_output( out, queue ):
    for line in iter( out.readline, b'' ):
            queue.put( line )
    out.close()

class TrafficMonitor():
    
    def __init__( self, mn_pipes_file, demand_file ):
        # for writing demand to file
        self.demand_file = demand_file
      
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
        # module loading 
        self.start_module()

        env = os.environ.copy()
        env['LC_ALL'] = 'C'
        cat = Popen( ['cat', '/proc/net/tcpprobe'], env=env, stdout=PIPE, bufsize=1,
            close_fds=ON_POSIX )

        q = Queue()
        t1 = threading.Thread( target=enqueue_output, args=(cat.stdout, q) )
        t1.daemon = True
        t1.start()

        t2 = threading.Thread( target=self.continous_update, args=(q,) )
        t2.daemon = True
        t2.start()
       
        t3 = threading.Thread( target=self.timed_update )
        t3.start()

        t3.join()
        cat.terminate()
        # module unloading
        self.stop_module()
        return

    def start_module( self ):
        # unload kernel module
        subprocess.call( ['modprobe', '-r', 'tcp_probe'] )

        # load kernel module
        subprocess.call( ['modprobe', 'tcp_probe', 'full=0'] )

        # change permissions to read on tcp_probe output
        subprocess.call( ['chmod', '444', '/proc/net/tcpprobe'] )

    def stop_module( self ):
        # unload kernel module
        subprocess.call( ['modprobe', '-r', 'tcp_probe'] )

    def continous_update( self, q ):
        while True:
            try:
                line = q.get_nowait()
            except Empty:
                line = None
            else:
                lineparts = line.split( ' ' )

                src = lineparts[1].split( ':' )
                src = src[0].strip()
                dest = lineparts[2].split( ':' )
                dest = dest[0].strip()

                for pipe in self.pipes_table:
                    if pipe['src'] == src and pipe['dest'] == dest:
                        if pipe['nxt'] != lineparts[4]:
                            pipe['nxt'] = lineparts[4]
                        else:
                            pipe['nxt'] = 0

    def timed_update( self ):
        while True:
            demand = open( self.demand_file, 'w' )
            for pipe in self.pipes_table:
                demand.write( pipe['sim_src']+' '+pipe['sim_dest']+' '+str(pipe['nxt'] )+'\n' )
                time.sleep(1)
            demand.close()
        return
