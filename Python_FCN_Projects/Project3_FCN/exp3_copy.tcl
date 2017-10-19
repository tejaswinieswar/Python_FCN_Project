set ns [new Simulator]
set tf [open exp3_out.tr w]
$ns trace-all $tf

set variant [lindex $argv 1]

proc finish {} {
	global ns tf
	$ns flush-trace	
	close $tf
	exit 0
}

set N1 [$ns node]
set N2 [$ns node]
set N3 [$ns node]
set N4 [$ns node]
set N5 [$ns node]
set N6 [$ns node]

$ns duplex-link $N1 $N2 10Mb 10ms [lindex $argv 1]
$ns duplex-link $N2 $N5 10Mb 10ms [lindex $argv 1]
$ns duplex-link $N2 $N3 10Mb 10ms [lindex $argv 1]
$ns duplex-link $N3 $N4 10Mb 10ms [lindex $argv 1]
$ns duplex-link $N3 $N6 10Mb 10ms [lindex $argv 1]

set tcp1 [new Agent/[lindex $argv 0]]
$ns attach-agent $N1 $tcp1

set tcp_sink [new Agent/TCPSink/Sack1]
$ns attach-agent $N4 $tcp_sink

$ns connect $tcp1 $tcp_sink
$tcp1 set fid_ 1
$tcp1 set packet_size_ 2000
$tcp1 set window_ 120
$tcp1 set maxcwnd_ 150

set cbr_src [new Agent/UDP]
$ns attach-agent $N5 $cbr_src

set cbr [new Application/Traffic/CBR]
$cbr attach-agent $cbr_src

set cbr_sink [new Agent/Null]
$ns attach-agent $N6 $cbr_sink

$ns connect $cbr_src $cbr_sink
$ns queue-limit $N2 $N3 10
$cbr_src set fid_ 2

$ns queue-limit $N1 $N2 10
$ns queue-limit $N2 $N5 10
$ns queue-limit $N3 $N4 10
$ns queue-limit $N3 $N6 10

$cbr set type_ CBR
$cbr set packet_size_ 500
$cbr set rate_ 9mb

set ftp [new Application/FTP]
$ftp attach-agent $tcp1
$ftp set type_ FTP

$ns at [lindex $argv 2] "$ftp start"
$ns at [lindex $argv 3] "$cbr start"
$ns at [lindex $argv 4] "$cbr stop"
$ns at [lindex $argv 5] "$ftp stop"

$ns at [lindex $argv 6] "finish"

$ns run
