#!/bin/bash
for i in {1..20}
do
    ss --tcp | awk -v peerip=$1 '{if (NR!=1 && $4 == peerip) {print $3}}'
    sleep 1s
done
