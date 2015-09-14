#!/home/clizarraga/usr/python/bin/bin/python3.4
from __future__ import print_function
import sys
import subprocess
import pdb
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
    path = Config.get("DIRECTORIES", "combined") + "/" + prefix + ".fastq.gz"
    OR = Config.get("DIRECTORIES", "reads")+"/"
    if os.path.exists("{0}{1}.R1.fastq".format(OR, prefix)) \
       and os.path.exists("{0}{1}.R2.fastq".format(OR, prefix)):
        print("Reads have already been deinterleaved: {0}".format(path))
    else:
        print("Unzipping file: "+path)
        cmd = "gunzip "+path
        print("Running command: \n{0}".format(cmd))
        subprocess.call(cmd, shell=True)
        script = Config.get("PATHS", "fqscript")
        P1 = Config.get("DIRECTORIES", "combined")+"/"+prefix+".fastq"
        capt = "/1"
        cmd1 = "perl "+script+" "+P1+" "+OR+" R1 R2 "+capt+" H1s"
        print("Running command: \n{0}".format(cmd1))
        subprocess.call(cmd1, shell=True)
        cmd2 = "gzip {0}".format(P1)
        print("Zipping combined file: \n{0}".format(cmd2))
        subprocess.call(cmd2, shell=True)

if __name__ == "__main__":
    # Attempting with pool of workers.
    pool = mp.Pool(processes=Config.getint("OPTIONS", "processes"))

    results = [pool.apply_async(func=worker, args=(i, )) for i in LineNo]
    for result in results:
        z = result.get()

    print("="*100)
    print("{0} has finished running.".format(__file__))
