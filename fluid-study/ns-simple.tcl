#Create a simulator object
set ns [new Simulator]
set tcp_tick       0.001
set dt 0.1 ; # sampling interval (in seconds) used when logging cwnd etc
set psize   1500
set bsize 10000000
set max_window     20000
set tcp_tick       0.001

### PRINT INDIVIDUAL CWND #################################################
proc printtcp {fp tcp sink lastbytes rate T} {
  global ns dt tcp_tick

  set now [$ns now]
  if { $T >=1.0} {
      set rate [expr ([$sink set bytes_]-$lastbytes)*8.0/(1000000*$T) ]
      set lastbytes [$sink set bytes_]
      set T 0.0
   }
  puts $fp "[format %.2f $now] [$tcp set cwnd_] [expr [$tcp  set srtt_]/8*$tcp_tick*1000]  [$sink set bytes_] $rate"
  $ns at [expr $now+$dt] "printtcp $fp $tcp $sink $lastbytes $rate [expr $T+$dt]"
}

proc print-tcpstats {tcp sink starttime label} {
  global ns dt
  set fp [open "$label.out" w]
  set lastbytes 0
  $ns at $starttime "printtcp $fp $tcp $sink 0 0 0"
}

### PRINT INDIVIDUAL QUEUE #################################################
proc printqueue {fp queue} {
  global ns dt
  set now [$ns now]
  puts $fp "[format %.2f $now] [$queue set size_] [$queue set pkts_] [$queue set parrivals_] [$queue set barrivals_] [$queue set pdepartures_] [$queue set bdepartures_] [$queue set pdrops_] [$queue set bdrops_]";
  $ns at [expr $now+$dt] "printqueue $fp $queue"
}

proc print-qstats {fname queue} {
  global ns
  set fp [open "$fname.out" w]
  $ns at 0.0 "printqueue $fp $queue"
}

#Define a 'finish' procedure
proc finish {} {
        global ns nf
	puts "NS -- Ending Simulation..."
        $ns flush-trace
        exit 0
}

#Create four nodes
set n0 [$ns node]
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]

#Create links between the nodes
$ns duplex-link $n0 $n2 1000Mb 1.1ms DropTail
$ns duplex-link $n1 $n2 1000Mb 1.05ms DropTail
$ns duplex-link $n2 $n3 10Mb 64.01ms DropTail

set qmon23 [$ns monitor-queue $n2 $n3 ""]
print-qstats queues_23 [set qmon23] ;

#Set Queue Size of link (n2-n3) to 10
$ns queue-limit $n2 $n3 50

#Setup a TCP connection
set tcp [new Agent/TCP]
$tcp set timestamps_ true
$tcp set parcial_ack_ true
$tcp set window_  $max_window
$tcp set maxcwnd_ $max_window
$tcp set packetSize_ [expr $psize - 40]
$tcp set tcpTick_ $tcp_tick

$ns attach-agent $n0 $tcp
set sink [new Agent/TCPSink]
$ns attach-agent $n3 $sink
$ns connect $tcp $sink
print-tcpstats [set tcp] [set sink] 0 tcp_cwnd_1 ;

#Setup a FTP over TCP connection
set ftp [new Application/FTP]
$ftp attach-agent $tcp
$ftp set type_ FTP
$ftp set maxpkts_ $bsize
$ftp set enableResume_ true

#Setup a second TCP connection
set tcp2 [new Agent/TCP]
$tcp2 set timestamps_ true
$tcp2 set parcial_ack_ true
$tcp2 set window_  $max_window
$tcp2 set maxcwnd_ $max_window
$tcp2 set packetSize_ [expr $psize - 40]
$tcp2 set tcpTick_ $tcp_tick

$ns attach-agent $n1 $tcp2
set sink2 [new Agent/TCPSink]
$ns attach-agent $n3 $sink2
$ns connect $tcp2 $sink2
print-tcpstats [set tcp2] [set sink2] 0 tcp_cwnd_2 ;

#Setup a FTP over TCP connection
set ftp2 [new Application/FTP]
$ftp2 attach-agent $tcp2
$ftp2 set type_ FTP
$ftp2 set maxpkts_ $bsize
$ftp2 set enableResume_ true

Application/FTP instproc resume {} {
    global ns
    puts "finished tcp"
    $ns at [expr [$ns now] + 0.5] "[$self agent] reset"
}

#Schedule events for the CBR and FTP agents
puts "Total number of packets [expr $bsize/$psize]"
$ns at 0.0 "$ftp start"
$ns at 0.0 "$ftp2 start"
$ns at 0.0 "$ftp produce [expr $bsize/$psize]"
$ns at 0.0 "$ftp2 produce [expr $bsize/$psize]"
#$ns at 0.0 "$ftp producemore [expr $bsize/$psize]"
#$ns at 0.0 "$ftp2 producemore [expr $bsize/$psize]"
#$ns at 100.0 "$ftp stop"
#$ns at 100.0 "$ftp2 stop"

$ns at 100.0 "finish"

#Run the simulation
$ns run
