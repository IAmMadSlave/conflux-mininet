#!/bin/bash
LOG="/home/localuser/Documents/Conflux/conflux-mininet/symbiosim-study/src/traffic_scripts/tempdisk/log.out"

START_LINE=$(grep -n -m 1 "10.0.0.1" $LOG)
START_LINE_NUM=$(echo $START_LINE | cut -d : -f 1)
START_SEC=$(echo $START_LINE | cut -d : -f 2 | cut -d . -f 1)

while :
do
    START_LINE=$(egrep -n -m 1 "^$START_SEC\\.[0-9]*\ 10\.0\.0\.1" $LOG)

    if [ -z "$START_LINE" ];then 
        break
    fi

    START_LINE_NUM=$(echo $START_LINE | cut -d : -f 1)
    echo $START_LINE | cut -d : -f 2-

    egrep -m 1 "^$START_SEC\\.[0-9]*\ 10\.0\.0\.2" $LOG
    egrep -m 1 "^$START_SEC\\.[0-9]*\ 10\.0\.0\.3" $LOG

    START_SEC=$((START_SEC+1))
done
