#!/bin/python

import numpy as np
import matplotlib.pyplot as plt

with open( 'tcpdump_set_a_10s_filtered_less.out', 'r' ) as log:
    lines = log.readlines()

    i = 0
    for i in range( len( lines ) ):
        lines[i] = lines[i].replace( ':', ' ' )
        lines[i] = lines[i].replace( '.', ' ' )
        lines[i] = lines[i].split()
        i = i + 1

    first_hr  = int( lines[0][0] )
    first_min = int( lines[0][1] )
    first_sec = int( lines[0][2] )
    first_ms  = int( lines[0][3] )
    prev_seq  = int( lines[0][4] )

    times = []
    total_bytes = []
    for line in lines:
        time_hours = ( int(line[0]) - first_hr ) * 3600
        time_mins  = ( int(line[1]) - first_min ) * 60
        time_secs  = ( int(line[2]) - first_sec )
        time_ms    = int(line[3])

        time_total = int(time_hours) + int(time_mins) + int(time_secs)
        time_total = str(time_total) + '.' + str(time_ms)
        time_total = float( time_total )

        total_byte = int(line[4]) - prev_seq

        times.append( time_total )
        total_bytes.append( total_byte )

    plt.plot( times, total_bytes, 'r--' ) 
    plt.xlabel('Time (s)')
    plt.ylabel('Total bytes')
    plt.axis( [0, 201, 0, 150000000] )
    plt.grid(True)
    plt.savefig( 'plot.png' )
