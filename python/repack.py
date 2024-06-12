import argparse
import tarfile
import os
import time
import datetime

import numpy as np
import ROOT
from array import array


src = input("File name: ")
src_1 = src[:-5]

file = ROOT.TFile.Open("src/"+src, "READ")
tree = file.Get("sRPCdata")

hist1 = ROOT.TH2D("hist1", "2D; X-axis Title ; Y-axis Title ", 16, 0 , 16,200, -10 ,10)
hist2 = ROOT.TH2D("hist2", "2D; X-axis Title ; Y-axis Title ", 16, 0 , 16,200, -10 ,10)
hist3 = ROOT.TH2D("hist3", "2D; X-axis Title ; Y-axis Title ", 16, 0 , 16,200, -10 ,10)
hist4 = ROOT.TH2D("hist4", "2D; X-axis Title ; Y-axis Title ", 16, 0 , 16,200, -10 ,10)

histall = ROOT.TH2D("histall", "2D; X-axis Title ; Y-axis Title ", 16,0,16,200,-10,10)

for i in range(tree.GetEntries()):  # Print first 5 elements
    a = 0
    tree.GetEntry(i)
    if tree.trigger==1:
        for plane in tree.plane:
            if plane == 0:
                hist1.Fill(tree.strip[a],tree.TF[a]-tree.TB[a])
            if plane == 1:
                hist2.Fill(tree.strip[a],tree.TF[a]-tree.TB[a])
            if plane == 2:
                hist3.Fill(tree.strip[a],tree.TF[a]-tree.TB[a])
            if plane == 3:
                hist4.Fill(tree.strip[a],tree.TF[a]-tree.TB[a])
            a = a + 1

hist1.SetTitle("Hits Plane 1 per coordinates")
hist2.SetTitle("Hits Plane 2 per coordinates")
hist3.SetTitle("Hits Plane 3 per coordinates")
hist4.SetTitle("Hits Plane 4 per coordinates")

hist1.SetStats(0)
hist2.SetStats(0)
hist3.SetStats(0)
hist4.SetStats(0)

canvas = ROOT.TCanvas("canvas", "2D Histogram Example", 800, 600)


hist1.Draw("COLZ")

hist1.GetXaxis().SetTitle("Strip")
hist1.GetYaxis().SetTitle("TF-TB")
hist1.GetZaxis().SetTitle("n_hits")

canvas.Draw()
canvas.Update()
canvas.SaveAs(src_1+".1Plane.png")
canvas.WaitPrimitive()

hist2.Draw("COLZ")

hist2.GetXaxis().SetTitle("Strip")
hist2.GetYaxis().SetTitle("TF-TB")
hist2.GetZaxis().SetTitle("n_hits")

canvas.Update()
canvas.SaveAs(src_1+".2Plane.png")
canvas.WaitPrimitive()

hist3.Draw("COLZ")

hist3.GetXaxis().SetTitle("Strip")
hist3.GetYaxis().SetTitle("TF-TB")
hist3.GetZaxis().SetTitle("n_hits")

canvas.Update()
canvas.SaveAs(src_1+".3Plane.png")
canvas.WaitPrimitive()

hist4.Draw("COLZ")

hist4.GetXaxis().SetTitle("Strip")
hist4.GetYaxis().SetTitle("TF-TB")
hist4.GetZaxis().SetTitle("n_hits")

canvas.Update()
canvas.SaveAs(src_1+".4Plane.png")
canvas.WaitPrimitive()

file.Close()

