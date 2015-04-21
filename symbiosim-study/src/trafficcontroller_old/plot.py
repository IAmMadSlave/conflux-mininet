#!/bin/python
import pygal
from pygal.style import BlueStyle

with open('temp_filter.out', 'r' ) as temp:
    lines = temp.readlines()

    data = []
    for line in lines:
        new_line = line.split()
        seq = new_line[1].replace( ':', ' ' )
        seq = seq.split()
        data.append( (new_line[0], seq[0]) )

xy_chart = pygal.XY( stroke=False, fill=True, human_readable=True, show_legend=False, dots_size=2,  style=BlueStyle, x_title='Time (s)', y_title='Total Bytes' )
xy_chart.add( 'A', data )
xy_chart.render_to_file( 'plot.svg' )

