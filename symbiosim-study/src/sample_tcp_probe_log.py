#!/usr/bin/python

if __name__ == '__main__':
    with open('log.out', 'r') as openfileobject:
        firstLine = openfileobject.readline()
        tokens = firstLine.split()
        maxNum = tokens[0]
        maxNum = maxNum.split('.')
        maxNum = maxNum[0]
        for t in tokens:
            print '%s ' % t,
        print '\n'
        #openfileobject.seek(0)
        for line in openfileobject:
            tokens = line.split()
            temp = tokens[0].split('.')[0]
            if temp > maxNum:
                maxNum = temp
                for t in tokens:
                    print '%s ' % t, 
                print '\n'
