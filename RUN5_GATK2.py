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
    base = prefix
    java = Config.get("PATHS", "java")
    gatk = Config.get("PATHS", "gatk")
    ref = Config.get("PATHS", "reference")
    callgatk = "{0} -jar {1}".format(java, gatk)
    tmp = Config.get("DIRECTORIES", "temp_dir")
    inputDir = Config.get("DIRECTORIES", "output_dir")
    prefix = "{0}/{1}".format(inputDir, base)
    gatkdir = "{0}/gatk-results".format(prefix)
    if not os.path.exists(gatkdir):
        os.makedirs(gatkdir)
    
    if Config.getint("PIPELINE", "RealignTC"):
        # Getting target intervals to realign into.
        finput = "{0}/{1}.PicardSorted.DeDupped.RG.bam".format(gatkdir, base)
        foutput = "{0}/{1}.target_intervals.list".format(gatkdir, base)
        cmd = "{0} -T RealignerTargetCreator -R {1} -I {2} -o {3}".format(callgatk, ref, finput, foutput)
        print("Running commmand:\n{0}".format(cmd))
        subprocess.call(cmd, shell=True)

    if Config.getint("PIPELINE", "IndelRealign"):
        # Realigning the Indels using the target intervals list.
        finput = "{0}/{1}.PicardSorted.DeDupped.RG.bam".format(gatkdir, base)
        target_intervals = "{0}/{1}.target_intervals.list".format(gatkdir, base)
        foutput = "{0}/{1}.RealignedReads.bam".
        format(gatkdir, base)
        cmd = "{0} -T IndelRealigner -R {1} -I {2} -targetIntervals {3} -o {4}".format(callgatk, rf, finput, target_intervals, foutput)
        print("Running commmand:\n{0}".format(cmd))
        subprocess.call(cmd, shell=True)

    if Config.getint("PIPELINE", "HaplotypeCall"):
        # Calling the SNPs in Discovery Mode!
        finput = "{0}/{1}.RealignedReads.bam".format(gatkdir, base)
        foutput = "{0}/{1}.raw.snps.vcf".format(gatkdir, base)
        gtmode = Config.get("GATK", "gtmode")
        outmode = Config.get("GATK", "outmode")
        opts = "{0} -T HaploTypeCaller -R {1} -I {2} -gt_mode {3} -out_mode {4} -o {5} -nct {6}".format(callgatk, ref, finput, gtmode, outmode, foutput, nThreads)
        print("Running commmand:\n{0}".format(cmd))
        subprocess.call(cmd, shell=True)

    
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
