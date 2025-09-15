#!/usr/bin/env python

import sys
import math
import sys
import glob
import os
import copy
import shutil
import pickle
import json
import scipy
import scipy.integrate
from collections import defaultdict
from os.path import join as pjoin

yWW_binning = [[-100,-3.5],[-3.5,-2.5],[-2.5,-2.0],[-2.0,-1.5],[-1.5,-1.0],[-1.0,-0.5],[-0.5,0.0],[0.0,0.5],[0.5,1.0],[1.0,1.5],[1.5,2.0],[2.0,2.5],[2.5,3.5],[3.5,100]]

dyWpWm_binning = [[-100,-5.2],[-5.2,-4.8],[-4.8,-4.4],[-4.4,-4.0],[-4.0,-3.6],[-3.6,-3.2],[-3.2,-2.8],[-2.8,-2.4],[-2.4,-2.0],[-2.0,-1.6],[-1.6,-1.2],[-1.2,-0.8],[-0.8,-0.4],[-0.4,-0.0],[0.0,0.4],[0.4,0.8],[0.8,1.2],[1.2,1.6],[1.6,2.0],[2.0,2.4],[2.4,2.8],[2.8,3.2],[3.2,3.6],[3.6,4.0],[4.0,4.4],[4.4,4.8],[4.8,5.2],[5.2,100]]

pTWm_binning = [[0.0,17.5],[17.5,25.],[25.,30.],[30.,35.],[35.,40.],[40,47.5],[47.5,57.5],[57.5,72.5],[72.5,100.],[100.,200.],[200.,350.],[350.,600.],[600.,1000.],[1000.,1500.],[1500.,100000.]]

if(len(sys.argv) != 3):
    print("ERROR - need exactly two arguments: one file path: central AND name-of-contribution")
    exit(0)
file_central = sys.argv[1]
#file_min = sys.argv[2]
#file_max = sys.argv[3]
ending = sys.argv[2]
if not os.path.isfile(file_central):
    print("ERROR - file %s does not exist" % file_central)
    exit(0)
#if not os.path.isfile(file_min):
#    print("ERROR - file %s does not exist" % file_min)
#    exit(0)
#if not os.path.isfile(file_max):
#    print("ERROR - file %s does not exist" % file_max)
#    exit(0)

print("")

#{{{ hard-code plot mappings:
plot_mapping = []
plot_mapping.append("total_rate__"+ending+".dat") # 0
# plot_mapping.append("theta_CS.Wm_0.1__"+ending+".dat") # 1
# plot_mapping.append("phi_CS.Wm_0.1__"+ending+".dat") # 2
# plot_mapping.append("theta_CS.Wp_0.1__"+ending+".dat") # 3
# plot_mapping.append("phi_CS.Wp_0.1__"+ending+".dat") # 4
# plot_mapping.append("pT.WW_25__"+ending+".dat") # 5
# plot_mapping.append("pT.Wp_25__"+ending+".dat") # 6
# plot_mapping.append("pT.Wp_5__"+ending+".dat") # 7
# plot_mapping.append("pT.Wm_25__"+ending+".dat") # 8
# plot_mapping.append("pT.Wm_5__"+ending+".dat") # 9
# plot_mapping.append("y.WW_0.25__"+ending+".dat") # 10
# plot_mapping.append("dy.WmWp_0.25__"+ending+".dat") # 11
# plot_mapping.append("m.Wm_5.0__"+ending+".dat") # 12
# plot_mapping.append("m.Wm_20.0__"+ending+".dat") # 13
# plot_mapping.append("m.Wp_5.0__"+ending+".dat") # 14
# plot_mapping.append("m.Wp_20.0__"+ending+".dat") # 15
#}}}

def rec_dd():
    return defaultdict(rec_dd)

#{{{ def: readin_all_distributions(filename)
def readin_ddd_distribution(filename):
    mydict = rec_dd()
    plotname = ""
    with open(filename, 'r+') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                index = line.split("index")[1].strip()
                plotname = line.split("index")[0].strip()
                if "# x" in plotname:
                    plotname = ""
                plotname = plotname.replace("# ","").replace("pt.","pT.")
                if plotname.startswith("y.WpWm"):
                    plotname = plotname.replace("y.WpWm","y.WW")
                if plotname.startswith("total_incl") or plotname.startswith("total_fid") or plotname.startswith("total_fid_veto"):
                    plotname = plotname.replace("total_","total_rate_")
                continue
            if not plotname:
                continue
            x_value    = float(line.split()[0].replace("D","E"))
            x_value_up = float(line.split()[1].replace("D","E"))
            binsize = 1.
            # if plotname == "dy.WpWm_0.1_incl" or plotname == "dy.WpWm_0.1_fid" or plotname == "dy.WpWm_0.1_fid_veto":
            #     binsize = 2.
            if plotname == "dy.WpWm_incl" or plotname == "dy.WpWm_fid" or plotname == "dy.WpWm_fid_veto" or "dy.WpWm_mom" in plotname:
                index = int(x_value)
                index_up = int(x_value_up)
                x_value = dyWpWm_binning[index][0]
                x_value_up = dyWpWm_binning[index][1]
                binsize = abs(x_value_up-x_value)
            if plotname == "y.WW_incl" or plotname == "y.WW_fid" or plotname == "y.WW_fid_veto" or "y.WW_mom" in plotname:
                index = int(x_value)
                index_up = int(x_value_up)
                if index > 13 :
                    continue
                x_value = yWW_binning[index][0]
                x_value_up = yWW_binning[index][1]
                binsize = abs(x_value_up-x_value)
            if plotname == "pT.Wm_incl" or plotname == "pT.Wm_fid" or plotname == "pT.Wm_fid_veto" or "pT.Wm_mom" in plotname or plotname == "pT.Wp_incl" or plotname == "pT.Wp_fid" or plotname == "pT.Wp_fid_veto" or "pT.Wp_mom" in plotname:
                index = int(x_value)
                index_up = int(x_value_up)
                x_value = pTWm_binning[index][0]
                x_value_up = pTWm_binning[index][1]
                binsize = abs(x_value_up-x_value)

            y_value    = float(line.split()[2].replace("D","E"))*1000./binsize
            y_err      = float(line.split()[3].replace("D","E"))*1000./binsize
            # if plotname == "dy.WpWm_incl" or plotname == "dy.WpWm_fid" or plotname == "dy.WpWm_fid_veto" or "dy.WpWm_mom" in plotname:
            #     mydict[plotname][round(-x_value-binsize,10)] = [0.,0.]
            # if plotname == "dy.WpWm_0.1_incl" or plotname == "dy.WpWm_0.1_fid" or plotname == "dy.WpWm_0.1_fid_veto":
            #     mydict[plotname][round(-x_value-0.1,10)] = [y_value,y_err]
#                mydict[plotname][round(-x_value_up-binsize/2.,10)] = [y_value,y_err]
            mydict[plotname][round(x_value,10)] = [y_value,y_err]
            mydict[plotname][round(x_value_up,10)] = [y_value,y_err]
    return mydict
#}}}



# reading files and create dicts

central_dict = readin_ddd_distribution(file_central)
min_dict = readin_ddd_distribution(file_central)
max_dict = readin_ddd_distribution(file_central)


length = 15

# try:
#     os.makedirs(pjoin(plotfolder,"distributions"))
# except:
#     pass

plotfolder = pjoin(ending+"-run")
cases = [""]

for case in cases:
    try:
        os.makedirs(pjoin(plotfolder+case,"distributions"))
    except:
       pass

for plot_name_tmp in central_dict:
  plot_name = plot_name_tmp
  plot_path = ""
  for case in cases:
    if plot_name.endswith(case):
      plot_name = plot_name.replace(case,"")
      plot_path = pjoin(plotfolder+case,"distributions",plot_name+"__"+ending+".dat")
    elif case == "":
      plot_path = pjoin(plotfolder,"distributions",plot_name+"__"+ending+".dat")
  if not plot_path:
      print("ERROR: don't know case of plot_name = %s" % plot_name)
      continue
      exit(0)
  with open(plot_path, 'w') as f:
    x_values = sorted(list(copy.copy(central_dict)[plot_name_tmp].keys()))
    observable = plot_name.split("__")[0].strip()
    observable2 = "" # usually not two line are needed
    if len(observable)>14:
        observable2 = observable[13:]
        observable = observable[:13]
    central = "central"
    minimum = "min (scale)"
    maximum = "max (scale)"
    num_err = "num_err"
    line = "#"+" "*(length-len(observable)-1)+observable # 1 column title: observable
    line = line+" "*(length-len(central))+central # 2: central cross section
    line = line+" "*(length-len(num_err))+num_err # 3: num_err
    line = line+" "*(length-len(minimum))+minimum # 4: minimal cross section due to scale variation
    line = line+" "*(length-len(num_err))+num_err # 5: num_err
    line = line+" "*(length-len(maximum))+maximum # 6: maximal cross section due to scale variation
    line = line+" "*(length-len(num_err))+num_err # 7: num_err
    f.write(line+"\n")
#    print(line)
    if observable2:
        f.write("# "+observable2+"\n")
#        print("# "+observable2)

    fakeerr=0
    for x_value in x_values:
            valuemin = central_dict[plot_name_tmp][x_value][0] - central_dict[plot_name_tmp][x_value][1]
            valuemax = central_dict[plot_name_tmp][x_value][0] + central_dict[plot_name_tmp][x_value][1]
            line = ""
            line = line+" "*(length-len("%.8g" % x_value))+"%.8g" % x_value
            line = line+" "*(length-len("%.8g" % central_dict[plot_name_tmp][x_value][0]))+"%.8g" % central_dict[plot_name_tmp][x_value][0]
            line = line+" "*(length-len("%.8g" % fakeerr))+"%.8g" % fakeerr
            line = line+" "*(length-len("%.8g" % valuemin))+"%.8g" % valuemin
            line = line+" "*(length-len("%.8g" % fakeerr))+"%.8g" % fakeerr
            line = line+" "*(length-len("%.8g" % valuemax))+"%.8g" % valuemax
            line = line+" "*(length-len("%.8g" % fakeerr))+"%.8g" % fakeerr
            f.write(line+"\n")
#            print(line)





