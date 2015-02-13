#!/bin/bash

# This will be a script to load the tcp_probe kernel module as well as start the background logging of the probes output in the ramdisk
# this script needs sudo

# setup temporary ramdisk
mkdir tempdisk
mount -t tmpfs -o size=512m tmpfs ./tempdisk

# load tcp_probe kernel module
modprobe -r tcp_probe
modprobe tcp_probe full=1

# log output of tcp_probe module
chmod 444 /proc/net/tcpprobe
cat /proc/net/tcpprobe > ./tempdisk/log.out &
echo $! > ./tempdisk/log_pid
