import re
import os
import sys
import time
import subprocess
import threading
import socket
from subprocess import Popen, PIPE
from Queue import Queue, Empty
from datetime import datetime

ON_POSIX = 'posix' in sys.builtin_module_names

#sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
#server_address = ( 'localhost', 51717 )
#sock.connect( server_address )

def enqueue_output( out, queue ):
    for line in iter( out.readline, b'' ):
            queue.put( line )
    out.close()

class TrafficMonitor():
    
    def __init__( self, mn_pipes_file, demand_file, sock ):
        # for writing demand to file
        self.demand_file = demand_file
        self.sock = sock
        print('TrafficMonitor:sock %s' % self.sock)
      
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
       
        t3 = threading.Thread( target=self.timed_update )
        t3.start()

        t3.join()
        cat.terminate()
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
                            testfile.write(lineparts[0]+' '+'0'+'\n' )
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

    def timed_update( self ):
        with open( self.demand_file, 'w' ) as demand:
            while True:
                msg = ''
                for pipe in self.pipes_table:
                    if pipe['delta'] != 0:
                        demand.write( pipe['sim_src']+' '+pipe['sim_dest']+' '+str( pipe['delta'] )+' '+str( pipe['nxt'] )+'\n' )
                        demand.flush()
                        msg += pipe['sim_src']+' '+pipe['sim_dest']+' '+str(pipe['delta'])+'\n'
                        #print msg
                        pipe['delta'] = 0
                    else:
                        msg += pipe['sim_src']+' '+pipe['sim_dest']+' '+str( 0 )+'\n'
                #msg = pipe['sim_src']+' '+pipe['sim_dest']+' '+str(10000)+'\n'
                #self.sock.sendall( msg )
                #print('msg:%s at %s'% (msg, str(datetime.now())))
                #data = self.sock.recv(256)
                #received = len(data)
                #print('msg: %s at: %s size: of %s'%(data, str(datetime.now()),str(received)))
                time.sleep(1)

#if __name__ == '__main__':
#    tm = TrafficMonitor( 'mn_pipes_file', 'demand_file' )
