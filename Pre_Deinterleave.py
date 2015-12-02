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
        print("Running python deinterleave script")
        python = Config.get('PATHS', 'python')
        script = Config.get("PATHS", "deinterleave")
        file_in = os.path.join(Config.get("DIRECTORIES", "combined"), prefix+".fastq.gz")
        file_r1 = os.path.join(OR, prefix + ".R1.fastq.gz")
        file_r2 = os.path.join(OR, prefix + ".R2.fastq.gz")
        dic = {"python":python, "script":script, "file_in":file_in, "file_r1":file_r1, "file_r2":file_r2}
        cmd = "{python} {script} {file_in} {file_r1} {file_r2}".format(**dic)
        print("Running command: \n{0}".format(cmd))
        subprocess.call(cmd, shell=True)

if __name__ == "__main__":
    # Attempting with pool of workers.
    pool = mp.Pool(processes=Config.getint("OPTIONS", "processes"))

    results = [pool.apply_async(func=worker, args=(i, )) for i in LineNo]
    for result in results:
        z = result.get()

    print("="*100)
    print("{0} has finished running.".format(__file__))
