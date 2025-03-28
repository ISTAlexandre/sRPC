#!/bin/bash
#SBATCH -p lipq

# Transfer input files
# INPUT = python

# Transfer output files
# OUTPUT = 

module load pythia/8.2.15
module load root/6.14.06

python3.6 python/teste.py