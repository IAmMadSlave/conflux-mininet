import re
import os
import sys
import time
import logging
import subprocess
from threading import Thread
import threading

def threaded( fn ):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

class Traffic_Monitor( Thread ):
    
    def __init__( self, flows_file ):
        Thread.__init__( self )

        self.readloop = True

        self.flows = []
        with open( flows_file, 'r') as openfile:
            for line in openfile:
                self.flows.append( line )

        i = 0
        for i in range( len( self.flows ) ):
            self.flows[i] = self.flows[i].split( ' ' )
            
        self.flow_table = []
        for f in self.flows:
            self.flow_table.append( {'dest': f[2].strip(), 'src': f[1].strip(), 'old': None, 'new': None, 'name': f[0].replace( ':', '' ) } )
        
    def run( self ):
        for f in self.flow_table:
            f['old'] = 0

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
        with open( '/proc/net/tcpprobe' ) as tcplog:
            #try:
                while (not stop_event.is_set):
                    for line in tcplog:
                        if re.match( '^[0-9]*\.[0-9]*\ '+self.flow_table[0]['src']+':[0-9]*\ '+self.flow_table[0]['dest'], line ):
                            lineparts = line.split( ' ' )
                            self.flow_table[0]['new'] = lineparts[4]
            #except KeyboardInterrupt:
            #    print 'done'

    def timed_update( self ):
        logging.info( 'print flows' ) 
        # print flows every 1 second
        # add drift control here
        t1_stop = threading.Event()
        t1 = threading( target=self.continous_update, args=t1_stop )

        count = 0
        for count in range( 20 ):
            print self.flow_table[0]['new']
            time.sleep(1)

        stop_event.set()

    def __str__( self ):
        line = ''

        for f in self.flow_table:
            line = line + str( f ) + '\n'

        return line

if __name__== '__main__':
        tm = Traffic_Monitor( 'flows' )

        print 'OLD...'
        print tm

        tm.start()
        tm.start_module()
        
        tm.timed_update()
        
        tm.stop_module()
        tm.join()

        print 'NEW...'
        print tm
        print 'finished..'
