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
folder_path = "data_ready"  # Change to your folder path

# Get all files from the folder
all_files = sorted(glob(os.path.join(folder_path, "*.root")))  # Sort to ensure consistent order

df = pd.read_csv("src/offsetF.asc", delimiter=" ", header=0)
db = pd.read_csv("src/offsetB.asc", delimiter=" ", header=0)
dt = pd.read_csv("src/Q_offset.asc", delimiter=" ", header=0)

#Get highest 3 values of array and their indexes
def get_highest_values(new_array_B,new_array_F):
    new_array = []
    for j in range(len(new_array_B)):
        new_array.append((new_array_B[j]+new_array_F[j]))
    new_array_sorted = sorted(new_array,reverse=True)
    return [(new_array_sorted[0],new_array.index(new_array_sorted[0])),(new_array_sorted[1],new_array.index(new_array_sorted[1])),(new_array_sorted[2],new_array.index(new_array_sorted[2]))]

def get_highest_values_two(new_array_B,new_array_F):
    new_array = []
    for j in range(len(new_array_B)):
        new_array.append((new_array_B[j]+new_array_F[j]))
    new_array_sorted = sorted(new_array,reverse=True)
    return [(new_array_sorted[0],new_array.index(new_array_sorted[0])),(new_array_sorted[1],new_array.index(new_array_sorted[1]))]

def get_highest_values_one(new_array_B,new_array_F):
    new_array = []
    for j in range(len(new_array_B)):
        new_array.append((new_array_B[j]+new_array_F[j]))
    new_array_sorted = sorted(new_array,reverse=True)
    return [(new_array_sorted[0],new_array.index(new_array_sorted[0]))]

# Read the tree
def read_tree(tree,concluded):
    for event in range(tree.GetEntries()):
        tree.GetEntry(event)
        if tree.trigger == 1:
            miss = list(tree.n_hits_per_plane).count(0)
            if miss == 1 or miss == 0:
                n_hits_per_plane = list(tree.n_hits_per_plane)
                s = 0
                weighted_coords_s = []
                weighted_coords_t = []
                plane_coords = []
                coords_s = []
                coords_t = []
                for n_hits in n_hits_per_plane:
                    if n_hits == 0:
                        continue
                    original_strips = list(tree.strip)[s:n_hits+s]
                    original_TB = list(tree.TB)[s:n_hits+s]
                    original_TF = list(tree.TF)[s:n_hits+s]
                    original_plane = list(tree.plane)[s:n_hits+s]
                    original_QB = list(tree.QB)[s:n_hits+s]
                    original_QF = list(tree.QF)[s:n_hits+s]
                    s += n_hits

                    new_QB = []
                    new_QF = []
                    for k in range(n_hits):
                        new_QB.append(original_QB[k]-db.loc[original_plane[k]+4*original_strips[k], "OFFSET_PER_STRIP_PER_PLANE"])
                        new_QF.append(original_QF[k]-df.loc[original_plane[k]+4*original_strips[k], "OFFSET_PER_STRIP_PER_PLANE"])

                    if n_hits >= 3:
                        values = get_highest_values(new_QB,new_QF)
                        three_Q = [values[0][0],values[1][0],values[2][0]]
                        three_strips = [original_strips[values[0][1]],original_strips[values[1][1]],original_strips[values[2][1]]]

                        T1 = (original_TB[values[0][1]]-original_TF[values[0][1]])/2 - dt.loc[original_plane[values[0][1]] + original_strips[values[0][1]]*4,"TOFFSET_PER_STRIP_PER_PLANE"]
                        T2 = (original_TB[values[1][1]]-original_TF[values[1][1]])/2 - dt.loc[original_plane[values[1][1]] + original_strips[values[1][1]]*4,"TOFFSET_PER_STRIP_PER_PLANE"]
                        T3 = (original_TB[values[2][1]]-original_TF[values[2][1]])/2 - dt.loc[original_plane[values[2][1]] + original_strips[values[2][1]]*4,"TOFFSET_PER_STRIP_PER_PLANE"]
                        T = [T1,T2,T3]

                        #Weighted mean
                        T_tensor = torch.tensor(T)
                        strips_tensor = torch.tensor(three_strips)
                        Q_tensor = torch.tensor(three_Q)
                        weights = F.softmax(Q_tensor,dim=0)
                        weighted_mean_T = torch.sum(T_tensor*weights)
                        weighted_mean_strip = torch.sum(strips_tensor*weights)
                    
                    if n_hits == 2:
                        values = get_highest_values_two(new_QB,new_QF)
                        two_Q = [values[0][0],values[1][0]]
                        two_strips = [original_strips[values[0][1]],original_strips[values[1][1]]]

                        T1 = (original_TB[values[0][1]]-original_TF[values[0][1]])/2 - dt.loc[original_plane[values[0][1]] + original_strips[values[0][1]]*4,"TOFFSET_PER_STRIP_PER_PLANE"]
                        T2 = (original_TB[values[1][1]]-original_TF[values[1][1]])/2 - dt.loc[original_plane[values[1][1]] + original_strips[values[1][1]]*4,"TOFFSET_PER_STRIP_PER_PLANE"]
                        T = [T1,T2]

                        #Weighted mean
                        T_tensor = torch.tensor(T)
                        strips_tensor = torch.tensor(two_strips)
                        Q_tensor = torch.tensor(two_Q)
                        weights = F.softmax(Q_tensor,dim=0)
                        weighted_mean_T = torch.sum(T_tensor*weights)
                        weighted_mean_strip = torch.sum(strips_tensor*weights)

                    if n_hits == 1:
                        values = get_highest_values_one(new_QB,new_QF)
                        one_Q = [values[0][0]]
                        one_strips = [original_strips[values[0][1]]]

                        T1 = (original_TB[values[0][1]]-original_TF[values[0][1]])/2 - dt.loc[original_plane[values[0][1]] + original_strips[values[0][1]]*4,"TOFFSET_PER_STRIP_PER_PLANE"]
                        T = [T1]

                        #Weighted mean
                        T_tensor = torch.tensor(T)
                        strips_tensor = torch.tensor(one_strips)
                        Q_tensor = torch.tensor(one_Q)
                        weights = F.softmax(Q_tensor,dim=0)
                        weighted_mean_T = torch.sum(T_tensor*weights)
                        weighted_mean_strip = torch.sum(strips_tensor*weights)

                    weighted_coords_s.append(weighted_mean_strip*18)
                    weighted_coords_t.append(weighted_mean_T*165.7+200)
                    plane_coords.append(original_plane[values[0][1]])
                
                if miss == 1:
                    concluded.write(f"{plane_coords[0]} {weighted_coords_t[0]} {weighted_coords_s[0]} {plane_coords[1]} {weighted_coords_t[1]} {weighted_coords_s[1]} {plane_coords[2]} {weighted_coords_t[2]} {weighted_coords_s[2]}\n") 
                if miss == 0:
                    concluded.write(f"{plane_coords[0]} {weighted_coords_t[0]} {weighted_coords_s[0]} {plane_coords[1]} {weighted_coords_t[1]} {weighted_coords_s[1]} {plane_coords[2]} {weighted_coords_t[2]} {weighted_coords_s[2]} {plane_coords[3]} {weighted_coords_t[3]} {weighted_coords_s[3]}\n")

                

# Distribute files among processes
for i in range(rank, len(all_files), size):
    file = ROOT.TFile.Open(all_files[i], "READ")
    tree_to_read = file.Get("sRPCdata")
    print(f"Process {rank} read file: {all_files[i]}")
    with open("coordinates/"+str(all_files[i])[10:-5]+".asc", "w") as concluded:
        read_tree(tree_to_read,concluded)
    file.Close()

if rank == 0:
    folder_path = "coordinates"  # Change to your folder path
    # Get all files from the folder
    # Get all files from the folder
    all_files = sorted(glob(os.path.join(folder_path, "*.asc")))  # Sort to ensure consistent order
    with open("coordinates/coordinates.asc", "w") as concluded:
        concluded.write("plane1 t1 s1 plane2 t2 s2 plane3 t3 s3 plane4 t4 s4\n")
        for i in range(len(all_files)):
            with open(all_files[i], "r") as file:
                for line in file:
                    fields = line.strip().split()
                    if len(fields) >= 9:
                        plane1 = fields[0]
                        t1 = fields[1]
                        s1 = fields[2]
                        plane2 = fields[3]
                        t2 = fields[4]
                        s2 = fields[5]
                        plane3 = fields[6]
                        t3 = fields[7]
                        s3 = fields[8]
                        if len(fields) >= 12:
                            plane4 = fields[9]
                            t4 = fields[10]
                            s4 = fields[11]
                            concluded.write(f"{plane1} {t1} {s1} {plane2} {t2} {s2} {plane3} {t3} {s3} {plane4} {t4} {s4}\n")
                        else:
                            concluded.write(f"{plane1} {t1} {s1} {plane2} {t2} {s2} {plane3} {t3} {s3}\n")
            #os.remove(all_files[i])               