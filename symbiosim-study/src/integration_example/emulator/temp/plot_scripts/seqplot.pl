#!/usr/bin/perl

$filename = "chicago.log";
$seqfile = "seqno";
$ackfile = "ackno";
$dir_src = "10.10.0.17.2778";  # the server
$dir_dst = "10.10.0.34.5001";   # the client

die "Can't open $filename\n" unless open(TCPDUMP, "sudo tcpdump -tt -S -n -r $filename |");
die "Can't open $seqfile\n" unless open(SEQFILE, ">$seqfile");
die "Can't open $ackfile\n" unless open(ACKFILE, ">$ackfile");

$startime = -1.0;
$last_ack = 0;
while(<TCPDUMP>) {
  chomp($_);
  if(/([0-9.]+) IP ([^ ]+) > ([^:]+): ([A-Z.]) (.*)/) {
    $tm = $1; $src = $2; $dst = $3;
    if($startime < 0) { $startime = $tm; }
    $flags = $4; $rest = $5;
    $tm -= $startime;
    print "$tm $src > $dst $flags $rest\n";
    if($dir_src eq $src &&
       $rest =~ /(\d+):\d+\(\d+\)/) {
      $seqno = $1;
      #print SEQFILE "$tm $seqno\n";
      print $seqfile "$tm $seqno\n";
    }
    if($dir_src eq $dst &&
       $rest =~ /ack (\d+)/) {
      $ackno = $1;
      print ACKFILE "$tm $ackno\n";
    }
  }
}

close(TCPDUMP);
close(SEQFILE);
close(ACKFILE);
