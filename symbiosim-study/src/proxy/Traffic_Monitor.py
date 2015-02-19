import os
import time
import logging
import subprocess
from threading import Thread

class Traffic_Monitor( Thread ):
    
    def __init__( self ):
        Thread.__init__( self )

        # open downscaled topo
        # parse links and create table
        self.links = []
        
    def run( self ):
        # overloaded Thread.run
        for i in xrange(3):
            self.links.append(i)

        #while not self.cancelled:
        #    self.update()

            # add drift control to sleep
        #    time.sleep(1)

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
        for link in self.links:
            line += str(link)
            line += '\n'

        return line

if __name__== '__main__':
    try:
        tm = Traffic_Monitor()
        tm.start()

        print tm

        tm.join()
        print 'finished..'

    except IOError as e:
        if( e[0] == errno.EPERM ):
            print >> sys.sterr, 'Please run with root permissions'
            sys.exit(1)
