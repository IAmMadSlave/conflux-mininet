import re
import os
import sys
import time
import subprocess
import threading

from subprocess import Popen, PIPE
from Queue import Queue, Empty
from datetime import datetime

ON_POSIX = 'posix' in sys.builtin_module_names

def enqueue_output( out, queue ):
    for line in iter( out.readline, b'' ):
        queue.put( line )
    out.close()

class TrafficMonitor():

    def __init__( self, mn_pipes_file ):
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
            self.pipes_table.append( {'delta': 0, 'sim_dest': p[4].strip(), 'dest':
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
        t1 = threading.Thread( target=enqueue_output, args=(cat.stdout, q,) )
        t1.daemon = True
        t1.start()

        t2 = threading.Thread( target=self.continous_update, args=(q,) )
        t2.daemon = True
        t2.start()


        # module unloading
        self.stop_module()
        return

    def start_module( self ):
        # unload kernel module
        subprocess.call( ['sudo', 'modprobe', '-r', 'tcp_probe'] )

        # load kernel module
        subprocess.call( ['sudo', 'modprobe', 'tcp_probe', 'full=0'] )

        # change permissions to read on tcp_probe output
        subprocess.call( ['sudo', 'chmod', '444', '/proc/net/tcpprobe'] )

    def stop_module( self ):
        # unload kernel module
        subprocess.call( ['sudo', 'modprobe', '-r', 'tcp_probe'] )

    def continous_update( self, q ):
        testfile = open('test_file', 'w')
        while True:
            try:
                line = q.get_nowait()
            except Empty:
                line = None
	    	time.sleep(0.001)
            else:
                lineparts = line.split( ' ' )

                src = lineparts[1].split( ':' )
                src = src[0].strip()
                dest = lineparts[2].split( ':' )
                dest = dest[0].strip()

                for pipe in self.pipes_table:
                    if pipe['src'] == src and pipe['dest'] == dest:
                        seq = str( lineparts[4] )
                        seq = int( seq, 16 )
                        if pipe['nxt'] == 0:
                            tempseq = seq
                            testfile.write(lineparts[0]+ ' '+'0'+'\n')
                            testfile.flush()
                            pipe['nxt'] = seq
                        else:
                            testfile.write(lineparts[0]+' '+str(seq-tempseq)+'\n')
                            testfile.flush()

                            delta  = seq - pipe['nxt']
                            if delta < 0:
                                delta = delta + 0xffffffff
                                #print seq, pipe['nxt']

                            pipe['delta'] = pipe['delta'] + delta
                            pipe['nxt'] = seq
