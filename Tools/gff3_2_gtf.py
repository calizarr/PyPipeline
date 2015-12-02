#!/usr/bin/env python
# Only for Phytozome gff's.
import sys

inFile = open(sys.argv[1], 'r')

for line in inFile:
    # skip comment lines that start with the '#' character
    if line[0] != '#':
        # split line into columns by tab
        data = line.strip().split('\t')
        if data[2] == "CDS":
            dic = {}
            # Splitting the last line up.
            parts = data[-1].split(';')
            # Parts are now all the individually separated by semicolon
            # ID=,Parent= etc.
            for x in parts:
                y = x.split('=')
                dic[y[0]] = y[1]
            gene_id = dic['Parent'][:-7]
            #  gene_version = dic['Parent'][-4:]
            gene_version = dic['Parent'][-1]
            transcript_id = dic['Parent'][:-5]
            transcript_version = dic["Parent"][-6:-5]
            exon_number = dic["ID"][-1]
            protein_id = transcript_id
            data[-1] = 'gene_id "' + gene_id + '"; gene_version"' + \
                       gene_version + '"; transcript_id "' + transcript_id + \
                       '"; transcript_version "' + transcript_version + \
                       '"; exon_number "' + exon_number + '"; protein_id"' + protein_id
            # This is a Brachy only hack, will have to regex it later. Changing
            # only to chromosome number except for the supers.
            if data[0][:2] == "Bd":
                data[0] = data[0][-1]
            # Printing the CDS then the codons.
            print("\t".join(data))
            # Making the start and stop codon regions.
            # start_codon = "\t".join([data[0], data[1], "start_codon", data[3], str(int(data[3])+2), data[5], data[6], data[7], data[8]])
            # Printing them to output
            # print start_codon
            # stop_codon = "\t".join([data[0], data[1], "stop_codon", str(int(data[4])-2), data[4], data[5], data[6], data[7], data[8]])
            # print stop_codon
            # If feature is an exon, using the protocol and making a proper GTF
            # file.
        elif data[2] == "exon":
            dic = {}
            parts = data[-1].split(';')
            for x in parts:
                y = x.split('=')
                dic[y[0]] = y[1]
            gene_id = dic['Parent'][:-7]
            gene_version = dic['Parent'][-1]
            transcript_id = dic['Parent'][:-5]
            transcript_version = dic["Parent"][-6:-5]
            exon_number = dic["ID"][-1]
            data[-1] = 'gene_id "' + gene_id + '"; gene_version"' + gene_version + \
                       '"; transcript_id "' + transcript_id + '"; transcript_version "' + \
                       transcript_version + '"; exon_number "' + exon_number
            if data[0][:2] == "Bd":
                data[0] = data[0][-1]
            print("\t".join(data))
        # Adding in 3UTR though not strictly necessary.
        elif data[2] == "three_prime_UTR":
            dic = {}
            parts = data[-1].split(';')
            for x in parts:
                y = x.split('=')
                dic[y[0]] = y[1]
            gene_id = dic['Parent'][:-7]
            gene_version = dic['Parent'][-1]
            transcript_id = dic['Parent'][:-5]
            transcript_version = dic["Parent"][-6:-5]
            data[-1] = 'gene_id "' + gene_id + '"; gene_version"' + gene_version + \
                       '"; transcript_id "' + transcript_id + '"; transcript_version "' + \
                       transcript_version + '"; exon_number "' + exon_number
            if data[0][:2] == "Bd":
                data[0] = data[0][-1]
            data[2] = "3UTR"
        # ADDING IN 5UTR though not strictly necessary.
        elif data[2] == "five_prime_UTR":
            dic = {}
            parts = data[-1].split(';')
            for x in parts:
                y = x.split('=')
                dic[y[0]] = y[1]
            gene_id = dic['Parent'][:-7]
            gene_version = dic['Parent'][-1]
            transcript_id = dic['Parent'][:-5]
            transcript_version = dic["Parent"][-6:-5]
            data[-1] = 'gene_id "' + gene_id + '"; gene_version"' + gene_version + \
                       '"; transcript_id "' + transcript_id + '"; transcript_version "' + \
                       transcript_version + '"; exon_number "' + exon_number
            if data[0][:2] == "Bd":
                data[0] = data[0][-1]
            data[2] = "5UTR"
            print("\t".join(data))
