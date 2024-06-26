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

file = ROOT.TFile.Open(args.input_file, "READ")
tree = file.Get("sRPCdata")

tree.GetEntry(106)

df = pd.read_csv("src/offsetF.asc", delimiter=" ", header=0)
db = pd.read_csv("src/offsetB.asc", delimiter=" ", header=0)
N = 0
QB = []
QF = []
print(list(tree.n_hits_per_plane))
print(list(tree.strip))

for hit in tree.n_hits_per_plane:
    for k in range(hit):
        new_QB = tree.QB[N] - db.loc[tree.plane[N] + tree.strip[N]*4,"OFFSET_PER_STRIP_PER_PLANE"]
        new_QF = tree.QF[N] - df.loc[tree.plane[N] + tree.strip[N]*4,"OFFSET_PER_STRIP_PER_PLANE"]
        new_Q = (new_QB+new_QF)/2
        QB.append(new_QB)
        QF.append(new_QF)
        N += 1

print(QB)
print(QF)