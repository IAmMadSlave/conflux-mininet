import re
import os
import sys
import time
import logging
import subprocess
import threading

class Traffic_Monitor():
    
    def __init__( self, mn_flows_file, demand_file ):
        flows = []
        self.demand_file = demand_file
        
        with open( mn_flows_file, 'r') as openfile:
            for line in openfile:
                self.flows.append( line )

        i = 0
        for i in range( len( self.flows ) ):
            flows[i] = flows[i].split( ' ' )
            
        self.flow_table = []
        for f in self.flows:
            self.flow_table.append( {'dest': f[2].strip(), 'src': f[1].strip(),
                'nxt': 0, 'name': f[0].replace( ':', '' ) } )

    def run( self ):
        # module loading and unloading, etc
        self.start_module()

        # start continous logging
        t1_stop = threading.Event()
        t1 = threading.Thread( target=self.continous_update, args=(t1_stop,) )
        t1.start()

        # start timed updates
        self.timed_update( t1_stop )
        t1.join()

        self.stop_module()

    def start_module( self ):
        logging.info( 'unload kernel module' )
        subprocess.call( ['modprobe', '-r', 'tcp_probe'] )

        logging.info( 'load kernel module' )
        subprocess.call( ['modprobe', 'tcp_probe', 'full=0'] )

        logging.info( 'change permissions to read on tcp_probe output' )
        subprocess.call( ['chmod', '444', '/proc/net/tcpprobe'] )

    def stop_module( self ):
        logging.info( 'unload kernel module' )
        subprocess.call( ['modprobe', '-r', 'tcp_probe'] )

    def continous_update( self, stop_event ):
        logging.info( 'update flows' )
        # continuously read /proc/net/tcpprobe
        i = 0
        with open( '/proc/net/tcpprobe' ) as tcplog:
            #while (not stop_event.is_set() ):
                for line in tcplog:
                    for flow in self.flow_table:
                        if re.match( '^[0-9]*\.[0-9]*\ '
                                +str(flow['src']).strip()
                                +'\:[0-9]*\ '
                                +str(flow['dest']).strip(), line ):
                            lineparts = line.split( ' ' )
                            flow['nxt'] = int( lineparts[4], 16 )
                            if stop_event.is_set():
                                break;
                    
   
    def timed_update( self, stop_event ):
        logging.info( 'print flows' ) 

        with open( self.demand_file, 'w') as demand:
            # print flows every 1 second
            i= 0
            for i in range( 5 ):
                for flow in self.flow_table:
                    demand.write( flow['nxt'] )
                time.sleep(1)
                # add drift control here

        stop_event.set()

    def __str__( self ):
        line = ''

        for f in self.flow_table:
            line = line + str( f ) + '\n'

        return line

if __name__== '__main__':
        tm = Traffic_Monitor( 'flows' )
        tm.run()
