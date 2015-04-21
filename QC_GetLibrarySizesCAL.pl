#!/usr/bin/perl
use warnings;
use strict;
use FindBin;
use lib "$FindBin::Bin/Lib";

use Tools;
use Configuration;

use threads;
use threads::shared;
use Thread::Queue;

my $q = Thread::Queue->new();
die "usage: perl $0 <Config file>\n\n" unless $#ARGV==0;
my $Config = Configuration->new($ARGV[0]);

my $nThreads = $Config->get("OPTIONS","Threads");

warn "Recognizing $nThreads as max threading...\n";

my $ref=$Config->get("PATHS","reference");
warn "Finding total number of files...\n";
my @LineNo = $Config->getAll("NUMBER_MULTIPLE");

foreach my $i (@LineNo){
      $q->enqueue($i);
}
for(my$i=0;$i<1;$i++){
      my $thr=threads->create(\&worker);
}
while(threads->list()>0){
      my @thr=threads->list();
      $thr[0]->join();
}

sub worker {
	my $TID=threads->tid() -1 ;
	while(my$j=$q->dequeue_nb()){
	  my $prefix;
	  my $mult = $Config->get("NUMBER_MULTIPLE",$j);
#	  print "This is the mult variable. $mult\n";
	  if ($mult > 1) {
	    $prefix = $Config->get("COMBINE_ACCESSIONS",$j);
#	    print "This is $prefix for multiple accessions. \n";
	  } else {
	     $prefix = $Config->get("SINGLE_ACCESSIONS",$j);
#	    print "This is $prefix for single accessikons. I shouldn't see this. \n";
	  }
          #	  print "Did we see $prefix? \n";
          my $P1 = $Config->get("DIRECTORIES","reads")."/".$prefix.".R1.fastq.gz";
          my $P2 = $Config->get("DIRECTORIES","reads")."/".$prefix.".R2.fastq.gz";
          my $cmd = "gunzip -c $P1 | wc -l";
          open(CMD,"-|",$cmd);
          my @output = <CMD>;
          close CMD;
          my $num;
          $num = $num + $output[0];
          $cmd = "gunzip -c $P2 | wc -l";
          open(CMD,"-|",$cmd);
          @output = <CMD>;
          $num = $num + $output[0];
          my $divisible;
          if ($num % 4 == 0) {
              $divisible = "File has right number of lines!";
          } else {
              $divisible = "Warning! Not divisible!";
          }
          $num = $num/4;
	  print $prefix."\t".$num."\n".$divisible."\n";
      }
    }

# /home/ec2-user/Store1/bin/delly  -t TRA -o TRA.vcf -q 20 -g TwoChrom.fasta pGC1_Raw.sorted.bam

exit(0);


