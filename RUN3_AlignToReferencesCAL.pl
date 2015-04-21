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
        # my ($R1,$R2)=split(/\,/,$Config->get("DATA",$j)); Not used.
        my $prefix;
        my $mult = $Config->get("NUMBER_MULTIPLE",$j);
        if ($mult > 1) {
	    $prefix = $Config->get("COMBINE_ACCESSIONS",$j);
        } else {
            $prefix = $Config->get("SINGLE_ACCESSIONS",$j);
        }
        my $P1=$Config->get("DIRECTORIES","filtered_dir")."/".$prefix.".R1.fastq";
        my $P2=$Config->get("DIRECTORIES","filtered_dir")."/".$prefix.".R2.fastq";
        my $outputDir = $Config->get("DIRECTORIES","output_dir")."/".$prefix;
        my $base = $prefix;
        # Where I will output my Bowtie2 Alignments.
        my $bowRoot = $outputDir."/$base.Alignments";
        my $samtools = $Config->get("PATHS","samtools");
        # Where presumably the Bowtie2 reference to put in command.
        my $bowRef = $Config->get("PATHS","indices");
        
        mkdir $outputDir unless -e $outputDir;
        # The final Bowtie2 Alignment file.
        my $bowAln = $bowRoot.".bam";
#        print "Did we make it this far?\n";
        my $phred = "phred".$Config->get("OPTIONS","phred");
        my $cmd = $Config->get("PATHS","bowtie2")." -p $nThreads --very-sensitive --seed 0821986 --$phred -x $bowRef -1 $P1 -2 $P2 | $samtools view -bS - > $bowAln";
#        print "This be the command we gonna run, son! \n";
#        print "$cmd\n";
#        die "NO WE NOT!";
        warn $cmd."\n";
        `$cmd`;
        my $sorted = $bowRoot.".sorted";
        $cmd = $samtools." sort $bowAln $sorted";
        `$cmd`;
        $cmd = $samtools." index ".$sorted.".bam";
        `$cmd`;
        my $depthscript = $Config->get("PATHS","depthScript");
        my $depthout	= $outputDir."/ContigDepths.txt";
        $cmd = $samtools." depth ".$sorted.".bam | perl $depthscript > $outputDir/$base.ContigDepths.txt";
        `$cmd`;        
    }
}

# /home/ec2-user/Store1/bin/delly  -t TRA -o TRA.vcf -q 20 -g TwoChrom.fasta pGC1_Raw.sorted.bam

exit(0);


