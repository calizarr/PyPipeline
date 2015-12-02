#!env/bin/python
#This Python script requires Biopython 1.51 or later
from __future__ import print_function
from Bio.SeqIO.QualityIO import FastqGeneralIterator
import itertools
import argparse
import gzip
import os
import pdb

def options():
    parser = argparse.ArgumentParser(description="De-Interleave paired fastq files.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("file_in", help="Input interleaved fastq file.")
    parser.add_argument("file_r1", help="Read_1 File.")
    parser.add_argument("file_r2", help="Read_2 File.")
    args = parser.parse_args()
    return args

def main():
    args = options()
    # pdb.set_trace()
    if os.path.splitext(args.file_in)[1] == ".gz":
        f_iter = FastqGeneralIterator(gzip.open(args.file_in, "rU"))
    else:
        f_iter = FastqGeneralIterator(open(args.file_in, "rU"))
    if os.path.splitext(args.file_r1)[1] != ".gz" and os.path.splitext(args.file_r2)[1] != ".gz":
        args.file_r1 += ".gz"
        args.file_r2 += ".gz"
    r1_handle = gzip.open(args.file_r1, "wb")
    r2_handle = gzip.open(args.file_r2, "wb")
    count_r1 = 0
    count_r2 = 0
    for(f_id, f_seq, f_q) in f_iter:
        dic = {"f_id":f_id, "f_seq":f_seq, "f_q":f_q}
        if f_id.endswith("/1"):
            r1_handle.write("@{f_id}\n{f_seq}\n+\n{f_q}\n".format(**dic))
            count_r1 += 1
        elif f_id.endswith("/2"):
            r2_handle.write("@{f_id}\n{f_seq}\n+\n{f_q}\n".format(**dic))
            count_r2 += 1
    r1_handle.close()
    r2_handle.close()
    print("{r1_records} records written to {r1_handle}".format(r1_records=count_r1, r1_handle=args.file_r1))
    print("{r2_records} records written to {r2_handle}".format(r2_records=count_r2, r2_handle=args.file_r2))

if __name__ == "__main__":
    main()
