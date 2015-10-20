#!/bin/bash

if [[ $# -lt 7 ]]; then
    echo "$0: <Config file> <Prepare Reference Switch> <Filter Reads Switch> <Alignment Switch> <Prep BAM Switch> <GATK2 Switch> <VEP Switch>"
    echo "Switches are turned on by passing 1 and off by 0"
   exit 1
fi

echo "Make sure that all Pre steps of Pipeline have been run. This script only launches RUN1-RUN6."
echo "Config file: $1. Prepare Reference: $2. Filter Reads: $3. Align to Genome: $4. Prep BAMS <PicardTools>: $5. GATK2: $6. Variant Effect Predictor: $7."

LOG_ERR="SNP_Pipeline.error.log"
LOG_OUT="SNP_Pipeline.output.log"

if [ -f $LOG_ERR ]; then
    rm $LOG_ERR
fi

if [ -f $LOG_OUT ]; then
    rm $LOG_OUT
fi

touch $LOG_ERR
touch $LOG_OUT

# Run prepare references step of pipeline
if [[ $2 -eq 1 ]]; then
    echo "python RUN1_PrepareReferences.py $1"
    # python RUN1_PrepareReferences.py $1
    (time python RUN1_PrepareReferences.py $1 | tee -a $LOG_OUT) 3>&1 1>&2 2>&3 | tee -a $LOG_ERR
fi

# Run filter step of pipeline
if [[ $3 -eq 1 ]]; then
    echo "python RUN2_Filter_Trimmomatic.py $1"
    # python RUN2_Filter_Trimmomatic.py $1 > >(tee $LOG_OUT) 2> >(tee $LOG_ERR >&2)
    (time python RUN2_Filter_Trimmomatic.py $1 | tee -a $LOG_OUT) 3>&1 1>&2 2>&3 | tee -a $LOG_ERR
fi

# Run Alignment to Genome step of pipeline.
if [[ $4 -eq 1 ]]; then
    echo "python RUN3_AlignToReference.py $1"
    # python RUN3_AlignToReference.py $1 > >(tee $LOG_OUT) 2> >(tee $LOG_ERR >&2)
    (time python RUN3_AlignToReference.py $1 | tee -a $LOG_OUT) 3>&1 1>&2 2>&3 | tee -a $LOG_ERR
fi

# Run Preparing BAM files with PicardTools step of pipeline.
if [[ $5 -eq 1 ]]; then
    echo "python RUN4_PrepBAM.py $1"
    # python RUN4_PrepBAM.py $1 > >(tee $LOG_OUT) 2> >(tee $LOG_ERR >&2)
    (time python RUN4_PrepBAM.py $1 | tee -a $LOG_OUT) 3>&1 1>&2 2>&3 | tee -a $LOG_ERR
fi

# Run GATK2 on prepared BAM files.
if [[ $6 -eq 1 ]]; then
    echo "python RUN5_GATK2.py $1"
    # python RUN5_GATK2.py $1 > >(tee $LOG_OUT) 2> >(tee $LOG_ERR >&2)
    (time python RUN5_GATK2.py $1 | tee -a $LOG_OUT) 3>&1 1>&2 2>&3 | tee -a $LOG_ERR
fi

# RUN Variant Effect Predictor on GATK2 BAM files.
if [[ $7 -eq 1 ]]; then
    echo "python RUN6_VEP.py $1"
    # python RUN6_VEP.py $1 > >(tee $LOG_OUT) 2> >(tee $LOG_ERR >&2)
    (time python RUN6_VEP.py $1 | tee -a $LOG_OUT) 3>&1 1>&2 2>&3 | tee -a $LOG_ERR
fi

if [[ -n $8 ]]; then
    echo "SNP_Pipeline.sh done. Check the output and error logs for more information." | mailx -s "SNP Pipeline Done." $8
fi

echo "All steps finished running. Check $LOG_ERR and $LOG_OUT for errors and output log respectively."
echo "These many seconds since the entire script started: $SECONDS. Compare it to time if you launch time $0"
