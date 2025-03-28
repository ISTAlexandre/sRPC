#!/bin/bash
#SBATCH -p lipq
# Transfer input files
# INPUT = python coordinates n_hits

# Transfer output files
# OUTPUT = n_hits

module load root/6.16.00

# Run the script
python3 python/planes.py