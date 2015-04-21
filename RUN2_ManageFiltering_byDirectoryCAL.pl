#!/usr/bin/perl
use warnings;
use strict;
use threads;
use Thread::Queue;
use FindBin;
use lib "$FindBin::Bin/Lib";
use Configuration;
use Tools;

my $configFile=$ARGV[0];

die "usage : perl $0 <config file governing all filtering>\n\n" unless $#ARGV==0;

my $q = Thread::Queue->new();
my $config = Configuration->new($configFile);
my $threads = $config->get("OPTIONS","Threads");
my @Groups = $config->getAll("DATA");

for(my $i=0;$i<=$#Groups;$i++){
	warn "enqueuing $i ($Groups[$i])\n";
	$q->enqueue($Groups[$i]);
}

for(my$i=0;$i<=$threads;$i++){
	my $thr=threads->create(\&workerThread);
}
while(threads->list()>0){
	my @thr=threads->list();
	$thr[0]->join();
}


sub workerThread{
	while(my $work=$q->dequeue_nb()){
            my $grp=$work;
#            die "Just stop here, alright? \n";
            my $DataDir = $config->get("DIRECTORIES","reads");
            my $OutDir  = $config->get("DIRECTORIES","output_dir");
            my $FiltDir = $config->get("DIRECTORIES","filtered_dir");
            #	my $workThreads = $config->get("OPTIONS","workThreads");
            my $base;
            my $mult = $config->get("NUMBER_MULTIPLE",$grp);
            if ($mult > 1) {
                $base = $config->get("COMBINE_ACCESSIONS",$grp);
            } else {
                $base = $config->get("SINGLE_ACCESSIONS",$grp);
            }
#            my $base = $config->get("CELL_LINE",$grp);
            my @CurrentSourcePaths;
            my @GarbageCollector;
            my $dir=$DataDir;
            warn "Working with $dir...\n";
            #my @CurrentFiles = split(/\,/,$config->get("DATA",$grp));
            opendir(DIR,$dir) || die "cannot open directory : $dir \n";
            #            my @CurrentFiles = grep {m/$base\.R\d\.test/} readdir DIR;
            my @CurrentFiles = grep {m/$base/} readdir DIR;
            closedir DIR;
            print "These are the files we have acquired: \n";
            print "@CurrentFiles \n";
            map {push @CurrentSourcePaths, $dir."/".$_} @CurrentFiles;
            warn "working with $grp\n";
            if($config->get("PIPELINE","Compressed")){
                warn "Treating files as compressed.\n";
                my @thisSet = @CurrentSourcePaths;
                @CurrentSourcePaths=();
                foreach my $file (@thisSet){
                    if($file=~m/gz$/){
                        my $nPath=$file;
                        $nPath=~s/\.gz//;
                        my $command = "gunzip ".$file;
                        warn $command."\n";
                        `$command`;
                        push @CurrentSourcePaths, $nPath;
                    }else{
                        push @CurrentSourcePaths, $file;
                    }
                    #				push @GarbageCollector, $nPath;
                }	
            }
            if($config->get("PIPELINE","FivePrimeFilter")){
                warn "Trimming 5' end of sequences...\n";
                my @thisSet = @CurrentSourcePaths;
                print "The current files to be used: @thisSet \n";
                @CurrentSourcePaths=();
                my $script=$config->get("PATHS","FivePrimeTrimmer");
                my $length=$config->get("OPTIONS","LengthOf5pTrim");
                foreach my $file (@thisSet){
                    my $oPath=$file;
                    $oPath=~s/fastq/5pTrim\.fastq/;
                    $oPath=~s/fq/5pTrim\.fastq/;
                    print "The output path: $oPath\n";
                    my $command="perl $script $file $oPath $length";
                    warn $command."\n";
                    `$command`;
                    push @CurrentSourcePaths, $oPath;
                    push @GarbageCollector, $oPath if $config->get("PIPELINE","Compressed");
                }
            }
            if($config->get("PIPELINE","ThreePrimeFilter")){
                # Always check your phred score first. 33 or 64?
                warn "Trimming 3' end on quality...\n";
                my @thisSet = @CurrentSourcePaths;
                print "The current files to be used: @thisSet \n";
                @CurrentSourcePaths=();
                my $script = $config->get("PATHS","fastq_quality_trimmer");
                my $MinL   = $config->get("OPTIONS","Min3pLength");
                my $MinQ   = $config->get("OPTIONS","Min3pQuality");
                my $phred  = $config->get("OPTIONS","phred");
                my $opts   = "-t $MinQ -Q $phred -l $MinL";
                foreach my $file (@thisSet){
                    my $oPath=$file;
                    $oPath=~s/fastq/3pTrim\.fastq/;
                    $oPath=~s/fq/3pTrim\.fastq/;
                    print "The output path: $oPath\n";
                    my $command="$script $opts -i $file -o $oPath";
                    warn $command."\n";
                    `$command`;
                    push @CurrentSourcePaths, $oPath;
                    push @GarbageCollector, $oPath;
                }
            }
#            die "Let's just stop here for now, shall we?\n";
            if($config->get("PIPELINE","Paired")){
                warn "Parsing for Pairs...\n";
                my @thisSet = @CurrentSourcePaths;
                print "What files are we working with?\n@thisSet\n";
                @CurrentSourcePaths=();
                my $script = $config->get("PATHS","PairsAndOrphans");
                my @R1=grep {m/R1/} @thisSet;
                my @R2=grep {m/R2/} @thisSet;
                print "These are the R1s and R2s: \n@R1\n@R2\n";
                my $T1=$DataDir."/$grp.TempRead1.fastq";
                my $T2=$DataDir."/$grp.TempRead2.fastq";
                my $command="cat ".join(" ",@R1)." > $T1";
                warn $command."\n";
                `$command`;
                $command   ="cat ".join(" ",@R2)." > $T2";
                warn $command."\n";
                `$command`;
                push @GarbageCollector, $T1;
                push @GarbageCollector, $T2;
                my $O=$DataDir."/$grp";
                my $OR1=$DataDir."/$grp".".R1.fastq";
                my $OR2=$DataDir."/$grp".".R2.fastq";
                my $ORO=$DataDir."/$grp".".orphan.fastq";
                my $FR1=$FiltDir."/$base".".R1.fastq";
                my $FR2=$FiltDir."/$base".".R2.fastq";
                $command="perl $script $T1 $T2 $O";
                warn $command."\n";
                `$command`;
                $command = "mv $OR1 $FR1";
                `$command`;
                $command = "mv $OR2 $FR2";
                `$command`;
                push @GarbageCollector, $OR1;
                push @GarbageCollector, $OR2;
                push @GarbageCollector, $ORO;
                push @CurrentSourcePaths, $OR1;
                push @CurrentSourcePaths, $OR2;
                push @CurrentSourcePaths, $ORO;
            }
#            prepFinal($OutDir,@CurrentSourcePaths);
#            collectTheGarbage(@GarbageCollector);
	}
    }

sub collectTheGarbage {
    my @files = @_;
    foreach my $file (@files){
        my $command="rm -rf $file";
        warn $command."\n";
        `$command`;
    }
	return 1;
}

sub prepFinal {
    my $finalDir = shift @_;
    my @files = @_;
    foreach my $file (@files){
        my $sPath=$file;
        my $oPath=$file;
        $oPath=~s/.+\///g;
        $oPath=$finalDir."/".$oPath;
        my $command = "mv $sPath $oPath";
        warn $command."\n";
        `$command`;
    }
    return 1;
}
