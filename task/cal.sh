#!/bin/bash
#SBATCH -p lipq
# Transfer input files
# INPUT = python offset data_ready/dabc24124000030.root src

# Transfer output files
# OUTPUT = offset src

# Load environment
module load root/6.16.00
module load openmpi/4.0.3
module load python/3.9.12

pip install numpy<2
pip install pandas
pip install torch

mkdir data_ready
mv *.root data_ready

# Run the Python script
python3 python/QB2.py data_ready/dabc24124000030.root