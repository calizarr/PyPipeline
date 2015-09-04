# SNP Calling Pipeline Information: #

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

Use the sample configurations as a guideline for your own (if tweaking.) Several viewings of the script files may be necessary.
You will need to replace the paths to where the files will be stored.

## Requirements: ##

-------------------------------------------------------------------------------
- Python 3.4 or greater (preferably: Python 3.4)
    - A local compile or virtual environment of Python 3.4 would be ideal.
    - [Download Python 3.4](https://www.python.org/download/releases/3.4.0/)
- Python 2.6/2.7 should be compatible at this point.
- Perl 5.10 and dependencies for Variant Effect Predictor scripts.
    - Can be installed using local::lib and cpanm:
        - [How to install local::lib and cpanm bootstrapping (no root/sudo access)](http://stackoverflow.com/questions/2980297/how-can-i-use-cpan-as-a-non-root-user)
    - Then simply do cpanm [ModuleNameHere] and install the required dependencies.
    - [Download Perl](http://www.perl.org/)
- Java 7 (or greater):
    - [Download Java](https://java.com/en/download/)
- Variant Effect Predictor:
    - [Download VEP](http://useast.ensembl.org/info/docs/tools/vep/script/vep_download.html?redirect=no)
    - Only works with VEP v78. 79+ do not work with the infrastructure and freeze.
- Genome Analysis Toolkit 2:
    - [Download GATK2](https://www.broadinstitute.org/gatk/download/)
- PicardTools:
    - [Download PicardTools](http://broadinstitute.github.io/picard/)
    - All other tools currently exist on infrastructure:
        - Bowtie2, fastx toolkit (fastq_quality_trimmer), and samtools.

## Usage: ##

-------------------------------------------------------------------------------

- python RUNX_ABC.py ConfigurationFile.txt
- Configuration Files are included. They contain paths to the directories where files, programs, etc. are located and the directories where you will be outputting results.
  - Please change paths, directories, etc. for local machine use as well as software and applications.
  - To turn off options, make the value a zero (0). To turn on options, make the value a one (1).
- They also contain options etc. for the general pipeline run.

## Configuration File: ##
   
-------------------------------------------------------------------------------

  * Processes/Threads are the essentially the same. Python uses multiprocessing.
  * VEP makeCDB doesn't work for now. 78 only takes gtf.
  * Java maxheap and minheap parameters are supremely important. They determine how many accessions can run at once.
    * About a 1/3 of RAM is fine for maxheap and a little more than 1/2 of maxheap for minheap.

## QC and Pre Steps: ##

-------------------------------------------------------------------------------

##### 1. Always check FastQC either after Combine/Deinterleave or after 5' Trimming, but always before 3' Trimming. #####

  - Always check FastQC after and before any major changes that will be made to the fastq files.
   
##### 2. Check the library sizes with QC_GetLibrarySizes. It should return a number that is divisible by 4. #####

##### 3. If necessary use either of the two Pre steps: #####

  - Combine is to concatenate together accession files which have been separated.
  - Deinterleave is to separate a FastQ file into two separate Read 1 and Read 2 files while maintaining order.
    * Deinterleave now uses findFastq.pl in Tools, it is a perl script used to separate the Reads via capture strings.
    * Usage is specified if you just run perl findFastq.pl

##### 4. Illumina 1.5 Reads: #####

  - Check if your reads are between Illumina 1.3+ and Illumina 1.8. If so, check for "B" quality scores.
    * If they exist, run QC_Illumina1.5.py and it will trim the reads from the first B onwards.
     
## RUN STEPS: ##

-------------------------------------------------------------------------------

##### 1. RUN1_PrepareReferences will index your genome file. #####

- Uses bowtie2-build with default parameters.
   
##### 2. RUN2_Filter will take your FastQ files, 3p and 5p trim them and then separate the pairs and orphans. #####

  - 5pTrim uses a custom Perl script to remove the first 15 nucleotides.
    * Option to turn off 5pTrim option if undesired.
  - 3pTrim uses the fastq_quality_trimmer in the fastx_toolkit.
  - RUN2_Filter_Trimmomatic.py does the same thing, but is much faster and multithreaded.
 
##### 3. RUN3_AlignToReferences will take your filtered FastQ read pairs and align them to the Bowtie2 indices/reference genome. #####

  - Using the output from RUN1 of the indexed reference from Bowtie2, use Bowtie2 to align the references.
  - Final step with Reads, from here on out only the BAM file. Reads will be gzipped automatically.
  - Bowtie2 in here is set to very sensitive so it takes longer but is more accurate.
   
##### 4. RUN4_PrepBAM takes the alignment BAM, sorts it, replaces duplicates, and adds/replaces read groups. #####

  - The Read Groups are currently dummy read groups and can be changed if one has information about flowcell, sequencer, and lane for your reads. GATK2's documentation on read groups is good for this.
   
##### 5. RUN5_GATK2 runs the prepped bam file through the Genome Analysis Toolkit: #####

  - Targetting intervals where it might be best to realign indels.
  - Realigning those intervals.
  - Calling SNPS with HaplotypeCaller.
    * Currently it is set to discover snps and emit all sites whether they are high or low quality. These settings can be changed in the configuration file.
     
##### 6. RUN6_VEP will take the vcf and call possible effects of SNPs on those sites. #####

  - The functions to make the cache database and convert to gtf are preliminary and only work for certain files. It is not recommended to use them. The configuration file has their options set to 0 for that reason.
  - If using a species that does not exist in the database, you will have to create your own cache database from a gtf file. The creation of the database is a straight VEP perl script, however, converting from gff to gtf is not so straightforward.

-------------------------------------------------------------------------------

Notes:
  - If the Pipeline is run with several accessions there can only be one overall minimum quality score and length. If your reads differ significantly, make two configuration files (or more) for the reads that can't be filtered the same way.
  - Filtering for SNPs or Indels and quality filtering can be done between the RUN5 and RUN6 versions. GATK2 has functions for filtering, bcftools does as well, and finally you can also make your own with linux command line tools (sed, awk, grep piped work well.)

Optional:
  * There are two optional phred quality score guessing scripts in the Scripts folder. One is in Python and the other one is in Perl. If you already know the quality score for your FastQ files then ignore them, but if you can't make an educated guess see if these two scripts may help you. This is important. The best way to find out Phred score quality is to manually, visually inspect the fastq files yourself.
