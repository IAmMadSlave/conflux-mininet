import sys
import re


with open (sys.argv[1], 'r') as log:
    lines = log.readlines()
#output = open(sys.argv[2], 'w')
out = []
lastseq = 0
for line in lines:
    temp = line.split('\t')
    time = (temp[0].split(':'))[2]
    if re.match(r"0+\d+\.\d*", time):
        if time.lstrip('0').startswith('.'):
            time = '0' + time.lstrip('0')
        else:
            time = time.lstrip('0')
    seq = (temp[1].split(':'))[0].replace(',\t', '')
    seq = int(seq)
    if seq - lastseq < 0:
        print seq, lastseq
        for item in out[::-1]:
            if item[1] > seq:
                #print item
                out.remove(item)
            else:
                break
    out.append((time,seq))
    lastseq = seq
output = open(sys.argv[2], 'w')
for item in out:
    #print item[0],item[1]
    output.write('%s %s\n' % (str(item[0]), str(item[1])))





