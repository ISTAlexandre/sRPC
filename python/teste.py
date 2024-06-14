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

lum = pd.read_csv("src/luminosity.csv")
lum['time'] = pd.to_datetime(lum['time'])
lum.set_index('time', inplace=True)

n_tree_entries = tree.GetEntries()
tree.GetEntry(0)
inicio = tree.year*3.154e+7+tree.month*2.628e+6+tree.day*86400+tree.hour*3600+tree.minute*60+tree.second
tree.GetEntry(n_tree_entries-1)
fim = tree.year*3.154e+7+tree.month*2.628e+6+tree.day*86400+tree.hour*3600+tree.minute*60+tree.second
tempo = fim - inicio

year = int(args.input_file[15:17]) + 2000  # Assuming '24' means 2024
day_of_year = int(args.input_file[17:20])
hour = int(args.input_file[20:22])
minute = int(args.input_file[22:24])
second = int(args.input_file[24:26])

# Convert day of the year to month and day
start_date = datetime.datetime(year, 1, 1) + datetime.timedelta(days=day_of_year - 1)
month = start_date.month
day = start_date.day

# Create the datetime object
start_time = datetime.datetime(year, month, day, hour-1, minute, second)

# Format the datetime object as a string
formatted_time = start_time.strftime("%Y-%m-%d %H:%M:%S")

start_time = pd.Timestamp(formatted_time)
end_time = start_time + pd.Timedelta(minutes=tempo/60)
start_time2 = start_time.floor('min')
end_time2 = end_time.floor('min')

print(start_time)
print(end_time)
filtered_lum = lum.loc[start_time2:end_time2]
integrated = 0
for i in range(len(filtered_lum["Lum"])):
    if i == 0:
        il = filtered_lum["Lum"].iloc[i]*(60-start_time.second)
    if i == len(filtered_lum["Lum"]) -1:
        il = filtered_lum["Lum"].iloc[i]*(end_time.second)
    if i != 0 and i != len(filtered_lum["Lum"]) -1:
        il = filtered_lum["Lum"].iloc[i]*60
    integrated += il
print(tempo)
print(filtered_lum)
print(integrated)
