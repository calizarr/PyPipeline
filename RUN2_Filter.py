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
    if mult > 1:
        base = Config.get("COMBINE_ACCESSIONS", i)
    else:
        base = Config.get("SINGLE_ACCESSIONS", i)
    # Lists to hold paths and garbage to be collected.
    CurrentSourcePaths = []
    GarbageCollector = []
    dir = DataDir
    print("Working with {0}".format(dir))
    # Attempting to get the read files.
    # DIR = os.listdir(dir)
    try:
        DIR = os.listdir(dir)
    except OSError as e:
        print "OSError [%d]: %s at %s" % (e.errno, e.strerror, e.filename)
    CurrentFiles = []
    for filename in DIR:
        if base in filename:
            CurrentFiles.append(os.path.abspath(filename))
    # Read files should've been acquired.
    print("These are the files we have acquired: \n")
    print(CurrentFiles,"\n")
    if Config.get("PIPELINE", "Compressed"):
        print("Treating files as compressed. \n")
        thisSet = CurrentSourcePaths[:]
        CurrentSourcePaths = []
        for filename in thisSet:
            if filename.endswith("gz"):
                nPath = filename
                nPath = nPath[:-3]
                command = "gunzip "+filename
                CurrentSourcePaths.append(nPath)
            else:
                CurrentSourcePaths.append(filename)

    # if Config.get("PIPELINE", "FivePrimeFilter"):
    #     print("Trimming 5' end of sequences...\n")
    #     thisSet = CurrentSourcePaths[:]
    #     print("The current files to be used: {0} \n".format(thisSet))
    #     CurrentSourcePaths = []
    #     script = Config.get("PATHS", "FivePrimeTrimmer")
    #     length = Config.get("OPTIONS", "LengthOf5pTrim")
    #     for filename in thisSet:
    #         oPath = filename
    #         oPath = oPath.replace("fastq", "5pTrim.fastq")
    #         oPath = oPath.replace("fq", "5pTrim.fastq")
    #         print("The output path is: {0}\n".format(oPath))
    #         command = "{0} {1} -i {2} -o {3}".format(script, opts, filename, oPath)
    #         print("Running command: {0}\n".format(command))
    #         subprocess.call(command, shell=True)
    #         CurrentSourcePaths.append(oPath)
    #         GarbageCollector.append(oPath)

    # if Config.get("PIPELINE", "ThreePrimeFilter"):
    #     # Always check your phred scores.
    #     print("Trimming 3' end on quality...\n")
    #     thisSet = CurrentSourcePaths[:]
    #     print("The current files to be used: {0}\n".format(thisSet))
    #     CurrentSourcePaths = []
    #     script = Config.get("PATHS", "fastq_quality_trimmer")
    #     MinL = Config.get("OPTIONS", "Min3pLength")
    #     phred = Config.get("OPTIONS", "phred")
    #     opts = "-t {0} -Q {1} -l {2}".format(MinQ, phred, MinL)
    #     for filename in thisSet:
    #         oPath = filename
    #         oPath = oPath.replace("fastq", "3pTrim.fastq")
    #         oPath = oPath.replace("fq", "3pTrim.fastq")
    #         print("The output path is: {0}\n".format(oPath))
    #         command = "{0} {1} -i {2} -o {3}".format(script, opts, filename, oPath)
    #         print("Running: {0}\n".format(command))
    #         subprocess.call(command, shell=True)
    #         CurrentSourcePaths.append(oPath)
    #         GarbageCollector.append(oPath)

    # if Config.get("PIPELINE", "Paired"):
    #     print("Parsing for Pairs..\n")
    #     thisSet = CurrentSourcePaths[:]
    #     print("What files are we working with?\n{0}\n".format(thisSet))
    #     CurrentSourcePaths = []
    #     script = config.get("PATHS", "PairsAndOrphans")
    #     R1, R2 = [],[]
    #     for filename in thisSet:
    #         if "R1" in filename:
    #             R1.append(filename)
    #         elif "R2" in filename:
    #             R2.append(filename)
    #     print("These are the R1s and R2s: \n{0}\n{1}\n".format(R1,R2))
    #     T1 = "{0}/{1}.TempRead1.fastq".format(DataDir, base)
    #     T2 = "{0}/{1}.TempRead2.fastq".format(DataDir, base)
    #     command = "cat {0} > {1}".format(" ".join(R1), T1)
    #     print("Running command: {0}\n".format(command))
    #     subprocess.call(command, shell=True)
    #     command = "cat {0} > {1}".format(" ".join(R2), T2)
    #     print("Running command: {0}\n".format(command))
    #     GarbageCollector.append(T1)
    #     GarbageCollector.append(T2)
    #     O = "{0}/{1}".format(DataDir, base)
    #     OR1 = "{0}/{1}.R1.fastq".format(DataDir, base)
    #     OR2 = "{0}/{1}.R2.fastq".format(DataDir, base)
    #     ORO = "{0}/{1}.orphan.fastq"
    #     FR1 = "{0}/{1}.R1.fastq"
    #     FR2 = "{0}/{1}.R2.fastq"
    #     command = "perl {0} {1} {2} {3}".format(script, T1, T2, O)
    #     print("Running command:\n{0}\n".format(command))
    #     subprocess.call(command)
    #     command = "mv {0} {1}".format(OR1, FR1)
    #     print("Running command:\n{0}\n".format(command))
    #     subprocess.call(command)
    #     command = "mv {0} {1}".format(OR2, FR2)
    #     print("Running command:\n{0}\n".format(command))
    #     subprocess.call(command)
    #     GarbageCollector.append(OR1)
    #     GarbageCollector.append(OR2)
    #     GarbageCollector.append(ORO)
    #     CurrentSourcePaths.append(OR1)
    #     CurrentSourcePaths.append(OR2)
    #     CurrentSourcePaths.append(ORO)
    # prepFinal(OutDir, CurrentSourcePaths)
    # collectTheGarbage(GarbageCollector)

def collectTheGarbage(files):
    for filename in files:
        command  = "rm -rf {0}".format(filename)
        print("Running command:\n{0}\n".format(command))
        subprocess.call(command, shell=True)
    return 1

if __name__ == "__main__":
    # Setup list of processes to run
    processes = [mp.Process(target=worker,args=(i,)) for i in LineNo]
    # Run processes
    for p in processes:
        p.start()
    # Exit the completed processes.
    for p in processes:
        p.join()

    print("Everything is over.")
    # results = [output.get() for p in processes]
    # print(results)
