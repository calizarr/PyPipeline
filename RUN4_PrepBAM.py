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
    picard = Config.get("PATHS", "picard")
    callpicard = "{0} -jar {1}".format(java, picard)
    tmp = Config.get("DIRECTORIES", "temp_dir")
    inputDir = Config.get("DIRECTORIES", "output_dir")
    prefix = "{0}/{1}".format(inputDir, base)
    gatkdir = "{0}/gatk-results".format(prefix)
    if not os.path.exists(gatkdir):
        os.makedirs(gatkdir)
    
    if Config.getint("PIPELINE", "SortSam"):
        # Sorting bam with PicardTools in Coordinate Order.
        finput = "{0}/{1}.Alignments.bam".format(prefix, base)
        foutput = "{0}/{1}.Alignments.PicardSorted.bam".format(gatkdir, base)
        
        cmd = "{0} SortSam I={1} O={2} SO=coordinate TMP_DIR={3}".format(callpicard, finput, foutput, tmp)
        print("Running commmand:\n{0}".format(cmd))
        subprocess.call(cmd, shell=True)

    if Config.getint("PIPELINE", "MarkDups"):
        # Marking duplicates in the bam with PicardTools
        finput = foutput
        foutput = "{0}/{1}.PicardSorted.DeDupped.bam".format(gatkdir, base)
        metrics = "{0}/{1}.metrics".format(gatkdir, base)
        cmd = "{0} MarkDuplicates I={1} O={2} METRICS_FILE={3}".format(callpicard, finput, foutput, metrics)
        print("Running commmand:\n{0}".format(cmd))
        subprocess.call(cmd, shell=True)

    if Config.getint("PIPELINE", "ReadGroups"):
        # Adding or Replacing Read Groups with Picard Tools
        finput = foutput
        # Read Group ID
        RGID = "foo"
        # Read Group Label
        RGLB = "bar"
        # Read Group Sequencing Brand
        RGPL = "Illumina"
        # Read Group PU
        RGPU = "blah"
        # Read Group EH?
        RGSM = "JGI"
        foutput = "{0}/{1}.PicardSorted.DeDupped.RG.bam".format(gatkdir, base)
        cmd = "{0} AddOrReplaceReadGroups I={1} O={2} RGID={3} RGLB={4} RGPL={5} RGPU={6} RGSM={7} CREATE_INDEX=True".format(callpicard, finput, foutput, RGID, RGLB, RGPL, RGPU, RGSM)
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
