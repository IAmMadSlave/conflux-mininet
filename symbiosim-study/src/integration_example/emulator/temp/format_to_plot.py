#!/bin/python

import sys
import pygal
from pygal.style import LightColorizedStyle

with open( sys.argv[1], 'r' ) as log:
    lines = log.readlines()

    i = 0
    for i in range( len( lines ) ):
        #lines[i] = lines[i].replace( ',', '' )
        lines[i] = lines[i].replace( ':', ' ' )
        lines[i] = lines[i].replace( '.', ' ' )
        lines[i] = lines[i].split()
        i = i + 1

    first_hr  = int( lines[0][0] )
    first_min = int( lines[0][1] )
    first_sec = int( lines[0][2] )
    #first_ms  = int( lines[0][3] )
    #prev_seq  = int( lines[0][4] )

    times = []
    total_bytes = []
    total_byte = 0
    for line in lines:
        time_hours = ( int(line[0]) - first_hr ) * 3600
        time_mins  = ( int(line[1]) - first_min ) * 60
        time_secs  = ( int(line[2]) - first_sec )
        #time_ms    = int(line[3])
        time_ms    = float('0.' + str(line[3]))

        time_total = int(time_hours) + int(time_mins) + int(time_secs)
        #time_total = str(time_total) + '.' + str(time_ms)
        time_total = float(time_total) + time_ms

        total_byte = total_byte + int(line[4])

        times.append( time_total )
        total_bytes.append( total_byte )

    data_set = []
    i = 0
    for i in range( len( times ) ):
        if ( i % 10 == 0 ):
            data_set.append( (times[i], total_bytes[i]) )
        i = i + 1

    print len( times )
    print len( total_bytes )

    xy_chart = pygal.XY( stroke=False, human_readable=True, show_legend=False, dots_size=1,  style=LightColorizedStyle )
    xy_chart.add( 'A', data_set )
    xy_chart.render_to_file( 'plot.svg' )

    #plt.plot( times, total_bytes, 'r--' ) 
    #plt.xlabel('Time (s)')
    #plt.ylabel('Total bytes')
    #plt.grid(True)
    #plt.savefig( 'plot.png' )
