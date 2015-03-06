import re
import os
import sys
import time
import subprocess
import threading

class Traffic_Monitor():
    
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

    def run( self ):
        # module loading 
        self.start_module()
        print 'start module'

        # start continous logging
        t1_stop = threading.Event()
        t1 = threading.Thread( target=self.continous_update, args=(t1_stop,) )
        t1.start()
        print 'start t1'

        # start timed updates
        # change timeout from interval based to mininet finish?
        self.timed_update( t1_stop, 20)
        print 'start timed_update'
        t1_stop.set()
        t1.join()

        # module unloading
        self.stop_module()

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

    def continous_update( self, stop_event ):
        # continuously read /proc/net/tcpprobe and update pipe info
        with open( '/proc/net/tcpprobe' ) as tcplog:
                for line in tcplog:
                    for pipe in self.pipes_table:
                        if re.match( '^[0-9]*\.[0-9]*\ '
                                +str(pipe['src']).strip()
                                +'\:[0-9]*\ '
                                +str(pipe['dest']).strip(), line ):
                            lineparts = line.split( ' ' )
                            pipe['nxt'] = int( lineparts[4], 16 )
                    if stop_event.is_set():
                        break;
   
    def timed_update( self, probe_stop_event, timeout ):
        # write periodic traffic demand to file
        with open( self.demand_file, 'w') as demand:
            # write demand once per second
            i= 0
            for i in range( timeout ):
                for pipe in self.pipes_table:
                    demand.write( pipe['sim_src']+' '+pipe['sim_dest']+' '+str(
                        pipe['nxt'] ) +'\n' )
                time.sleep(1)
                # add drift control here

        probe_stop_event.set()

if __name__== '__main__':
        tm = Traffic_Monitor( 'mn_pipes_file', 'demand_file' )
        tm.run()
