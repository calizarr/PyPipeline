#!/usr/bin/env python
from __future__ import print_function
import sys
import subprocess

# Equivalent to Perl's FindBin...sorta
import os
bindir = os.path.abspath(os.path.dirname(__file__))

# Python Choose ConfigParser Based On Version
if sys.version_info[0] < 3:
    import ConfigParser
    Config = ConfigParser.ConfigParser()
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


def worker(i):
    mult = int(LineNo[i])
    if mult > 1:
        prefix = Config.get("COMBINE_ACCESSIONS", i)
    else:
        prefix = Config.get("SINGLE_ACCESSIONS", i)
    P1 = "{0}/{1}.R1.fastq".format(Config.get("DIRECTORIES", "filtered_dir"), prefix)
    P2 = "{0}/{1}.R2.fastq".format(Config.get("DIRECTORIES", "filtered_dir"), prefix)
    outputDir = "{0}/{1}".format(Config.get("DIRECTORIES", "output_dir"), prefix)
    base = prefix
    # Location of Bowtie2 Alignments
    bowRoot = "{0}/{1}.Alignments".format(outputDir, base)
    samtools = Config.get("PATHS", "samtools")
    # Where the Bowtie2 references/indices come from.
    bowRef = Config.get("PATHS", "indices")
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    # Moving orphan files to read specific folder.
    # orphan = "{0}/{1}.orphan.fastq".format(Config.get("DIRECTORIES", "output_dir"), base)
    # neworphan = os.path.join(outputDir, os.path.basename(orphan))
    # cmd = "mv {0} {1}".format(orphan, neworphan)
    # print("Running commands: \n{0}".format(cmd))
    # subprocess.call(cmd, shell=True)
    # Orphan has been moved to base specific results folder.
    # Final Bowtie2 Alignment file.
    bowAln = "{0}.bam".format(bowRoot)
    phred = "phred{0}".format(Config.get("OPTIONS", "phred"))
    seed = "0821986"
    # {0} Threads {1} Seed Num {2} phred {3} indices {4} Read 1 {5} Read 2 {6} samtools {7} filename
    opts = "-p {0} --very-sensitive --seed {1} --{2} -x {3} -1 {4} -2 {5} | {6} view -bS - > {7}" \
           .format(nThreads, seed, phred, bowRef, P1, P2, samtools, bowAln)
    # opts = "-p {0} --very-sensitive --{1} -x {2} -0 {3} -1 {4} | {5} view -bS - > {6}" \
    # .format(nThreads, phred, bowRef, P1, P2, samtools, bowAln)
    cmd = "{0} {1}".format(Config.get("PATHS", "bowtie2"), opts)
    print("Running command:\n{0}".format(cmd))
    fdir = "{0}/{1}.bowtie2.log".format(outputDir, base)
    f = open(fdir, "w")
    subprocess.call(cmd, shell=True, stdout=f, stderr=f)
    # Making log
    print("Making bowtie2 log")
    print("Saving to:\n{0}".format(fdir))
    f.close()
    # print("Zipping read files. No longer needed.")
    # cmd = "gzip {0} {1}".format(P1, P2)
    # subprocess.call(cmd, shell=True)

if __name__ == "__main__":
    # Attempting with pool of workers.
    pool = mp.Pool(processes=Config.getint("OPTIONS", "processes"))

    results = [pool.apply_async(func=worker, args=(i, )) for i in LineNo]
    for result in results:
        z = result.get()

    print("="*100)
    print("{0} has finished running.".format(__file__))
