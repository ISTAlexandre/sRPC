import argparse
import tarfile
import os
import time
import datetime

import numpy as np
import ROOT
from array import array
import string

#start_time = time.time()
ROOT.gROOT.SetBatch(True)
start_time = time.time()
parser = argparse.ArgumentParser(prog = "TH2D_planes",
                                 description = "TH2D_planes for .root file")
parser.add_argument("input_file", help = "Input .root file")

args = parser.parse_args()


file = ROOT.TFile.Open(args.input_file, "READ")
tree = file.Get("sRPCdata")

canvas = ROOT.TCanvas("canvas", "1D tupleogram Example", 800, 600)

all_tuple = [[] for _ in range(64)]
all_tuple2 = [[] for _ in range(64)]
all_tuple_TB = [[] for _ in range(64)]
all_tuple_TF = [[] for _ in range(64)]

def create_cdf(hist,cdf_hist):
    num_bins = hist.GetNbinsX() #Bins x 700
    total_entries = hist.GetEntries() #Numero de entradas
    
    cdf_hist.SetName(hist.GetName()+"_cdf")
    cdf_hist.SetTitle(hist.GetTitle()+" CDF")
    cdf_hist.SetBins(num_bins,0,1)
    
    cumulative_sum = 0.0
    for i in range(1, num_bins + 1):
        bin_content = hist.GetBinContent(i) #Entrada
        cumulative_sum += bin_content
        cdf_hist.SetBinContent(i, cumulative_sum / total_entries)
    
    return cdf_hist        

def get_max_point(graph):
    max_x = None
    max_y = None
    max_index = -1

    for i in range(graph.GetN()):
        x = graph.GetX()[i]
        y = graph.GetY()[i]
        #graph.GetPoint(i, x, y)
        if max_y is None or y > max_y:
            max_x = x
            max_y = y
            max_index = i

    return max_x

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

def get_max_bin_values(hist):
    num_bins = hist.GetNbinsX()
    max_bin_content = -1
    max_bin_x = 0

    for i in range(1, num_bins + 1):
        bin_content = hist.GetBinContent(i)
        if bin_content > max_bin_content:
            max_bin_content = bin_content
            max_bin_x = hist.GetXaxis().GetBinCenter(i)

    return max_bin_x

def get_max_bin_entries(hist):
    num_bins = hist.GetNbinsX()
    max_bin_entries = -1

    for i in range(1,1+num_bins):
        bin_entries = hist.GetBinContent(i)
        if bin_entries > max_bin_entries:
            max_bin_entries = bin_entries

    return max_bin_entries

def mega(hist,threshold):
    num_bins = hist.GetNbinsX()
    first = False
    for i in  range(1,1+num_bins):
        bin_entries = hist.GetBinContent(i)
        if bin_entries < threshold and first == True:
            second_x = hist.GetXaxis().GetBinCenter(i)
        if bin_entries > threshold and first == False:
            first = True
            first_x = hist.GetXaxis().GetBinCenter(i)
    media = (first_x + second_x)/2
    return media

def intercept_histogram_with_constant(hist, constant_value,flag):
    num_bins = hist.GetNbinsX()
    intersection_points = []
    maximum = get_max_bin_entries(hist)

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
            if (crossing_x <=2 and crossing_x >=-3.5) and flag==True:
                intersection_points.append((crossing_x, constant_value))
            if (crossing_x <=maximum+50 and crossing_x >=0) and flag==False:
                intersection_points.append((crossing_x, constant_value))

    return intersection_points

for event in range(tree.GetEntries()):
    tree.GetEntry(event)
    if tree.trigger==1:
        miss = list(tree.n_hits_per_plane).count(0)
        if miss == 1 or miss == 0:
            for index_plane in range(len(tree.plane)):
                if 0 < abs(tree.QB[index_plane]) < 700:
                    all_tuple[tree.strip[index_plane]*4+tree.plane[index_plane]].append(abs(tree.QB[index_plane]))
                if 0 < abs(tree.QF[index_plane]) < 700:
                    all_tuple2[tree.strip[index_plane]*4+tree.plane[index_plane]].append(abs(tree.QF[index_plane]))
                if tree.TB[index_plane] == 0 or tree.TF[index_plane] == 0:
                    continue
                all_tuple_TF[tree.strip[index_plane]*4+tree.plane[index_plane]].append(abs(tree.TB[index_plane]))
                all_tuple_TB[tree.strip[index_plane]*4+tree.plane[index_plane]].append(abs(tree.TF[index_plane]))


linear_func = ROOT.TF1("linear_func","x",0,1)

tuple_index = 1

hist1 = ROOT.TH1F("hist1","QB"+ str(tuple_index), 700,0,700)
hist1.SetLineWidth(3)

cdf_hist = ROOT.TH1D(hist1.GetName() + "_cdf", hist1.GetTitle() + " CDF", 700, 0, 1)
cdf_hist.SetLineWidth(3)

graph1 = ROOT.TGraph()
graph1.GetXaxis().SetLimits(0, 1)
graph1.SetMinimum(0)
graph1.SetMaximum(1)
graph1.SetLineWidth(3)

with open("src/offsetB.asc", "w") as asc:
    asc.write(f"OFFSET_PER_STRIP_PER_PLANE\n")

    for n_tuple in all_tuple:

        for Q in n_tuple:
            hist1.Fill(Q)

        hist1.SetTitle("QB"+ str(tuple_index))
        hist1.GetXaxis().SetRangeUser(min(n_tuple),max(n_tuple))

        hist1.Draw("L")
        canvas.Draw()
        canvas.Update()
        canvas.SaveAs("offset/QStrips/B/"+ str(tuple_index)+".png")

        cdf_hist = create_cdf(hist1,cdf_hist)

        cdf_hist.Draw("L")
        linear_func.Draw("SAME")
      
        canvas.Update()
        canvas.SaveAs("offset/CDF/B/"+ str(tuple_index)+".png")
    
        # Create a TGraph to store the points

        for i in range(1, cdf_hist.GetNbinsX() + 1):
            bin_content = cdf_hist.GetBinContent(i)
            x_value = cdf_hist.GetXaxis().GetBinCenter(i)
            y_value = bin_content
            
            # Calculate distance from y = x line
            distance = y_value - x_value
            
            point_index = graph1.GetN()
            graph1.SetPoint(point_index, x_value, abs(distance))

        # Plot the points

        graph1.Draw("AL")

        canvas.Update()

        canvas.SaveAs("offset/X-CDF/B/"+ str(tuple_index)+".png")

        e_offset = get_max_point(graph1)
        initial_offset = convert_cdf_to_initial(hist1,e_offset)
        asc.write(f"{initial_offset}\n")

        tuple_index += 1
        
        graph1.Set(0)
        hist1.Reset()
        cdf_hist.Reset()

tuple_index = 1

hist1 = ROOT.TH1F("hist1","QF"+ str(tuple_index), 700,0,700)
hist1.SetLineWidth(3)

cdf_hist = ROOT.TH1D(hist1.GetName() + "_cdf", hist1.GetTitle() + " CDF", 700, 0, 1)
cdf_hist.SetLineWidth(3)

graph1 = ROOT.TGraph()
graph1.GetXaxis().SetLimits(0, 1)
graph1.SetMinimum(0)
graph1.SetMaximum(1)
graph1.SetLineWidth(3)

with open("src/offsetF.asc", "w") as asc:
    asc.write(f"OFFSET_PER_STRIP_PER_PLANE\n")

    for n_tuple in all_tuple2:

        for Q in n_tuple:
            hist1.Fill(Q)

        hist1.SetTitle("QF"+ str(tuple_index))
        hist1.GetXaxis().SetRangeUser(min(n_tuple),max(n_tuple))

        hist1.Draw("L")
        canvas.Update()
        canvas.SaveAs("offset/QStrips/F/"+ str(tuple_index)+".png")

        cdf_hist = create_cdf(hist1,cdf_hist)

        cdf_hist.Draw("L")
        linear_func.Draw("SAME")

        canvas.Update()
        canvas.SaveAs("offset/CDF/F/"+ str(tuple_index)+".png")

        for i in range(1, cdf_hist.GetNbinsX() + 1):
            bin_content = cdf_hist.GetBinContent(i)
            x_value = cdf_hist.GetXaxis().GetBinCenter(i)
            y_value = bin_content
            
            # Calculate distance from y = x line
            distance = y_value - x_value
            
            point_index = graph1.GetN()
            graph1.SetPoint(point_index, x_value, abs(distance))

        # Plot the points

        graph1.Draw("AL")

        canvas.Update()

        canvas.SaveAs("offset/X-CDF/F/"+ str(tuple_index)+".png")

        e_offset = get_max_point(graph1)
        initial_offset = convert_cdf_to_initial(hist1,e_offset)
        asc.write(f"{initial_offset}\n")

        graph1.Set(0)
        hist1.Reset()
        tuple_index += 1
        cdf_hist.Reset()

with open("src/Q_offset.asc", "w") as asc:
    asc.write(f"TOFFSET_PER_STRIP_PER_PLANE OTHER_TIME\n")
    hist = ROOT.TH1D("hist","(TB-TF)/2",400,-10,10)
    hist.SetLineWidth(3)

    for tuple_index in range(len(all_tuple_TF)):

        for Q_index in range(len(all_tuple_TF[tuple_index])):
            hist.Fill((all_tuple_TB[tuple_index][Q_index]-all_tuple_TF[tuple_index][Q_index])/2)

        n_entries_max = get_max_bin_entries(hist)
        threshold = ROOT.TF1("threshold",str(n_entries_max*0.5),-10,10)

        hist.Draw("L")
        threshold.Draw("SAME")
        canvas.Draw()
        canvas.Update()
        canvas.SaveAs("offset/Toffset/"+ str(tuple_index)+".png")
        points = intercept_histogram_with_constant(hist,n_entries_max*0.5,True)
        #print(points[-1][0])
        media = (points[0][0]+points[-1][0])/2
        asc.write(f"{media}\n")

        hist.Reset()

#end_time = time.time()

#print((end_time-start_time)//60)
file.Close()