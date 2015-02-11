#!/bin/bash
LOG="/home/localuser/Documents/Conflux/conflux-mininet/symbiosim-study/src/logs/log.out"

COUNTER=$(head -n 1 $LOG | cut -d '.' -f 1)
MAX=$(tail -n 1 $LOG | cut -d '.' -f 1)
START_LINE=$(egrep -n -m 1 "^${COUNTER}\\.[0-9]*\ 10\.0\.0\.1" $LOG)
START_LINE_NUM=$(echo $START_LINE | cut -d : -f 1)
START_LINE_NUM_TEMP=0

while [ $START_LINE_NUM_TEMP -ge 0 ] 
do
    START_LINE=$(tail -n +$START_LINE_NUM $LOG | egrep -n -m 1 "^${COUNTER}\\.[0-9]*\ 10\.0\.0\.1")
    START_LINE_NUM_TEMP=$(echo $START_LINE | cut -d : -f 1)
    START_LINE_NUM_TEMP=$((START_LINE_NUM_TEMP-1))
    START_LINE_NUM=$((START_LINE_NUM_TEMP+START_LINE_NUM))
    echo $START_LINE | cut -d : -f 2-

    tail -n +$START_LINE_NUM $LOG | egrep -m 1 "^${COUNTER}\\.[0-9]*\ 10\.0\.0\.2" 
    tail -n +$START_LINE_NUM $LOG | egrep -m 1 "^${COUNTER}\\.[0-9]*\ 10\.0\.0\.3"
    COUNTER=$((COUNTER+1))
done
