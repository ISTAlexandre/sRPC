import argparse
import tarfile
import os
import time
import datetime

import pandas as pd
import numpy as np
import ROOT
from array import array
import string

parser = argparse.ArgumentParser(prog = "T_strips",
                                 description = "T_strips for .root file")
parser.add_argument("input_file", help = "Input .root file")

args = parser.parse_args()

list_dic = [{} for _ in range(4)]
list_dic_t = [{} for _ in range(4)]

file = ROOT.TFile.Open(args.input_file, "READ")
tree = file.Get("sRPCdata")

df = pd.read_csv("src/offsetF.asc", delimiter=" ", header=0)
db = pd.read_csv("src/offsetB.asc", delimiter=" ", header=0)
dt = pd.read_csv("src/Q_offset.asc", delimiter=" ", header=0)

canvas = ROOT.TCanvas("canvas", "1D tupleogram Example", 800, 600)
c = 29.9792
main_list = [[] for _ in range(256)]

for event in range(tree.GetEntries()):
        tree.GetEntry(event)
        if tree.trigger==1:
            miss = list(tree.n_hits_per_plane).count(0)
            if miss == 0:
                N=0
                tempo_list = []
                p_charge = [[],[],[],[]]
                sorted_p_charge = []
                min_hit = None
                for hit in tree.n_hits_per_plane:
                    if min_hit == None or min_hit > hit:
                        min_hit = hit
                    QF = None
                    QB = None
                    Q = None
                    if hit != 0:
                        for k in range(hit):
                            new_QB = tree.QB[N] - db.loc[tree.plane[N] + tree.strip[N]*4,"OFFSET_PER_STRIP_PER_PLANE"]
                            new_QF = tree.QF[N] - df.loc[tree.plane[N] + tree.strip[N]*4,"OFFSET_PER_STRIP_PER_PLANE"]
                            new_Q = (new_QB+new_QF)/2
                            p_charge[tree.plane[N]].append((new_Q,(tree.TB[N]+tree.TF[N])/2,tree.strip[N]))
                            N += 1
                for s in range(4):
                    sorted_p = sorted(p_charge[s], key=lambda x: x[0], reverse=True)
                    sorted_p_charge.append(sorted_p)
                for k in range(min_hit):
                    main_list[sorted_p_charge[0][k][2]+16*sorted_p_charge[3][k][2]].append(sorted_p_charge[3][k][1]-sorted_p_charge[0][k][1])

for i in range(len(main_list)):
    hist = ROOT.TH1D("hist","time",50,-50,250)
    for k in range(len(main_list[i])):
        hist.Fill(main_list[i][k]*c)
    hist.SetMarkerSize(10)
    hist.Draw("P")
    canvas.Draw()
    canvas.Update()
    canvas.SaveAs("offset/time/"+str(i)+".png")




    

    