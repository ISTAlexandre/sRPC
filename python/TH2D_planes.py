import argparse
import tarfile
import os
import time
import datetime

import pandas as pd
import numpy as np
import ROOT
from array import array
ROOT.gROOT.SetBatch(True)

df = pd.read_csv("src/offsetF.asc", delimiter=" ", header=0)
db = pd.read_csv("src/offsetB.asc", delimiter=" ", header=0)
dT = pd.read_csv("src/Q_offset.asc", delimiter=" ", header=0)


parser = argparse.ArgumentParser(prog = "TH2D_planes",
                                 description = "TH2D_planes for .root file")
parser.add_argument("input_file", help = "Input .root file")

args = parser.parse_args()


file = ROOT.TFile.Open(args.input_file, "READ")
tree = file.Get("sRPCdata")

hist1 = ROOT.TH2D("hist1", "2D; X-axis Title ; Y-axis Title ", 16, 0 , 288,72, -200 ,200)
hist2 = ROOT.TH2D("hist2", "2D; X-axis Title ; Y-axis Title ", 16, 0 , 288,72, -200 ,200)
hist3 = ROOT.TH2D("hist3", "2D; X-axis Title ; Y-axis Title ", 16, 0 , 288,72, -200 ,200)
hist4 = ROOT.TH2D("hist4", "2D; X-axis Title ; Y-axis Title ", 16, 0 , 288,72, -200 ,200)

histall = ROOT.TH2D("histall", "2D; X-axis Title ; Y-axis Title ", 16,0,288,200,-300,300)

histall.GetXaxis().SetTitle("Strip y (mm)")
histall.GetYaxis().SetTitle("(TF-TB)/2 x (mm)")
histall.GetZaxis().SetTitle("n_hits")

hist4.GetXaxis().SetTitle("Strip y (mm)")
hist4.GetYaxis().SetTitle("(TF-TB)*v/2 x (mm)")
hist4.GetZaxis().SetTitle("n_hits")

hist1.GetXaxis().SetTitle("Strip y (mm)")
hist1.GetYaxis().SetTitle("(TF-TB)*v/2 x (mm)")
hist1.GetZaxis().SetTitle("n_hits")

hist2.GetXaxis().SetTitle("Strip y (mm)")
hist2.GetYaxis().SetTitle("(TF-TB)*v/2 x (mm)")
hist2.GetZaxis().SetTitle("n_hits")

hist3.GetXaxis().SetTitle("Strip y (mm)")
hist3.GetYaxis().SetTitle("(TF-TB)*v/2 x (mm)")
hist3.GetZaxis().SetTitle("n_hits")

for i in range(tree.GetEntries()):  # Print first 5 elements
    miss = 0
    tree.GetEntry(i)
    if tree.trigger==1:
        miss = list(tree.n_hits_per_plane).count(0)
        if miss == 1 or miss == 0:
            N=0
            actual_N = 0
            for hit in tree.n_hits_per_plane:
                    QF = None
                    QB = None
                    if hit != 0:
                        for k in range(hit):
                            new_QB = tree.QB[N] - db.loc[tree.plane[N] + tree.strip[N]*4,"OFFSET_PER_STRIP_PER_PLANE"]
                            new_QF = tree.QF[N] - df.loc[tree.plane[N] + tree.strip[N]*4,"OFFSET_PER_STRIP_PER_PLANE"]
                            new_Q = (new_QB+new_QF)/2
                            if QF == None or QF < new_QF:
                                QF = new_QF
                                actual_NF = N
                            if QB == None or QB < new_QB:
                                QB = new_QB
                                actual_NB = N
                            N = N + 1
                        if QB < QF:
                            actual_N = actual_NF
                        if QF <= QB:
                            actual_N = actual_NB
                    offsetT = dT.loc[tree.plane[actual_N] + tree.strip[actual_N]*4,"TOFFSET_PER_STRIP_PER_PLANE"]
                    #t = (tree.TB[actual_N]-tree.TF[actual_N])/2
                    t = (tree.TB[actual_N]-tree.TF[actual_N])/2 - offsetT
                    strip = tree.strip[actual_N]
                    if tree.plane[actual_N] == 0:
                        hist1.Fill(strip*18, t*165.7)
                    if tree.plane[actual_N] == 1:
                        hist2.Fill(strip*18, t*165.7)
                    if tree.plane[actual_N] == 2:
                        hist3.Fill(strip*18, t*165.7)
                    if tree.plane[actual_N] == 3:
                        hist4.Fill(strip*18, t*165.7)
                    histall.Fill(strip*18, t*165.7)

hist1.SetTitle("Hits Plane 1 per coordinates")
hist2.SetTitle("Hits Plane 2 per coordinates")
hist3.SetTitle("Hits Plane 3 per coordinates")
hist4.SetTitle("Hits Plane 4 per coordinates")
histall.SetTitle("Hits ALL Plane per coordinates")


hist1.SetStats(0)
hist2.SetStats(0)
hist3.SetStats(0)
hist4.SetStats(0)
histall.SetStats(0)

canvas = ROOT.TCanvas("canvas", "2D Histogram Example", 600, 800)


hist1.Draw("COLZ")

canvas.Draw()
canvas.Update()
canvas.SaveAs("n_hits/P1.png")

hist2.Draw("COLZ")

canvas.Update()
canvas.SaveAs("n_hits/P2.png")

hist3.Draw("COLZ")

canvas.Update()
canvas.SaveAs("n_hits/P3.png")

hist4.Draw("COLZ")

canvas.Update()
canvas.SaveAs("n_hits/P4.png")

histall.Draw("COLZ")

canvas.Update()
canvas.SaveAs("n_hits/all.png")
#canvas.WaitPrimitive()
file.Close()

