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


# Reading configuration file.
if len(sys.argv)==1:
    sys.exit("usage: py3 {0}  <Config file>\n".format(__file__))

Config.read(sys.argv[1])

ref = Config.get("PATHS","reference")

def worker():
    bowtie2 = Config.get("PATHS", "bowtie2")
    java = Config.get("PATHS", "java")
    picard = Config.get("PATHS", "picard")
    minheap = Config.get("OPTIONS", "minheap")
    maxheap = Config.get("OPTIONS", "maxheap")
    callpicard = "{0} -Xms{1} -Xmx{2} -jar {3}".format(java, minheap, maxheap, picard)
    dic = Config.get("PATHS", "fadict")
    tmp = Config.get("DIRECTORIES", "temp_dir")
    ref = Config.get("PATHS", "reference")
    indices = Config.get("PATHS", "indices")
    samtools = Config.get("PATHS", "samtools")
    cmd = "{0}-build {1} {2}".format(bowtie2, ref, indices)
    print("Running command (bowtie2-build): ")
    print(cmd)
    subprocess.call(cmd, shell=True, executable="/bin/bash")
    cmd1 = "{0} CreateSequenceDictionary R={1} O={2} TMP_DIR={3}".format(callpicard, ref, dic, tmp)
    print("Running command (GATK2 dictionary): ")
    print(cmd1)
    subprocess.call(cmd1, shell=True, executable="/bin/bash")
    cmd2 = "{0} faidx {1}".format(samtools, ref)
    print("Running command (SAMTOOLS indexing): ")
    print(cmd2)
    subprocess.call(cmd2, shell=True, executable="/bin/bash")
    
if __name__=="__main__":
    worker()
    print("="*100)
    print("{0} has finished running.".format(__file__))
