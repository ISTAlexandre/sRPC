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

plot1 = ROOT.TH2D(f"plane_1", f"plane_1", 16, 0 , 288,72, 0 ,400)
plot1.GetYaxis().SetTitle("Time x (mm)")
plot1.GetXaxis().SetTitle("Strip y (mm)")

plot2 = ROOT.TH2D(f"plane_2", f"plane_2", 16, 0 , 288,72, 0 ,400)
plot2.GetYaxis().SetTitle("Time x (mm)")
plot2.GetXaxis().SetTitle("Strip y (mm)")

plot3 = ROOT.TH2D(f"plane_3", f"plane_3", 16, 0 , 288,72, 0 ,400)
plot3.GetYaxis().SetTitle("Time x (mm)")
plot3.GetXaxis().SetTitle("Strip y (mm)")

plot4 = ROOT.TH2D(f"plane_4", f"plane_4", 16, 0 , 288,72, 0 ,400)
plot4.GetYaxis().SetTitle("Time x (mm)")
plot4.GetXaxis().SetTitle("Strip y (mm)")

def plane_plot(data):
    for row_index in range(len(data)):
        for col_index in range(0,len(data.columns),3):
            if data.iloc[row_index][col_index] == 0:
                plot1.Fill(data.iloc[row_index][col_index+2],data.iloc[row_index][col_index+1])
            if data.iloc[row_index][col_index] == 1:
                plot2.Fill(data.iloc[row_index][col_index+2],data.iloc[row_index][col_index+1])
            if data.iloc[row_index][col_index] == 2:
                plot3.Fill(data.iloc[row_index][col_index+2],data.iloc[row_index][col_index+1])
            if data.iloc[row_index][col_index] == 3:
                plot4.Fill(data.iloc[row_index][col_index+2],data.iloc[row_index][col_index+1])

for i in range(rank, len(all_files), size):
    print(f"Process {rank} read file: {all_files[i]}")
    df = pd.read_csv(all_files[i], delimiter=" ", header=None)
    plane_plot(df)

all_plot1 = comm.gather(plot1, root=0)
all_plot2 = comm.gather(plot2, root=0)
all_plot3 = comm.gather(plot3, root=0)
all_plot4 = comm.gather(plot4, root=0)

if rank == 0:
    merged_plot1 = ROOT.TH2D(f"merged_plane_1", f"plane_1", 16, 0 , 288,72, 0 ,400)
    merged_plot2 = ROOT.TH2D(f"merged_plane_2", f"plane_2", 16, 0 , 288,72, 0 ,400)
    merged_plot3 = ROOT.TH2D(f"merged_plane_3", f"plane_3", 16, 0 , 288,72, 0 ,400)
    merged_plot4 = ROOT.TH2D(f"merged_plane_4", f"plane_4", 16, 0 , 288,72, 0 ,400)
    for plot in all_plot1:
        merged_plot1.Add(plot)
    for plot in all_plot2:
        merged_plot2.Add(plot)
    for plot in all_plot3:
        merged_plot3.Add(plot)
    for plot in all_plot4:
        merged_plot4.Add(plot)
    merged_plot1.Draw("colz")
    canvas.SaveAs(f"n_hits/Plane_0.png")
    merged_plot2.Draw("colz")
    canvas.SaveAs(f"n_hits/Plane_1.png")
    merged_plot3.Draw("colz")
    canvas.SaveAs(f"n_hits/Plane_2.png")
    merged_plot4.Draw("colz")
    canvas.SaveAs(f"n_hits/Plane_3.png")