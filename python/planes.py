import os
from glob import glob

import argparse
import tarfile
import time
import datetime

import numpy as np
import ROOT
from array import array
import string

#import torch
#import torch.nn.functional as F
import pandas as pd

ROOT.gROOT.SetBatch(True)

# Specify folder containing files
folder_path = "~/sRPC/coordinates"  # Change to your folder path

canvas = ROOT.TCanvas("canvas", "canvas", 800, 800)
print("after root")
plot1 = ROOT.TH2D(f"plane_1", f"plane_1", 16, 0 , 288,72, 0 ,400)
plot1.GetYaxis().SetTitle("Time x (mm)")
plot1.GetXaxis().SetTitle("Strip y (mm)")
print("after plot1")
plot2 = ROOT.TH2D(f"plane_2", f"plane_2", 16, 0 , 288,72, 0 ,400)
plot2.GetYaxis().SetTitle("Time x (mm)")
plot2.GetXaxis().SetTitle("Strip y (mm)")

plot3 = ROOT.TH2D(f"plane_3", f"plane_3", 16, 0 , 288,72, 0 ,400)
plot3.GetYaxis().SetTitle("Time x (mm)")
plot3.GetXaxis().SetTitle("Strip y (mm)")

plot4 = ROOT.TH2D(f"plane_4", f"plane_4", 16, 0 , 288,72, 0 ,400)
plot4.GetYaxis().SetTitle("Time x (mm)")
plot4.GetXaxis().SetTitle("Strip y (mm)")
print("before function")
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


df = pd.read_csv("coordinates/coordinates.asc", delimiter=" ", header=0)
plane_plot(df)
print("after function")
plot1.Draw("colz")
canvas.SaveAs("n_hits/Plane_1.png")

plot2.Draw("colz")
canvas.SaveAs("n_hits/Plane_2.png")

plot3.Draw("colz")
canvas.SaveAs("n_hits/Plane_3.png")

plot4.Draw("colz")
canvas.SaveAs("n_hits/Plane_4.png")