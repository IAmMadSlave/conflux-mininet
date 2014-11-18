import math
import fileinput
import re
import string
import sys
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt 
from os import listdir,system
from os.path import join

#Parse loss file to generate the loss probability curve
lossfile = open(sys.argv[1], 'r')
tcpfile = open(sys.argv[2], 'r')
times = []
accumlosses = []
for line in lossfile.readlines():
    time = float(line.split()[0])
    times.append(time)
    accumloss = float(line.split()[1])
    accumlosses.append(accumloss) 
#print times[0], times[len(times)-1]
def loss(x):
    loss = 0
    if x < times[0] and x >= 0:
#        print "I am in first time slot."
        loss = 0        
    elif x >= times[len(times)-1]: 
#        print "I am in last time slot."
        loss = accumlosses[len(times)-1]
    else:
        for i in range(len(times)):
            if x < times[i] and x >= times[i-1]:
#                print times[i-1],times[i]
#                print "I am in %d time slot."%(i-1)
                loss = accumlosses[i-1]
                break
    return loss
# Calculate the estimated sent packets
# Put timestamp, the estimated sent packets, the actual sent packets(from trace) into a file  
b = 1
totalsent = 0
lasttime = 0
lastthru = 0
nline = 0
finalfile = open(sys.argv[3], 'w')
flowstart = sys.argv[4]
for line in tcpfile.readlines():
    attr = line.split()
    recvtime = float(attr[0])
    if nline == 0 and recvtime != flowstart:
        recvtime = float(flowstart)
    rtt = float(attr[2])
    prevtime = recvtime-rtt
    cwnd = float(attr[1])
    ack = float(attr[3])
    currloss = loss(recvtime)
    prevloss = loss(prevtime)
    if currloss != prevloss:
#        print "currtime:%.4f prevtime:%.4f window:%.1f currloss:%.4f prevloss:%.4f"%(recvtime,prevtime,lastcwnd,currloss,prevloss)
        prob = (currloss - prevloss)/cwnd
#        print prob
    else:
        prob = 0
    if prob == 0:
        if rtt == 0:
            thru = 0
        else:
            thru = cwnd/rtt
    else:
        thru = min(1/(rtt*sqrt(2*b*prob/3) + 0.2*(3*sqrt(3*b*prob/8)*prob*(1+32*pow(prob,2)))),cwnd/rtt)
    if 0:    
        lastsent = lastthru*(recvtime-lasttime)
        totalsent = totalsent+lastsent
        print "currtime:%.4f lasttime:%.4f cwnd:%.4f rtt:%.4f lastthru:%.4f sent:%.4f total_sent:%.4f"%(recvtime,lasttime,cwnd,rtt,lastthru,lastsent,totalsent)
    sent = thru*(recvtime-lasttime)
    totalsent = totalsent+sent  
#    print "currtime:%.4f lasttime:%.4f cwnd:%.4f rtt:%.4f thru:%.4f sent:%.4f total_sent:%.4f"%(recvtime,lasttime,cwnd,rtt,thru,sent,totalsent)
    finalfile.write("%8.5f %6.3f %6.3f\n"%(recvtime, ack, totalsent))
    lasttime = recvtime
    lastthru = thru
    nline = nline+1
    


    

   
    





    

      
