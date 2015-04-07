#!/bin/python

import random
import decimal

data_list = []

i = 0
for i in range(10):
    j = 1
    r = random.randrange(100)
    for j in range(r): 
     data_list.append( float(i + decimal.Decimal(j)/100) )


temp_list = []
plot_list = []

current_interval = int(data_list[0])

i = 0
for i in range( len( data_list ) ):
    if int( data_list[i] ) == current_interval:
        temp_list.append( data_list[i] )
    else:
        j = 0
        sample_counter = 0
        for j in range( len ( temp_list ) ):
            if sample_counter == 5:
                break
            else:
                if j % (len( temp_list ) / 5 ) == 0:
                    plot_list.append(temp_list[j])
                    sample_counter = sample_counter + 1
        current_interval = int(data_list[i] )
        temp_list = []
        temp_list.append(data_list[i])
    i = i + 1

for p in plot_list:
    print p 
