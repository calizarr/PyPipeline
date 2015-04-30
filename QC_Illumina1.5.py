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
    # Location of the read files.
    DataDir = Config.get("DIRECTORIES", "reads")+"/"
    F1 = Config.get("DIRECTORIES", "reads")+"/"+prefix+".R1.fastq"
    O1 = "B1 R1.QC"
    T1 = "{0}/{1}.B1.fastq".format(DataDir, prefix)
    F2 = Config.get("DIRECTORIES", "reads")+"/"+prefix+".R2.fastq"
    O2 = "B2 R2.QC"
    T2 = "{0}/{1}.B2.fastq".format(DataDir, prefix)
    capt = "B Q1"
    script = Config.get("PATHS", "fqscript")
    cmd1 = "perl {0} {1} {2} {3} {4}".format(script, F1, DataDir, O1, capt)
    print("Running command:\n{0}".format(cmd1))
    subprocess.call(cmd1, shell=True)
    cmd2 = "perl {0} {1} {2} {3} {4}".format(script, F2, DataDir, O2, capt)
    print("Running command:\n{0}".format(cmd2))
    subprocess.call(cmd2, shell=True)
    for filename in [T1, T2]:
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))
        else:
            print("Sorry, I can not find %s file." %filename)    
    

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
