#!/usr/bin/perl
use warnings;
use strict;
# use lib '/home/clizarraga/scripts/Pipeline/Lib';

my $usage = "perl $0 <fastq file 1> <output root> <sub name 1> <sub name 2> <capture string(s)> <line H1s,S1,H1q,Q1>\n";
# print "Current Commands: ".scalar(@ARGV)."\n";
die $usage unless $#ARGV>=2;

# print "Here are my arguments: @ARGV \n";
my $FQ1=$ARGV[0];
my $OR =$ARGV[1];
my $SB1 = $ARGV[2];
my $SB2 = $ARGV[3];
my $capture = $ARGV[4];
my @capt = split(/\,/,$capture);
my $line = "\$".$ARGV[5];
my ($base,$outOne,$outElse);
chomp $capture;
print STDERR "Here's the line: $line and here's the capture: $capture\n";
# Extracting file name.
# my $lastInd = rindex($FQ1,"/");
# $FQ1 = substr($FQ1,$lastInd);
if ($FQ1 =~ /(\w+[-\d+]?[-\d+]?\w+?)\./) {
    $base = $1;
    print STDERR "This is the captured name: $base\n";
} else {
    die "Filename not captured.";
}
# if ($FQ1 =~ /\/(\w+([-\d+])?([\d+\w+])?([\w+])?(.R\d)?)/) {
#     $base = $1;
#     print STDERR "This is the captured name: $base\n";
# } else {
#     die "Filename not captured.";
# }                     ;
$outOne=$OR."$base.$SB1.fastq";
$outElse=$OR."$base.$SB2.fastq";
open(FQ1,"<",$FQ1) || die "cannot open $FQ1!\n$!\nexiting...\n";
open(O1,">",$outOne) || die "cannot open $outOne!\n$!\nexiting...\n";
open(O2,">",$outElse) || die "canot open $outElse!\n$!\nexiting... \n";

my $i=0;
while(1){
    unless(eof(FQ1)){
        my $H1s=<FQ1>;
        my $S1 =<FQ1>;
        my $H1q=<FQ1>;
        my $Q1 =<FQ1>;
        chomp $H1s;
        chomp $S1;
        chomp $H1q;
        chomp $Q1;
        if (substr($H1s,0,2) eq "--") {
	  next;
	  }
        my $line = eval "$line";
        # my $count = eval "$line =~ tr/$capture//";
        foreach my $capt (@capt) {
	  my $exist = index($line, $capt);
	  if ($exist > -1) {
	    if ($capt eq "B") {
	        $S1 = substr($S1,0,$exist);
		$Q1 = substr($Q1,0,$exist);
		print O2 $H1s."\n".$S1."\n".$H1q."\n".$Q1."\n";
	      } else {
		print O1 $H1s."\n".$S1."\n".$H1q."\n".$Q1."\n";
	      }
	  } else {
	    print O2 $H1s."\n".$S1."\n".$H1q."\n".$Q1."\n";
	  }
        }
      }
    last if (eof(FQ1));
    $i++;
  }
close O1;
close O2;
close FQ1;
print "We closed all the files! They should exist!. \n";


