#!/usr/bin/env python
import sys

inFile = open(sys.argv[1],'r')

for line in inFile:
  #skip comment lines that start with the '#' character
  if line[0] != '#':
    #split line into columns by tab
    data = line.strip().split('\t')
    accepted = ["C.avellana_Jefferson_02823","C.avellana_Jefferson_03213","C.avellana_Jefferson_00628","C.avellana_Jefferson_00044"]
    if data[0] in accepted:
      #Splitting the last line up.
      #Parts are now all the individually separated by semicolon ID=,Parent= etc.
      dic = {}
      parts = data[-1].split(';')
      for x in parts:
        y = x.split('=')
        dic[y[0]] = y[1]
      parts = data[-1].split(';')
      if data[2] == "mRNA":
        gene = dic['geneID']
        exonNumber = 0
        cdsNumber = 0
      # If feature is an exon, using the protocol and making a proper GTF file.
      elif data[2] == "exon":
        gene_id = dic['Parent'][:-3]
        # gene_version = dic['Parent'][-1]
        transcript_id = dic['Parent'][-2:]
        # transcript_version = dic["Parent"][-6:-5]
        exonNumber = exonNumber + 1
        data[-1] = 'gene_id "'+gene_id+'"; transcript_id "'+transcript_id+'"; exon_number "'+str(exonNumber)
        data[0] = data[0]
        print "\t".join(data)
      #Adding in 3UTR though not strictly necessary.
      elif data[2] == "CDS":
        gene_id = dic['Parent'][:-3]
        # gene_version = dic['Parent'][-4:]
        # gene_version = dic['Parent'][-1]
        transcript_id = dic['Parent'][-2:]
        # transcript_version = dic["Parent"][-6:-5]
        cdsNumber = cdsNumber + 1
        protein_id = transcript_id
        data[-1] = 'gene_id "'+gene_id+'"; transcript_id "'+transcript_id+'"; exon_number "'+str(cdsNumber)
        #Printing the CDS then the codons.
        print "\t".join(data)
      elif data[2] == "three_prime_UTR":
        gene_id = dic['Parent'][:-7]
        gene_version = dic['Parent'][-1]
        transcript_id = dic['Parent'][:-5]
        transcript_version = dic["Parent"][-6:-5]
        data[-1] = 'gene_id "'+gene_id+'"; gene_version"'+gene_version+'"; transcript_id "'+transcript_id+'"; transcript_version "'+transcript_version+'"; exon_number "'+exon_number
        if data[0][:2] == "Bd":
          data[0] = data[0][-1]
        data[2] = "3UTR"
      #Adding in 5UTR though not strictly necessary.
      elif data[2] == "five_prime_UTR":
        gene_id = dic['Parent'][:-7]
        gene_version = dic['Parent'][-1]
        transcript_id = dic['Parent'][:-5]
        transcript_version = dic["Parent"][-6:-5]
        data[-1] = 'gene_id "'+gene_id+'"; gene_version"'+gene_version+'"; transcript_id "'+transcript_id+'"; transcript_version "'+transcript_version+'"; exon_number "'+exon_number
        if data[0][:2] == "Bd":
          data[0] = data[0][-1]
        data[2] = "5UTR"
        print "\t".join(data)
