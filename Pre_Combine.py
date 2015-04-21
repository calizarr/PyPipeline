#!/home/clizarraga/usr/python/bin/bin/python3.4
import sys
import subprocess
# Equivalent to Perl's FindBin...sorta
import os
bindir = os.path.abspath(os.path.dirname(__file__))

# Python 3.4 Configuration Parser
import configparser

# Multi processing begins.
import multiprocessing as mp
output = mp.Queue()

# Reading configuration file.
if len(sys.argv)==1:
    sys.exit("usage: py3 {0}  <Config file>\n".format(__file__))

Config = configparser.ConfigParser()
Config.read(sys.argv[1])
nThreads = Config.get("OPTIONS", "Threads")

print("Recognizing {0} as max threading...".format(nThreads))

ref = Config.get("PATHS","reference")
LineNo = dict(Config.items('NUMBER_MULTIPLE'))
print(LineNo)
print("Finding total number of files: {0}".format(len(LineNo)))

def worker(i):
    mult = int(LineNo[i])
    if mult > 1:
        prefix = Config.get("COMBINE_ACCESSIONS", i)
    else:
        prefix = Config.get("SINGLE_ACCESSIONS", i)
    accessions = Config.get("DATA", i).split(',')
    result = Config.get("DIRECTORIES", "combined") + "/" + prefix + ".fastq.gz"
    # cmds = []
    cmd = "cat"
    # cmds.append('cat')
    for f in accessions:
        path = " "+Config.get("DIRECTORIES", "data_dir") + f
        cmd = cmd + path
        # cmds.append(path)
    # cmds.append(">")
    # cmds.append(result)
    cmd = cmd+" > "+result
    print(cmd)
    # Insert Subprocess call here.
    output.put(subprocess.call(cmd, shell=True))
    print("Command is run and files should be in their proper places.\n")


if __name__ == "__main__":
    # Setup list of processes to run
    processes = [mp.Process(target=worker,args=(i,)) for i in LineNo]
    # Run processes
    for p in processes:
        p.start()
    # Exit the completed processes.
    for p in processes:
        p.join()

    results = [output.get() for p in processes]
    print(results)
