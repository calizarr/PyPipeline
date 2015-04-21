#!/usr/bin/perl

use warnings;
use strict;
use lib '/home/clizarraga/scripts/Pipeline/Lib';

my $usage = "perl $0 <fastq file 1> <fastq file 2> <output root> <capture string(s)> <line S1 or Q1> <maximum amount of captured strings>\n";
# print "Current Commands: ".scalar(@ARGV)."\n";
die $usage unless $#ARGV>=2;

# print "Here are my arguments: @ARGV \n";
my $FQ1=$ARGV[0];
my $FQ2=$ARGV[1];
my $OR =$ARGV[2];
my $amt = $ARGV[5];
my $capture = $ARGV[3];
my @capt = split(/\,/,$capture);
my $line = "\$".$ARGV[4];
my ($base,$outOne,$outTwo,$outOrphan);
chomp $capture;
# print "This is what we wanna capture: $capture \n";
chomp $amt;
if ($FQ1 =~ /\/(\w+([-\d+])?([\d+\w+])?).R\d/) {
    $base = $1;
} else {
    die "Filename not captured.";
}
$outOne=$OR."$base.R1.QC.I15.fastq";
$outTwo=$OR."$base.R2.QC.I15.fastq";
$outOrphan=$OR."$base.lost.fastq";
open(FQ1,"<",$FQ1) || die "cannot open $FQ1!\n$!\nexiting...\n";
open(FQ2,"<",$FQ2) || die "cannot open $FQ2!\n$!\nexiting...\n";
open(O1,">",$outOne) || die "cannot open $outOne!\n$!\nexiting...\n";
open(O2,">",$outTwo) || die "cannot open $outTwo!\n$!\nexiting...\n";
open(OO,">",$outOrphan) || die "cannot open $outOrphan!\n$!\nexiting...\n";

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
        my $count = eval "$line =~ tr/$capture//";
        # print "Here's the quality: \n $Q1 \n";
        # print "Here's the count: \n $count \n";
        if ($count < $amt) {
            print O1 $H1s."\n".$S1."\n".$H1q."\n".$Q1."\n";
        } else {
            print OO $H1s."\n".$S1."\n".$H1q."\n".$Q1."\n";
        }
            # die "Should be one by now?\n";
    }
    unless(eof(FQ2)){
        my $H1s=<FQ2>;
        my $S1 =<FQ2>;
        my $H1q=<FQ2>;
        my $Q1 =<FQ2>;
        chomp $H1s;
        chomp $S1;
        chomp $H1q;
        chomp $Q1;
        my $count = eval "$line =~ tr/$capture//";
        # print "Here's the quality: \n $Q1 \n";
        # print "Here's the count: \n $count \n";
        if ($count < $amt) {
            print O2 $H1s."\n".$S1."\n".$H1q."\n".$Q1."\n";
        } else {
            print OO $H1s."\n".$S1."\n".$H1q."\n".$Q1."\n";
        }
        # die "Should be one by now?\n";
    }

last if ((eof(FQ1))&&(eof(FQ2)));
$i++;
}
close O1;
close O2;
close OO;
close FQ1;
close FQ2;
print "We closed all the files! They should exist!. \n";


