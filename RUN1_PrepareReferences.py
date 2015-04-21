#!/home/clizarraga/usr/python/bin/bin/python3.4
import sys
import subprocess
from subprocess import Popen, PIPE

# Equivalent to Perl's FindBin...sorta
import os
bindir = os.path.abspath(os.path.dirname(__file__))

# Python 3.4 Configuration Parser
import configparser

# Reading configuration file.
if len(sys.argv)==1:
    sys.exit("usage: py3 {0}  <Config file>\n".format(__file__))

Config = configparser.ConfigParser()
Config.read(sys.argv[1])

ref = Config.get("PATHS","reference")

def worker():
    bowtie2 = Config.get("PATHS", "bowtie2")
    ref = Config.get("PATHS", "reference")
    indices = Config.get("PATHS", "indices")
    cmd = "{0}-build {1} {2}".format(bowtie2, ref, indices)
    print("Running command: ")
    print(cmd)
    subprocess.call(cmd, shell=True)

if __name__=="__main__":
    worker()
