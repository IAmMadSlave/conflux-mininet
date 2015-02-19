#!/bin/bash
for i in {1..20}
do
    TIMESTAMP=$(date "+%H:%M:%S:%N")
    ss --tcp | awk -v "ts=$TIMESTAMP" '{if (NR!=1) {printf "%-20d\t%-20d\t%-20s\t%-20s\t%-20s\n", $2, $3, $4, $5, ts}}'
    sleep 0.01s
done
