#!/home/clizarraga/usr/python/bin/bin/python3.4
from __future__ import print_function
import sys
import subprocess

# Equivalent to Perl's FindBin...sorta
import os
import itertools
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
if len(sys.argv)==1:
    sys.exit("usage: py3 {0}  <Config file>\n".format(__file__))

Config.read(sys.argv[1])
nThreads = Config.get("OPTIONS", "Threads")

print("Recognizing {0} as max threading...".format(nThreads))

ref = Config.get("PATHS","reference")
LineNo = dict(Config.items('NUMBER_MULTIPLE'))
print(LineNo)
print("Finding total number of files: {0}".format(len(LineNo)))

def worker(i):
    try:
        mult = int(LineNo[i])
    except KeyError:
        return "IGNORE ME!"
    if mult > 1:
        prefix = Config.get("COMBINE_ACCESSIONS", i)
    else:
        prefix = Config.get("SINGLE_ACCESSIONS", i)
    GarbageCollector = []
    base = prefix
    java = Config.get("PATHS", "java")
    picard = Config.get("PATHS", "picard")
    minheap = Config.get("OPTIONS", "minheap")
    maxheap = Config.get("OPTIONS", "maxheap")
    callpicard = "{0} -Xms{1} -Xmx{2} -XX:+UseG1GC -XX:+UseStringDeduplication -jar {3}".format(java, minheap, maxheap, picard)
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
        cmd = "{0} SortSam I={1} O={2} SO=coordinate TMP_DIR={3} CREATE_INDEX=true VALIDATION_STRINGENCY=SILENT".format(callpicard, finput, foutput, tmp)
        print("Running commmand:\n{0}".format(cmd))
        subprocess.call(cmd, shell=True)
        GarbageCollector.append(finput)

    if Config.getint("PIPELINE", "MarkDups"):
        # Marking duplicates in the bam with PicardTools
        finput = "{0}/{1}.Alignments.PicardSorted.bam".format(gatkdir, base)
        foutput = "{0}/{1}.PicardSorted.DeDupped.bam".format(gatkdir, base)
        metrics = "{0}/{1}.metrics".format(gatkdir, base)
        file_handles = int(subprocess.check_output("ulimit -n", shell=True))-100
        max_file_handles = "MAX_FILE_HANDLES_FOR_READ_ENDS_MAP={0}".format(file_handles)
        cmd = "{0} MarkDuplicates I={1} O={2} METRICS_FILE={3} TMP_DIR={4} ASSUME_SORTED=true VALIDATION_STRINGENCY=SILENT SORTING_COLLECTION_SIZE_RATIO=.35 {5}".format(callpicard, finput, foutput, metrics, tmp, max_file_handles)
        print("Running commmand:\n{0}".format(cmd))
        subprocess.call(cmd, shell=True)
        GarbageCollector.append(finput)

    if Config.getint("PIPELINE", "ReadGroups"):
        # Adding or Replacing Read Groups with Picard Tools
        finput = "{0}/{1}.PicardSorted.DeDupped.bam".format(gatkdir, base)
        # Read Group ID
        RGID = "foo"
        # Read Group Label
        RGLB = "bar"
        # Read Group Sequencing Brand
        RGPL = "Illumina"
        # Read Group PU
        RGPU = "blah"
        # Read Group Sample (in this case accession name)
        RGSM = base
        foutput = "{0}/{1}.PicardSorted.DeDupped.RG.bam".format(gatkdir, base)
        cmd = "{0} AddOrReplaceReadGroups I={1} O={2} RGID={3} RGLB={4} RGPL={5} RGPU={6} RGSM={7} TMP_DIR={8} CREATE_INDEX=true VALIDATION_STRINGENCY=SILENT".format(callpicard, finput, foutput, RGID, RGLB, RGPL, RGPU, RGSM, tmp)
        print("Running commmand:\n{0}".format(cmd))
        subprocess.call(cmd, shell=True)
        GarbageCollector.append(finput)

    # collectTheGarbage(GarbageCollector)

def collectTheGarbage(files):
    for filename in files:
        command = "rm -rf {0}".format(filename)
        print("Running command:\n{0}\n".format(command))
        subprocess.call(command, shell=True)
    return 1

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return itertools.zip_longest(fillvalue=fillvalue, *args)

if __name__ == "__main__":
    # Attempting with pool of workers.
    # Getting total memory of machine
    meminfo = dict((i.split()[0].rstrip(':'),int(i.split()[1])) for i in open('/proc/meminfo').readlines())
    mem_total_kib = meminfo['MemTotal']
    mem_total_gib = mem_total_kib*1.0e-6
    # Getting number of total processes that can be run at once given memory constraints.
    memper = int(Config.get("OPTIONS", "maxheap")[:-1])
    at_once = int(mem_total_gib//memper)
    print("This is the total number allowed at once: {0}".format(at_once))
    total = grouper(LineNo.keys(), at_once)
    # pool = mp.Pool(processes=Config.getint("OPTIONS", "processes"))
    pool = mp.Pool(processes=at_once)
    for group in total:
        results = [pool.apply_async( func=worker, args=(i, ) ) for i in group]
        for result in results:
            z = result.get()
        print("="*100)
        print("{0} has finished running.".format(str(group)))

    # results = [pool.apply_async( func=worker,args=(i,) ) for i in LineNo]
    # for result in results:
    #     z = result.get()

    print("="*200)
    print("{0} has finished running.".format(__file__))
