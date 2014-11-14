##### Declare Simulator and default configuration
set ns [new Simulator]
set psize   1500
set max_window     200
set tcp_tick       0.001
set TCP_ACK_Variant	"Agent/TCPSink/Sack1"
#set TCP_Variant 	"Agent/TCP/Linux"
#set TCP_Name	"cubic"
#set FlowNumber 	1
#set MainBW 	"10Mb"
#set SideBW	"1000Mb"
#set MainDelay 	"64ms"
#set SideDelay	"1ms"
#set MainBuffer 50
#set FTPEndTime 30
#set EndTime 40
set config $argv

##### Read configuration file
set conf [open $config r]
set FlowNumber	[gets $conf]
set MainBW 	[gets $conf]
set SideBW	[gets $conf]
set MainDelay 	[gets $conf]
set SideDelay	[gets $conf]
set DeltaDelay	[gets $conf]
set MainBuffer 	[gets $conf]
set FTPStartTime [gets $conf]
set DeltaTime	[gets $conf]
set FTPEndTime [gets $conf]
set EndTime [gets $conf]
set TCP_Variant [gets $conf]
set TCP_Name [gets $conf]

##### Output configuration
puts "$FlowNumber (flow_number)"
puts "$TCP_Variant (tcp_variant)"
puts "$TCP_Name (tcp_name)"
puts "$MainBW (main bw)"
puts "$SideBW (side bw)"
puts "$MainDelay (main delay)"
puts "$SideDelay (side delay)"
puts "$DeltaDelay (delta delay)"
puts "$MainBuffer (main buffer)"
puts "$FTPStartTime (ftp start)"
puts "$DeltaTime (delta time)"
puts "$FTPEndTime (ftp end)"
puts "$EndTime (simulation end)"

##### Setting output file
if {$TCP_Variant == "Agent/TCP/Linux"} {
	set name $TCP_Name
} else { 
	set name "reno"	
}
set file [open conflux-mininet/fluid-study/ns2/out-$name.tr w]
$ns trace-all $file
for {set i 0}  {$i < $FlowNumber}  {incr i 1} {
	set tcpfile($i) [open conflux-mininet/fluid-study/ns2/out-$name.tcp$i w]
}
Agent/TCP set trace_all_oneline_ true
##### Setting Main Node
set n1 [$ns node]
set n2 [$ns node]
##### Setting Link
set MainBW_ "[expr $MainBW]Mb"
set MainDelay_ "[expr $MainDelay]ms"
puts "Bottleneck link:$MainBW_ $MainDelay_"
$ns duplex-link $n1 $n2 $MainBW_ $MainDelay_ DropTail
##### Setting Queue Length
$ns queue-limit $n1 $n2 $MainBuffer
##### Setting TCP Connections
for {set i 0}  {$i < $FlowNumber}  {incr i 1}  {
	set src($i) [$ns node]
	set dst($i) [$ns node]
	set SideBW_ "[expr $SideBW]Mb"
#	set SideDelay_ "[expr $SideDelay]ms"
	set SideDelay_ "[expr $SideDelay + $i * $DeltaDelay]ms"	
	puts "Sidelink:$SideBW_ $SideDelay_"
	$ns duplex-link $src($i) $n1 $SideBW_ $SideDelay_ DropTail
	$ns duplex-link $n2 $dst($i) $SideBW_ $SideDelay_ DropTail
	set tcp($i) [new $TCP_Variant]
	$tcp($i) set timestamps_ true
	$tcp($i) set parcial_ack_ true
	$tcp($i) set window_  $max_window
	$tcp($i) set maxcwnd_ $max_window
	$tcp($i) set packetSize_ [expr $psize - 40]
	$tcp($i) set tcpTick_ $tcp_tick
	$tcp($i) set fid_ $i
	$ns attach-agent $src($i) $tcp($i)
	set sink($i) [new $TCP_ACK_Variant]
	$ns attach-agent $dst($i) $sink($i)
	$ns connect $tcp($i) $sink($i)
##### Setting tcp trace to output
	$tcp($i) attach-trace $tcpfile($i)
	$tcp($i) trace cwnd_
##### Setting FTP Application
	set ftp($i) [new Application/FTP]
	$ftp($i) attach-agent $tcp($i)
	$ftp($i) set type_ FTP
##### Setting different flavor
	if {$TCP_Variant == "Agent/TCP/Linux"} {
		$ns at 0 "$tcp($i) select_ca cubic"
	}
	set FTPStartTime_ [expr $FTPStartTime + $i * $DeltaTime]
	puts "ftp start at: $FTPStartTime_"
	$ns at $FTPStartTime_ "$ftp($i) start"
	puts "ftp stop at: $FTPEndTime"
	$ns at $FTPEndTime "$ftp($i) stop"
}
$ns at $EndTime "finish"

proc finish {} {
global ns file
$ns flush-trace
close $file
exit 0
}
##### Finish setting and start simulation
$ns run
