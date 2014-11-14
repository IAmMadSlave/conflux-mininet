import math
import fileinput
import re
import string
import sys
import numpy
from math import sqrt 
from os import listdir,system
from os.path import join

#Parse tcp and trace files
directory = sys.argv[1]
lossfiles = []
for file in listdir(directory):
    if 'tcp' in file:
        dst = join(directory,file.replace('out-', ''))
        cmd = "sed '/conn/d' %s > %s"%(join(directory,file),dst)
        system(cmd)
    elif 'tr' in file:
        dst = join(directory,(file.replace('out-', '')).replace('tr','ploss'))
        cmd = "grep 'd' %s > %s"%(join(directory,file),dst)
        lossfiles.append(dst)
        system(cmd)
# accumulate losses        
for file in lossfiles:
    file1 = open(file, "r")
    line1 = file1.readline()
    flowtable = {}
    loss = {}
    while line1: 
        param = line1.split(" ")
        time = float(param[1])
        flowid = int(param[7])
        if flowid not in flowtable.keys(): 
            flowtable[flowid]=[]
            loss[flowid]=0
        src = param[8]
        dst = param[9]
        loss[flowid] = loss[flowid] + 1
        a = (time,loss[flowid])
        flowtable[flowid].append(a)
        line1 = file1.readline()
    for item in flowtable:
        output = str(item) + ".loss"
        if 'reno' in file:
            output = output + ".reno"
        elif 'cubic' in file:
            output = output + ".cubic"    
        outputfile = open(join(directory,output), "w")
        for elem in flowtable[item]:
            outputfile.write("%s %s\n"%(elem[0],elem[1]))

    
    

      
