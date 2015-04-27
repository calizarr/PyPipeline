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
    path = Config.get("DIRECTORIES", "combined") + "/" + prefix + ".fastq.gz"
    print("Unzipping file: "+path)
    cmd = "gunzip "+path
    print(cmd+"\n")
    subprocess.call(cmd, shell=True)
    OR = Config.get("DIRECTORIES", "reads")+"/"
    script = Config.get("PATHS", "fqscript")
    P1 = Config.get("DIRECTORIES", "combined")+"/"+prefix+".fastq"
    capt = "/1"
    cmd1 = "perl "+script+" "+P1+" "+OR+" R1 R2 "+capt+" H1s"
    print(cmd1+"\n")
    print("Being run: "+cmd1)
    subprocess.call(cmd1, shell=True)
    cmd2 = "gzip {0}".format(P1)
    print("Zipping combined file.")
    subprocess.call(cmd2, shell=True)

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
