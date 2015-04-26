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
    # accessions = Config.get("DATA", i).split(',')
    F1 = Config.get("DIRECTORIES", "reads")+"/"+prefix+".R1.fastq"
    F2 = Config.get("DIRECTORIES", "reads")+"/"+prefix+".R2.fastq"
    out = 0
    cmd = "wc -l "+F1
    # cmd = "head "+F1+" | wc -l"
    out = subprocess.check_output(cmd, shell=True)
    out = int(out.split()[0], 10)
    # print(mp.current_process())
    num = out
    cmd = "wc -l "+F2
    # cmd = "head "+F2+" | wc -l"
    out = subprocess.check_output(cmd, shell=True)
    out = int(out.split()[0], 10)
    num += out
    print("Here is our total: {0}".format(num))
    # print(mp.current_process())
    if num % 4 == 0:
        print("Proper number of lines in file!")
    else:
        print("These files are not proper: "+F1+" "+F2)

if __name__ == "__main__":
    # Setup list of processes to run
    # processes = [mp.Process(target=worker,args=(i,)) for i in LineNo]
    # # Run processes
    # for p in processes:
    #     p.start()
    # # Exit the completed processes.
    # for p in processes:
    #     p.join()

    # Attempting with pool of workers.
    pool = mp.Pool(processes=Config.getint("OPTIONS", "processes"))
    # processes = [mp.Process(target=worker,args=(i,)) for i in LineNo]

    results = [pool.apply_async( func=worker,args=(i,) ) for i in LineNo]
    for result in results:
        z = result.get()

    print("Everything is over.")
    # results = [output.get() for p in processes]
    # print(results)
