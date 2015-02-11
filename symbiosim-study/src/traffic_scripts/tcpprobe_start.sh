# This will be a script to load the tcp_probe kernel module as well as start the background logging of the probes output in the ramdisk
# this script needs sudo

# if ubuntu or debian? use /run
# else maybe /shm/dev

# in this example we will be using /run

#!/bin/bash

modprobe -r tcp_probe
modprobe tcp_probe full=1
chmod 444 /proc/net/tcpprobe
mkdir /run/parasite
cat /proc/net/tcpprobe > /run/parasite/log.out &
echo $! > /run/parasite_pid
