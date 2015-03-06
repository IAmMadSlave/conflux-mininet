import re
import os
import sys
import time
import logging
import subprocess
from threading import Thread
import threading


class Traffic_Monitor():
    
    def __init__( self, flows_file ):
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
            self.flow_table.append( {'dest': f[2].strip(), 'src': f[1].strip(),
                'nxt': 0, 'name': f[0].replace( ':', '' ) } )

    def run( self ):
        # do main stuff here
        print 'OLD...'
        print self.__str__()

        # module loading and unloading, etc
        self.start_module()

        # logging as well
        t1_stop = threading.Event()
        t1 = threading.Thread( target=self.testing, args=(t1_stop,) )
        t1.start()

        i = 0
        for i in range(5):
            print 'MAIN...'
            time.sleep(0.5)

        t1_stop.set()

        self.stop_module()
        print 'NEW...'
        print self.__str__()

        t1.join()

    def testing( self, stop_event ):
        while( not stop_event.is_set() ):
            for t in self.flow_table:
                print t['nxt']
            time.sleep(0.3)

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
                        if re.match( '^[0-9]*\.[0-9]*\ '+flow_table[0]['src']+':[0-9]*\ '+flow_table[0]['dest'], line ):
                            lineparts = line.split( ' ' )
                            flow_table[0]['new'] = lineparts[4]
            #except KeyboardInterrupt:
            #    print 'done'
   
    def timed_update( self ):
        logging.info( 'print flows' ) 
        # print flows every 1 second
        # add drift control here

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
        tm.run()
