import os
from glob import glob
from mpi4py import MPI

import argparse
import tarfile
import time
import datetime

import numpy as np
import ROOT
from array import array
import string

import torch
import torch.nn.functional as F
import pandas as pd

# Initialize MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

ROOT.gROOT.SetBatch(True)

# Specify folder containing files
folder_path = "parameters"  # Change to your folder path

# Get all files from the folder
all_files = sorted(glob(os.path.join(folder_path, "*")))  # Sort to ensure consistent order

strip_angle = ROOT.TH1D("strip_angle", "strip_angle degrees", 90, -180, 180)
time_angle = ROOT.TH1D("time_angle", "time_angle degrees", 180, -180, 180)

canvas = ROOT.TCanvas("canvas", "canvas", 800, 800)

def angle(file):
    for row_index in range(len(file)):
        strip_angle.Fill(np.arctan(file.iloc[row_index][3]/10)*180/np.pi)
        time_angle.Fill(np.arctan(file.iloc[row_index][1]/10)*180/np.pi)

for i in range(rank, len(all_files), size):
    file = pd.read_csv(all_files[i], delimiter=" ", header=None)
    print(f"Process {rank} read file: {all_files[i]}")
    angle(file)

all_strip_angles = comm.gather(strip_angle, root=0)
all_time_angles = comm.gather(time_angle, root=0)

if rank == 0:
    merged_strip_angle = ROOT.TH1D("merged_strip_angle", "strip_angle degrees", 90, -180, 180)
    merged_time_angle = ROOT.TH1D("merged_time_angle", "time_angle degrees", 180, -180, 180)
    
    for hist in all_strip_angles:
        merged_strip_angle.Add(hist)
    
    for hist in all_time_angles:
        merged_time_angle.Add(hist)
    
    # Draw and save the merged histograms
    merged_strip_angle.Draw("hist")
    canvas.SaveAs(f"angle/Strip_angle.png")
    merged_time_angle.Draw("hist")
    canvas.SaveAs(f"angle/Time_angle.png")