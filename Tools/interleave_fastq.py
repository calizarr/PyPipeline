#!env/bin/python
#This Python script requires Biopython 1.51 or later
from __future__ import print_function
from Bio.SeqIO.QualityIO import FastqGeneralIterator
import itertools
import argparse
import gzip
import os
# import pdb

def options():
    parser = argparse.ArgumentParser(description="Interleave paired fastq files.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("file_f", help="Read_1 File or Forward strand file")
    parser.add_argument("file_r", help="Read_2 File or Reverse strand file")
    parser.add_argument("file_out", help="Output filename")
    args = parser.parse_args()
    return args

def main():
    args = options()
    # pdb.set_trace()
    if os.path.splitext(args.file_f)[1]==".gz" and os.path.splitext(args.file_r)[1]==".gz":
        f_iter = FastqGeneralIterator(gzip.open(args.file_f, "rU"))
        r_iter = FastqGeneralIterator(gzip.open(args.file_r, "rU"))
    else:
        f_iter = FastqGeneralIterator(open(args.file_f,"rU"))
        r_iter = FastqGeneralIterator(open(args.file_r,"rU"))
    if os.path.splitext(args.file_out)[1] != ".gz":
        args.file_out = args.file_out+".gz"
    handle = gzip.open(args.file_out, "wb")
    count = 0
    for (f_id, f_seq, f_q), (r_id, r_seq, r_q) \
        in itertools.izip(f_iter,r_iter):
        if f_id.endswith("/1") and r_id.endswith("/2"):
            assert f_id[:-2] == r_id[:-2]
            paired = True
        else:
            assert f_id == r_id
            strands = True
        count += 2
        #Write out both reads with "/1" and "/2" suffix on ID
        dic = {"f_id":f_id, "f_seq":f_seq, "f_q":f_q, "r_id":r_id, "r_seq":r_seq, "r_q":r_q}
        if paired:
            handle.write("@{f_id}\n{f_seq}\n+\n{f_q}\n@{r_id}\n{r_seq}\n+\n{r_q}\n".format(**dic))
        elif strands:
            handle.write("@%s/1\n%s\n+\n%s\n@%s/2\n%s\n+\n%s\n" \
                     % (f_id, f_seq, f_q, r_id, r_seq, r_q))
    handle.close()
    print("%i records written to %s" % (count, args.file_out))

if __name__ == "__main__":
    main()
