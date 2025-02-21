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

hist1_s = ROOT.TH1D("hist1_s", "Plane 1 Distance to Strip Track", 20, -100, 100)
hist2_s = ROOT.TH1D("hist2_s", "Plane 2 Distance to Strip Track", 20, -100, 100)
hist3_s = ROOT.TH1D("hist3_s", "Plane 3 Distance to Strip Track", 20, -100, 100)
hist4_s = ROOT.TH1D("hist4_s", "Plane 4 Distance to Strip Track", 20, -100, 100)

hist1_t = ROOT.TH1D("hist1_t", "Plane 1 Distance to Time Track", 200, -100, 100)
hist2_t = ROOT.TH1D("hist2_t", "Plane 2 Distance to Time Track", 200, -100, 100)
hist3_t = ROOT.TH1D("hist3_t", "Plane 3 Distance to Time Track", 200, -100, 100)
hist4_t = ROOT.TH1D("hist4_t", "Plane 4 Distance to Time Track", 200, -100, 100)

def errors(file_c, file_p):
    for row_index in range(len(file_c)):
        slope_t = file_p.iloc[row_index][1]
        intercept_t = file_p.iloc[row_index][2]
        slope_s = file_p.iloc[row_index][3]
        intercept_s = file_p.iloc[row_index][4]
        plane_miss = file_p.iloc[row_index][0]

        point_list = []
        pre_point_list = []
        for j in range(0,12,3):
            if not pd.isna(file_c.iloc[row_index][j]):
                point_list.append([file_c.iloc[row_index][j], file_c.iloc[row_index][j+1], file_c.iloc[row_index][j+2]])
                pre_point_t = file_c.iloc[row_index][j]*slope_t+intercept_t
                pre_point_s = file_c.iloc[row_index][j]*slope_s+intercept_s
                pre_point_list.append([file_c.iloc[row_index][j], pre_point_t, pre_point_s])

        for p_index in range(len(point_list)):
            error_t = point_list[p_index][1] -pre_point_list[p_index][1]
            error_s = point_list[p_index][2] -pre_point_list[p_index][2]
            plane = point_list[p_index][0]

            if plane == 0:
                hist1_t.Fill(error_t)
                hist1_s.Fill(error_s)
            if plane == 1:
                hist2_t.Fill(error_t)
                hist2_s.Fill(error_s)
            if plane == 2:
                hist3_t.Fill(error_t)
                hist3_s.Fill(error_s)
            if plane == 3:
                hist4_t.Fill(error_t)
                hist4_s.Fill(error_s)

for i in range(rank, len(all_files), size):
    file_parameters = pd.read_csv(all_files[i], delimiter=" ", header=None)
    file_coordinates = pd.read_csv(all_files[i].replace("parameters", "coordinates"), delimiter=" ", header=None)
    print(f"Process {rank} read file: {all_files[i]}")
    errors(file_coordinates, file_parameters)

all_hist1_t = comm.gather(hist1_t, root=0)
all_hist2_t = comm.gather(hist2_t, root=0)
all_hist3_t = comm.gather(hist3_t, root=0)
all_hist4_t = comm.gather(hist4_t, root=0)

all_hist1_s = comm.gather(hist1_s, root=0)
all_hist2_s = comm.gather(hist2_s, root=0)
all_hist3_s = comm.gather(hist3_s, root=0)
all_hist4_s = comm.gather(hist4_s, root=0)

if rank == 0:
    merged_hist1_t = ROOT.TH1D("merged_hist1_t", "Plane 1 Distance to Time Track", 200, -100, 100)
    merged_hist2_t = ROOT.TH1D("merged_hist2_t", "Plane 2 Distance to Time Track", 200, -100, 100)
    merged_hist3_t = ROOT.TH1D("merged_hist3_t", "Plane 3 Distance to Time Track", 200, -100, 100)
    merged_hist4_t = ROOT.TH1D("merged_hist4_t", "Plane 4 Distance to Time Track", 200, -100, 100)

    merged_hist1_s = ROOT.TH1D("merged_hist1_s", "Plane 1 Distance to Strip Track", 20, -100, 100)
    merged_hist2_s = ROOT.TH1D("merged_hist2_s", "Plane 2 Distance to Strip Track", 20, -100, 100)
    merged_hist3_s = ROOT.TH1D("merged_hist3_s", "Plane 3 Distance to Strip Track", 20, -100, 100)
    merged_hist4_s = ROOT.TH1D("merged_hist4_s", "Plane 4 Distance to Strip Track", 20, -100, 100)

    canvas = ROOT.TCanvas("canvas", "canvas", 800, 800)
    for hist in all_hist1_t:
        merged_hist1_t.Add(hist)
    for hist in all_hist2_t:
        merged_hist2_t.Add(hist)
    for hist in all_hist3_t:
        merged_hist3_t.Add(hist)
    for hist in all_hist4_t:
        merged_hist4_t.Add(hist)
    for hist in all_hist1_s:
        merged_hist1_s.Add(hist)
    for hist in all_hist2_s:
        merged_hist2_s.Add(hist)
    for hist in all_hist3_s:
        merged_hist3_s.Add(hist)
    for hist in all_hist4_s:
        merged_hist4_s.Add(hist)
    
    merged_hist1_t.Draw("hist")
    canvas.SaveAs(f"errors/Plane1_Time.png")
    merged_hist2_t.Draw("hist")
    canvas.SaveAs(f"errors/Plane2_Time.png")
    merged_hist3_t.Draw("hist")
    canvas.SaveAs(f"errors/Plane3_Time.png")
    merged_hist4_t.Draw("hist")
    canvas.SaveAs(f"errors/Plane4_Time.png")

    merged_hist1_s.Draw("hist")
    canvas.SaveAs(f"errors/Plane1_Strip.png")
    merged_hist2_s.Draw("hist")
    canvas.SaveAs(f"errors/Plane2_Strip.png")
    merged_hist3_s.Draw("hist")
    canvas.SaveAs(f"errors/Plane3_Strip.png")
    merged_hist4_s.Draw("hist")
    canvas.SaveAs(f"errors/Plane4_Strip.png")