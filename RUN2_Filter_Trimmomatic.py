#!/usr/bin/env python
from __future__ import print_function
import sys
import subprocess
import itertools
import glob
import pdb

# Equivalent to Perl's FindBin...sorta
import os
bindir = os.path.abspath(os.path.dirname(__file__))

# Python Choose ConfigParser Based On Version
if sys.version_info[0] < 3:
    import ConfigParser
    Config = ConfigParser.ConfigParser()
    itertools.zip_longest = itertools.izip_longest
else:
    import configparser
    Config = configparser.ConfigParser()

# Multi processing begins.
import multiprocessing as mp
output = mp.Queue()

# Reading configuration file.
if len(sys.argv) == 1:
    sys.exit("usage: py3 {0}  <Config file>\n".format(__file__))

Config.read(sys.argv[1])
nThreads = Config.get("OPTIONS", "Threads")

print("Recognizing {0} as max threading...".format(nThreads))

ref = Config.get("PATHS", "reference")
LineNo = dict(Config.items('NUMBER_MULTIPLE'))
print(LineNo)
print("Finding total number of files: {0}".format(len(LineNo)))


# Garbage Collector as of yet unused.
def collectTheGarbage(files):
    for filename in files:
        command = "rm -rf {0}".format(filename)
        print("Running command:\n{0}\n".format(command))
        subprocess.call(command, shell=True)
    return 1

def worker(i):
    # Getting paths for everything.
    DataDir = Config.get("DIRECTORIES", "reads")
    # OutDir = Config.get("DIRECTORIES", "output_dir")
    FiltDir = Config.get("DIRECTORIES", "filtered_dir")
    mult = int(LineNo[i])
    # Getting Trimmomatic Configs.
    trim = Config.get("PATHS", "trimmomatic")
    java = Config.get("PATHS", "java")
    maxheap = Config.get("OPTIONS", "maxheap")
    minheap = Config.get("OPTIONS", "minheap")
    phred = Config.get("OPTIONS", "phred")
    
    if mult > 1:
        base = Config.get("COMBINE_ACCESSIONS", i)
    else:
        base = Config.get("SINGLE_ACCESSIONS", i)
    # Lists to hold paths and garbage to be collected.
    CurrentSourcePaths = []
    GarbageCollector = []
    directory = DataDir
    print("Working with {0}".format(directory))
    # Attempting to get the read files.
    try:
        DIR = os.listdir(directory)
    except OSError as e:
        print("OSError [%d]: %s at %s" % (e.errno, e.strerror, e.filename))
    CurrentFiles = []
    for filename in DIR:
        if base in filename:
            CurrentFiles.append(directory+"/"+filename)
    CurrentFiles.sort()
    # Read files should've been acquired.
    print("These are the files we have acquired:\n{0}".format(CurrentFiles))
    CurrentSourcePaths = CurrentFiles[:]

    # May be obsolete soon, taking advantage of the fact that Trimmomatic can use .gz files and output .gz files
    if Config.getint("PIPELINE", "Compressed"):
        print("Treating files as compressed.")
        thisSet = CurrentSourcePaths[:]
        CurrentSourcePaths = []
        for filename in thisSet:
            if filename.endswith("gz"):
                nPath = filename
                nPath = nPath[:-3]
                command = "gunzip "+filename
                subprocess.call(command, shell=True)
                CurrentSourcePaths.append(nPath)
            else:
                CurrentSourcePaths.append(filename)

    # Proper filtering starts here.
    if Config.getint("PIPELINE", "FivePrimeFilter") \
       and Config.getint("PIPELINE", "ThreePrimeFilter") \
       and Config.getint("PIPELINE", "PairedEnd"):
        # Getting paths to current files and directories.
        
        # Used in constructing new paths.
        basedir = os.path.dirname(CurrentSourcePaths[0])
        # Path to log Trimmomatic specific log file.
        log = os.path.join(basedir, "{0}.trimlog".format(base))
        # Read 1 of pair
        read1 = CurrentSourcePaths[0]
        # Read 2 of pair
        read2 = CurrentSourcePaths[1]
        # Path & Filename for Filtered Read 1
        out1 = os.path.join(basedir, "{0}.R1.3pTrim.5pTrim.Paired.fastq.gz"
                            .format(base))
        # Path & Filename for Filtered Read 2
        out2 = os.path.join(basedir, "{0}.R2.3pTrim.5pTrim.Paired.fastq.gz"
                            .format(base))
        # Path & Filename for orphaned reads from R1.
        orphan1 = os.path.join(basedir, "{0}.R1.orphan".format(base))
        # Path & Filename for orphaned reads from R2.
        orphan2 = os.path.join(basedir, "{0}.R2.orphan".format(base))
        # Length to crop from beginning of read. Used in old Illumina sequencing because of known errors.
        length = Config.get("OPTIONS", "LengthOf5pTrim")
        # Minimum quality of nucleotide before it gets cut.
        minqual = Config.get("OPTIONS", "Min3pQuality")
        # Getting sequence average sequence length from fastqc reports then determining minimum sequence length for pairs.
        fastqc_dir = os.path.join(DataDir, "fastqc")
        globsearch = os.path.join(fastqc_dir, "{base}.R*_fastqc.zip".format(base=base))
        fqcfiles = glob.glob(globsearch)
        if len(fqcfiles) == 2:
            r1cmd = "unzip -p {fastqc}/{base}.R1_fastqc.zip {base}.R1_fastqc/fastqc_data.txt | grep length | cut -f2".format(base=base, fastqc=fastqc_dir)
            r2cmd = "unzip -p {fastqc}/{base}.R2_fastqc.zip {base}.R2_fastqc/fastqc_data.txt | grep length | cut -f2".format(base=base, fastqc=fastqc_dir)
            r1length = [(int(x)-int(length))/2 for x in subprocess.check_output(r1cmd, shell=True).strip().split('-')]
            r2length = [(int(x)-int(length))/2 for x in subprocess.check_output(r2cmd, shell=True).strip().split('-')]
            if min(r1length) < 25:
                r1length = max(r1length)
            else:
                r1length = min(r1length)
            if min(r2length) < 25:
                r2length = max(r2length)
            else:
                r2length = min(r2length)
            lengths = [r1length, r2length]
            minlength = sum(lengths) / len(lengths)
        else:
            minlength = Config.get("OPTIONS", "Min3pLength")
        # Setting up and calling Trimmomatic on the command line.
        calltrimmomatic = "{0} -Xms{1} -Xmx{2} -XX:+UseG1GC -XX:+UseStringDeduplication -jar {3}" \
                          .format(java, minheap, maxheap, trim)
        cmd = "{0} PE -threads {1} -phred{2} -trimlog {3} {4} {5} {6} {7} {8} {9} HEADCROP:{10} TRAILING:{11} MINLEN:{12}" \
              .format(calltrimmomatic, nThreads, phred, log, read1, read2,
                      out1, orphan1, out2, orphan2, length, minqual, minlength)
        print("Running commmand:\n{0}".format(cmd))
        subprocess.call(cmd, shell=True)
        GarbageCollector.append(read1)
        GarbageCollector.append(read2)

        # Moving files to appropriate folders.
        # Path & Filename for final R1 file.
        FR1 = os.path.join(FiltDir, "{0}.R1.fastq.gz".format(base))
        # Path & Filename for final R2 file.
        FR2 = os.path.join(FiltDir, "{0}.R2.fastq.gz".format(base))
        # Path for Orphan directory.
        ORO = os.path.join(FiltDir, "Orphans")
        # Path for log directory.
        LOGS = os.path.join(FiltDir, "Logs")
        # Moving R1/R2 files
        cmd = "mv {0} {1}".format(out1, FR1)
        print("Running commmand:\n{0}".format(cmd))
        subprocess.call(cmd, shell=True)
        cmd = "mv {0} {1}".format(out2, FR2)
        print("Running commmand:\n{0}".format(cmd))
        subprocess.call(cmd, shell=True)
        # Checking if Orphan directory exists, if not create and move.
        if not os.path.exists(ORO):
            os.makedirs(ORO)
        cmd = "mv {0} {1}".format(orphan1, ORO)
        print("Running commmand:\n{0}".format(cmd))
        subprocess.call(cmd, shell=True)
        cmd = "mv {0} {1}".format(orphan2, ORO)
        print("Running commmand:\n{0}".format(cmd))
        subprocess.call(cmd, shell=True)
        # Checking if Logs directory exists, if not create and move.
        if not os.path.exists(LOGS):
            os.makedirs(LOGS)
        cmd = "mv {0} {1}".format(log, LOGS)
        print("Running commmand:\n{0}".format(cmd))
        subprocess.call(cmd, shell=True)
        # Removing intermediary files
        # collectTheGarbage(GarbageCollector)

# Necessary to group processes by memory.
def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return itertools.zip_longest(fillvalue=fillvalue, *args)

if __name__ == "__main__":
    # Attempting with pool of workers.
    # Getting total memory of machine
    meminfo = dict((i.split()[0].rstrip(':'), int(i.split()[1]))
                   for i in open('/proc/meminfo').readlines())
    mem_total_kib = meminfo['MemTotal']
    mem_total_gib = mem_total_kib*1.0e-6
    # Getting number of total processes that can be run at once given memory constraints.
    memper = int(Config.get("OPTIONS", "maxheap")[:-1])
    at_once = int(mem_total_gib//memper)
    print("This is the total number allowed at once: {0}".format(at_once))
    total = grouper(LineNo.keys(), at_once)
    totalcpu = mp.cpu_count() / int(nThreads)
    print("Total processes at a time: {0}".format(totalcpu))
    # pool = mp.Pool(processes=Config.getint("OPTIONS", "processes"))
    print("Choosing the lesser of the two: {0}".format(min([at_once, totalcpu])))
    pool = mp.Pool(processes=min([at_once, totalcpu]))
    for group in total:
        results = [pool.apply_async(func=worker, args=(i, )) for i in group]
        for result in results:
            result.wait()
        print("="*100)
        print("{0} has finished running.".format(str(group)))

    print("="*200)
    print("{0} has finished running.".format(__file__))

    # # Trimmomatic runs multi-thread on ALL threads so run each accession at a time.
    # for i in LineNo.keys():
    #     worker(i)
    #     print("="*100)
    #     print("{0} has finished running.".format(str(i)))
    # print("="*200)
    # print("{0} has finished running.".format(__file__))
