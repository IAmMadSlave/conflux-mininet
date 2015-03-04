#!/bin/env python

import os
import time
import logging
import subprocess

import threading

def start_module():
    logging.info( 'unload kernel module' )
    subprocess.call( ['modprobe', '-r', 'tcp_probe'] )

    logging.info( 'load kernel module' )
    subprocess.call( ['modprobe', 'tcp_probe', 'full=1', 'bufsize=512'] )

    logging.info( 'change permissions to read on tcpprobe output' )
    subprocess.call( ['chmod', '444', '/proc/net/tcpprobe'] )

def stop_module():
    logging.info( 'unload kernel module' )
    subprocess.call( ['modprobe', '-r', 'tcp_probe'] )

def update_log( logfile ):
    while True:
        line = logfile.readline()
        if not line:
            time.sleep(0.1)
            continue
        line

try:
    # 
    logfile = open( '/proc/net/tcpprobe' )
    log = update_log( logfile )

    
except IOError as e:
    if( e[0] == errno.EPERM ):
        print >> sys.stderr, "Please run with root permissions"
        sys.exit(1)
