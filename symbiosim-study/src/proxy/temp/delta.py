#!/bin/python

with open( 'snd_nxt_dec_start', 'r') as snd_nxt:
    lines = snd_nxt.readlines()
   
    current = 0
    for line in lines:
        print (int( line ) - current)
        current = int( line )
        
