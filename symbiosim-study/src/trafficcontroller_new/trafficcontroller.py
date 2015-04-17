#!/bin/python

import threading
import subprocess
from mininet.net import Mininet
from time import sleep
from datetime import datetime

class trafficmonitor():

    def __init__( self, mn ):
        self.mn = mn
        self.run()
   
    # tc listener
    def run( self ):
        return

    def setup_tc( self, host ):
        cmd = '
        return

    def tc_change( self, host, bandwidth, drop_prob ):
        return
