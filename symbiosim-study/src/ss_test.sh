#!/bin/bash
for i in {1..20}
do
    TIMESTAMP=$(date "+%H:%M:%S:%N")
    ss --tcp | awk -v "ts=$TIMESTAMP" '{if (NR!=1) {printf "%d\t%d\t %s \t %s \t %s\n", $2, $3, $4, $5, ts}}'
    sleep 1s
done
