from mininet.topo import Topo

import json
from pprint import pprint

class MiniSymbio( object ):

    def __init__( self, downscaled_topo ):
        # parse downscaled topology and create mappings
            # These could be just on the sim side
            # sim hosts to mininet hosts
            # mininet hosts to sim hosts
            # sim queues to mininet links
        emu_topo = Topo.__init__( self )

        d_topo_file = open( downscaled_topo)
        d_topo_data = json.load( d_topo_file )

        hosts_info = []
        for k in  d_topo_data['net']['hosts']:
            hosts.append( k )

        mn_hosts = []
        i = 1
        for h in hosts:
            mn_hosts[i] = 

        switches = []
        for s in d_topo_data['net']['switches']:
            switches.append( s )

        links = []
        for l in d_topo_data['net']['links']:
            links.append( l )

        for h in hosts:
            print h['name']

        print hosts

        d_topo_file.close()

        # instantiate mininet objects (nodes & links)
        # start the parasite
        # setup comms with sim this includes
            # a file for traffic demand going out
            # a file for tc changes coming from sim
            # protocol and formats will be specified later

#    def start():

#    def stop():

#    def async_cmd( cmd ):
        # returns a data structure with popen objects and their respecitive
        # hosts
        # PIPE for stdin, stdout, stderr
        # way to monitor

#    def async_terminate( hosts, cmd ):
        # terminate respective tasks

#    def async_wait( popen ):
        # wait for respective tasks (this is like a join operation)

#    def sync_cmd( hosts, cmd ):
        # sync_cmd

#    def run_cmd_on_hosts_collect_results( h, cmd ):
        # I don't know what this does!
    
if __name__== '__main__':
    ms = MiniSymbio( 'downscaled_topology.json' )
