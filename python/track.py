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

fit_s = ROOT.TGraph()
fit_t = ROOT.TGraph()

fit_s.SetMarkerStyle(20)
fit_t.SetMarkerStyle(20)

fit_s.SetMarkerSize(0.5)
fit_t.SetMarkerSize(0.5)

canvas = ROOT.TCanvas("canvas", "canvas", 800, 800)

fit_s.GetYaxis().SetTitle("Strip y (mm)")
fit_t.GetYaxis().SetTitle("Time x (mm)")
fit_s.GetXaxis().SetTitle("Plane z (cm)")
fit_t.GetXaxis().SetTitle("Plane z (cm)")

fit_s.GetXaxis().SetLimits(-17, 51)
fit_t.GetXaxis().SetLimits(-17, 51)
fit_s.GetYaxis().SetRangeUser(0, 288)
fit_t.GetYaxis().SetRangeUser(0, 400)

linear_func = ROOT.TF1("linear_func", "[0]*x+[1]", -17, 51)
linear_func.SetLineColor(ROOT.kRed)
linear_func.SetLineWidth(1)

def track(file,concluded):
    for row_index in range(len(file)):
        plane_miss_list = []
        fit_s.SetTitle(f"Fit Strip Track {row_index}")
        fit_t.SetTitle(f"Fit Time Track {row_index}")
        
        fit_s.SetPoint(0, file.iloc[row_index][0]*17, file.iloc[row_index][2])
        fit_s.SetPoint(1, file.iloc[row_index][3]*17, file.iloc[row_index][5])
        fit_s.SetPoint(2, file.iloc[row_index][6]*17, file.iloc[row_index][8])
        
        fit_t.SetPoint(0, file.iloc[row_index][0]*17, file.iloc[row_index][1])
        fit_t.SetPoint(1, file.iloc[row_index][3]*17, file.iloc[row_index][4])
        fit_t.SetPoint(2, file.iloc[row_index][6]*17, file.iloc[row_index][7])

        plane_miss_list.append(file.iloc[row_index][0])
        plane_miss_list.append(file.iloc[row_index][3])
        plane_miss_list.append(file.iloc[row_index][6])
        if not pd.isna(file.iloc[row_index][9]): 
            fit_s.SetPoint(3, file.iloc[row_index][9]*17, file.iloc[row_index][11])
            fit_t.SetPoint(3, file.iloc[row_index][9]*17, file.iloc[row_index][10])
            plane_miss_list.append(file.iloc[row_index][9])

        fit_s.Fit("linear_func", "Q")
        slope_s = linear_func.GetParameter(0)
        intercept_s = linear_func.GetParameter(1)

        fit_t.Fit("linear_func", "Q")
        slope_t = linear_func.GetParameter(0)
        intercept_t = linear_func.GetParameter(1)

        for k in range(4):
            if k not in plane_miss_list:
                missed_plane = k
                break
            else:
                missed_plane = None

        concluded.write(f"{missed_plane} {slope_t} {intercept_t} {slope_s} {intercept_s}\n")
        fit_s.Set(0)
        fit_t.Set(0)

for i in range(rank, len(all_files), size):
    file = pd.read_csv(all_files[i], delimiter=" ", header=None)
    print(f"Process {rank} read file: {all_files[i]}")
    with open("parameters/"+str(all_files[i])[11:-4]+".asc", "w") as final:
        track(file,final)