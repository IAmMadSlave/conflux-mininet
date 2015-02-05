#!/bin/bash
LOG="log.out"
COUNTER=$(head -n 1 $LOG | cut -d '.' -f 1)
MAX=$(tail -n 1 $LOG | cut -d '.' -f 1)

while [ $COUNTER -le $MAX ]
do
    grep -m 1 "^${COUNTER}\\." $LOG
    COUNTER=$((COUNTER+1))
done
