# Stop parasite logging and unload module
# this script needs sudo

# if ubuntu or debian? use /run
# else maybe /shm/dev

# in this example we will be using /run

#!/bin/bash

PARASITE_PID=$(cat /run/parasite/parasite_pid)
kill -9 $PARASITE_PID
rm /run/parasite/parasite_pid
modprobe -r tcp_probe
