#!/bin/python

import sys
import pygal
from pygal.style import BlueStyle

with open( sys.argv[1], 'r' ) as log:
    lines = log.readlines()

    i = 0
    for i in range( len( lines ) ):
        lines[i] = lines[i].replace( ',', '' )
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

    full = []
    i = 0
    for t in times:
        full.append( (times[i], total_bytes[i]) )
        i = i + 1

    graph_title = sys.argv[1]
    last_index = graph_title.rfind( '/' )
    graph_title = graph_title[last_index+1::]

    xy_chart = pygal.XY( stroke=False, fill=True, human_readable=True,
            show_legend=False, dots_size=2,  style=BlueStyle, x_title='Time (s)', y_title='Total Bytes', title=graph_title )
    #xy_chart.add( 'A', plot_list )
    xy_chart.add( 'A', full )
    #xy_chart.render_to_png( 'plot.png' )
    xy_chart.render_to_file( 'plot.svg' )
