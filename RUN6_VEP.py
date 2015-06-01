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

version = Config.get("VEP", "version")
species = Config.get("VEP", "species")
ref = Config.get("PATHS", "reference")

def convert2GTF():
    # Unsupported for now, do manually instead.
    gff = input("Absolute path to gff")
    gtf = input("Output path for gtf")
    python = Config.get("PATHS", "python")
    command = "{0} {1} > {2}".format(python, gff, gtf)
    print("Running commmand:\n{0}".format(command))
    subprocess.call(command, shell=True)

def makeCDB():
    # Unsupported for now, do manually instead.
    gtf = input("Absolute path to gtf")
    build = Config.get("PATHS", "vepcache")
    command = "{0} -i {1} -f {2} -d {3} -s {4}".format(build, gtf, ref, version, species)
    print("Running commmand:\n{0}".format(command))    
    subprocess.call(command, shell=True)
    
def worker(i):
    mult = int(LineNo[i])
    if mult > 1:
        prefix = Config.get("COMBINE_ACCESSIONS", i)
    else:
        prefix = Config.get("SINGLE_ACCESSIONS", i)
    base = prefix
    GarbageCollector = []
    vep = Config.get("PATHS", "vep")
    gatkdir = Config.get("DIRECTORIES", "output_dir")+"/"+base+"/gatk-results"
    vepdir = Config.get("DIRECTORIES", "output_dir")+"/"+base+"/VEP"
    if not os.path.exists(vepdir):
        os.makedirs(vepdir)
    filename = Config.get("FILENAMES", "vepvcf")
    finput = gatkdir+"/"+base+filename
    foutput = vepdir+"/"+base+".vep"+filename[9:-3]+"vcf"
    stats = vepdir+"/"+base+".vep"+filename[9:-3]+"stats.html"
    command = "perl {0} -v -fork {1} -offline --species {2} -i {3} -o {4} --stats_file {5} --cache --cache_version {6} --fasta {7} --vcf".format(vep, nThreads, species, finput, foutput, stats, version, ref)
    print("Running commmand:\n{0}".format(command))    
    subprocess.call(command, shell=True)
    GarbageCollector.append(finput)
    print("Collecting Garbage")
    # collectTheGarbage(GarbageCollector)

def collectTheGarbage(files):
    for filename in files:
        command = "rm -rf {0}".format(filename)
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
