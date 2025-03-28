#!/bin/bash
#SBATCH -p lipq
#SBATCH --cpus-per-task=20 # Request 20 CPU cores on a single node
# Transfer input files
# INPUT = data/dataConverter2.py /share/deteclab/sRPC/data/asci/dabc24121*.da* /share/deteclab/sRPC/data/asci/dabc24122*.da* /share/deteclab/sRPC/data/asci/dabc24123*.da* /share/deteclab/sRPC/data/asci/dabc24124*.da* /share/deteclab/sRPC/data/asci/dabc24125*.da* /share/deteclab/sRPC/data/asci/dabc24126*.da*

# Transfer output files
# OUTPUT = data_ready

# Load environment
module load root/6.16.00
module load openmpi/4.0.3
module load python/3.9.12

pip install pandas
pip install tqdm
pip install numpy<2

mkdir data
mkdir data_ready
mv *.da* data

# Run the Python script
mpirun --oversubscribe -np 20 python dataConverter2.py
