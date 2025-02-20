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
folder_path = "coordinates"  # Change to your folder path

# Get all files from the folder
all_files = sorted(glob(os.path.join(folder_path, "*")))  # Sort to ensure consistent order

canvas = ROOT.TCanvas("canvas", "canvas", 800, 800)
def plane_plot(rank,data):
    plot = ROOT.TH2D(f"plane_{rank}", f"plane_{rank}", 16, 0 , 288,72, 0 ,400)
    plot.GetYaxis().SetTitle("Time x (mm)")
    plot.GetXaxis().SetTitle("Strip y (mm)")
    
    for row_index, value in data.iterrows():
        plot.Fill(value[rank*3+2],value[rank*3+1])

    plot.Draw("colz")
    canvas.SaveAs(f"n_hits/Plane_{rank}.png")
    plot.Reset()

for i in range(len(all_files)):
    print(f"Process {rank} read file: {all_files[i]}")
    df = pd.read_csv(all_files[i], delimiter=" ", header=None)
    plane_plot(rank,df)