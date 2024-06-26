import argparse
import tarfile
import os
import time
import datetime

from itertools import combinations
import math
from ctypes import c_double
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

    tuple_dic1 = {}
    tuple_dic2 = {}
    for i in range(1, histogram.GetNbinsX() + 1):
        for j in range(1, histogram.GetNbinsY() + 1):
            x = histogram.GetXaxis().GetBinCenter(i)
            y = histogram.GetYaxis().GetBinCenter(j)
            z = histogram.GetBinContent(i, j)
            tuple_dic1[(x,y)] = z

    for i in range(1, hist2.GetNbinsX() + 1):
        for j in range(1, hist2.GetNbinsY() + 1):
            x = hist2.GetXaxis().GetBinCenter(i)
            y = hist2.GetYaxis().GetBinCenter(j)
            z = hist2.GetBinContent(i,j)
            tuple_dic2[(x,y)] = z
    for coords in tuple_dic2:
        if tuple_dic2[coords] !=0:
            new_hist.Fill(coords[0],coords[1],tuple_dic1[coords]/tuple_dic2[coords])
        #if coords not in tuple_dic1:
            #print("ERROR")
    return new_hist

list_dic = [{} for _ in range(4)]
list_dic_t = [{} for _ in range(4)]

file = ROOT.TFile.Open(args.input_file, "READ")
tree = file.Get("sRPCdata")
#histograma.SetStats(0)
canvas = ROOT.TCanvas("canvas", "2D Histogram Example", 600, 800)

df = pd.read_csv("src/offsetF.asc", delimiter=" ", header=0)
db = pd.read_csv("src/offsetB.asc", delimiter=" ", header=0)
dt = pd.read_csv("src/Q_offset.asc", delimiter=" ", header=0)

def get_point_coordinates(graph, point_index):
    x_val = array('d', [0])
    y_val = array('d', [0])
    graph.GetPoint(point_index, x_val, y_val)
    return x_val[0], y_val[0]

contagem = 0

with open("src/parameters.asc", "w") as asc, open("src/parameters2.asc", "w") as asc2:
    asc2.write(f"Intercept Slope Intercept_Error Slope_Error Reduced_CHI Get_N\n")
    asc.write(f"Intercept Slope Intercept_Error Slope_Error Reduced_CHI Get_N\n")

    graph = ROOT.TGraph()
    graph2 = ROOT.TGraphErrors()
    graph.SetTitle("Coordinates for each hit")
    graph2.SetTitle("Coordinates for each hit")
    graph.GetXaxis().SetLimits(0, 51)
    graph.SetMinimum(0)
    graph.SetMaximum(400)
    graph.SetMarkerSize(1)
    graph.SetMarkerStyle(20)

    graph_temp = ROOT.TGraph()
    graph2_temp = ROOT.TGraphErrors()
    graph_temp.SetTitle("Coordinates for each hit")
    graph2_temp.SetTitle("Coordinates for each hit")

    graph_temp.GetXaxis().SetRangeUser(0, 51)
    graph_temp.SetMinimum(0)
    graph_temp.SetMaximum(400)
    graph_temp.SetMarkerSize(1)
    graph_temp.SetLineWidth(1)
    graph_temp.SetMarkerStyle(20)

    graph2_temp.GetXaxis().SetRangeUser(0, 51)
    graph2_temp.SetMinimum(0)
    graph2_temp.SetMaximum(288)
    graph2_temp.SetMarkerSize(1)
    graph2_temp.SetLineWidth(10)
    graph2_temp.SetMarkerStyle(20)

    graph2.GetXaxis().SetLimits(0, 51)
    graph2.SetMinimum(0)
    graph2.SetMaximum(288)
    graph2.SetMarkerSize(1)
    graph2.SetMarkerStyle(20)

    graph2.GetXaxis().SetTitle("Plane z (cm)")
    graph2.GetYaxis().SetTitle("strip  y (mm)")

    graph.GetXaxis().SetTitle("Plane z (cm)")
    graph.GetYaxis().SetTitle("(TF-TB)/2*165.7  x (mm)")

    graph2_temp.GetXaxis().SetTitle("Plane z (cm)")
    graph2_temp.GetYaxis().SetTitle("strip  y (mm)")

    graph_temp.GetXaxis().SetTitle("Plane z (cm)")
    graph_temp.GetYaxis().SetTitle("(TF-TB)/2*165.7  x (mm)")

    linear_func = ROOT.TF1("linear_func", "[0] + [1]*x", 0, 51)
    linear_func.SetParNames("Intercept", "Slope")

    linear_func2 = ROOT.TF1("linear_func2", "[0] + [1]*x", 0, 51)
    linear_func2.SetParNames("Intercept", "Slope")

    miss_list = [0,0,0,0]
    total_list = [0,0,0,0]

    planes_list = [0,1,2,3]
    planes_combinations = list(combinations(planes_list, 3))

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
                    graph2.SetPointError(point_index,0,18/math.sqrt(12))
                    plane_coordinates.append(tree.plane[actual_N])
                if graph.GetN() > 2:
                    contagem +=1
                    if graph.GetN() == 4:
                        for plane in range(4):
                            total_list[plane] += 1    
                            miss_list[plane] += 1
                        for combination in planes_combinations:
                            plane_coordinates2 = []
                            for plane in combination:
                                point_index = graph_temp.GetN()

                                x_val, y_val = c_double(0) , c_double(0)
                                graph.GetPoint(plane, x_val, y_val)
                                graph_temp.SetPoint(point_index, x_val, y_val)

                                x_val, y_val = c_double(0) , c_double(0)
                                graph2.GetPoint(plane, x_val, y_val)
                                graph2_temp.SetPoint(point_index, x_val, y_val)
                                graph2_temp.SetPointError(point_index,0,18/math.sqrt(12))

                                plane_coordinates2.append(int(x_val.value//17))

                            for t in range(4):
                                if t not in plane_coordinates2:
                                    plane_miss = t
                            
                            graph_temp.Draw("AP")

                            graph_temp.Fit(linear_func, "Q","",0,51)
                            linear_func.Draw("SAME")
                            graph_temp.GetXaxis().SetLimits(0, 51)

                            chi1 = linear_func.GetChisquare()
                            ndf = linear_func.GetNDF()
                            reduced_chi1 = chi1/ndf

                            intercept = linear_func.GetParameter(0)
                            slope = linear_func.GetParameter(1)
                            intercept_error = linear_func.GetParError(0)
                            slope_error = linear_func.GetParError(1)

                            canvas.Update()
                            canvas.Draw()
                        
                            time_intercept = intercept
                            time_slope = slope
                            time_intercept_error = intercept_error
                            time_slope_error= slope_error

                            graph2_temp.Draw("AP")
                    
                            graph2_temp.Fit(linear_func2, "Q","",0,51)
                            linear_func2.Draw("SAME")
                            graph2_temp.GetXaxis().SetLimits(0, 51)

                            chi2 = linear_func2.GetChisquare()
                            ndf = linear_func2.GetNDF()
                            reduced_chi2 = chi2/ndf

                            intercept = linear_func2.GetParameter(0)
                            slope = linear_func2.GetParameter(1)
                            intercept_error = linear_func2.GetParError(0)
                            slope_error = linear_func2.GetParError(1)
                            
                            canvas.Update()

                            strip_intercept = intercept
                            strip_slope = slope
                            strip_intercept_error = intercept_error
                            strip_slope_error = slope_error

                            asc2.write(f"{strip_intercept} {strip_slope} {strip_intercept_error} {strip_slope_error} {reduced_chi2} {graph.GetN()}\n")
                            asc.write(f"{time_intercept} {time_slope} {time_intercept_error} {time_slope_error} {reduced_chi1} {graph.GetN()}\n")
                            
                            #if reduced_chi1 < 1000 and reduced_chi2 < 1000:
                            
                            strip_miss = plane_miss*17*strip_slope+strip_intercept
                            time_miss = plane_miss*17*time_slope+time_intercept

                            strip_miss = round(strip_miss,2)
                            time_miss = round(time_miss,2)

                            if (strip_miss,time_miss) not in list_dic[plane_miss]:
                                list_dic[plane_miss][(strip_miss,time_miss)] = 1
                            if (strip_miss,time_miss) in list_dic[plane_miss]:
                                list_dic[plane_miss][(strip_miss,time_miss)] += 1

                            if (strip_miss,time_miss) not in list_dic_t[plane_miss]:
                                list_dic_t[plane_miss][(strip_miss,time_miss)] = 1
                            if (strip_miss,time_miss) in list_dic_t[plane_miss]:
                                list_dic_t[plane_miss][(strip_miss,time_miss)] += 1
                            
                            graph_temp.Set(0)
                            graph2_temp.Set(0)

                            
                    if graph.GetN() == 3:
                        for t in range(4):
                            if t not in plane_coordinates:
                                plane_miss = t
                        miss_list[plane_miss] += 1

                        graph.Draw("AP")

                        graph.Fit(linear_func, "Q","",0,51)
                        linear_func.Draw("SAME")
                        
                        chi1 = linear_func.GetChisquare()
                        ndf = linear_func.GetNDF()
                        reduced_chi1 = chi1/ndf

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

                        chi2 = linear_func2.GetChisquare()
                        ndf = linear_func2.GetNDF()
                        reduced_chi2 = chi2/ndf

                        intercept = linear_func2.GetParameter(0)
                        slope = linear_func2.GetParameter(1)
                        intercept_error = linear_func2.GetParError(0)
                        slope_error = linear_func2.GetParError(1)
                        
                        canvas.Update()

                        strip_intercept = intercept
                        strip_slope = slope
                        strip_intercept_error = intercept_error
                        strip_slope_error = slope_error

                        asc2.write(f"{strip_intercept} {strip_slope} {strip_intercept_error} {strip_slope_error} {reduced_chi2} {graph.GetN()}\n")
                        asc.write(f"{time_intercept} {time_slope} {time_intercept_error} {time_slope_error} {reduced_chi1} {graph.GetN()}\n")

                        #if reduced_chi1 < 1000 and reduced_chi2 < 1000:
                            
                        strip_miss = plane_miss*17*strip_slope+strip_intercept
                        time_miss = plane_miss*17*time_slope+time_intercept

                        strip_miss = round(strip_miss,2)
                        time_miss = round(time_miss,2)

                        if (strip_miss,time_miss) not in list_dic[plane_miss]:
                            list_dic[plane_miss][(strip_miss,time_miss)] = 1
                        if (strip_miss,time_miss) in list_dic[plane_miss]:
                            list_dic[plane_miss][(strip_miss,time_miss)] += 1

                graph.Set(0)
                graph2.Set(0)
                    
a = total_list[0]/miss_list[0]
b = total_list[1]/miss_list[1]
c = total_list[2]/miss_list[2]
d = total_list[3]/miss_list[3]

eff_list = [float(a),float(b),float(c),float(d)]
for i in range(4):
    ehist1 = ROOT.TH2D("ehist1", "2D Histogram", 16, 0, 288,72, 0, 400)
    ehist2 = ROOT.TH2D("ehist2", "2D Histogram", 16, 0, 288,72, 0, 400)
    for square in list_dic_t[i]:
        ehist1.Fill(square[0],square[1],list_dic_t[i][square])
    for square in list_dic[i]:
        ehist2.Fill(square[0],square[1],list_dic[i][square])
            
    new_hist = help(ehist1,ehist2)
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
start_time = datetime.datetime(year, month, day, hour-1, minute, second)

# Format the datetime object as a string
formatted_time = start_time.strftime("%Y-%m-%d %H:%M:%S")

start_time = pd.Timestamp(formatted_time)
end_time = start_time + pd.Timedelta(minutes=tempo/60)
start_time2 = start_time.floor('min')
end_time2 = end_time.floor('min')

filtered_lum = lum.loc[start_time2:end_time2]
integrated_luminosity_ratio = 0
for i in range(len(filtered_lum["Lum"])):
    if i == 0:
        il = filtered_lum["Lum"].iloc[i]*(60-start_time.second)
    if i == len(filtered_lum["Lum"]) -1:
        il = filtered_lum["Lum"].iloc[i]*(end_time.second)
    if i != 0 and i != len(filtered_lum["Lum"]) -1:
        il = filtered_lum["Lum"].iloc[i]*60
    integrated_luminosity_ratio += il


rc = contagem/(Area*denominador*integrated_luminosity_ratio) *10**9

with open("src/flux.asc", 'a') as asc:
    asc.write(f"{rc} {contagem} {tempo} {integrated_luminosity_ratio} {args.input_file} {eff_list[0]} {eff_list[1]} {eff_list[2]} {eff_list[3]} {denominador}\n")

#end_min = time.time()
#print((end_min-start_min)//60)

file.Close()
