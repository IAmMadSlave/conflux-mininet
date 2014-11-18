import math
import fileinput
import re
import string
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from math import sqrt 
from os import listdir,system
from os.path import join

#plot the data
plotfile = open(sys.argv[1], 'r')
t = []
p = []
ep = []
diffs = []
sample = 0
for line in plotfile.readlines():
    attr = line.split()
    time = float(attr[0])
    actual = float(attr[1])
    estimate = float(attr[2])
    if sample % 100 == 0:
        t.append(time)
        p.append(actual)
        ep.append(estimate)
        if actual == 0:
            diff = 0
        else:
            diff = abs(actual-estimate)/actual
        diffs.append(diff)
    sample = sample + 1
p = ((np.asarray(p)-min(p))/(max(p)-min(p))).tolist()
ep = ((np.asarray(ep)-min(ep))/(max(ep)-min(ep))).tolist()
print len(t),len(t),len(ep)    

fig, ax = plt.subplots()
plot1= ax.plot(t,p,'r',label='Measured')
plot2= ax.plot(t,ep,'go',label='Estimated', ms = 4)
plot3= ax.plot(t,diffs,'b--',label='Difference', ms = 4)
start,end = ax.get_xlim()
ax.xaxis.set_ticks(np.arange(start, end, 1))
ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.2f'))
starty,endy = ax.get_ylim()
ax.yaxis.set_ticks(np.arange(starty, endy, 0.1))
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
plt.title('total_sent_packets vs total_estimate_packets')
plt.xlabel('time')
plt.ylabel('normalized # of packets')
plt.legend(loc='upper left',numpoints=1)
plt.show()
fig.savefig(sys.argv[1]+".pdf",format='pdf')