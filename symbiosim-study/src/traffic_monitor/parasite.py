#!/bin/env python

import logging
import os
import subprocess
import time

try:
    logging.info( 'unload kernel module' )
    subprocess.call( ['modprobe', '-r', 'tcp_probe'] )

    logging.info( 'load kernel module' )
    subprocess.call( ['modprobe', 'tcp_probe', 'full=1', 'bufsize=512'] )

    logging.info( 'change permissions to read on tcpprobe output' )
    subprocess.call( ['chmod', '444', '/proc/net/tcpprobe'] )

    with open( '/proc/net/tcpprobe' ) as f:
        for i in range(1, 10):
            flag = True
            while flag:
                f.readline()
            print f.readline()

    logging.info( 'close devnull' )
    devnull.close()

except IOError as e:
    if( e[0] == errno.EPERM ):
        print >> sys.stderr, "Please run with root permissions"
        sys.exit(1)
