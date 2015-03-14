#!/bin/python

import os
import time
from mininet.net import Mininet

class TrafficController():
    def __init__( self, mn_pipes_file, tc_file, mn_ips ):
        self.tc_file = tc_file
        self.mn_ips = mn_ips

        self.pipes = []
        with open( mn_pipes_file, 'r' ) as openfile:
            for line in openfile:
                self.pipes.append( line )
        
        i = 0
        for i in range( len( self.pipes ) ):
            self.pipes[i] = self.pipes[i].split( ' ' )
            #self.pipes[i].append( mn_ips[i].get( 'name' ) )
            j = 0
            for j in range( len( self.pipes[i] ) ):
                self.pipes[i][j] = self.pipes[i][j].strip()
    
    def timed_read( self ):
        while True:
            with open( self.tc_file, 'r' ) as tcfile:
                lines = tcfile.readlines()
                for line in lines:
                    lineparts = line.split( ' ' )
                    for pipe in self.pipes:
                        # match pipe id in tc_file
                        if pipe[0] == lineparts[0]:
                            # get mn hostname
                            for ip in self.mn_ips:
                                if ip.get( 'ip' ) == pipe[1]:
                                    print ip.get( 'name' )
            time.sleep(1)



if __name__ == '__main__':
    mn_ips = [ {'name': 'h1', 'ip': '10.0.0.1'}, {'name': 'h2', 'ip':
    '10.0.0.2'} ]

    tc = TrafficController( 'mn_pipes_file', 'tc_file', mn_ips )
    tc.timed_read()
