import argparse
import tarfile
import os
import time
import datetime
import sys

import pandas as pd
import numpy as np
import ROOT
from array import array
import string
from scipy.special import factorial

def create_cdf(hist):
    num_bins = hist.GetNbinsX() #Bins x 700
    total_entries = hist.GetEntries() #Numero de entradas
    
    cdf_hist = ROOT.TH1D(hist.GetName() + "_cdf", hist.GetTitle() + " CDF", num_bins, 0, 1)
    
    cumulative_sum = 0.0
    for i in range(1, num_bins + 1):
        bin_content = hist.GetBinContent(i) #Entrada
        cumulative_sum += bin_content
        cdf_hist.SetBinContent(i, cumulative_sum / total_entries)
    return cdf_hist    

def intercept_histogram_with_constant(hist, constant_value):
    num_bins = hist.GetNbinsX()
    intersection_points = []

    # Iterate over each bin and check for crossings
    for i in range(1, num_bins + 1):
        bin_center = hist.GetXaxis().GetBinCenter(i)
        hist_value = hist.GetBinContent(i)
        if (hist_value < constant_value and hist.GetBinContent(i + 1) > constant_value) or (hist_value > constant_value and hist.GetBinContent(i + 1) < constant_value):
            # Interpolate to find the x-value where the crossing occurs
            x1 = hist.GetXaxis().GetBinLowEdge(i)
            x2 = hist.GetXaxis().GetBinLowEdge(i + 1)
            y1 = hist_value
            y2 = hist.GetBinContent(i + 1)
            slope = (y2 - y1) / (x2 - x1)
            crossing_x = x1 + (constant_value - y1) / slope
            if (crossing_x <=1 and crossing_x >=0):
                intersection_points.append((crossing_x, constant_value))
            

    return intersection_points

def convert_cdf_to_initial(hist, cdf_value):
    num_bins = hist.GetNbinsX()
    total_entries = hist.GetEntries()
    
    cumulative_sum = 0.0
    for i in range(1, num_bins + 1):
        bin_content = hist.GetBinContent(i)
        cumulative_sum += bin_content / total_entries  # normalize by total entries to get CDF
        if cumulative_sum >= cdf_value:
            # Found the bin where CDF crosses or exceeds the given value
            return hist.GetXaxis().GetBinCenter(i)
        if hist.GetXaxis().GetBinCenter(i) >= hist.GetXaxis().GetXmax():
            return hist.GetXaxis().GetXmax()
    # If CDF value is larger than the maximum CDF of the histogram
    return hist.GetXaxis().GetXmax()

ROOT.gROOT.SetBatch(True)

df = pd.read_csv("src/parameters.asc", delimiter=" ", header=0)
db = pd.read_csv("src/parameters2.asc", delimiter=" ", header=0)
canvas = ROOT.TCanvas("canvas", "2D Histogram Example", 800, 600)
hist1 = ROOT.TH1D("hist", "Angle plane x T", 100,-10,10)
hist2 = ROOT.TH1D("his2", "Angle plane x strip", 100,-10,10)
hist3 = ROOT.TH2D("hist3","Angle Distribution", 100,-10,10,360,-10,10)

reduced_qui_list = []
# Iterate over each element in the DataFrame
for i in range(df.shape[0]):
    slope1 = df.loc[i,"Slope"]
    slope1 = np.arctan(slope1/10)
    hist1.Fill(np.degrees(slope1))

    slope2 = db.loc[i,"Slope"]
    slope2 = np.arctan(slope2/10)
    hist2.Fill(np.degrees(slope2))
    hist3.Fill(np.degrees(slope2),np.degrees(slope1))

hist1.SetMarkerSize(1)
hist2.SetMarkerSize(1)
hist2.SetLineWidth(5)
hist1.SetLineWidth(5)
hist1.SetStats(0)
hist2.SetStats(0)

hist1.Draw("L")
#hist1_back.Draw("SAMEP")
#hist1_front.Draw("SAMEP")
canvas.Draw()
canvas.Update()
canvas.SaveAs("angle/hist1.png")

hist2.Draw("L")

canvas.Update()
canvas.SaveAs("angle/hist2.png")

hist3.Draw("COLZ")

canvas.Update()
canvas.SaveAs("angle/hist3.png")
