#!/bin/bash
#SBATCH -p lipq
#SBATCH --cpus-per-task=10 # Request 10 CPU cores on a single node
# Transfer input files
# INPUT = python src data_ready

# Transfer output files
# OUTPUT = coordinates

module load gcc83/root/6.30.04
module load openmpi/4.0.3

pip install torch
pip install pandas

mkdir coordinates
mkdir data_ready2
mv data_ready/dabc24124*.root data_ready2
rm -r data_ready
mkdir data_ready
mv data_ready2/coordinates/* data_ready

mpirun --oversubscribe -np 10 python python/coordinates.py