set ns [new Simulator]
set type [lindex $argv 0]
set rate [lindex $argv 1]
#puts $type
set tf [open exp1_out_${type}_${rate}.tr w]


$ns trace-all $tf

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

$ns duplex-link $N1 $N2 10Mb 10ms DropTail
$ns duplex-link $N2 $N5 10Mb 10ms DropTail
$ns duplex-link $N2 $N3 10Mb 10ms DropTail
$ns duplex-link $N3 $N4 10Mb 10ms DropTail
$ns duplex-link $N3 $N6 10Mb 10ms DropTail

if {$type == "TCP"} {
	set tcp1 [new Agent/$type]
	} elseif {$type != "TCP"} {
	set tcp1 [new Agent/TCP/$type]
	}
$ns attach-agent $N1 $tcp1

set tcp_sink [new Agent/TCPSink]
$ns attach-agent $N4 $tcp_sink

$ns connect $tcp1 $tcp_sink
$tcp1 set fid_ 1
$tcp1 set packet_size_ 2000

set cbr_src [new Agent/UDP]
$ns attach-agent $N2 $cbr_src

set cbr [new Application/Traffic/CBR]
$cbr attach-agent $cbr_src

set cbr_sink [new Agent/Null]
$ns attach-agent $N3 $cbr_sink

$ns connect $cbr_src $cbr_sink
$ns queue-limit $N2 $N3 10
$cbr_src set fid_ 2

$cbr set type_ CBR
$cbr set packet_size_ 500
$cbr set rate_ [lindex $argv 1]Mb

set ftp [new Application/FTP]
$ftp attach-agent $tcp1
$ftp set type_ FTP

$ns at 0.0 "$cbr start"
$ns at 1.0 "$ftp start"
$ns at 10.0 "$ftp stop"
$ns at 10.0 "$cbr stop"

$ns at 10.0 "finish"

$ns run
