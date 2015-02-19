#!/bin/bash

# Stop parasite logging and unload module
# this script needs sudo

# kill tcp_probe logging
LOG_PID=$(cat ./tempdisk/log_pid)
kill -9 $PARASITE_PID

# kill any other processes using the ramdisk
# i think this is a bad idea?
#lsof | grep $(pwd)"/tempdisk" | awk '{if (NR!=1) {print $2}}' | xargs kill -9

# unmount and delete ramdisk
umount -l ./tempdisk
rmdir tempdisk

# unload tcp_probe kernel module
modprobe -r tcp_probe
