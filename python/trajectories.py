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

#start_min = time.time()
ROOT.gROOT.SetBatch(True)

parser = argparse.ArgumentParser(prog = "T_strips",
                                 description = "T_strips for .root file")
parser.add_argument("input_file", help = "Input .root file")

args = parser.parse_args()

lum = pd.read_csv("src/luminosity.csv")
lum['time'] = pd.to_datetime(lum['time'])
lum.set_index('time', inplace=True)

def help(histogram,hist2):
    new_hist = ROOT.TH2D("new_hist", "2D Histogram", 16, 0, 288,72, 0, 400)
    xaxis = histogram.GetXaxis()
    yaxis = histogram.GetYaxis()

    nx = xaxis.GetNbins()
    ny = yaxis.GetNbins()

    sum_ = 0
    _sum = 0
    tuple_dic1 = {}
    tuple_dic2 = {}
    for i in range(1, nx + 1):
        for j in range(1, ny + 1):
            x = histogram.GetXaxis().GetBinCenter(i)
            y = histogram.GetYaxis().GetBinCenter(j)
            z = histogram.GetBinContent(i, j)
            tuple_dic1[(x,y)] = z
    
    xaxis = hist2.GetXaxis()
    yaxis = hist2.GetYaxis()

    nx = xaxis.GetNbins()
    ny = yaxis.GetNbins()

    for i in range(1, nx+ 1):
        for j in range(1, ny + 1):
            x = hist2.GetXaxis().GetBinCenter(i)
            y = hist2.GetYaxis().GetBinCenter(j)
            z = hist2.GetBinContent(i,j)
            tuple_dic2[(x,y)] = z
    for coords in tuple_dic1:
        if coords in tuple_dic2 and tuple_dic1[coords] != 0:
            new_hist.Fill(coords[0],coords[1],1-tuple_dic2[coords]/tuple_dic1[coords])
            sum_ += (1-tuple_dic2[coords]/tuple_dic1[coords])
            _sum += 1
        if coords in tuple_dic2 and tuple_dic1[coords] == 0:
            new_hist.Fill(coords[0],coords[1],0.01)
        if coords not in tuple_dic2 and tuple_dic1[coords] != 0:
            new_hist.Fill(coords[0],coords[1],1)
            sum_ += 1
            _sum += 1
        if coords not in tuple_dic2 and tuple_dic1[coords] == 0:
            continue
    return new_hist, sum_/_sum

list_dic = [{} for _ in range(4)]
list_dic_t = [{} for _ in range(4)]

file = ROOT.TFile.Open(args.input_file, "READ")
tree = file.Get("sRPCdata")
#histograma.SetStats(0)
canvas = ROOT.TCanvas("canvas", "2D Histogram Example", 800, 600)

df = pd.read_csv("src/offsetF.asc", delimiter=" ", header=0)
db = pd.read_csv("src/offsetB.asc", delimiter=" ", header=0)
dt = pd.read_csv("src/Q_offset.asc", delimiter=" ", header=0)

def get_point_coordinates(graph, point_index):
    x_val = array('d', [0])
    y_val = array('d', [0])
    graph.GetPoint(point_index, x_val, y_val)
    return x_val[0], y_val[0]

inshalla = 0

with open("src/parameters.asc", "a") as asc, open("src/parameters2.asc", "a") as asc2:
    graph = ROOT.TGraphErrors()
    graph2 = ROOT.TGraphErrors()
    graph.SetTitle("Coordinates for each hit")
    graph2.SetTitle("Coordinates for each hit")
    graph.GetXaxis().SetLimits(0, 51)
    graph.SetMinimum(0)
    graph.SetMaximum(400)
    graph.SetMarkerSize(10)

    graph2.GetXaxis().SetLimits(0, 51)
    graph2.SetMinimum(0)
    graph2.SetMaximum(288)
    graph2.SetMarkerSize(10)

    graph2.GetXaxis().SetTitle("Plane x (cm)")
    graph2.GetYaxis().SetTitle("strip  y (mm)")

    graph.GetXaxis().SetTitle("Plane x (cm)")
    graph.GetYaxis().SetTitle("(TF-TB)/2*165.7  z (mm)")

    linear_func = ROOT.TF1("linear_func", "[0] + [1]*x", 0, 51)
    linear_func.SetParNames("Intercept", "Slope")

    linear_func2 = ROOT.TF1("linear_func2", "[0] + [1]*x", 0, 51)
    linear_func2.SetParNames("Intercept", "Slope")

    miss_list = [0,0,0,0]
    total_list = [0,0,0,0]

    for event in range(tree.GetEntries()):
        tree.GetEntry(event)
        plane_coordinates = []
        if tree.trigger==1:
            miss = list(tree.n_hits_per_plane).count(0)
            if miss == 1 or miss == 0:
                graph.SetTitle("Coordinates for each hit")
                graph2.SetTitle("Coordinates for each hit")
                N=0
                actual_N = 0
                for hit in tree.n_hits_per_plane:
                    QF = None
                    QB = None
                    Q = None
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
                        '''
                        if Q == None or Q < new_Q:
                            Q = new_Q
                            actual_N = N
                        '''
                        N += 1
                    if QB  == None or QF == None:
                        continue
                    if QB < QF:
                        actual_N = actual_NF
                    if QF <= QB:
                        actual_N = actual_NB
                    point_index = graph.GetN()
                    offset = dt.loc[tree.plane[actual_N] + tree.strip[actual_N]*4,"TOFFSET_PER_STRIP_PER_PLANE"]
                    timet = (tree.TB[actual_N]-tree.TF[actual_N])/2-offset
                    
                    if timet*165.7 < -200 and timet*165.7 > 200:
                        continue

                    graph.SetPoint(point_index,tree.plane[actual_N]*17,timet*165.7+200)
                    graph2.SetPoint(point_index,tree.plane[actual_N]*17,tree.strip[actual_N]*18)
                    graph2.SetPointError(point_index,0,9)
                    plane_coordinates.append(tree.plane[actual_N])
                if graph.GetN() > 4:
                    raise ValueError("MAIS DO QUE 4 VALORES")
                if graph.GetN() > 2:
                    inshalla +=1

                    graph.Draw("AP")

                    graph.Fit(linear_func, "Q","",0,51)
                    linear_func.Draw("SAME")

                    intercept = linear_func.GetParameter(0)
                    slope = linear_func.GetParameter(1)
                    intercept_error = linear_func.GetParError(0)
                    slope_error = linear_func.GetParError(1)

                    canvas.Draw()
                    canvas.Update()
                    
                    time_intercept = intercept
                    time_slope = slope
                    time_intercept_error = intercept_error
                    time_slope_error= slope_error

                    graph2.Draw("AP")
                    
                    graph2.Fit(linear_func2, "Q","",0,51)
                    linear_func2.Draw("SAME")

                    #print(reduced_chi_squared2)

                    intercept = linear_func2.GetParameter(0)
                    slope = linear_func2.GetParameter(1)
                    intercept_error = linear_func2.GetParError(0)
                    slope_error = linear_func2.GetParError(1)
                    
                    canvas.Update()

                    strip_intercept = intercept
                    strip_slope = slope
                    strip_intercept_error = intercept_error
                    strip_slope_error = slope_error

                    #if 0<= strip_intercept <= 288 and 0 <= time_intercept <=400 and 0 <= strip_intercept + 51*strip_slope <= 288 and 0 <= time_intercept + 51*time_slope<=400:
                    asc2.write(f"{strip_intercept} {strip_slope} {strip_intercept_error} {strip_slope_error}\n")
                    asc.write(f"{time_intercept} {time_slope} {time_intercept_error} {time_slope_error}\n")
                    if graph.GetN() == 3:
                        for t in range(4):
                            if t not in plane_coordinates:
                                plane_miss = t
                        
                        strip_miss = plane_miss*17*strip_slope+strip_intercept
                        time_miss = plane_miss*17*time_slope+time_intercept

                        strip_miss = round(strip_miss,2)
                        time_miss = round(time_miss,2)

                        miss_list[plane_miss] += 1
                        #graph.SetPoint(4,plane_miss*17,time_coords)
                        #graph2.SetPoint(4,plane_miss*17,strip_coords)
                        if (strip_miss,time_miss) not in list_dic[plane_miss]:
                            list_dic[plane_miss][(strip_miss,time_miss)] = 1
                        if (strip_miss,time_miss) in list_dic[plane_miss]:
                            list_dic[plane_miss][(strip_miss,time_miss)] += 1
                    '''
                    for plane in range(4):
                        x_coord, t_coord = get_point_coordinates(graph, plane)
                        y_coord, s_coord = get_point_coordinates(graph2, plane)
                        strip = int(s_coord/18)
                        ttime = int(t_coord/(600/108))
                        total_list[plane][ttime,strip] +=1
                    '''        
                    for plane in range(4):
                        strip = plane*strip_slope*17+strip_intercept
                        ttime = plane*time_slope*17+time_intercept

                        strip = round(strip,2)
                        ttime = round(ttime,2)
                        total_list[plane] += 1    

                        if (strip,ttime) not in list_dic_t[plane]:
                            list_dic_t[plane][(strip,ttime)] = 1
                        if (strip,ttime) in list_dic_t[plane]:
                            list_dic_t[plane][(strip,ttime)] += 1
                graph.Set(0)
                graph2.Set(0)
                    

eff_list = []
for i in range(4):
    ehist1 = ROOT.TH2D("ehist1", "2D Histogram", 16, 0, 288,72, 0, 400)
    ehist2 = ROOT.TH2D("ehist2", "2D Histogram", 16, 0, 288,72, 0, 400)
    for square in list_dic_t[i]:
        ehist1.Fill(square[0],square[1],list_dic_t[i][square])
        if square in list_dic[i]:
            ehist2.Fill(square[0],square[1],list_dic[i][square])
            
    new_hist, eff = help(ehist1,ehist2)
    eff_list.append(eff)
    ehist1.Draw("COLZ")
    canvas.Update()
    canvas.SaveAs("efficiency/T"+str(i)+".png")
    ehist2.Draw("COLZ")
    canvas.Update()
    canvas.SaveAs("efficiency/M"+str(i)+".png")
    new_hist.Draw("COLZ")
    canvas.Update()
    canvas.SaveAs("efficiency/E"+str(i)+".png")

denominador =eff_list[0]*eff_list[1]*eff_list[2]+eff_list[0]*eff_list[1]*eff_list[3]+eff_list[0]*eff_list[2]*eff_list[3]+eff_list[1]*eff_list[2]*eff_list[3]-3*eff_list[0]*eff_list[1]*eff_list[2]*eff_list[3]

Area = 900

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
start_time = datetime.datetime(year, month, day, hour, minute, second)

# Format the datetime object as a string
formatted_time = start_time.strftime("%Y-%m-%d %H:%M:%S")

start_time = pd.Timestamp(formatted_time)
end_time = start_time + pd.Timedelta(minutes=tempo//60)
start_time2 = start_time.round('min')
end_time2 = end_time.round('min')

filtered_lum = lum.loc[start_time2:end_time2]
int1 = filtered_lum['Lum'].iloc[0]*(60-start_time.second)
int2 = filtered_lum['Lum'].iloc[1]*(tempo-60+start_time.second)

integrated_luminosity_ratio = int1 + int2

rc = inshalla/(Area*denominador*integrated_luminosity_ratio) *10**9

with open("src/flux.asc", 'a') as asc:
    asc.write(f"{rc} {inshalla} {tempo} {integrated_luminosity_ratio} {args.input_file} {eff_list[0]} {eff_list[1]} {eff_list[2]} {eff_list[3]} {denominador} \n")

#end_min = time.time()
#print((end_min-start_min)//60)

print(1-miss_list[0]/total_list[0])
print(1-miss_list[1]/total_list[1])
print(1-miss_list[2]/total_list[2])
print(1-miss_list[3]/total_list[3])
file.Close()