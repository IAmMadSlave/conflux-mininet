#Assuming that the primogeni and conflux-mininet is checkout at the same directory.
echo "Enter primogeni directory: "
read primogeni 
echo "Enter conflux-mininet directory: "
read confluxmininet
echo "Primogeni: $primogeni, conflux-mininet: $confluxmininet"

if [ -d $primogeni ]; then
	if [ -d $confluxmininet ]; then
		echo "Source and destination exists."
		cp ${confluxmininet}/mininet-study/portal_device.cc ${primogeni}/netsim/src/ssfnet/os/emu/
                cp ${confluxmininet}/mininet-study/portal_device.h ${primogeni}/netsim/src/ssfnet/os/emu/
		echo "copied two files"
	else
		echo "fail"
	fi
else 
	echo "fail"
fi
	

#mv $confluxmininet/
