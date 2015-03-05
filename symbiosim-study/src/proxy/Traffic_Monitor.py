import os
import sys
import time
import logging
import subprocess
from threading import Thread

class Traffic_Monitor( Thread ):
    
    def __init__( self, flows_file ):
        Thread.__init__( self )
       
        self.flows = []
        with open( flows_file, 'r') as openfile:
            for line in openfile:
                self.flows.append( line )

        i = 0
        for i in range( len( self.flows ) ):
            self.flows[i] = self.flows[i].split( ' ' )
            
        self.flow_table = []
        for f in self.flows:
            self.flow_table.append( {'name': f[0], 'old': None, 'new': None} )
        
    def run( self ):
        i = 0
        for f in self.flow_table:
            f['old'] = i
            i = i + 1

    def start_module( self ):
        logging.info( 'unload kernel module' )
        subprocess.call( ['modprobe', '-r', 'tcp_probe'] )

        logging.info( 'load kernel module' )
        subprocess.call( ['modprobe', 'tcp_probe', 'full=1'] )

        logging.info( 'change permissions to read on tcp_probe output' )
        subprocess.call( ['chmod', '444', '/proc/net/tcpprobe'] )

    def stop_module( self ):
        logging.info( 'unload kernel module' )
        subprocess.call( ['modprobe', '-r', 'tcp_probe'] )

    def update( self ):
        loggin.info( 'update links' )

    def __str__( self ):
        line = ''

        for f in self.flow_table:
            line = line + str( f ) + '\n'

        return line

if __name__== '__main__':
    try:
        #flows = [1, 2, 3]

        tm = Traffic_Monitor( 'flows' )
        print 'OLD...'
        print tm
        tm.start()
        tm.join()
        print '\n'
        print 'NEW...'
        print tm
        print 'finished..'

    except IOError as e:
        if( e[0] == errno.EPERM ):
            print >> sys.sterr, 'Please run with root permissions'
            sys.exit(1)
