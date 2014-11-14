##### Declare Simulator
set ns [new Simulator]
set psize   1500
set bsize 10000000
set max_window     200
set tcp_tick       0.001
##### Setting output file
set file [open conflux-mininet/fluid-study/ns2/out-cubic.tr w]
$ns trace-all $file
set tcpfile [open conflux-mininet/fluid-study/ns2/out-cubic.tcp w]
Agent/TCP set trace_all_oneline_ true
##### Setting Node
set n0 [$ns node]
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
##### Setting Link
$ns duplex-link $n0 $n1 1Gb 1ms DropTail
$ns duplex-link $n1 $n2 10Mb 64ms DropTail
$ns duplex-link $n2 $n3 1Gb 1ms DropTail
##### Setting Queue Length
$ns queue-limit $n1 $n2 50
##### Setting TCP Agent
set tcp [new Agent/TCP/Linux]
$tcp set timestamps_ true
$tcp set parcial_ack_ true
$tcp set window_  $max_window
$tcp set maxcwnd_ $max_window
$tcp set packetSize_ [expr $psize - 40]
$tcp set tcpTick_ $tcp_tick
$ns attach-agent $n0 $tcp
set sink [new Agent/TCPSink/Sack1]
$ns attach-agent $n3 $sink
$ns connect $tcp $sink
### Setting output file of TCP Agent
$tcp attach-trace $tcpfile
$tcp trace cwnd_
##### Setting FTP Application
set ftp [new Application/FTP]
$ftp attach-agent $tcp
$ftp set type_ FTP
#### Setting TCP flavor to be cubic
$ns at 0 "$tcp select_ca cubic"
##### Setting time schedule of simulation
$ns at 0.0 "$ftp start"
$ns at 30.0 "$ftp stop"
$ns at 40.0 "finish"
proc finish {} {
global ns file tcpfile
$ns flush-trace
close $file
close $tcpfile
exit 0
}
##### Finish setting and start simulation
$ns run
