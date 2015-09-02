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
    # Getting paths for everything.
    DataDir = Config.get("DIRECTORIES", "reads")
    OutDir = Config.get("DIRECTORIES", "output_dir")
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
    # DIR = os.listdir(dir)
    try:
        DIR = os.listdir(directory)
    except OSError as e:
        print("OSError [%d]: %s at %s" % (e.errno, e.strerror, e.filename))
    CurrentFiles = []
    for filename in DIR:
        if base in filename:
            CurrentFiles.append(directory+"/"+filename)
    # Read files should've been acquired.
    print("These are the files we have acquired:\n{0}".format(CurrentFiles))
    CurrentSourcePaths = CurrentFiles[:]

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

    if Config.getint("PIPELINE", "FivePrimeFilter") and Config.getint("PIPELINE", "ThreePrimeFilter") and Config.getint("PIPELINE", "PairedEnd"):
        basedir = os.path.dirname(CurrentSourcePaths[0])
        log = os.path.join(basedir, "{0}.trimlog".format(base))
        read1 = CurrentSourcePaths[0]
        read2 = CurrentSourcePaths[1]
        out1 = os.path.join(basedir, "{0}.R1.3pTrim.5pTrim.Paired.fastq".format(base))
        out2 = os.path.join(basedir, "{0}.R2.3pTrim.5pTrim.Paired.fastq".format(base))
        orphan1 = os.path.join(basedir, "{0}.R1.orphan".format(base))
        orphan2 = os.path.join(basedir, "{0}.R2.orphan".format(base))
        length = Config.get("OPTIONS", "LengthOf5pTrim")
        minqual = Config.get("OPTIONS", "Min3pQuality")
        minlength = Config.get("OPTIONS", "Min3pLength")
        calltrimmomatic = "{0} -Xms{1} -Xmx{2} -XX:+UseG1GC -XX:+UseStringDeduplication -jar {3}".format(java, minheap, maxheap, trim)
        cmd = "{0} PE -threads {1} -phred{2} -trimlog {3} {4} {5} {6} {7} {8} {9} HEADCROP:{10} TRAILING:{11} MINLEN:{12}".format(calltrimmomatic, nThreads, phred, log, read1, read2, out1, orphan1, out2, orphan2, length, minqual, minlength)
        print("Running commmand:\n{0}".format(cmd))
        # subprocess.call(cmd, shell=True)

        FR1 = os.path.join(FiltDir, "{0}.R1.fastq".format(base))
        FR2 = os.path.join(FiltDir, "{0}.R2.fastq".format(base))
        ORO = os.path.join(FiltDir, "Orphans")
        LOGS = os.path.join(FiltDir, "Logs")
        cmd = "mv {0} {1}".format(out1, FR1)
        print("Running commmand:\n{0}".format(cmd))
        subprocess.call(cmd, shell=True)
        cmd = "mv {0} {1}".format(out2, FR2)
        print("Running commmand:\n{0}".format(cmd))
        subprocess.call(cmd, shell=True)
        if not os.path.exists(ORO):
            os.makedirs(ORO)
        cmd = "mv {0} {1}".format(orphan1, ORO)
        print("Running commmand:\n{0}".format(cmd))
        subprocess.call(cmd, shell=True)
        cmd = "mv {0} {1}".format(orphan2, ORO)
        print("Running commmand:\n{0}".format(cmd))
        subprocess.call(cmd, shell=True)
        if not os.path.exists(LOGS):
            os.makedirs(LOGS)
        cmd = "mv {0} {1}".format(log, LOGS)
        print("Running commmand:\n{0}".format(cmd))
        subprocess.call(cmd, shell=True)    
        
def collectTheGarbage(files):
    for filename in files:
        command  = "rm -rf {0}".format(filename)
        print("Running command:\n{0}\n".format(command))
        subprocess.call(command, shell=True)
    return 1

if __name__ == "__main__":
    # Attempting with pool of workers.
    pool = mp.Pool(processes=Config.getint("OPTIONS", "processes"))

    results = [pool.apply_async( func=worker,args=(i,) ) for i in LineNo]
    for result in results:
        z = result.get()

    print("="*100)
    print("{0} has finished running.".format(__file__))
