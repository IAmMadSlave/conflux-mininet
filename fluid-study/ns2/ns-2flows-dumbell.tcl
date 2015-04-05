##### Declare Simulator
set ns [new Simulator]
set psize   1500
set bsize 10000000
set max_window     200
set tcp_tick       0.001
##### Setting output file
set file [open conflux-mininet/fluid-study/ns2/out.tr w]
$ns trace-all $file
set tcpfile1 [open conflux-mininet/fluid-study/ns2/out.tcp1 w]
set tcpfile2 [open conflux-mininet/fluid-study/ns2/out.tcp2 w]
Agent/TCP set trace_all_oneline_ true
##### Setting Node
set n0 [$ns node]
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
##### Setting Link
$ns duplex-link $n0 $n1 1Gb 1ms DropTail
$ns duplex-link $n4 $n1 1Gb 1ms DropTail
$ns duplex-link $n1 $n2 10Mb 64ms DropTail
$ns duplex-link $n2 $n3 1Gb 1ms DropTail
$ns duplex-link $n2 $n5 1Gb 1ms DropTail
##### Setting Queue Length
$ns queue-limit $n1 $n2 50
##### Setting TCP Agent
set tcp1 [new Agent/TCP]
$tcp1 set timestamps_ true
$tcp1 set parcial_ack_ true
$tcp1 set window_  $max_window
$tcp1 set maxcwnd_ $max_window
$tcp1 set packetSize_ [expr $psize - 40]
$tcp1 set tcpTick_ $tcp_tick
$tcp1 set fid_ 0
$ns attach-agent $n0 $tcp1
set sink [new Agent/TCPSink]
$ns attach-agent $n3 $sink
$ns connect $tcp1 $sink
set tcp2 [new Agent/TCP]
$tcp2 set timestamps_ true
$tcp2 set parcial_ack_ true
$tcp2 set window_  $max_window
$tcp2 set maxcwnd_ $max_window
$tcp2 set packetSize_ [expr $psize - 40]
$tcp2 set tcpTick_ $tcp_tick
$tcp2 set fid_ 1
$ns attach-agent $n4 $tcp2
set sink1 [new Agent/TCPSink]
$ns attach-agent $n5 $sink1
$ns connect $tcp2 $sink1
### Setting output file of TCP Agent
$tcp1 attach-trace $tcpfile1
$tcp1 trace cwnd_
$tcp2 attach-trace $tcpfile2
$tcp2 trace cwnd_
##### Setting FTP Application
set ftp1 [new Application/FTP]
$ftp1 attach-agent $tcp1
$ftp1 set type_ FTP
set ftp2 [new Application/FTP]
$ftp2 attach-agent $tcp2
$ftp2 set type_ FTP
##### Setting time schedule of simulation
$ns at 0.0 "$ftp1 start"
$ns at 15.0 "$ftp2 start"
$ns at 30.0 "$ftp1 stop"
$ns at 30.0 "$ftp2 stop"
$ns at 40.0 "finish"
proc finish {} {
global ns file tcpfile1 tcpfile2
$ns flush-trace
close $file
close $tcpfile1
close $tcpfile2
exit 0
}
##### Finish setting and start simulation
$ns run
