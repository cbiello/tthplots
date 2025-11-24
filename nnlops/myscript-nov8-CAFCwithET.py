#!/usr/bin/eAnv python
# -*- coding: utf-8 -*-

import re
import sys
import os
import shutil
import glob
import copy
import math
import subprocess
import textwrap
import time
import pikepdf
from os.path import join as pjoin
if not __name__ == "__main__":
    from initialize_classes import out

if __name__ == "__main__":
  def is_number(s):
      try:
          float(s)
          return True
      except ValueError:
          return False
  def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
#{{{ class: bcolors
  class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
#}}}
#{{{ class: print_output()
  class print_output():
#{{{ def: __init__(self)
    def __init__(self):
        global wrapper
        wrapper = textwrap.TextWrapper()
        wrapper.width = 80
#}}}
#{{{ def: print_error_no_stop(self,string)
    def print_error_no_stop(self,string):
        wrapper.initial_indent    = "<<MATRIX-ERROR>> "
        wrapper.subsequent_indent = "                 "
        try:
            print(bcolors.FAIL + "%s" % "\n".join(wrapper.wrap(string)) + bcolors.ENDC)
        except:
            print("%s" % "\n".join(wrapper.wrap(string)))
            pass
#}}}
#{{{ def: print_error(self,string)
    def print_error(self,string):
        wrapper.initial_indent    = "<<MATRIX-ERROR>> "
        wrapper.subsequent_indent = "                 "
        try:
            print(bcolors.FAIL + "%s" % "\n".join(wrapper.wrap(string)) + bcolors.ENDC)
        except:
            print("%s" % "\n".join(wrapper.wrap(string)))
            pass
        sys.exit(1)
#}}}
#{{{ def: print_warning(self,string)
    def print_warning(self,string):
        wrapper.initial_indent    = "<<MATRIX-WARN>> "
        wrapper.subsequent_indent = "                "
        try:
            print(bcolors.WARNING + "%s" % "\n".join(wrapper.wrap(string)) + bcolors.ENDC)
        except:
            print("%s" % "\n".join(wrapper.wrap(string)))
            pass
#}}}
#{{{ def: print_info(self,string)
    def print_info(self,string):
        wrapper.initial_indent    = "<<MATRIX-INFO>> "
        wrapper.subsequent_indent = "                "
        try:
            print(bcolors.OKGREEN + "%s" % "\n".join(wrapper.wrap(string)) + bcolors.ENDC)
        except:
            print("%s" % "\n".join(wrapper.wrap(string)))
            pass
#}}}
#{{{ def: print_jobs(self,string)
    def print_jobs(self,string):
        wrapper.width = 200
        wrapper.initial_indent    = "<<MATRIX-JOBS>> "
        wrapper.subsequent_indent = "                "
        print("%s" % "\n".join(wrapper.wrap(string)))
        wrapper.width = 80
#}}}
#{{{ def: print_result(self,string)
    def print_result(self,string):
        wrapper.width = 200
        wrapper.initial_indent    = "<MATRIX-RESULT> "
        wrapper.subsequent_indent = "                "
        print("%s" % "\n".join(wrapper.wrap(string)))
        wrapper.width = 80
#}}}
#{{{ def: print_read(self,string)
    def print_read(self,string):
        wrapper.initial_indent    = "<<MATRIX-READ>> "
        wrapper.subsequent_indent = "                "
        print("%s" % "\n".join(wrapper.wrap(string)))
#}}}
#{{{ def: print_list(self,list_path,output_type="default")
    def print_list(self,list_path,output_type="default"):
        # define color of output
        color_end = bcolors.ENDC
        if output_type == "error":
            color_start = bcolors.FAIL
        elif output_type == "warning":
            color_start = bcolors.WARNING
        elif output_type == "info":
            color_start = bcolors.OKGREEN
        elif output_type == "default":
            color_start = ""
            color_end = ""
        else:
            self.print_error("Given output_type %s in function print_list not known." % output_type)

        with open(list_path,'r') as list_file:
            for entry in list_file:
                print(color_start + "|============>> " + entry.strip() + color_end)
#}}}
#}}}

#{{{ class: gnuplot
class gnuplot():
    """Class to automatically create nice gnuplot files and plot the MATRIX distributions"""
#{{{ def: __init__(self,result_folder_path_in)
    def __init__(self,result_folder_path_in):
        self.curve_list = [] # initialize an empty curve list
        self.orig_curve_dict = {} # keep original curves as dictinary of new curves giving old curves, needed for normalization
        self.curve_properties = {} # and an empty dictionary for the properties of these curves (linestyle, coloer, ...)
        self.plot_properties = {} # and another empty dictionary for the properties of the plot (xmin, xmax,...)
        self.result_folder_path  = result_folder_path_in # use pwd in stand alone mode
        self.gnuplot_folder_name = "gnuplot_minnlo"
        self.gnuplot_folder_path = pjoin(self.result_folder_path,self.gnuplot_folder_name)
        self.define_all_label_mappings()
        self.binwidth = 0
        # special cases:
        # self.njets_plot = False # in this plot we combine n_jets and total_rate
        try:
            os.makedirs(self.gnuplot_folder_path)
        except:
            pass
#}}}
#{{{ def: add_curve(self,path,properties = {})
    def add_curve(self,path,properties = {}):
        # function to add a curve (data file under path) to the list of curves, where you can give properties 
        # which is a dictionary that contains, eg, {'color': red/RGB, 'format': histogram, 'linewidth': 1, 'linestyle': 1,'label', 'uncertainties': True ... more?}
        # if you give no properties, the default properties (line styles) are used
        # default for uncertainties is Trues; this assumes a file with $1: x-value, $2: central, $3: err_central, $4/$6: up/down or down/up, $5/$7: their errors
        if not os.path.isfile(path): # maybe loosen this later and only skip the plot
            out.print_error("Trying to add a curve under path \"%s\" that does not exist. Exiting..." % path)
        if self.plot_properties:
            out.print_error("Trying to add curve, but plot properties already set. You have to first add all curves, and then you can specify the plot properties.")
        self.curve_list.append(path)
        # check first wether the property input is valid
        self.check_curve_properties(properties)
        self.curve_properties[path] = properties
#}}}
#{{{ def: check_curve_properties(self,properties)
    def check_curve_properties(self,properties):
        # function to check wether the given curve properties are valid
        # properties can be either a dictionary of dictionaries of all curves, or a dictionary for one curve
        allowed_properties = {}
        allowed_properties["line_style"]  = [] 
        allowed_properties["color"]  = [] #["red","blue","green","black"] # too many possibilities also RGB colors allowed...
        allowed_properties["format"] = ["lines","histogram","sigma_per_bin","data"]
        allowed_properties["normalization_constant"] = []
        allowed_properties["label"]  = [] # if empty everything is allowed (specify later)
        allowed_properties["exclude_from_ratio"]  = [True,False] # if empty everything is allowed (specify later)
        allowed_properties["exclude_from_main"]  = [True,False] # if empty everything is allowed (specify later)
        allowed_properties["uncertainties"]  = [True,False] # if empty everything is allowed (specify later)
        allowed_properties["show_uncertainties"]  = [True,False] # if empty everything is allowed (specify later)
        for item0 in properties:
            if isinstance(item0, dict):
                for item in item0:
                    if not item in allowed_properties:
                        out.print_error("Item %s has no entry in the dictionary of allowed_properties of a curve." % item)
                    elif allowed_properties[item] and not properties[item] in allowed_properties[item]:
                        out.print_error("Property %s of a curve for item %s is not in the list of allowed_properties for that item." % (properties[item], item))
            else:
                item = item0
                if not item in allowed_properties:
                    out.print_error("Item %s has no entry in the dictionary of allowed_properties of a curve." % item)
                elif allowed_properties[item] and not properties[item] in allowed_properties[item]:
                    out.print_error("Property %s of a curve for item %s is not in the list of allowed_properties for that item." % (properties[item], item))
#}}}
#{{{ def: get_name(self,curve_list)
    def get_name(self,curve_list = {}):
        # function that determines a name for the plot (from the names of the files of each curve) and returns it
        # first get the names from the curve_list which contains the full paths
        if "name" in self.plot_properties: # in case name is set manually use that and return
            return self.plot_properties["name"]
        
        if not curve_list:
            curve_list = self.curve_list
        name_list = []
        for curve in curve_list:
            name_list.append(curve.rsplit('/',1)[1])
        name = os.path.commonprefix(name_list).rstrip(".dat").rstrip("_")
        if len(name) < 2 or os.path.exists(pjoin(self.gnuplot_folder_path,name+".gnu")):
            name = '+'.join(name_list)
        return name
#}}}
#{{{ def: clean_gnuplot_folder(self)
    def clean_gnuplot_folder(self):
        # function that removes everything in the gnuplot folder
        try:
            shutil.rmtree(self.gnuplot_folder_path)
        except:
            pass        
        try:
            os.makedirs(self.gnuplot_folder_path)
        except:
            pass        
#}}}
#{{{ def: convert_to_histogram(self,path)
    def convert_to_histogram(self,path, normalization_constant = 1, rebin = 1,convert_to_sigma_per_bin = False):
        # converts a normal (space-separated) data file into a histrogram:  0  XXX         0  XXX
        #                                                                   5  YYY         5  XXX
        #                                                                  10  ZZZ   ==>   5  YYY
        #                                                                  15  ...        10  YYY
        #                                                                  ..             10  ZZZ
        # the assumption is that the histograms always start at the lower bound; 2do: add bin correction
        min_x_for_rebin = self.plot_properties.get("min_x_for_rebin","")
        rebin_above_x = self.plot_properties.get("rebin_above_x","")
        # special case: for njets plots we must add the total rate between x-values of -1 and 0
        add_total_rate = None
        if path.rsplit('/',1)[1].startswith("n_jets"):
            # get the corresponding total rate
            total_path = pjoin(path.rsplit('/',1)[0],path.rsplit('/',1)[1].replace("n_jets","total_rate"))
            with open(total_path, 'r') as f:
                for line in f:
                    if line.strip()[0]=="" or line.strip()[0]=="%" or line.strip()[0]=="#": 
                        continue
                    add_total_rate = line.split(None,1)[1].strip()
        # first try to create a histgram folder inside the gnuplot folder, where all the histograms can be
        try:
            os.makedirs(pjoin(self.gnuplot_folder_path,"histograms"))
        except:
            pass
        # then do the conversion to a histgram file
        histogram_file_name = path.rsplit('/',1)[1].replace(".dat",".hist")
        previous_y_values = None # initialize since start of first bin does not need to be repeated
        filelength = file_len(path)/rebin
#        print filelength, path
        with open(pjoin(self.gnuplot_folder_path,"histograms",histogram_file_name),'w') as hist_file:
          with open(pjoin(self.gnuplot_folder_path,"histograms",histogram_file_name.replace(".hist","_yerror.hist")),'w') as hist_file_yerr:
            with open(path, 'r') as orig_file:
                if add_total_rate: # add total rate at the very beginning of njets plot
                    hist_file.write("-1  "+add_total_rate+"\n")
                    hist_file.write("0  "+add_total_rate+"\n")
                    hist_file_yerr.write("-1  "+add_total_rate+"\n")
                    hist_file_yerr.write("0  "+add_total_rate+"\n")
                count_since_rebin = 0
                saved_y_values_array = []
                counter = 1
                firsttime = True
                for line in orig_file:
                    counter += 1
                    line = line.strip() # strip removes all spaces (including tabs and newlines)
                    # if any line starts with %, # or is an emtpy line (disregarding spaces) it is a comment line and should be skipped
                    if line=="" or line[0]=="%" or line[0]=="#": 
#                        hist_file.write(line+"\n")
                        continue
                    count_since_rebin += 1
                    x_value  = line.split(None,1)[0].strip()
                    if rebin_above_x and (float(x_value) >= float(min_x_for_rebin)):
                        rebin = rebin_above_x
                    y_values_array = line.split(None,1)[1].strip().split()
                    y_values = ""
                    if count_since_rebin == 1:
                        saved_x_value = x_value
                    if count_since_rebin < rebin:
                        saved_y_values_array.append(y_values_array)
                        continue
                    else:
                        for array in saved_y_values_array:
                            for index, value in enumerate(array):
                                if index % 2 == 0:
                                    y_values_array[index] = str(float(y_values_array[index])+float(value))
                                else:
#                                    y_values_array[index] = str(float(y_values_array[index])+float(value))
                                    y_values_array[index] = str(((float(y_values_array[index]))**2+float(value)**2)**(1/2.))
                        if not convert_to_sigma_per_bin:
                            for index, value in enumerate(y_values_array):
                                y_values_array[index] = str(float(y_values_array[index])/rebin) # for histograms need to devide out rebinning
#                        x_value_for_next = copy.copy(x_value)
                        x_value = saved_x_value
                        count_since_rebin = 0
                        saved_y_values_array = []
                    next_x_value_set = False
                    for value in y_values_array:
                        if convert_to_sigma_per_bin:
                            # get the next x-value
                            nextone = False
                            with open(path, 'r') as orig_file2:
                              for line2 in orig_file2:
                                line2 = line2.strip() # strip removes all spaces (including tabs and newlines)
                                # if any line starts with %, # or is an emtpy line (disregarding spaces) it is a comment line and should be skipped
                                if line2=="" or line2[0]=="%" or line2[0]=="#": 
                                    continue
                                x_value2  = line2.split(None,1)[0].strip()
                                if nextone:
                                    next_x_value = x_value2
                                    next_x_value_set = True
                                    break
                                elif float(x_value2) == float(x_value):
                                    nextone = True
                            if next_x_value_set:
                                y_values = y_values + "  " + str(float(value)*(float(next_x_value) - float(x_value)) * normalization_constant)
                            else:
                                y_values = previous_y_values
                            binwidth2 = (float(next_x_value)-float(x_value))#*rebin
                            if counter == filelength/2:
                                self.binwidth = (float(next_x_value)-float(x_value))#*rebin
 #                               print "yeeees",self.binwidth
 #                               print self.binwidth
                        else:
                            y_values = y_values + "  " + str(float(value) * normalization_constant)
                            binwidth2 = 0.
                    if previous_y_values: hist_file.write(x_value+"  "+previous_y_values+"\n")
                    if previous_y_values and next_x_value_set:
                        hist_file_yerr.write(str(float(x_value)+binwidth2/2)+"  "+previous_y_values+"\n")
                    hist_file.write(x_value+"  "+y_values+"\n")
                    if firsttime and "dy.WpWm__" in histogram_file_name:
                        hist_file_yerr.write(str(-5.4)+"  "+y_values+"\n")
                        firsttime = False
                    elif firsttime and "pT.Wm__" in histogram_file_name:
                        hist_file_yerr.write(str(13.4)+"  "+y_values+"\n")
                        firsttime = False
                    elif firsttime and "y.WW__" in histogram_file_name:
                        hist_file_yerr.write(str(-3.75)+"  "+y_values+"\n")
                        firsttime = False
                    else:
                        hist_file_yerr.write(str(float(x_value)+binwidth2/2)+"  "+y_values+"\n")
                    previous_y_values = y_values
                if self.binwidth == 0: self.binwidth = binwidth2
                # print "---------------------------------"
                # print path
                # print self.binwidth
                if "dy.WpWm__" in histogram_file_name:
                    hist_file_yerr.write(str(5.4)+"  "+y_values+"\n")
                    hist_file_yerr.write(str(5.4)+"  "+y_values+"\n")
                elif "pT.Wm__" in histogram_file_name:
                    hist_file_yerr.write(str(2100)+"  "+y_values+"\n")
                    hist_file_yerr.write(str(2100)+"  "+y_values+"\n")
                elif "y.WW__" in histogram_file_name:
                    hist_file_yerr.write(str(3.75)+"  "+y_values+"\n")
                    hist_file_yerr.write(str(3.75)+"  "+y_values+"\n")
                if count_since_rebin > 0:
                    if previous_y_values: hist_file.write(x_value+"  "+previous_y_values+"\n")
                    if previous_y_values: hist_file_yerr.write(str(float(x_value)+binwidth2/2)+"  "+previous_y_values+"\n")
        if path in self.curve_list: # if the original file was already added to the curve_list
            # remove the original file in the curve_list and add the new histogram file
            self.curve_list.remove(path)
            self.curve_list.append(pjoin(self.gnuplot_folder_path,"histograms",histogram_file_name))
            # and replace its properties
            self.curve_properties[pjoin(self.gnuplot_folder_path,"histograms",histogram_file_name)] = self.curve_properties.pop(path)
            # keep original curves as dictinary of new curves giving old curves, needed for normalization
            self.orig_curve_dict[pjoin(self.gnuplot_folder_path,"histograms",histogram_file_name)] = path
#}}}
#{{{ def: run_gnuplot(self,gnu_file)
    def run_gnuplot(self,gnu_file):
        # function to execute gnuplot with gnu_file as first argument
        out.print_info("Running gnuplot...")
        gnuplot = subprocess.Popen(["gnuplot",gnu_file])#, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#}}}
#{{{ def: plot(self)
    def plot(self,curve_list = [],curve_properties = {},plot_properties = {}):
        # function to start the final plotting
        # you can give the curve_list and its properties also altogether via their arguments here. THE ORDERING OF BOTH IS IMPORTANT!
        if curve_list: # if not empty
            self.curve_list = curve_list # overwrite the curve list belonging to the class
            self.check_curve_properties(curve_properties)   # check input for all curves
            for curve in curve_list:
#                self.check_curve_properties(curve_properties.get(curve,{}))   # check input for each curve
                self.curve_properties[curve] = curve_properties.get(curve,{}) # and its properties (second argument is the default, which is an empty list)
        if plot_properties: # if not empty
            self.check_plot_properties(plot_properties)
            self.plot_properties = plot_properties
        # first do some checks:
        if not self.curve_list:
            out.print_error_no_stop("Trying to plot data, but curve_list is empty.")
            return
        self.check_concistency_of_curve_properties(self.curve_properties)
        # other checks?

        # first determine name of the plot (because of njet/total rate special case)
        self.plot_name = self.get_name(self.curve_list)
        out.print_info("Trying to plot: %s" %self.plot_name)
        gnu_file = pjoin(self.gnuplot_folder_path,self.plot_name+".gnu")
        # then convert all histogram curves (note currently only supported that none or all are histograms; catched in check_concistency_of_curve_properties)
        tmp_curve_list = []
        for item in self.curve_list:
            tmp_curve_list.append(item) # make a copy to be able to change the orignal list while looping over
            # if self.plot_name == "n_jets": # for n_jet plots
            #     self.njets_plot = True
            #     tmp_curve_list.append(item.replace("n_jets","total_rate")) # add also total rate
            #     self.curve_properties[item.replace("n_jets","total_rate")] = {} # and add empty properties
        for curve in tmp_curve_list:
            if not "format" in self.curve_properties[curve] or self.curve_properties[curve]["format"] == "histogram": # histograms is default, so do the conversion also if no format is given
                self.convert_to_histogram(curve,self.curve_properties[curve].get("normalization_constant",1.),self.plot_properties.get("rebin",1))
            elif self.curve_properties[curve]["format"] == "sigma_per_bin":
                self.convert_to_histogram(curve,self.curve_properties[curve].get("normalization_constant",1.),self.plot_properties.get("rebin",1),True)
            elif self.curve_properties[curve]["format"] == "data" or self.curve_properties[curve]["format"] == "lines":
                # make sure the position in the curve list stays the same
                self.curve_list.remove(curve)
                self.curve_list.append(curve)
            else:
                out.print_error("Curve \"format\" not recognized.")
        # check if the values in the files are all zeros (stop the plotting if that is the case)
        if not self.get_axis_properties():
            out.print_error_no_stop("The plots appear to be all empty (or contain only zeros and nans). Skipping this plot...")
        else:
            # create gnuplot file
            self.create_gnu_file(gnu_file)
            # execute gnuplot for gnu_file
            self.run_gnuplot(gnu_file)
            out.print_info("Plot successfully generated.")
#}}}
#{{{ def: check_concistency_of_curve_properties(self,curve_properties)
    def check_concistency_of_curve_properties(self,curve_properties):
        # function to check wether the properties of the different curves are consistent with each other
        pass
        # should work now for data
        # 1. check: we can only plot curves of the same format into the same plot
        # curve_format = ""
        # for curve, properties in curve_properties.iteritems():
        #     if curve_format and not curve_format == properties.get("format",""):
        #         out.print_error("Currently, one can combine only curves of the same format into the same plot, but trying to combine format \"%s\" and format \"%s\"" % (curve_format,properties.get("format")))
        #     else:
        #         curve_format = properties.get("format","")
#}}}
#{{{ def: set_plot_properties(self,properties,value = None)
    def set_plot_properties(self,properties,value = None):
        # function to set plot properties; with one argument you directly give the full list under properties (and overwrite any given plot properties before)
        # with two arguments you can set a single property to the given value (Note: the value must be different from None!)
        self.check_plot_properties(properties,value)
        if value is None and isinstance(properties, dict):
            self.plot_properties[properties] = value
        else:
            self.plot_properties[properties] = value
#}}}
#{{{ def: check_plot_properties(self,properties,value = None)
    def check_plot_properties(self,properties,value = None):
        # function to check wether the given plot properties are valid
        # properties can be either a dictionary of all properties, or a single property of a plot
        allowed_properties = {}
        allowed_properties["name"]  = [] # set name of plot, otherwise automatically determined
        allowed_properties["rebin"]  = [] # if empty everything is allowed (specify types later)
        allowed_properties["rebin_above_x"]  = [] # if empty everything is allowed (specify types later)
        allowed_properties["min_x_for_rebin"]  = [] # if empty everything is allowed (specify types later)
        allowed_properties["xmin"]  = [] # if empty everything is allowed (specify types later)
        allowed_properties["xmax"]  = []
        allowed_properties["ymin"]  = []
        allowed_properties["ymax"]  = []
        allowed_properties["ymin_ratio"] = []
        allowed_properties["ymax_ratio"] = []
        allowed_properties["title"]    = []
        allowed_properties["process"]  = []
        allowed_properties["collider"] = []
        allowed_properties["energy"]   = []
        allowed_properties["normalization"] = [x for x in range(1,len(self.curve_list)+1)]
        allowed_properties["logscale_y"] = [True,False]
        allowed_properties["logscale_x"] = [True,False]
        allowed_properties["logscale_y_ratio"] = [True,False]
        allowed_properties["logscale_x_ratio"] = [True,False]
        allowed_properties["xlabel"] = []
        allowed_properties["xunit"]  = []
        allowed_properties["ylabel"] = []
        allowed_properties["yunit"]  = []
        allowed_properties["reference"] = []
        allowed_properties["version"]   = []
        allowed_properties["category"]  = []
        allowed_properties["categoryleft"]  = []
        allowed_properties["categorydownleft"]  = []
        allowed_properties["xtics"]  = []
        allowed_properties["mxtics"] = []
        allowed_properties["xtics_ratio"]  = []
        allowed_properties["xtics_add"]  = []
        allowed_properties["mxtics_ratio"] = []
        allowed_properties["ytics_ratio"]  = []
        allowed_properties["mytics_ratio"] = []
        allowed_properties["ytic_offset_x"]  = []
        allowed_properties["ytic_offset_y"] = []
        allowed_properties["xtic_offset_x"]  = []
        allowed_properties["xtic_offset_y"] = []
        allowed_properties["mytics"] = []
        allowed_properties["norm_label"] = []
        allowed_properties["exclude_from_ratio"] = [] # must be a list
        allowed_properties["exclude_from_main"] = [] # must be a list
        allowed_properties["legend"] = ["left","right","down","down down","down left","down center"] # must be a list
        allowed_properties["legend_ratio"] = ["left","right","down","down left"] # must be a list
        if value is None and isinstance(properties, dict): # dictionary of properties
            for item in properties:
                if not item in allowed_properties:
                    out.print_error("Item \"%s\" has no entry in the dictionary of allowed_properties of the plot." % item)
                elif allowed_properties[item] and not properties[item] in allowed_properties[item]:
                    out.print_error("Property \"%s\" of the plot for item \"%s\" is not in the list of allowed_properties for that item." % (properties[item], item))
        else: # single property
            if not properties in allowed_properties:
                out.print_error("Item \"%s\" has no entry in the dictionary of allowed_properties of the plot." % properties)
            elif allowed_properties[properties] and not value in allowed_properties[properties]:
                out.print_error("Property \"%s\" of the plot for item \"%s\" is not in the list of allowed_properties for that item." % (value, properties))
#}}}
#{{{ def: create_gnu_file(self,gnu_file)
    def create_gnu_file(self,gnu_file):
        # function to create the whole gnuplot file; this will be quite long and tricky
        # so it will be splitted in many steps
        with open(gnu_file, "w") as out_file:
            out_file.write(self.get_gnuplot_default_general()) # writes out the default general part
            out_file.write(self.get_gnuplot_settings_general()) # writes out the default general part
            out_file.write(self.get_gnuplot_default_main_frame()) # writes out the default general part
            out_file.write(self.get_gnuplot_settings_main_frame()) # writes out the default general part
            out_file.write(self.get_gnuplot_plot_main_frame()) # writes out the default general part
            out_file.write(self.get_gnuplot_default_ratio()) # writes out the default general part
            out_file.write(self.get_gnuplot_settings_ratio()) # writes out the default general part
            out_file.write(self.get_gnuplot_plot_ratio()) # writes out the default general part
#}}}
#{{{ def: get_gnuplot_default_general(self)
    def get_gnuplot_default_general(self):
        # function that returns the default general part to create the gnuplot file
        default_general = """
reset
set terminal pdfcairo enhanced dashed dl 1.5 lw 3 font \"Helvetica,29\" size 7.6, 8
set encoding utf8

## default key features
#set key at graph 1.03,0.97
set key reverse  # put text on right side
set key Left     # left bounded text
set key spacing 1.1
set key samplen 2
## to have a assisting grid of dashed lines
set grid front
## set margins
set lmargin 5
set rmargin 2
"""
        return default_general
#}}}
#{{{ def: get_gnuplot_settings_general(self)
    def get_gnuplot_settings_general(self):
        # function that returns the user-definable settings made in the general part to create the gnuplot file
        # create a parameter_list dictionary so that it is more obvious which values are set in the string created below
        parameter_list = {}
        # set all parameters that you can modify below, so that they can be passed to the string
        parameter_list["pdf_file"] = pjoin(self.gnuplot_folder_path,self.plot_name+".pdf") # path of the output pdf file
        parameter_list["MATRIX_reference"] = self.plot_properties.get("reference","XXXX.XXXXX") # set it to something meaningful later
# not used    parameter_list["MATRIX_version"] = self.plot_properties.get("version","0.0.1alpha") # set it to something meaningful later
        if self.plot_properties.get("legend","right") == "right":
            parameter_list["key_x"]  = 1.00 # x-position of key 
            parameter_list["key_y"]  = 0.95 # y-position of key 
        elif self.plot_properties.get("legend","right") == "left":
            parameter_list["key_x"]  = 0.68 # x-position of key 
            parameter_list["key_y"]  = 0.95 # y-position of key 
        elif self.plot_properties.get("legend","right") == "down":
            parameter_list["key_x"]  = 0.82 # x-position of key 
            parameter_list["key_y"]  = 0.32 # y-position of key 
        elif self.plot_properties.get("legend","right") == "down center":
            parameter_list["key_x"]  = 0.69 # x-position of key 
            parameter_list["key_y"]  = 0.27 # y-position of key 
        elif self.plot_properties.get("legend","right") == "down down":
            parameter_list["key_x"]  = 0.80 # x-position of key 
            parameter_list["key_y"]  = 0.19 # y-position of key 
        elif self.plot_properties.get("legend","right") == "down left":
            parameter_list["key_x"]  = 0.55 # x-position of key 
            parameter_list["key_y"]  = 0.45 # y-position of key 
        if is_number(self.get_axis_properties()["xtics"]): # only set it if a number is given
            parameter_list["xtics"]  = self.get_axis_properties()["xtics"]  # distance between big x-tics 
        else: # otherwise set it empty, as it will create bin labels below the main plot
            parameter_list["xtics"]  = ""
        parameter_list["xtics_add"] = re.sub(r'\".*?\"', '\"\"', self.plot_properties.get("xtics_add",""))
        parameter_list["mxtics"] = self.get_axis_properties()["mxtics"] # number of small x-tics between the big x-tics
        parameter_list["mytics"] = self.get_axis_properties()["mytics"] # number of small y-tics between the big y-tics
        if self.plot_properties.get("logscale_y",True):
            parameter_list["logscale_y"] = "set logscale y" # determine wether y-achsis uses a logscale
            parameter_list["format_y"] = "\"10^{\%T}\"" # format of the label of the y-tics
            parameter_list["mytics"] = 10 # number of small y-tics between the big y-tics
        else:
            parameter_list["logscale_y"] = "#set logscale y"
            parameter_list["format_y"] = "" # format of the label of the y-tics
        if self.plot_properties.get("logscale_x",False): parameter_list["logscale_x"] = "set logscale x" # determine wether x-achsis uses a logscale
        else: parameter_list["logscale_x"] = "#set logscale x"
        parameter_list["ytic_offset_x"] = self.plot_properties.get("ytic_offset_x",0)   # offset in x-direction of the label at the y-tics
        parameter_list["ytic_offset_y"] = self.plot_properties.get("ytic_offset_y",0.1) # offset in y-direction  of the label at the y-tics
        parameter_list["ylabel"] = self.get_axislabels_and_units()["ylabel"] # label of the y-axis
        parameter_list["yunit"]  = self.get_axislabels_and_units()["yunit"]  # unit of the y-axis
        if all(key in self.plot_properties for key in ("process","collider","energy")):
            parameter_list["title"] = self.plot_properties["process"]+"\\\\@"+self.plot_properties["collider"]+" "+self.plot_properties["energy"] # set upper right title
        elif "title" in self.plot_properties:
            parameter_list["title"] = self.plot_properties["title"]
        else:
            parameter_list["title"] = ""

        settings_general = """
## general settings
set key at graph %(key_x)s, %(key_y)s
set xtics %(xtics)s
set xtics add %(xtics_add)s
set mxtics %(mxtics)s
set mytics %(mytics)s
%(logscale_y)s
%(logscale_x)s
set ytic offset %(ytic_offset_x)s, %(ytic_offset_y)s
set format y %(format_y)s

set label \"%(ylabel)s %(yunit)s\" at graph 0, 1.07
set label \"%(title)s\" right at graph 1, graph 1.07

set output \"%(pdf_file)s\"
""" % parameter_list # takes the values from the parameter_list dictionary from the keys in the string
        return settings_general
#}}}
#{{{ def: get_gnuplot_default_main_frame(self)
    def get_gnuplot_default_main_frame(self):
        # function that returns the default settings for the main frame to create the gnuplot file
        default_main_frame = """
##############
# main frame #
##############

# origin, size of main frame
set origin 0, 0.48
set size 1, 0.47
set bmargin 0 # set marging to remove space
set tmargin 0 # set margin to remove space
set format x \"\"
"""
        return default_main_frame
#}}}
#{{{ def: get_gnuplot_settings_main_frame(self)
    def get_gnuplot_settings_main_frame(self):
        # function that returns user-definiable settings in the main frame to create the gnuplot file
        settings_main_frame = """
## define line styles
#MiNNLOPS 5FS (LHE 1, PS 2)
set style line 1 lc rgb \"blue\" lw 1
set style line 2 lc rgb \"dark-blue\" lw 1
set style line 11 dt (3,3) lc rgb \"dark-blue\" lw 0.1
set style line 12 dt (3,3) lc rgb \"dark-blue\" lw 0.1
#MiNLOp 5FS (LHE 3, PS 4)
set style line 3 dt (9,6) lc rgb \"blue\" lw 1
set style line 4 dt (9,6) lc rgb \"black\" lw 1
set style line 13 dt (8,4,8,4,3,4) lc rgb \"blue\" lw 0.1
set style line 14 dt (8,4,8,4,3,4) lc rgb \"black\" lw 0.1
#NLOPS 5FS (LHE 5, PS 6)
set style line 5 dt (15,2) lc rgb \"violet\" lw 1
set style line 6 dt (15,2) lc rgb \"purple\" lw 1
set style line 15 dt (10,3,3,3) lc rgb \"violet\" lw 0.1
set style line 16 dt (10,3,3,3) lc rgb \"purple\" lw 0.1
#MiNNLOPS 4FS (LHE 7 PS 8)
set style line 7 dt (3,3) lc rgb \"light-red\" lw 1 
set style line 8 dt (3,3) lc rgb \"dark-orange\" lw 1
set style line 17 dt (10,3,3,3) lc rgb \"light-red\" lw 0.1
set style line 18 dt (10,3,3,3) lc rgb \"dark-orange\" lw 0.1
#MiNLOp 4FS (LHE 9, PS 3 but activate it)
set style line 9 lc rgb \"web-green\" lw 1
#set style line 3 lc rgb \"dark-green\" lw 1
# set style line 19 dt (8,4,8,4,3,4) lc rgb \"web-green\" lw 0.1
# set style line 13 dt (8,4,8,4,3,4) lc rgb \"dark-green\" lw 0.1
#NLOPS 4FS (LHE 21, PS 22 but deactivate the others)
#set style line 1 lc rgb \"orange\" lw 1
#set style line 2 lc rgb \"coral\" lw 1
#set style line 11 dt (3,3) lc rgb \"orange\" lw 0.1
#set style line 12 dt (3,3) lc rgb \"coral\" lw 0.1


set style line 1 lc rgb \"blue\" lw 1
set style line 11 dt (8,4,8,4,3,4) lc rgb \"blue\" lw 0.1
set style line 2 dt (6,4) lc rgb \"slateblue1\" lw 1                                                                                           
set style line 12 dt (10,3,3,3) lc rgb \"slateblue1\" lw 0.1

        
## define ranges
set xrange [%(xmin)s:%(xmax)s]
set yrange [%(ymin)s:%(ymax)s]

set multiplot
""" % self.get_axis_properties()
        return settings_main_frame
#}}}
#{{{ def: get_gnuplot_plot_main_frame(self)
    def get_gnuplot_plot_main_frame(self):
        # function that returns the plotting of curves in the main frame to create the gnuplot file
        plot_main_frame = "plot "
        counter = 1
        order = ["LO","NLO","NNLO","N3LO","N4LO","N4LO","N4LO","N4LO","N4LO"] # use the order as the default label
        prop = self.curve_properties # introduce local short-cut
        # 2do: ADD LINE STYLES HERE !!! NOT ABOVE !!!
        last_curve = ""
        for curve in self.curve_list:
            line_style = prop[curve].get("line_style",counter)
            if counter in self.plot_properties.get("exclude_from_main",[]): 
                last_curve = curve
                counter += 1
                continue
            if prop[curve].get("exclude_from_main",False):
                last_curve = curve
                counter += 1
                continue
            if counter > 1 and counter-1 not in self.plot_properties.get("exclude_from_main",[]) and not prop.get(last_curve,{}).get("exclude_from_main",False): plot_main_frame += ",\\\n"
            if prop[curve].get("format") == "data":
                plot_main_frame += "\"%s\" using 1:2:($3*$2/100) with yerrorbars lc rgb \"dark-green\" lw 1 lt 7 ps 0.7 title \"%s\"" % (curve,prop[curve].get("label",order[counter-1]))
            else:
                plot_main_frame += "\"%s\" using 1:2 with lines ls %s title \"%s\"" % (curve,line_style,prop[curve].get("label",order[counter-1]))
            if prop[curve].get("uncertainties",True) and prop[curve].get("show_uncertainties",True):
                plot_main_frame += ", \"%s\" using 1:4:6 with filledcurves ls %s fs transparent solid 0.15 notitle" % (curve,line_style)
                plot_main_frame += ", \"%s\" using 1:4 with lines ls 1%s notitle" % (curve,line_style)
                plot_main_frame += ", \"%s\" using 1:6 with lines ls 1%s notitle" % (curve,line_style)
            last_curve = curve
            counter += 1
        return plot_main_frame
#}}}
#{{{ def: get_gnuplot_default_ratio(self)
    def get_gnuplot_default_ratio(self):
        # function that returns the default settings for the ratio frame to create the gnuplot file
        default_ratio = """
###############
# ratio inset #
###############

## remove previous settings
unset label  
#unset key
unset logscale y
unset format

## set ratio inset size
set size 1, 0.32
set origin 0, 0.11
"""
        return default_ratio
#}}}
#{{{ def: get_gnuplot_settings_ratio(self)
    def get_gnuplot_settings_ratio(self):
        # function that returns the user-definable settings of the ratio frame to create the gnuplot file
        order = ["LO","NLO","NNLO","N3LO","N4LO","N4LO","N4LO","N4LO","N4LO"] # use the order as the default label
        norm = self.curve_list[self.plot_properties.get("normalization",len(self.curve_list))-1] # gives the plot number that should be used for the normalization; default is to use the last        # create a parameter_list dictionary so that it is more obvious which values are set in the string created below
        parameter_list = {}
        # set all parameters that you can modify below, so that they can be passed to the string
        parameter_list["category"] = self.plot_properties.get("category","")
        parameter_list["categoryleft"] = self.plot_properties.get("categoryleft","")
        parameter_list["categorydownleft"] = self.plot_properties.get("categorydownleft","")
        parameter_list["xtics_add"] = self.plot_properties.get("xtics_add","")
        parameter_list["norm_label"] = self.plot_properties.get("norm_label",self.curve_properties[norm].get("label",order[self.plot_properties.get("normalization",len(self.curve_list))-1]))
        if self.plot_properties.get("legend_ratio","right") == "right":
            parameter_list["key_x"]  = 0.93 # x-position of key 
            parameter_list["key_y"]  = 0.95 # y-position of key 
        elif self.plot_properties.get("legend_ratio","right") == "left":
            parameter_list["key_x"]  = 0.34 # x-position of key 
            parameter_list["key_y"]  = 0.95 # y-position of key 
        elif self.plot_properties.get("legend_ratio","right") == "down":
            parameter_list["key_x"]  = 0.59 # x-position of key 
            parameter_list["key_y"]  = 0.22 # y-position of key 
        if self.plot_properties.get("logscale_y_ratio",False):
            parameter_list["logscale_y"] = "set logscale y" # determine wether y-achsis uses a logscale
            parameter_list["format_y"] = "\"10^{\%T}\"" # format of the label of the y-tics
            parameter_list["mytics_ratio"] = 10 # number of small y-tics between the big y-tics
        else:
            parameter_list["logscale_y"] = "#set logscale y"
            parameter_list["format_y"] = "" # format of the label of the y-tics
        if self.plot_properties.get("logscale_x_ratio",False): parameter_list["logscale_x"] = "set logscale x" # determine wether x-achsis uses a logscale
        else: parameter_list["logscale_x"] = "#set logscale x"
        parameter_list["xtic_offset_x"] = self.plot_properties.get("xtic_offset_x",-0.21)   # offset in x-direction of the label at the y-tics
        parameter_list["xtic_offset_y"] = self.plot_properties.get("xtic_offset_y",0.4) # offset in y-direction  of the label at the y-tics


        settings_ratio = """
## can be changed
%(logscale_y)s
%(logscale_x)s
set format y %(format_y)s
set key at graph %(key_x)s, %(key_y)s
#set label \"ratio to %(norm_label)s\" at graph 0, 1.01
set label \"d{/Symbol s}/d{/Symbol s}_{%(norm_label)s}\" at graph 0, 1.1
set label \"%(category)s\" at graph 0.03, 2.5
set label \"%(categoryleft)s\" at graph 0.03, 2.35
set label \"%(categorydownleft)s\" at graph 0.03, 2.2
set yrange [%(ymin_ratio)s:%(ymax_ratio)s]
set ytics %(ytics_ratio)s
set mytics %(mytics_ratio)s
set ytic offset 0.4, 0
set xtic offset %(xtic_offset_x)s,%(xtic_offset_y)s
set xtics %(xtics)s
set xtics add %(xtics_add)s
set mxtics %(mxtics)s
set xlabel offset 0,0.9
set xlabel  \"%(xlabel)s %(xunit)s\"
""" % dict(list(self.get_axislabels_and_units().items()) + list(self.get_axis_properties().items()) + list(parameter_list.items())) # concentrating the dictionaries (make sure no identical items)
        return settings_ratio
#}}}
#{{{ def: get_gnuplot_plot_ratio(self)
    def get_gnuplot_plot_ratio(self):
        # function that returns the plotting of curves in the ratio frame to create the gnuplot file
        plot_ratio = "plot "
        counter = 1
        order = ["LO","NLO","NNLO","N3LO","N4LO"] # use the order as the default label
        norm = self.curve_list[self.plot_properties.get("normalization",len(self.curve_list))-1] # gives the plot number that should be used for the normalization; default is to use the last curve
        prop = self.curve_properties # introduce local short-cut
        last_curve = ""
        for curve in self.curve_list:
            line_style = prop[curve].get("line_style",counter)
            if counter in self.plot_properties.get("exclude_from_ratio",[]): 
                last_curve = curve
                counter += 1
                continue
            if prop[curve].get("exclude_from_ratio",False):
                last_curve = curve
                counter += 1
                continue
            if counter > 1 and counter-1 not in self.plot_properties.get("exclude_from_ratio",[]) and not prop.get(last_curve,{}).get("exclude_from_ratio",False): plot_ratio += ",\\\n"
            columns = 7 if prop[curve].get("uncertainties",True) else 3 # determine number of comlumns simply by wether uncertainties are in file (7 columns) or not (3 columns)
            if prop[curve].get("format") == "data":
                plot_ratio += "\"<awk \'NR%%2==0\' %s | paste %s /dev/stdin\" using 1:($2/$5):($3*$2/100/$5) with yerrorbars lc rgb \"dark-green\" lw 1 lt 7 ps 0.7 %s" % (norm,curve,"title \"%s\"" % prop[curve].get("label",order[counter-1]) if prop[curve].get("exclude_from_main" ,False) or counter in self.plot_properties.get("exclude_from_main",[]) else "notitle")
#                plot_ratio += "\"<paste %s %s\" using 1:2/$5:($3*$2/100) with yerrorbars lc rgb \"dark-green\" lw 1 lt 111 ps 0.7 title \"%s\"" % (curve,norm,prop[curve].get("label",order[counter-1]))
            else:
                plot_ratio += "\"<paste %s %s\" using 1:($2/$%s) with lines ls %s %s" % (curve,norm,2+columns,line_style,"title \"%s\"" % prop[curve].get("label",order[counter-1]) if prop[curve].get("exclude_from_main" ,False) or counter in self.plot_properties.get("exclude_from_main",[]) else "notitle\\\n")
#                plot_ratio += "\"<paste %s %s\" using ($1+%s):($2/$%s):($3*2/$%s) every 2 with yerrorbars ls %s %s" % (curve.replace(".hist","_yerror.hist"),norm,self.binwidth/2,2+columns,2+columns,counter,"title \"%s\"" % prop[curve].get("label",order[counter-1]) if prop[curve].get("exclude_from_main" ,False) or counter in self.plot_properties.get("exclude_from_main",[]) else "notitle")
#                plot_ratio += "\"<paste %s %s\" using ($1):($2/$%s):($3*2/$%s) every 2 with yerrorbars ls %s %s" % (curve.replace(".hist","_yerror.hist"),norm,2+columns,2+columns,counter,"title \"%s\"" % prop[curve].get("label",order[counter-1]) if prop[curve].get("exclude_from_main" ,False) or counter in self.plot_properties.get("exclude_from_main",[]) else "notitle")
            if prop[curve].get("uncertainties",True) and prop[curve].get("show_uncertainties",True):
                plot_ratio += ", \"<paste %s %s\" using 1:($4/$%s):($6/$%s) with filledcurves ls %s fs transparent solid 0.15 notitle" % (curve,norm,2+columns,2+columns,line_style)
                plot_ratio += ", \"<paste %s %s\" using 1:($4/$%s) with lines ls 1%s notitle" % (curve,norm,2+columns,line_style)
                plot_ratio += ", \"<paste %s %s\" using 1:($6/$%s) with lines ls 1%s notitle" % (curve,norm,2+columns,line_style)
            last_curve = curve
            counter += 1

        return plot_ratio
#}}}
#{{{ def: get_axislabels_and_units(self)
    def get_axislabels_and_units(self):
        # function that returns a dictionary with all x and y labels and units
        axis_dict = {}

        # defaults if nothing is given or can be determined
        ylabel = "{/Symbol s}"
        yunit  = "[fb]"
        xlabel = self.plot_name
        xunit  = ""
        # try to determine labels from distribution input fil
        if os.path.isfile(pjoin(self.result_folder_path,"input_of_run","distribution.dat")):
            with open(pjoin(self.result_folder_path,"input_of_run","distribution.dat"),'r') as distribution_file:
                distribution_found = False
                particles = []
                for line in distribution_file:
                    if distribution_found:
                        # determine the properties of this distribution
                        if line.strip().startswith("distributiontype"):
                            distributiontype = line.split("=")[1].strip()
                        elif line.strip().startswith("particle"):
                            particles.append([line.split("=")[0].strip(),line.split("=")[1].strip()])
                        elif line.strip().startswith("distributionname"):
                            break
                    if line.strip().startswith("distributionname") and line.split("=")[1].strip() == self.plot_name: # check wether this distribution exists
                        distribution_found = True
                if not distribution_found:
                    axis_dict["ylabel"] = self.plot_properties.get("ylabel",ylabel)
                    axis_dict["yunit"]  = self.plot_properties.get("yunit",yunit)
                    axis_dict["xlabel"] = self.plot_properties.get("xlabel",xlabel)
                    axis_dict["xunit"]  = self.plot_properties.get("xunit",xunit)
                    return axis_dict
                # set label according to distributiontype and particles
                xlabel = self.distributiontype_mapping.get(distributiontype,distributiontype)
                previous = ""
                for item in particles:
                    if not previous:
                        xlabel += "({/Times=26"
                    elif previous == item[0]:
                        xlabel += "+"
                    else:
                        xlabel += ","
                    particle    = item[1].split()[0].strip()
                    try:
                        particle_nr = item[1].split()[1].strip()
                    except:
                        particle_nr = "{}"
                        pass
                    if particle_nr != "{}" and "^" in self.particle_mapping.get(particle,particle) and "/" in self.particle_mapping.get(particle,particle).replace("{/","nuuueeet"):
                        # both cases can happen at the same time for neutrinos
                        xlabel_tmp = self.particle_mapping.get(particle,particle).replace("{/","nuuueeet").split("/")[0]+"{/Times=26 _"+particle_nr+"}/"+self.particle_mapping.get(particle,particle).replace("{/","nuuueeet").split("/")[1]+"_"+particle_nr
                        xlabel += xlabel_tmp.replace("nuuueeet","{/").replace("^","\@^") # much simpler than with the splitting around "^" below !!! ...anyway both work; BUT DON'T REPLACE EVERYWHERE !!!
                    elif particle_nr != "{}" and "^" in self.particle_mapping.get(particle,particle):
                        # this is for the case when there is a "^" in the particle then we need to add an @ in case there is also a particle_nr
                        xlabel += self.particle_mapping.get(particle,particle).split("^")[0]+"\@^"+self.particle_mapping.get(particle,particle).split("^")[1]+"_"+particle_nr
                    elif particle_nr != "{}" and "/" in self.particle_mapping.get(particle,particle).replace("{/","nuuueeet"):
                        # this is for the case when there is a "/" in the particle then we need to add the subscript to both before and after the "/"
                        xlabel += self.particle_mapping.get(particle,particle).replace("{/","nuuueeet").split("/")[0]+"{/Times=26 _"+particle_nr+"}/"+self.particle_mapping.get(particle,particle).replace("{/","nuuueeet").split("/")[1]+"_"+particle_nr
                        xlabel = xlabel.replace("nuuueeet","{/")
                    else: # normal case
                        xlabel += "%s_%s" % (self.particle_mapping.get(particle,particle),particle_nr)
                    previous = item[0]
                if particles:
                    xlabel += "})"
                ylabel = "d{/Symbol s}/d%s" % self.plot_properties.get("xlabel",xlabel)
                if distributiontype in self.unit_mapping:# use if instead direct get to put brackets around if exists, and none otherwise
                    xunit = "[%s]" % self.unit_mapping[distributiontype]
                    if "yunit" in self.plot_properties:
                        yunit = "%s" % self.plot_properties.get("yunit",yunit)
                    else:
                        yunit = "[fb/%s]" % self.unit_mapping[distributiontype]
                else:
                    xunit = ""
                    yunit = "[fb]"

        # make special case for total cross section and jets
        # overwrite by presets
        ylabel = "d{/Symbol s}/d%s" % self.plot_properties.get("xlabel",xlabel)

        if self.plot_properties.get("xunit",xunit):
            yunit = "[fb/%s]" % self.plot_properties.get("xunit",xunit)
            xunit = "[%s]" % self.plot_properties.get("xunit",xunit)

        axis_dict["ylabel"] = self.plot_properties.get("ylabel",ylabel)
        axis_dict["yunit"]  = self.plot_properties.get("yunit",yunit)
        axis_dict["xlabel"] = self.plot_properties.get("xlabel",xlabel)
        axis_dict["xunit"]  = xunit
        return axis_dict
#}}}
#{{{ def: get_axis_properties(self)
    def get_axis_properties(self):
        # function that returns a dictionary with all x and y labels and units
        axis_dict = {}

        # defaults if nothing is given or can be determined
        # xtics  = 50
        # mxtics = 5
        # mytics = 10
        # xmin   = 0
        # xmax   = 200
        # ymin   = 0.0001
        # ymax   = 100
        # ytics_ratio = 0.2 #"(0.6, 0.8, 1, 1.2, 1.4)"
        # mytics_ratio= 4
        # ymin_ratio  = 0.5
        # ymax_ratio  = 1.5

        # loop through all curve files and determine minimum, maximum of x and y axis
        # also do this for y axis of ratio
        # first read normalization curve, then others (including uncertainties)
        with open(self.curve_list[self.plot_properties.get("normalization",len(self.curve_list))-1], 'r') as norm_curve:
            x_values = []
            y_values_norm = {}
            for line in norm_curve:
                line = line.strip() # strip removes all spaces (including tabs and newlines)
                # if any line starts with %, # or is an emtpy line (disregarding spaces) it is a comment line and should be skipped
                if line=="" or line[0]=="%" or line[0]=="#": 
                    continue
                x_value = float(line.split(None,1)[0].strip())
                x_values.append(x_value)
                y_value = float(line.split(None,1)[1].strip().split()[0])
                y_values_norm[x_value] = y_value
        # then loop over all other files to determine the maximum and minimum y values
        y_values = []
        y_values_ratio = []
        for curve in self.curve_list:
          if self.curve_properties[curve].get("format") == "data":
              continue
          with open(curve, 'r') as curve_in:
            counter = 0
            for line in curve_in:
                line = line.strip() # strip removes all spaces (including tabs and newlines)
                # if any line starts with %, # or is an emtpy line (disregarding spaces) it is a comment line and should be skipped
                if line=="" or line[0]=="%" or line[0]=="#": 
                    continue
                x_value = round(float(line.split(None,1)[0].strip()),10)
                if self.curve_properties[curve].get("uncertainties",True) and self.curve_properties[curve].get("show_uncertainties",True):
                    counter += 1
                    y_value1 = float(line.split(None,1)[1].strip().split()[0])
                    y_value2 = float(line.split(None,1)[1].strip().split()[2])
                    y_value3 = float(line.split(None,1)[1].strip().split()[4])
                    if y_value1 == 0 or y_value2 == 0 or y_value3 == 0 or math.isnan(y_value1) or math.isnan(y_value2) or math.isnan(y_value3):
                        continue
                    # for histograms we have to skip every even line
                    if not "format" in self.curve_properties[curve] or self.curve_properties[curve]["format"] == "histogram":
                        if counter % 2 == 0: # if the counter is even
                            continue
                    y_values.extend([y_value1,y_value2,y_value3])
                    try:
                        y_norm = y_values_norm[x_value]
                    except:
                        y_norm = 0
                    if y_norm == 0 or math.isnan(x_value): # skip zero values in norm (will make an infinitely large plot)
                        continue
                    y_values_ratio.extend([y_value1/y_norm,y_value2/y_norm,y_value3/y_norm])
                else:
                    y_value = float(line.split(None,1)[1].strip().split()[0])
                    y_values.append(y_value)
                    try:
                        y_norm = y_values_norm[x_value]
                    except:
                        y_norm = 0
                    if y_norm == 0 or math.isnan(x_value): # skip zero values in norm (will make an infinitely large plot)
                        continue
                    y_values_ratio.append(y_value/y_norm)


        if not y_values or not y_values_ratio:
            return False
        xmin  = min(x_values)
        xmax  = max(x_values)
        xtics  = "" # let gnuplot decide the distance between xtics
        mxtics = "" # let gnuplot decide the distance between small xtics
        mytics = ""
        ymin  = ""#min(y_values)  
        ymax  = ""#math.ceil(max(y_values))#int(math.ceil(max(y_values) / 10.0)) * 10 # rounds to the closest multiple of 10
        ymin_ratio = max(min(y_values_ratio),0)  
        ymax_ratio = min(max(y_values_ratio),3)
        axis_dict["ymin_ratio"]   = self.plot_properties.get("ymin_ratio",ymin_ratio)
        axis_dict["ymax_ratio"]   = self.plot_properties.get("ymax_ratio",ymax_ratio)
        ytics_ratio = math.ceil((axis_dict["ymax_ratio"]-axis_dict["ymin_ratio"])/5*10)/10
        mytics_ratio= ytics_ratio/0.1

        axis_dict["xtics"]  = self.plot_properties.get("xtics",xtics)
        axis_dict["mxtics"] = self.plot_properties.get("mxtics",mxtics)
        axis_dict["xtics_ratio"]  = self.plot_properties.get("xtics",xtics)
        axis_dict["mxtics_ratio"] = self.plot_properties.get("mxtics",mxtics)
#        if not "ymin" in self.plot_properties and not "ymax" in self.plot_properties:
        axis_dict["mytics"] = self.plot_properties.get("mytics",mytics)
        axis_dict["xmin"]  = self.plot_properties.get("xmin",xmin)
        axis_dict["xmax"]  = self.plot_properties.get("xmax",xmax)
        axis_dict["ymin"]  = self.plot_properties.get("ymin",ymin)
        axis_dict["ymax"]  = self.plot_properties.get("ymax",ymax)
        axis_dict["ytics_ratio"]  = self.plot_properties.get("ytics_ratio",ytics_ratio)
        if not "ymin_ratio" in self.plot_properties and not "ymax_ratio" in self.plot_properties:
            axis_dict["mytics_ratio"] = self.plot_properties.get("mytics_ratio",mytics_ratio)
        else:
            axis_dict["mytics_ratio"] = self.plot_properties.get("mytics_ratio","")
#        axis_dict[""]  = self.plot_properties.get("",)
        return axis_dict
#}}}
#{{{ def: define_all_label_mappings(self)
    def define_all_label_mappings(self):
        # function that defines class dictionaries for the mappings from the distribution.dat file to the labels
        # distributiontype: mapping from distributiontype to the xlabel
        self.distributiontype_mapping = {}
        self.distributiontype_mapping["pT"]           = "p_{/Times=18 T}"
        self.distributiontype_mapping["pTveto"]       = "p\@_{/Times=18 T}^{veto}"
        self.distributiontype_mapping["pTmin"]        = "p\@_{/Times=18 T}_{min}"
        self.distributiontype_mapping["pTmax"]        = "p\@_{/Times=18 T}_{max}"
        self.distributiontype_mapping["m"]            = "m"
        self.distributiontype_mapping["phi"]          = "{/Symbol Dj}"
        self.distributiontype_mapping["eta"]          = "{/Symbol h}"
        self.distributiontype_mapping["y"]            = "y"
        self.distributiontype_mapping["mTATLAS"]      = "m\@_{/Times=18 T}^{/Times=18 ATLAS}"
        self.distributiontype_mapping["multiplicity"] = "#"
        
        # determine units for these distributions
        self.unit_mapping = {}
        self.unit_mapping["pT"]           = "GeV"
        self.unit_mapping["pTveto"]       = "GeV"
        self.unit_mapping["pTmin"]        = "GeV"
        self.unit_mapping["pTmax"]        = "GeV"
        self.unit_mapping["m"]            = "GeV"
#        self.unit_mapping["phi"]          = ""
#        self.unit_mapping["eta"]          = ""
#        self.unit_mapping["y"]            = ""
        self.unit_mapping["mTATLAS"]      = "GeV"
#        self.unit_mapping["multiplicity"] = ""

        # define nicer output for particles
        self.particle_mapping = {}
        self.particle_mapping["photon"] = "{/Symbol g}"
        self.particle_mapping["lep"]    = "l"
        self.particle_mapping["nclep"]  = "l^-"
        self.particle_mapping["pclep"]  = "l^+"
        self.particle_mapping["e"]      = "e"
        self.particle_mapping["em"]     = "e^-"
        self.particle_mapping["ep"]     = "e^+"
        self.particle_mapping["mu"]     = "{/Symbol m}"
        self.particle_mapping["tau"]    = "{/Symbol t}"
        self.particle_mapping["mum"]    = "{/Symbol m}^-"
        self.particle_mapping["mup"]    = "{/Symbol m}^+"
        self.particle_mapping["taum"]   = "{/Symbol g}^-"
        self.particle_mapping["taup"]   = "{/Symbol t}^+"
        self.particle_mapping["ljet"]   = "light-j"
        self.particle_mapping["jet"]    = "j"
        self.particle_mapping["bjet"]   = "b"
        self.particle_mapping["tjet"]   = "t/~t\342\200\276&{t}"
        self.particle_mapping["top"]    = "t"
        self.particle_mapping["atop"]   = "~t\342\200\276&{t}"
        self.particle_mapping["wm"]     = "W^-"
        self.particle_mapping["wp"]     = "W^+"
        self.particle_mapping["z"]      = "Z"
        self.particle_mapping["h"]      = "H"
        self.particle_mapping["nua"]    = "{/Symbol n/~n{/Times=26 \342\200\276}&{.}}"
        self.particle_mapping["nu"]     = "{/Symbol n}"
        self.particle_mapping["nux"]    = "{/Symbol ~n{/Times=26 \342\200\276}&{.}}"
        self.particle_mapping["nea"]    = "{/Symbol n^{/Times=26 e}/~n{/Times=26 \342\200\276}&{.}^{/Times=26 e}}"
        self.particle_mapping["ne"]     = "{/Symbol n^{/Times=26 e}}"
        self.particle_mapping["nex"]    = "{/Symbol ~n{/Times=26 \342\200\276}&{.}^{/Times=26 e}}"
        self.particle_mapping["nma"]    = "{/Symbol n^{m}/~n{/Times=26 \342\200\276}&{.}^{m}}"
        self.particle_mapping["nm"]     = "{/Symbol n^{m}}"
        self.particle_mapping["nmx"]    = "{/Symbol ~n{/Times=26 \342\200\276}&{.}^{m}}"
        self.particle_mapping["nta"]    = "{/Symbol n^{t}/~n{/Times=26 \342\200\276}&{.}^{t}}"
        self.particle_mapping["nt"]     = "{/Symbol n^{t}}"
        self.particle_mapping["ntx"]    = "{/Symbol ~n{/Times=26 \342\200\276}&{.}^{t}}"
#}}}

#}}}


if __name__ == "__main__":
#    all_plots = glob.iglob(pjoin(os.getcwd(),"MATRIX_NNLO_31_inclusive_sumETscale-run/distributions/*.dat"))
    all_plots = glob.iglob(pjoin(os.getcwd(),"datfiles/nov8-collectDAT/CAFC-RFvar-merge2-run/distributions/*.dat"))
#    all_plots = glob.iglob(pjoin(os.getcwd(),"run_nnpdf31_new_kq05_inclusive_lhef-run/distributions/*.dat"))

    out = print_output()
    gnu = gnuplot(os.getcwd())
    gnu.clean_gnuplot_folder()
    for plot in all_plots:
        
        if "debug" in plot:
            continue

        gnu = gnuplot(os.getcwd())
        
#        plot_MATRIX_NNLO = plot
#        plot_MATRIX_NNLO_30 = plot.replace("MATRIX_NNLO-run", "MATRIX_NNLO_30-run")
#        plot_MATRIX_NNLO_31_inclusive = plot.replace("MATRIX_NNLO-run", "MATRIX_NNLO_31_inclusive-run")

#        plot_MATRIX_NNLO_31_inclusive_mT = plot
#        plot_MATRIX_NNLO_31_inclusive_Q = plot.replace("MATRIX_NNLO_31_inclusive_mTscale", "MATRIX_NNLO_31_inclusive_Qscale").replace("NNLO_QCD","NNLO_QCD_Qscale")
#        plot_MATRIX_NNLO_31_inclusive_fixed = plot.replace("MATRIX_NNLO_31_inclusive_mTscale", "MATRIX_NNLO_31_inclusive_fixedscale").replace("NNLO_QCD","NNLO_QCD_fixedscale")
#        plot_MATRIX_NNLO_31_inclusive_sumET = plot.replace("MATRIX_NNLO_31_inclusive_mTscale", "MATRIX_NNLO_31_inclusive_sumETscale").replace("NNLO_QCD","NNLO_QCD_sumETscale")
#        plot_MATRIX_NNLO_31_inclusive_sumET = plot
#        plot_exact = plot
        plot_scales = plot
        plot_eta = plot.replace("RFvar","ETvar")
#        plot_Ht4 = plot.replace("PSfin-4FS-mh40-minnlo","PSfin-4FS-Ht40-minnlo")
#        plot_5fs = plot.replace("MiNNLO4FSLHE16aug","MiNNLO5FSLHE")
#        plot_minnlofo = plot.replace("pths-h50-k025-lhe","FOhs-h50-k025-lhe").replace("MiNNLOlhe1","MiNNLOlhe2")
#        plot_minnlolhefo = plot.replace("NNLLKQ05-run","FOh00-k05-clhe").replace("NNLLKQ05","MiNNLOlhe3")
#        plot_nnlo5 = plot.replace("MiNNLO5FS-bjet","MiNNLO-test14jul") 
#        plot_minnlo2= plot.replace("NNLO_NNLL_k025_zoom-run","pt-h50-k025-lhe").replace("NNLO_NNLL_k025_zoom","MiNNLOlhe1")
#        plot_minnlo1= plot.replace("NNLO_NNLL_k025_zoom-run","pt51-k025-lhe").replace("NNLO_NNLL_k025_zoom","MiNNLOlhe4") 
#        plot_nnll= plot.replace("NNLOmw-run","NNLO_NNLLmw-run").replace("NNLOmw","NNLO_NNLLmw")
#        plot_minnlo2= plot.replace("NNLO-NNLL-40","NNPDF40-pt51-k025-lhe").replace("MW","MiNNLOlhe2")
#        plot_4= plot.replace("FO40-h51-k025-Mpy6","FO40-h51-k075-Mpy1").replace("MiNNLOpy6","MiNNLOpy1")
#        plot_3= plot.replace("NNPDF40-FO51-k025","NNPDF40-FO51-k05").replace("MW","MiNNLOpy")
#        plot_4= plot.replace("NNPDF40-FO51-k025","NNPDF40-FO51-k075").replace("MiNNLOpy3","MiNNLOpy5")
#        plot_4= plot.replace("PY0-run","PY1-r01-run").replace("PY0","PY1-r01")
#        plot_lhe =  plot.replace("LHE-mh125", "LHE-mh200").replace("MiNNLOlhe","MiNNLOphe")
#        plot_tre =  plot.replace("NNPDF30-FO51", "NNPDF30-pt51").replace("MiNNLO1","MiNNLO2")

        # plot_third_run_lhef = plot.replace("MATRIX_NNLO", "third_run_lhef").replace("NNLO_QCD","run_nnpdf31_new_inclusive_lhef")
        # plot_third_run_high_stat_lhef = plot.replace("MATRIX_NNLO", "third_run_high_stat_lhef").replace("NNLO_QCD","run_nnpdf31_new_inclusive_lhef")
        # plot_run_nnpdf31_lhef = plot.replace("MATRIX_NNLO", "run_nnpdf31_lhef").replace("NNLO_QCD","run_nnpdf31_new_inclusive_lhef")
        # plot_run_nnpdf31_high_stat_lhef = plot.replace("MATRIX_NNLO", "run_nnpdf31_high_stat_lhef").replace("NNLO_QCD","run_nnpdf31_new_inclusive_lhef")
        # plot_run_nnpdf31_new_lhef = plot.replace("MATRIX_NNLO", "run_nnpdf31_new_lhef").replace("NNLO_QCD","run_nnpdf31_new_inclusive_lhef")
        # plot_run_nnpdf31_new_kq05_lhef = plot.replace("MATRIX_NNLO", "run_nnpdf31_new_kq05_lhef").replace("NNLO_QCD","run_nnpdf31_new_kq05_inclusive_lhef")
        # plot_run_nnpdf31_new_inclusive_lhef = plot.replace("MATRIX_NNLO_31_inclusive_mTscale", "run_nnpdf31_new_kq1_inclusive_lhef").replace("NNLO_QCD","run_nnpdf31_new_kq1_inclusive_lhef")
#        plot_run_nnpdf31_new_kq05_inclusive_lhef = plot.replace("MATRIX_NNLO_31_inclusive_sumETscale-run", "run_nnpdf31_new_kq05_inclusive_lhef-run").replace("__NNLO_QCD_sumETscale","__run_nnpdf31_new_kq05_inclusive_lhef")
#        plot_run_nnpdf31_new_kq05_inclusive_final_lhef = plot.replace("MATRIX_NLOqq_EW_incl_sum-run", "NLO_lhef-run").replace("__NLOqq_EW","__NLO_lhef")




        counter = 0

###################OLD RESULTS
#        if os.path.exists(plot_third_run_lhef):
#            gnu.add_curve(plot_third_run_lhef,{"format" : "histogram", "label" : "MiNNLO_{PS}","line_style" : 1})
#        if os.path.exists(plot_third_run_high_stat_lhef):
#            gnu.add_curve(plot_third_run_high_stat_lhef,{"format" : "histogram", "label" : "MiNNLO_{PS}","line_style" : 1})
#        if os.path.exists(plot_run_nnpdf31_lhef):
#            gnu.add_curve(plot_run_nnpdf31_lhef,{"format" : "histogram", "label" : "MiNNLO_{PS} low","line_style" : 3})
#        if os.path.exists(plot_run_nnpdf31_high_stat_lhef):
#            gnu.add_curve(plot_run_nnpdf31_high_stat_lhef,{"format" : "histogram", "label" : "MiNNLO_{PS} high","line_style" : 3}) #wrong

################## NEW RESULTS

#        print plot_run_nnpdf31_new_kq05_inclusive_final_lhef
#        if os.path.exists(plot_run_nnpdf31_new_kq05_inclusive_final_lhef): #new results
#            gnu.add_curve(plot_run_nnpdf31_new_kq05_inclusive_final_lhef,{"format" : "histogram", "label" : "NLO_{EW}+PS (LHE)","line_style" : 1})
#        if os.path.exists(plot_run_nnpdf31_new_inclusive_lhef):
#            gnu.add_curve(plot_run_nnpdf31_new_inclusive_lhef,{"format" : "histogram", "label" : "MiNNLO_{PS} kq1","line_style" : 2})

#        gnu.add_curve(plot_lhe,{"format" : "histogram", "label" : "mh=200 (NNPDF30-FO)","line_style" : 3})

#        gnu.add_curve(plot_3,{"format" : "histogram", "label" : "NNPDF40-FO51 kq=1.0","line_style" : 3}
#        gnu.add_curve(plot_nnll,{"format" : "histogram", "label" : "NNLO-NNLL' (MW)","line_style" : 2})
#        gnu.add_curve(plot_2,{"format" : "histogram", "label" : "MW K_Q=0.25","line_style" : 3})
#        gnu.add_curve(plot_minnlopt,{"format" : "histogram", "label" : "MiNNLO K_Q=0.25 (LHE)","line_style" : 1})
#        gnu.add_curve(plot_exact,{"format" : "histogram", "label" : "NLO_{PS} (exact)","line_style" : 1})
        gnu.add_curve(plot_scales,{"format" : "histogram", "label" : "MiNNLO_{PS} (CA_{FC}, RF)","line_style" : 2})
        gnu.add_curve(plot_eta,{"format" : "histogram", "label" : "MiNNLO_{PS} (CA_{FC}, ET)","line_style" : 1})
#        gnu.add_curve(plot_etaH,{"format" : "histogram", "label" : "MiNNLO_{PS} (SA, Q/2)","line_style" : 1})
#        gnu.add_curve(plot_Ht4,{"format" : "histogram", "label" : "MiNNLO_{PS} (4FS, {/Symbol m}_R^{(0),y}=H_T/4)","line_style" : 2})
#        gnu.add_curve(plot_5fs,{"format" : "histogram", "label" : "MiNNLOPS 5FS (LHE)","line_style" : 1})
#        gnu.add_curve(plot_minnlolhefo,{"format" : "histogram", "label" : "MiNNLO-FOatQ K_Q=0.5","line_style" : 3})
#        gnu.add_curve(plot_nnlo5,{"format" : "histogram", "label" : "MiNNLO-qp","line_style" : 3})
#        gnu.add_curve(plot_minnlopypt,{"format" : "histogram", "label" : "MiNNLO_{PS} {/Courier FOatQ} (LHE)","line_style" : 4})
#        gnu.add_curve(plot_3,{"format" : "histogram", "label" : "MiNNLO_{PS} FO51 K_Q=0.5","line_style" : 2})
##        gnu.add_curve(plot_4,{"format" : "histogram", "label" : "MiNNLO_{PS} K_Q=0.75","line_style" : 3})
#        gnu.add_curve(plot_3,{"format" : "histogram", "label" : "PWGFO-PY8 (dipole=1, r=0.4)","line_style" : 3})
#        gnu.add_curve(plot_4,{"format" : "histogram", "label" : "FO51-PY8 (dipole=1, r=0.1)","line_style" : 4})
#        gnu.add_curve(plot_4,{"format" : "histogram", "label" : "NNPDF40-FO51 kq=0.75","line_style" : 4})


#        if os.path.exists(plot_MATRIX_NNLO_31_inclusive_Q): #scale Q of WZ system
#            gnu.add_curve(plot_MATRIX_NNLO_31_inclusive_Q,{"format" : "histogram", "label" : "MATRIX incl, Q","line_style" : 3})
#        if os.path.exists(plot_MATRIX_NNLO_31_inclusive_mT): #scale mT^2=Q^2+pt^2 of WZ system
#            gnu.add_curve(plot_MATRIX_NNLO_31_inclusive_mT,{"format" : "histogram", "label" : "MATRIX incl, mT","line_style" : 4})
#        if os.path.exists(plot_MATRIX_NNLO_31_inclusive_fixed): #scale 0.5*(mw+mz) 
#            gnu.add_curve(plot_MATRIX_NNLO_31_inclusive_fixed,{"format" : "histogram", "label" : "MATRIX incl, fixed","line_style" : 5})
#        if os.path.exists(plot_MATRIX_NNLO_31_inclusive_sumET): #scale 0.5*(sqrt(m_ee^2+pT_ee^2)+sqrt(m_munu^2+pT_munu^2))  #final MATRIX result
#            gnu.add_curve(plot_MATRIX_NNLO_31_inclusive_sumET,{"format" : "histogram", "label" : "NLO_{EW} (MATRIX)","line_style" : 3})



#        if os.path.exists(plot_MATRIX_NNLO): #nnpdf31, with cuts
#            gnu.add_curve(plot_MATRIX_NNLO,{"format" : "histogram", "label" : "MATRIX","line_style" : 2})
#        if os.path.exists(plot_MATRIX_NNLO_30):
#            gnu.add_curve(plot_MATRIX_NNLO_30,{"format" : "histogram", "label" : "MATRIX 30","line_style" : 4})


        gnu.set_plot_properties("normalization",1)
        gnu.set_plot_properties("ymin_ratio",0.8)
        gnu.set_plot_properties("ymax_ratio",1.2)
        gnu.set_plot_properties("ytics_ratio",0.1)
#        if not gnu.get_name().startswith("ATLAS_") and not gnu.get_name().startswith("total_"):
#            gnu.set_plot_properties("rebin",1)
        # if gnu.get_name().startswith("ATLAS_"):
        #     continue
        # if "j1" in plot or "j2" in plot:
        #     continue



        if gnu.get_name().startswith("xsec"):
            gnu.set_plot_properties("xlabel","total")
            
        if gnu.get_name().startswith("ptHiggs"):
            gnu.set_plot_properties("xlabel","p_{T,H}")
            gnu.set_plot_properties("yunit","[fb/GeV]")
            gnu.set_plot_properties("xunit","GeV")
            gnu.set_plot_properties("xmin",0)
            gnu.set_plot_properties("xmax",800)
            gnu.set_plot_properties("rebin_above_x",4)
            gnu.set_plot_properties("min_x_for_rebin",400)
            gnu.set_plot_properties("ytics_ratio",0.1)
            gnu.set_plot_properties("mytics_ratio",1)

        if gnu.get_name().startswith("etaHiggs"):
            gnu.set_plot_properties("xlabel","{/Symbol h}_{H}")
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("yunit","[fb]")
            gnu.set_plot_properties("legend","down center")

        if gnu.get_name().startswith("yHiggs"):
            gnu.set_plot_properties("xlabel","y_{H}")
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("yunit","[fb]")
            gnu.set_plot_properties("xmin",-2)
            gnu.set_plot_properties("xmax",2)
            gnu.set_plot_properties("rebin",1)
            gnu.set_plot_properties("legend","down center")

        if gnu.get_name().startswith("massHiggs"):
            gnu.set_plot_properties("xlabel","m_{H}")
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("yunit","[fb/GeV]")
            gnu.set_plot_properties("xmin",110)

#------------------------------------------------------------------------------------
        if gnu.get_name().startswith("detaHiggstop"):
            gnu.set_plot_properties("xlabel","{/Symbol D}{/Symbol h}_{H,t}")
            gnu.set_plot_properties("yunit","[fb]")
            gnu.set_plot_properties("legend","down center")

        if gnu.get_name().startswith("dyHiggstop"):
            gnu.set_plot_properties("xlabel","{/Symbol D}{y}_{H,t}")
            gnu.set_plot_properties("yunit","[fb]")
            gnu.set_plot_properties("legend","down center")
            
        if gnu.get_name().startswith("dphiHiggstop"):
            gnu.set_plot_properties("xlabel","{/Symbol D}{/Symbol f}_{H,t}")
            gnu.set_plot_properties("yunit","[fb]")
            gnu.set_plot_properties("legend","down center")
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("ymin",0)
            
        if gnu.get_name().startswith("R_etaHiggstop"):
            gnu.set_plot_properties("xlabel","{/Symbol D}{R^{/Symbol h}}_{H,t}")
            gnu.set_plot_properties("yunit","[fb]")
            gnu.set_plot_properties("legend","down center")

        if gnu.get_name().startswith("R_yHiggstop"):
            gnu.set_plot_properties("xlabel","{/Symbol D}{R^y}_{H,t}")
            gnu.set_plot_properties("yunit","[fb]")
            gnu.set_plot_properties("legend","down center")

#-------------------------------------------------------------------------------

        if gnu.get_name().startswith("detaHiggstbar"):
            gnu.set_plot_properties("xlabel","{/Symbol D}{/Symbol h}_{H,{/b t\u0305}}")
            gnu.set_plot_properties("yunit","[fb]")
            gnu.set_plot_properties("legend","down center")

        if gnu.get_name().startswith("dyHiggstbar"):
            gnu.set_plot_properties("xlabel","{/Symbol D}{y}_{H,{/b t\u0305}}")
            gnu.set_plot_properties("yunit","[fb]")
            gnu.set_plot_properties("legend","down center")
            
        if gnu.get_name().startswith("dphiHiggstbar"):
            gnu.set_plot_properties("xlabel","{/Symbol D}{/Symbol f}_{H,{/b t\u0305}}")
            gnu.set_plot_properties("yunit","[fb]")
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("ymin",0)
            gnu.set_plot_properties("legend","down center")
            
        if gnu.get_name().startswith("R_etaHiggstbar"):
            gnu.set_plot_properties("xlabel","{/Symbol D}{R^{/Symbol h}}_{H,{/b t\u0305}}")
            gnu.set_plot_properties("yunit","[fb]")
            gnu.set_plot_properties("legend","down center")

        if gnu.get_name().startswith("R_yHiggstbar"):
            gnu.set_plot_properties("xlabel","{/Symbol D}{R^y}_{H,{/b t\u0305}}")
            gnu.set_plot_properties("yunit","[fb]")
            gnu.set_plot_properties("legend","down center")

#---------------------------------------------------------------------------------------------

        if gnu.get_name().startswith("ptHiggs+top+tbar"):
            gnu.set_plot_properties("xlabel","p_{T,t{/b t\u0305}H}")
            gnu.set_plot_properties("yunit","[fb/GeV]")
            gnu.set_plot_properties("xunit","GeV")
            gnu.set_plot_properties("xmin",0)
#            gnu.set_plot_properties("xmax",800)
            gnu.set_plot_properties("rebin_above_x",4)
            gnu.set_plot_properties("min_x_for_rebin",400)
            
        if gnu.get_name().startswith("massHiggs+top+tbar"):
            gnu.set_plot_properties("xlabel","m_{t{/b t\u0305}H}")
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("yunit","[fb/GeV]")
            gnu.set_plot_properties("xmin",450)
            gnu.set_plot_properties("legend","down center")

        if gnu.get_name().startswith("pttop"):
            gnu.set_plot_properties("xlabel","p_{T,t}")
            gnu.set_plot_properties("yunit","[fb/GeV]")
            gnu.set_plot_properties("xunit","GeV")
            gnu.set_plot_properties("xmin",0)
            gnu.set_plot_properties("xmax",800)
            gnu.set_plot_properties("rebin_above_x",4)
            gnu.set_plot_properties("min_x_for_rebin",400)

        if gnu.get_name().startswith("pttbar"):
            gnu.set_plot_properties("xlabel","p_{T,{/b t\u0305}}")
            gnu.set_plot_properties("yunit","[fb/GeV]")
            gnu.set_plot_properties("xunit","GeV")
            gnu.set_plot_properties("xmin",0)
            gnu.set_plot_properties("xmax",800)
            gnu.set_plot_properties("rebin_above_x",4)
            gnu.set_plot_properties("min_x_for_rebin",400)
#---------------------------------------------------------------------------------------------
            
        if gnu.get_name().startswith("etatop"):
            gnu.set_plot_properties("xlabel","{/Symbol h}_{t}")
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("yunit","[fb]")
            gnu.set_plot_properties("legend","down center")
            gnu.set_plot_properties("ymax",150)

        if gnu.get_name().startswith("etatbar"):
            gnu.set_plot_properties("xlabel","{/Symbol h}_{{/b t\u0305}}")
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("yunit","[fb]")
            gnu.set_plot_properties("legend","down center")
            gnu.set_plot_properties("ymax",150)

        if gnu.get_name().startswith("ytop"):
            gnu.set_plot_properties("xlabel","y_{t}")
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("yunit","[fb]")
            gnu.set_plot_properties("legend","down center")
            gnu.set_plot_properties("xmin",-3)
            gnu.set_plot_properties("xmax",3)

        if gnu.get_name().startswith("ytbar"):
            gnu.set_plot_properties("xlabel","y_{{/b t\u0305}}")
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("yunit","[fb]")
            gnu.set_plot_properties("legend","down center")
            gnu.set_plot_properties("ymin",-50)
            gnu.set_plot_properties("xmin",-3)
            gnu.set_plot_properties("xmax",3)

#---------------------------------------------------------------------------------------------            
            
        if gnu.get_name().startswith("masst+tbar"):
            gnu.set_plot_properties("xlabel","m_{t{/b t\u0305}}")
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("yunit","[fb/GeV]")
            gnu.set_plot_properties("xmin",320)

        if gnu.get_name().startswith("ptt+tbar"):
            gnu.set_plot_properties("xlabel","p_{T,t{/b t\u0305}}")
            gnu.set_plot_properties("yunit","[fb/GeV]")
            gnu.set_plot_properties("xunit","GeV")
            gnu.set_plot_properties("xmin",0)
            gnu.set_plot_properties("xmax",800)
            gnu.set_plot_properties("rebin_above_x",4)
            gnu.set_plot_properties("min_x_for_rebin",400)

        if gnu.get_name().startswith("detattbar"):
            gnu.set_plot_properties("xlabel","{/Symbol D}{/Symbol h}_{t,{/b t\u0305}}")
            gnu.set_plot_properties("yunit","[fb]")
            gnu.set_plot_properties("legend","down center")

        if gnu.get_name().startswith("dyttbar"):
            gnu.set_plot_properties("xlabel","{/Symbol D}{y}_{t,{/b t\u0305}}")
            gnu.set_plot_properties("yunit","[fb]")
            gnu.set_plot_properties("legend","down center")
            
        if gnu.get_name().startswith("dphittbar"):
            gnu.set_plot_properties("xlabel","{/Symbol D}{/Symbol f}_{t,{/b t\u0305}}")
            gnu.set_plot_properties("yunit","[fb]")
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("legend","left")

            
        if gnu.get_name().startswith("R_etattbar"):
            gnu.set_plot_properties("xlabel","{/Symbol D}{R^{/Symbol h}}_{t,{/b t\u0305}}")
            gnu.set_plot_properties("yunit","[fb]")
            gnu.set_plot_properties("legend","down center")

        if gnu.get_name().startswith("R_yttbar"):
            gnu.set_plot_properties("xlabel","{/Symbol D}{R^y}_{t,{/b t\u0305}}")
            gnu.set_plot_properties("yunit","[fb]")
            gnu.set_plot_properties("legend","down center")

# -----------------------------------------------------------------------------------------------

        if gnu.get_name().startswith("R_etattbarHiggs"):
            gnu.set_plot_properties("xlabel","{/Symbol D}{R^{/Symbol h}}_{t{/b t\u0305},H}")
            gnu.set_plot_properties("yunit","[fb]")
            gnu.set_plot_properties("legend","down center")

        if gnu.get_name().startswith("R_yttbarHiggs"):
            gnu.set_plot_properties("xlabel","{/Symbol D}{R^y}_{t{/b t\u0305},H}")
            gnu.set_plot_properties("yunit","[fb]")
            gnu.set_plot_properties("legend","down center")





















            


        if gnu.get_name().startswith("pt_j1_"):
            gnu.set_plot_properties("yunit","[fb/GeV]")
            gnu.set_plot_properties("xlabel","p_{T,j_{1}}")
            gnu.set_plot_properties("min_x_for_rebin",140)
            gnu.set_plot_properties("rebin_above_x",4)
            gnu.set_plot_properties("xmax",300)
        
        if gnu.get_name().startswith("pt_j1-zoom"):
            gnu.set_plot_properties("yunit","[fb/GeV]")
            gnu.set_plot_properties("xlabel","p_{T,j_{1}}")
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("xmin",6)
        
        if gnu.get_name().startswith("pt_j2_"):
            gnu.set_plot_properties("yunit","[fb/GeV]")
            gnu.set_plot_properties("xlabel","p_{T,j_{2}}")
            gnu.set_plot_properties("min_x_for_rebin",140)
            gnu.set_plot_properties("rebin_above_x",4)
            gnu.set_plot_properties("xmax",300)
        
        if gnu.get_name().startswith("pt_j2-zoom"):
            gnu.set_plot_properties("yunit","[fb/GeV]")
            gnu.set_plot_properties("xlabel","p_{T,j_{2}}")
            gnu.set_plot_properties("logscale_y",False)

        if gnu.get_name().startswith("pt_H-ptj30"):
            gnu.set_plot_properties("xlabel","p_{T,H}")
            gnu.set_plot_properties("xmax",450)
            gnu.set_plot_properties("min_x_for_rebin",250)
            gnu.set_plot_properties("rebin_above_x",4)
            gnu.set_plot_properties("category","p_{T,j_1}>30GeV, |{/Symbol h}_{j_1}|<4.5")
            
        if gnu.get_name().startswith("pt_H-ptj60"):
            gnu.set_plot_properties("xlabel","p_{T,H}")
            gnu.set_plot_properties("xmax",450)
            gnu.set_plot_properties("min_x_for_rebin",250)
            gnu.set_plot_properties("rebin_above_x",4)
            gnu.set_plot_properties("category","p_{T,j_1}>60GeV, |{/Symbol h}_{j_1}|<4.5")

#---------------------------------------------------------------------------------------------

        if gnu.get_name().startswith("dyHj1"):
            gnu.set_plot_properties("xlabel","{/Symbol D}y_{H,j1}")
            gnu.set_plot_properties("rebin",4)
            gnu.set_plot_properties("legend","down center")

        if gnu.get_name().startswith("detaHj1"):
            gnu.set_plot_properties("xlabel","{/Symbol D}{/Symbol h}_{H,j1}")
            gnu.set_plot_properties("rebin",3)
            gnu.set_plot_properties("ymax_ratio",1.3)
            gnu.set_plot_properties("ymin_ratio",0.5)
            gnu.set_plot_properties("legend","down center")
        
        if gnu.get_name().startswith("dphiHj1"):
            gnu.set_plot_properties("xlabel","{/Symbol D}{/Symbol f}_{Hj_1}")
            gnu.set_plot_properties("legend","left")

        if gnu.get_name().startswith("drHj1"):
            gnu.set_plot_properties("xlabel","{/Symbol D}R_{H,j1}")
            gnu.set_plot_properties("legend","left")
        

#-------------------------------------------------------------------------------------------
        if gnu.get_name().startswith("y_j1-ptj30"):
            gnu.set_plot_properties("xlabel","y_{j_1}")
            gnu.set_plot_properties("category","p_{T,j_1}>30 GeV")
            gnu.set_plot_properties("xmin",-4)
            gnu.set_plot_properties("xmax",4)
            gnu.set_plot_properties("rebin",4)
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("legend","down center")

        if gnu.get_name().startswith("y_j1-ptj60"):
            gnu.set_plot_properties("xlabel","y_{j_1}")
            gnu.set_plot_properties("category","p_{T,j_1}>60 GeV")
            gnu.set_plot_properties("xmin",-4)
            gnu.set_plot_properties("xmax",4)
            gnu.set_plot_properties("rebin",4)
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("legend","down center")

#-------------------------------------------------------------------------------------------

        if gnu.get_name().startswith("total-EXP-1bjet"):
            gnu.set_plot_properties("xlabel","total")
            gnu.set_plot_properties("category","1 b-j_{EXP}")
            gnu.set_plot_properties("categoryleft","p_{T,bj} > 30 GeV,\\ |{/Symbol h}_{bj}| < 2.4")
            
        if gnu.get_name().startswith("total-EXP-2bjet"):
            gnu.set_plot_properties("xlabel","total")
            gnu.set_plot_properties("category","2 bj_{EXP}")
            gnu.set_plot_properties("categoryleft","p_{T,bj} > 30 GeV,\\ |{/Symbol h}_{bj}| < 2.4")

        if gnu.get_name().startswith("total-1lightEXP"):
            gnu.set_plot_properties("xlabel","total")
            gnu.set_plot_properties("category","1 lj_{EXP}")

        if gnu.get_name().startswith("total-NAI-1bjet"):
            gnu.set_plot_properties("xlabel","total")
            gnu.set_plot_properties("category","1 bj_{NAI}")
            gnu.set_plot_properties("categoryleft","p_{T,bj} > 30 GeV,\\ |{/Symbol h}_{bj}| < 2.4")
            
        if gnu.get_name().startswith("total-NAI-2bjet"):
            gnu.set_plot_properties("xlabel","total")
            gnu.set_plot_properties("category","2 bj_{NAI}")
            gnu.set_plot_properties("categoryleft","p_{T,bj} > 30 GeV,\\ |{/Symbol h}_{bj}| < 2.4")

        if gnu.get_name().startswith("total-1lightNAI"):
            gnu.set_plot_properties("xlabel","total")
            gnu.set_plot_properties("category","1 lj_{NAI}")
            
        if gnu.get_name().startswith("total-1lightIFN"):
            gnu.set_plot_properties("xlabel","total")
            gnu.set_plot_properties("category","1 lj_{IFN}")
            
        if gnu.get_name().startswith("total-IFN-1bjet"):
            gnu.set_plot_properties("xlabel","total")
            gnu.set_plot_properties("category","1 bj_{IFN}")
            
        if gnu.get_name().startswith("total-IFN-2bjet"):
            gnu.set_plot_properties("xlabel","total")
            gnu.set_plot_properties("category","2 bj_{IFN}")

        if gnu.get_name().startswith("total-lightEXP-ptj30"):
            gnu.set_plot_properties("xlabel","total")
            gnu.set_plot_properties("category","p_{T,lj_{EXP}}>30 GeV")

        if gnu.get_name().startswith("total-lightEXP-ptj60"):
            gnu.set_plot_properties("xlabel","total")
            gnu.set_plot_properties("category","p_{T,lj_{EXP}}>60 GeV")

        if gnu.get_name().startswith("total-lightNAI-ptj30"):
            gnu.set_plot_properties("xlabel","total")
            gnu.set_plot_properties("category","p_{T,lj_{NAI}}>30 GeV")

        if gnu.get_name().startswith("total-lightNAI-ptj60"):
            gnu.set_plot_properties("xlabel","total")
            gnu.set_plot_properties("category","p_{T,lj_{NAI}}>60 GeV")
            
        if gnu.get_name().startswith("total-lightIFN-ptj30"):
            gnu.set_plot_properties("xlabel","total")
            gnu.set_plot_properties("category","p_{T,lj_{IFN}}>30 GeV")

        if gnu.get_name().startswith("total-lightIFN-ptj60"):
            gnu.set_plot_properties("xlabel","total")
            gnu.set_plot_properties("category","p_{T,lj_{IFN}}>60 GeV")
            
        if gnu.get_name().startswith("total-EXP_"):
            gnu.set_plot_properties("xlabel","total")
            gnu.set_plot_properties("category","p_{T,j_{EXP}}>30 GeV, |{/Symbol h}|<2.4")

        if gnu.get_name().startswith("total-IFN_"):
            gnu.set_plot_properties("xlabel","total")
            gnu.set_plot_properties("category","p_{T,j_{IFN}}>30 GeV, |{/Symbol h}|<2.4")
            
        if gnu.get_name().startswith("total-NAI_"):
            gnu.set_plot_properties("xlabel","total")
            gnu.set_plot_properties("category","p_{T,j_{NAI}}>30 GeV, |{/Symbol h}|<2.4")

        if gnu.get_name().startswith("total-ptj30"):
            gnu.set_plot_properties("xlabel","total")
            gnu.set_plot_properties("category","p_{T,j}>30 GeV, |{/Symbol h}|<4.5")
        
        if gnu.get_name().startswith("total-ptj60"):
            gnu.set_plot_properties("xlabel","total")
            gnu.set_plot_properties("category","p_{T,j}>60 GeV, |{/Symbol h}|<4.5")

#-------------------------------------------------------------------------------------------

        if gnu.get_name().startswith("pt_H-EXP-1bjet"):
            gnu.set_plot_properties("xlabel","p_{T,H}")
            gnu.set_plot_properties("xunit","GeV")
            gnu.set_plot_properties("yunit","[fb/GeV]")
            gnu.set_plot_properties("category","1 bj_{EXP}")
            gnu.set_plot_properties("ymax",1000)
            gnu.set_plot_properties("xmin",20)
            gnu.set_plot_properties("categoryleft","p_{T,bj} > 30 GeV")
            gnu.set_plot_properties("categorydownleft","|{/Symbol h}|_{bj} < 2.4")
            gnu.set_plot_properties("ymin_ratio",0.7)
            gnu.set_plot_properties("ymax_ratio",1.3)


        if gnu.get_name().startswith("pt_H-EXP-2bjet"):
            gnu.set_plot_properties("xlabel","p_{T,H}")
            gnu.set_plot_properties("category","2 bj_{EXP}")
            gnu.set_plot_properties("ymax","1")
            gnu.set_plot_properties("xmin",10)
            
        if gnu.get_name().startswith("pt_H-IFN-1bjet"):
            gnu.set_plot_properties("xlabel","p_{T,H}")
            gnu.set_plot_properties("category","1 bj_{IFN}")
            gnu.set_plot_properties("ymax",150)
            gnu.set_plot_properties("xmin",20)

        if gnu.get_name().startswith("pt_H-IFN-2bjet"):
            gnu.set_plot_properties("xlabel","p_{T,H}")
            gnu.set_plot_properties("category","2 bj_{IFN}")
            gnu.set_plot_properties("ymax","1")
            gnu.set_plot_properties("xmin",10)

        if gnu.get_name().startswith("pt_H-NAI-1bjet"):
            gnu.set_plot_properties("xlabel","p_{T,H}")
            gnu.set_plot_properties("category","1 bj_{NAI}")
            gnu.set_plot_properties("ymax",150)
            gnu.set_plot_properties("xmin",20)

        if gnu.get_name().startswith("pt_H-NAI-2bjet"):
            gnu.set_plot_properties("xlabel","p_{T,H}")
            gnu.set_plot_properties("category","2 bj_{NAI}")
            gnu.set_plot_properties("ymax","1")
            gnu.set_plot_properties("xmin",10)
            
        if gnu.get_name().startswith("pt_bjet1-EXP-1bjet"):
            gnu.set_plot_properties("xlabel","p_{T,bj_{1,EXP}}")
            gnu.set_plot_properties("category","1 bj_{EXP}")
            gnu.set_plot_properties("ymax",100)
            gnu.set_plot_properties("categoryleft","p_{T,bj} > 30 GeV,\\ |{/Symbol h}_{bj}| < 2.4")

        if gnu.get_name().startswith("pt_bjet1-IFN-1bjet"):
            gnu.set_plot_properties("xlabel","p_{T,bj_{1,IFN}}")
            gnu.set_plot_properties("category","1 bj_{IFN}")
            gnu.set_plot_properties("ymax",100)

        if gnu.get_name().startswith("pt_bjet1-NAI-1bjet"):
            gnu.set_plot_properties("xlabel","p_{T,bj_{1,IFN}}")
            gnu.set_plot_properties("category","1 bj_{NAI}")
            gnu.set_plot_properties("ymax",100)
 
        if gnu.get_name().startswith("pt_bjet2-EXP-2bjet"):
            gnu.set_plot_properties("xlabel","p_{T,bj_{2,EXP}}")
            gnu.set_plot_properties("category","2 bj_{EXP}")
            gnu.set_plot_properties("ymax",10)

        if gnu.get_name().startswith("pt_bjet2-IFN-2bjet"):
            gnu.set_plot_properties("xlabel","p_{T,bj_{2,IFN}}")
            gnu.set_plot_properties("category","2 bj_{IFN}")
            gnu.set_plot_properties("ymax",10)

        if gnu.get_name().startswith("pt_bjet2-NAI-2bjet"):
            gnu.set_plot_properties("xlabel","p_{T,bj_{2,NAI}}")
            gnu.set_plot_properties("category","2 bj_{NAI}")
            gnu.set_plot_properties("ymax",10)

#------------------------------------------------------------------------------

        if gnu.get_name().startswith("dR_H_bjet1-EXP-1bjet"):
            gnu.set_plot_properties("xlabel","{/Symbol D}R_{H,bj_{1}}")
            gnu.set_plot_properties("category","1 bj_{EXP}")
            gnu.set_plot_properties("ymax",1000)
#            gnu.set_plot_properties("legend","down center")
            gnu.set_plot_properties("categoryleft","p_{T,bj} > 30 GeV")
            gnu.set_plot_properties("categorydownleft","|{/Symbol h}|_{bj} < 2.4")
            gnu.set_plot_properties("ymax_ratio",1.3)

        if gnu.get_name().startswith("dR_H_bjet1-IFN-1bjet"):
            gnu.set_plot_properties("xlabel","{/Symbol D}R_{H,bj_{1,IFN}}")
            gnu.set_plot_properties("category","1 bj_{IFN}")
            gnu.set_plot_properties("ymax",1000)
            gnu.set_plot_properties("legend","down center")
            
        if gnu.get_name().startswith("dR_H_bjet1-NAI-1bjet"):
            gnu.set_plot_properties("xlabel","{/Symbol D}R_{H,bj_{1,NAI}}")
            gnu.set_plot_properties("category","1 bj_{NAI}")
            gnu.set_plot_properties("ymax",1000)
            gnu.set_plot_properties("legend","down center")

        if gnu.get_name().startswith("dy_H_bjet1-EXP-1bjet"):
            gnu.set_plot_properties("xlabel","{/Symbol D}y_{H,bj_{1}}")
            gnu.set_plot_properties("category","1 bj_{EXP}")
            gnu.set_plot_properties("legend","down center")
            gnu.set_plot_properties("categoryleft","p_{T,bj} > 30 GeV")
            gnu.set_plot_properties("categorydownleft","|{/Symbol h}|_{bj} < 2.4")

        if gnu.get_name().startswith("dy_H_bjet1-IFN-1bjet"):
            gnu.set_plot_properties("xlabel","{/Symbol D}y_{H,bj_{1,IFN}}")
            gnu.set_plot_properties("category","1 bj_{IFN}")
            gnu.set_plot_properties("legend","down center")
            
        if gnu.get_name().startswith("dy_H_bjet1-NAI-1bjet"):
            gnu.set_plot_properties("xlabel","{/Symbol D}y_{H,bj_{1,NAI}}")
            gnu.set_plot_properties("category","1 bj_{NAI}")
            gnu.set_plot_properties("legend","down center")
            
        if gnu.get_name().startswith("dR_Hbb-EXP-2bjet"):
            gnu.set_plot_properties("xlabel","{/Symbol D}R_{H,bj_{1,EXP}bj_{2,EXP}}")
            gnu.set_plot_properties("category","2 bj_{EXP}")
            gnu.set_plot_properties("legend","down center")

        if gnu.get_name().startswith("dR_Hbb-IFN-2bjet"):
            gnu.set_plot_properties("xlabel","{/Symbol D}R_{H,bj_{1,IFN}bj_{2,IFN}}")
            gnu.set_plot_properties("category","2 bj_{IFN}")
            gnu.set_plot_properties("legend","down center")
            
        if gnu.get_name().startswith("dR_Hbb-NAI-2bjet"):
            gnu.set_plot_properties("xlabel","{/Symbol D}R_{H,bj_{1,NAI}bj_{2,NAI}}")
            gnu.set_plot_properties("category","2 bj_{NAI}")
            gnu.set_plot_properties("legend","down center")

        if gnu.get_name().startswith("drHlj1-EXP"):
            gnu.set_plot_properties("xlabel","{/Symbol D}R_{H,lj_{1,EXP}}")
            gnu.set_plot_properties("legend","down center")
            
        if gnu.get_name().startswith("drHlj1-IFN"):
            gnu.set_plot_properties("xlabel","{/Symbol D}R_{H,lj_{1,IFN}}")
            gnu.set_plot_properties("legend","down center")
            
        if gnu.get_name().startswith("drHlj1-NAI"):
            gnu.set_plot_properties("xlabel","{/Symbol D}R_{H,lj_{1,NAI}}")
            gnu.set_plot_properties("legend","down center")
            
        if gnu.get_name().startswith("dyHlj1-EXP"):
            gnu.set_plot_properties("xlabel","{/Symbol D}y_{H,lj_{1,EXP}}")
            gnu.set_plot_properties("legend","down center")
            gnu.set_plot_properties("rebin",4)

        if gnu.get_name().startswith("dyHlj1-IFN"):
            gnu.set_plot_properties("xlabel","{/Symbol D}y_{H,lj_{1,IFN}}")
            gnu.set_plot_properties("legend","down center")
            gnu.set_plot_properties("rebin",4)
            
        if gnu.get_name().startswith("dyHlj1-NAI"):
            gnu.set_plot_properties("xlabel","{/Symbol D}y_{H,lj_{1,NAI}}")
            gnu.set_plot_properties("legend","down center")
            gnu.set_plot_properties("rebin",4)

#---------------------------------------

        if gnu.get_name().startswith("pt_lj1-EXP"):
            gnu.set_plot_properties("yunit","[fb/GeV]")
            gnu.set_plot_properties("xlabel","p_{T,lj_{1,EXP}}")
            gnu.set_plot_properties("min_x_for_rebin",140)
            gnu.set_plot_properties("rebin_above_x",4)
            gnu.set_plot_properties("xmax",300)
            
        if gnu.get_name().startswith("pt_lj2-EXP"):
            gnu.set_plot_properties("yunit","[fb/GeV]")
            gnu.set_plot_properties("xlabel","p_{T,lj_{2,EXP}}")
            gnu.set_plot_properties("min_x_for_rebin",140)
            gnu.set_plot_properties("rebin_above_x",4)
            gnu.set_plot_properties("xmax",300)
            
        if gnu.get_name().startswith("pt_lj1-NAI"):
            gnu.set_plot_properties("yunit","[fb/GeV]")
            gnu.set_plot_properties("xlabel","p_{T,lj_{1,NAI}}")
            gnu.set_plot_properties("min_x_for_rebin",140)
            gnu.set_plot_properties("rebin_above_x",4)
            gnu.set_plot_properties("xmax",300)
            
        if gnu.get_name().startswith("pt_lj2-NAI"):
            gnu.set_plot_properties("yunit","[fb/GeV]")
            gnu.set_plot_properties("xlabel","p_{T,lj_{2,NAI}}")
            gnu.set_plot_properties("min_x_for_rebin",140)
            gnu.set_plot_properties("rebin_above_x",4)
            gnu.set_plot_properties("xmax",300)
            
        if gnu.get_name().startswith("pt_lj1-IFN"):
            gnu.set_plot_properties("yunit","[fb/GeV]")
            gnu.set_plot_properties("xlabel","p_{T,lj_{1,IFN}}")
            gnu.set_plot_properties("min_x_for_rebin",140)
            gnu.set_plot_properties("rebin_above_x",4)
            gnu.set_plot_properties("xmax",300)
            
        if gnu.get_name().startswith("pt_lj2-IFN"):
            gnu.set_plot_properties("yunit","[fb/GeV]")
            gnu.set_plot_properties("xlabel","p_{T,lj_{2,IFN}}")
            gnu.set_plot_properties("min_x_for_rebin",140)
            gnu.set_plot_properties("rebin_above_x",4)
            gnu.set_plot_properties("xmax",300)

#------------------------------------------------------------------------------------------

        if gnu.get_name().startswith("y_H-1lightEXP"):
           gnu.set_plot_properties("yunit","[fb]")
           gnu.set_plot_properties("xlabel","y_{H}")
           gnu.set_plot_properties("logscale_y",False)
           gnu.set_plot_properties("category","1 lj_{EXP}")
           gnu.set_plot_properties("xmin",-3.8)
           gnu.set_plot_properties("xmax",3.8)
           gnu.set_plot_properties("rebin",4)
           gnu.set_plot_properties("legend","down center")
           
        if gnu.get_name().startswith("y_H-1lightIFN"):
           gnu.set_plot_properties("yunit","[fb]")
           gnu.set_plot_properties("xlabel","y_{H}")
           gnu.set_plot_properties("logscale_y",False)
           gnu.set_plot_properties("category","1 lj_{IFN}")
           gnu.set_plot_properties("xmin",-3.8)
           gnu.set_plot_properties("xmax",3.8)
           gnu.set_plot_properties("rebin",4)
           gnu.set_plot_properties("legend","down center")
           
        if gnu.get_name().startswith("y_H-1lightNAI"):
           gnu.set_plot_properties("yunit","[fb]")
           gnu.set_plot_properties("xlabel","y_{H}")
           gnu.set_plot_properties("logscale_y",False)
           gnu.set_plot_properties("category","1 lj_{NAI}")
           gnu.set_plot_properties("xmin",-3.8)
           gnu.set_plot_properties("xmax",3.8)
           gnu.set_plot_properties("rebin",4)
           gnu.set_plot_properties("legend","down center")

        if gnu.get_name().startswith("y_H-EXP-1bjet"):
           gnu.set_plot_properties("yunit","[fb]")
           gnu.set_plot_properties("xlabel","y_{H}")
           gnu.set_plot_properties("logscale_y",False)
           gnu.set_plot_properties("category","1 bj_{EXP}")
           gnu.set_plot_properties("xmin",-3)
           gnu.set_plot_properties("xmax",3)
           gnu.set_plot_properties("rebin_above_x",6)
           gnu.set_plot_properties("min_x_for_rebin",-3)
#           gnu.set_plot_properties("legend","down center")
           gnu.set_plot_properties("categoryleft","p_{T,bj} > 30 GeV")
           gnu.set_plot_properties("categorydownleft","|{/Symbol h}|_{bj} < 2.4")
           gnu.set_plot_properties("ymax",45)
           gnu.set_plot_properties("ymax_ratio",1.3)
           
        if gnu.get_name().startswith("y_H-NAI-1bjet"):
           gnu.set_plot_properties("yunit","[fb]")
           gnu.set_plot_properties("xlabel","y_{H}")
           gnu.set_plot_properties("logscale_y",False)
           gnu.set_plot_properties("category","1 bj_{NAI}")
           gnu.set_plot_properties("xmin",-3.8)
           gnu.set_plot_properties("xmax",3.8)
           gnu.set_plot_properties("rebin",4)
           gnu.set_plot_properties("legend","down center")

        if gnu.get_name().startswith("y_H-IFN-1bjet"):
           gnu.set_plot_properties("yunit","[fb]")
           gnu.set_plot_properties("xlabel","y_{H}")
           gnu.set_plot_properties("logscale_y",False)
           gnu.set_plot_properties("category","1 bj_{IFN}")
           gnu.set_plot_properties("xmin",-3.8)
           gnu.set_plot_properties("xmax",3.8)
           gnu.set_plot_properties("rebin",4)
           gnu.set_plot_properties("legend","down center")

        if gnu.get_name().startswith("y_H-EXP-2bjet"):
           gnu.set_plot_properties("yunit","[fb]")
           gnu.set_plot_properties("xlabel","y_{H}")
           gnu.set_plot_properties("logscale_y",False)
           gnu.set_plot_properties("category","2 bj_{EXP}")
           gnu.set_plot_properties("xmin",-2.8)
           gnu.set_plot_properties("xmax",2.8)
           gnu.set_plot_properties("rebin",4)
           gnu.set_plot_properties("legend","down center")

        if gnu.get_name().startswith("y_H-IFN-2bjet"):
           gnu.set_plot_properties("yunit","[fb]")
           gnu.set_plot_properties("xlabel","y_{H}")
           gnu.set_plot_properties("logscale_y",False)
           gnu.set_plot_properties("category","2 bj_{IFN}")
           gnu.set_plot_properties("xmin",-2.8)
           gnu.set_plot_properties("xmax",2.8)
           gnu.set_plot_properties("rebin",4)
           gnu.set_plot_properties("legend","down center")
           
        if gnu.get_name().startswith("y_H-NAI-2bjet"):
           gnu.set_plot_properties("yunit","[fb]")
           gnu.set_plot_properties("xlabel","y_{H}")
           gnu.set_plot_properties("logscale_y",False)
           gnu.set_plot_properties("category","2 bj_{NAI}")
           gnu.set_plot_properties("xmin",-2.8)
           gnu.set_plot_properties("xmax",2.8)
           gnu.set_plot_properties("rebin",4)
           gnu.set_plot_properties("legend","down center")
           
        if gnu.get_name().startswith("y_H-ptj30"):
           gnu.set_plot_properties("yunit","[fb]")
           gnu.set_plot_properties("xlabel","y_{H}")
           gnu.set_plot_properties("logscale_y",False)
           gnu.set_plot_properties("category","p_{T,j_{1}}>30GeV")
           gnu.set_plot_properties("xmin",-3.8)
           gnu.set_plot_properties("xmax",3.8)
           gnu.set_plot_properties("rebin",4)
           gnu.set_plot_properties("legend","down center")

        if gnu.get_name().startswith("y_H-ptj60"):
           gnu.set_plot_properties("yunit","[fb]")
           gnu.set_plot_properties("xlabel","y_{H}")
           gnu.set_plot_properties("logscale_y",False)
           gnu.set_plot_properties("category","p_{T,j_{1}}>60GeV")
           gnu.set_plot_properties("xmin",-3.8)
           gnu.set_plot_properties("xmax",3.8)
           gnu.set_plot_properties("rebin",4)
           gnu.set_plot_properties("legend","down center")
        
           
#-------------------------------------------------------------------------------------------

        if gnu.get_name().startswith("dR_bb-EXP-2bjet"):
            gnu.set_plot_properties("xlabel","{/Symbol D}R_{bj_{1,EXP}bj_{2,EXP}}")
            gnu.set_plot_properties("category","2 bj_{EXP}")
            
        if gnu.get_name().startswith("dR_bb-IFN-2bjet"):
            gnu.set_plot_properties("xlabel","{/Symbol D}R_{bj_{1,IFN}bj_{2,IFN}}")
            gnu.set_plot_properties("category","2 bj_{IFN}")
            
        if gnu.get_name().startswith("dR_bb-NAI-2bjet"):
            gnu.set_plot_properties("xlabel","{/Symbol D}R_{bj_{1,IFN}bj_{2,NAI}}")
            gnu.set_plot_properties("category","2 bj_{NAI}")

        if gnu.get_name().startswith("m_bb-EXP-2bjet"):
            gnu.set_plot_properties("xlabel","m_{bj_{1,EXP}bj_{2,EXP}}")
            gnu.set_plot_properties("category","2 bj_{EXP}")
            gnu.set_plot_properties("xmax",250)
            gnu.set_plot_properties("logscale_y",False)
#            gnu.set_plot_properties("legend","down center")
            gnu.set_plot_properties("ymax",0.05)
            gnu.set_plot_properties("ymin",0)
            gnu.set_plot_properties("ymax_ratio",1.2)
            
        if gnu.get_name().startswith("m_bb-IFN-2bjet"):
            gnu.set_plot_properties("xlabel","m_{bj_{1,IFN}bj_{2,IFN}}")
            gnu.set_plot_properties("category","2 bj_{IFN}")
            
        if gnu.get_name().startswith("m_bb-NAI-2bjet"):
            gnu.set_plot_properties("xlabel","m_{bj_{1,IFN}bj_{2,NAI}}")
            gnu.set_plot_properties("category","2 bj_{NAI}")

        if gnu.get_name().startswith("eta_bjet1-EXP-1bjet"):
            gnu.set_plot_properties("xlabel","|{/Symbol h}|_{bj_{1}}")
            gnu.set_plot_properties("category","1 bj_{EXP}")
            gnu.set_plot_properties("ymax",70)
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("categoryleft","p_{T,bj} > 30 GeV")
            gnu.set_plot_properties("categorydownleft","|{/Symbol h}|_{bj} < 2.4")
            gnu.set_plot_properties("ymax_ratio",1.3)

        if gnu.get_name().startswith("eta_bjet1-NAI-1bjet"):
            gnu.set_plot_properties("xlabel","{/Symbol h}_{bj_{1,NAI}}")
            gnu.set_plot_properties("category","1 bj_{NAI}")
            gnu.set_plot_properties("ymax",65)
            gnu.set_plot_properties("logscale_y",False)
            
        if gnu.get_name().startswith("eta_bjet1-IFN-1bjet"):
            gnu.set_plot_properties("xlabel","{/Symbol h}_{bj_{1,IFN}}")
            gnu.set_plot_properties("category","1 bj_{IFN}")
            gnu.set_plot_properties("ymax",65)
            gnu.set_plot_properties("logscale_y",False)
            
        if gnu.get_name().startswith("eta_bjet1-EXP-2bjet"):
            gnu.set_plot_properties("xlabel","{/Symbol h}_{bj_{1,EXP}}")
            gnu.set_plot_properties("category","2 bj_{EXP}")
            gnu.set_plot_properties("ymax",5)
            gnu.set_plot_properties("logscale_y",False)

            
        if gnu.get_name().startswith("eta_bjet1-IFN-2bjet"):
            gnu.set_plot_properties("xlabel","{/Symbol h}_{bj_{1,IFN}}")
            gnu.set_plot_properties("category","2 bj_{IFN}")
            gnu.set_plot_properties("ymax",5)
            gnu.set_plot_properties("logscale_y",False)
            
        if gnu.get_name().startswith("eta_bjet1-NAI-2bjet"):
            gnu.set_plot_properties("xlabel","{/Symbol h}_{bj_{1,NAI}}")
            gnu.set_plot_properties("category","2 bj_{NAI}")
            gnu.set_plot_properties("ymax",5)
            gnu.set_plot_properties("logscale_y",False)
            
#-------------------------------------------------------------------------------------------
#        if gnu.get_name().startswith("pt_"):
#            gnu.set_plot_properties("xlabel","ptH")
#            gnu.set_plot_properties("ylabel","d{/Symbol s}/{dptH}")
#            gnu.set_plot_properties("yunit","[fb/GeV]"
#            gnu.set_plot_properties("xmax",250)
     

#        if gnu.get_name().startswith("ptzoom_"):
#            gnu.set_plot_properties("xlabel","ptHzoom")
#            gnu.set_plot_properties("ylabel","d{/Symbol s}/{dp_{T,H}}")
#            gnu.set_plot_properties("ymin",0)
#            gnu.set_plot_properties("ymax",25)
#            gnu.set_plot_properties("logscale_y",False)
#            gnu.set_plot_properties("yunit","[fb/GeV]")
#            gnu.set_plot_properties("xlabel","p_{T,H}")
#            gnu.set_plot_properties("exclude_from_ratio",)

#        if gnu.get_name().startswith("dphi-h"):
#            gnu.set_plot_properties("xmin",1)
#            gnu.set_plot_properties("xmax",3.7)
#            gnu.set_plot_properties("legend","left")
            
#        if gnu.get_name().startswith("dphi-h-j1-ptj20_"):
#            gnu.set_plot_properties("xlabel","{/Symbol D}{/Symbol f}_{Hj_1} pt_{j_1}>20GeV")
#            gnu.set_plot_properties("legend","down down")
#
#        if gnu.get_name().startswith("dphi-h-j1-ptj60"):
#            gnu.set_plot_properties("xlabel","{/Symbol D}{/Symbol f}_{Hj_1} pt_{j_1}>60GeV")
#
#        if gnu.get_name().startswith("dphi-h-j1-ptj120"):
#            gnu.set_plot_properties("xlabel","{/Symbol D}{/Symbol f}_{Hj_1} pt_{j_1}>120GeV")
#
#        if gnu.get_name().startswith("dphi-h-j1-ptj30"):
#            gnu.set_plot_properties("xlabel","{/Symbol D}{/Symbol f}_{Hj_1} pt_{j_1}>30GeV")
#
#        if gnu.get_name().startswith("dphi-h-j1-ptj60"):
#            gnu.set_plot_properties("xlabel","{/Symbol D}{/Symbol f}_{Hj_1} pt_{j_1}>60GeV")
#
#        if gnu.get_name().startswith("dphi-h-j1-ptj200"):
#            gnu.set_plot_properties("xlabel","{/Symbol D}{/Symbol f}_{Hj_1} pt_{j_1}>200GeV")
#        
#        if gnu.get_name().startswith("dy-h-j1"):
#            gnu.set_plot_properties("legend", "down center")
#            gnu.set_plot_properties("xmin",-6)
#            gnu.set_plot_properties("xmax",6)
##            gnu.set_plot_properties("rebin_above_x",6)
##            gnu.set_plot_properties("min_x_for_rebin",4)
#            
#        
#        if gnu.get_name().startswith("dy-h-j1-ptj120"):
#            gnu.set_plot_properties("xlabel","{/Symbol D}{y}_{Hj_1} pt_{j_1}>120GeV")
#            gnu.set_plot_properties("rebin",6)
#
#        if gnu.get_name().startswith("dy-h-j1-ptj60"):
#            gnu.set_plot_properties("xlabel","{/Symbol D}{y}_{Hj_1} pt_{j_1}>60GeV")
#            gnu.set_plot_properties("rebin",5)
#
#
#        if gnu.get_name().startswith("dy-h-j1-ptj200"):
#            gnu.set_plot_properties("xlabel","{/Symbol D}{y}_{Hj_1} pt_{j_1}>200GeV")
#            gnu.set_plot_properties("rebin",10)
#
#
#        if gnu.get_name().startswith("dy-h-j1-ptj20_"):
#            gnu.set_plot_properties("xlabel","{/Symbol D}{y}_{Hj_1} pt_{j_1}>20GeV")
#            gnu.set_plot_properties("rebin",3)
#
#
#        if gnu.get_name().startswith("dy-h-j1-ptj30"):
#            gnu.set_plot_properties("xlabel","{/Symbol D}{y}_{Hj_1} pt_{j_1}>30GeV")
#            gnu.set_plot_properties("rebin",4)
#
#        if gnu.get_name().startswith("fiducial"):
#            gnu.set_plot_properties("logscale_y",False)
#            gnu.set_plot_properties("xlabel","{/Symbol s} pt_H<277.5 GeV")
#            gnu.set_plot_properties("ylabel","Integrated {/Symbol s}")
#     
#        if gnu.get_name().startswith("ptH-yj4-ptj20_"):
#            gnu.set_plot_properties("xmax",175)
#            gnu.set_plot_properties("rebin",2)
#            gnu.set_plot_properties("rebin_above_x",5)
#            gnu.set_plot_properties("min_x_for_rebin",100)
#            gnu.set_plot_properties("xlabel","pt_H |y_j|<4 pt_j>20GeV")
#            gnu.set_plot_properties("legend","down")
#            gnu.set_plot_properties("ylabel","d{/Symbol s}/{dpt_H}")
#            gnu.set_plot_properties("yunit","[fb/GeV]")
#
#        if gnu.get_name().startswith("ptH-yj4-ptj30_"):
#            gnu.set_plot_properties("xmax",175)
#            gnu.set_plot_properties("rebin",2)
#            gnu.set_plot_properties("rebin_above_x",5)
#            gnu.set_plot_properties("min_x_for_rebin",100)
#            gnu.set_plot_properties("xlabel","pt_H |y_j|<4 pt_j>30GeV")
#            gnu.set_plot_properties("legend","down")
#            gnu.set_plot_properties("ylabel","d{/Symbol s}/{dpt_H}")
#            gnu.set_plot_properties("yunit","[fb/GeV]")

#
#        if gnu.get_name().startswith("ptH-yj4-ptj60_"):
#            gnu.set_plot_properties("xmax",175)
#            gnu.set_plot_properties("rebin",2)
#            gnu.set_plot_properties("rebin_above_x",5)
#            gnu.set_plot_properties("min_x_for_rebin",100)
#            gnu.set_plot_properties("xlabel","pt_H |y_j|<4 pt_j>60GeV")
#            gnu.set_plot_properties("legend","down")
#            gnu.set_plot_properties("ylabel","d{/Symbol s}/{dpt_H}")
#            gnu.set_plot_properties("yunit","[fb/GeV]")
#
#        if gnu.get_name().startswith("ptj1_"):
#            gnu.set_plot_properties("rebin",1)
#            gnu.set_plot_properties("xmax",300) #poi da cambiare rilanciando MiNLO    
#            gnu.set_plot_properties("rebin_above_x",4)
#            gnu.set_plot_properties("min_x_for_rebin",150)
#            gnu.set_plot_properties("xlabel","pt_{j1}")
#            gnu.set_plot_properties("ylabel","d{/Symbol s}/{dpt_{j1}}")
#            gnu.set_plot_properties("yunit","[fb/GeV]")
#
#        if gnu.get_name().startswith("ptj2_"):
#            gnu.set_plot_properties("rebin",1)
#            gnu.set_plot_properties("xmax",300) #poi da cambiare rilanciando MiNLO    
#            gnu.set_plot_properties("rebin_above_x",4)
#            gnu.set_plot_properties("min_x_for_rebin",125)
#            gnu.set_plot_properties("xlabel","pt_{j2}")
#            gnu.set_plot_properties("ylabel","d{/Symbol s}/{dpt_{j2}}")
#            gnu.set_plot_properties("yunit","[fb/GeV]")


#        if gnu.get_name().startswith("ptj1zoom"):
#            gnu.set_plot_properties("xlabel","pt_{j1} zoom")
#            gnu.set_plot_properties("ylabel","d{/Symbol s}/{dpt_{j1}}")
#            gnu.set_plot_properties("xmin",6)
#            gnu.set_plot_properties("logscale_y",False)
#            gnu.set_plot_properties("yunit","[fb/GeV]")


#        if gnu.get_name().startswith("ptj2zoom"):
#            gnu.set_plot_properties("xlabel","pt_{j2} zoom")
#            gnu.set_plot_properties("ylabel","d{/Symbol s}/{dpt_{j2}}")
#            gnu.set_plot_properties("xmin",4)
#            gnu.set_plot_properties("logscale_y",False)
#            gnu.set_plot_properties("yunit","[fb/GeV]")

#        if gnu.get_name().startswith("y-j1"):
#            gnu.set_plot_properties("legend", "down center")
#            gnu.set_plot_properties("ylabel","d{/Symbol s}/dy_{j1}")
#            gnu.set_plot_properties("xmin",-6)
#            gnu.set_plot_properties("xmax",6)


#        if gnu.get_name().startswith("y-j1-ptj120"):
#            gnu.set_plot_properties("xlabel","{y}_{j_1} pt_{j_1}>120GeV")
#            gnu.set_plot_properties("rebin",4)
#            gnu.set_plot_properties("xmax",5)
#            gnu.set_plot_properties("xmin",-5)

#        if gnu.get_name().startswith("y-j1-ptj200"):
#            gnu.set_plot_properties("xlabel","{y}_{j_1} pt_{j_1}>200GeV")
#            gnu.set_plot_properties("rebin",5)
#            gnu.set_plot_properties("xmax",5)
#            gnu.set_plot_properties("xmin",-5)

#        if gnu.get_name().startswith("y-j1-ptj20_"):
#            gnu.set_plot_properties("xlabel","{y}_{j_1} pt_{j_1}>20GeV")
#            gnu.set_plot_properties("rebin",2)
        
        
#        if gnu.get_name().startswith("y-j1-ptj30"):
#            gnu.set_plot_properties("xlabel","{y}_{j_1} pt_{j_1}>30GeV")
#            gnu.set_plot_properties("rebin",3)

    
#        if gnu.get_name().startswith("y-j1-ptj60"):
#            gnu.set_plot_properties("xlabel","{y}_{j_1} pt_{j_1}>60GeV")
#            gnu.set_plot_properties("rebin",3)

#        if gnu.get_name().startswith("yH"):
#            gnu.set_plot_properties("xmin",-5)
#            gnu.set_plot_properties("xmax",5)
#            gnu.set_plot_properties("legend","down down")
#            gnu.set_plot_properties("rebin",2)
#            gnu.set_plot_properties("logscale_y",False)

#        if gnu.get_name().startswith("yH-pt"):
#            gnu.set_plot_properties("ylabel","d{/Symbol s}/dpt_{H}")
#            gnu.set_plot_properties("yunit","[fb/GeV]")
#            gnu.set_plot_properties("xlabel","y_H (pt_{H}>30 GeV)")
#            gnu.set_plot_properties("ymin_ratio",0.8)
#            gnu.set_plot_properties("ymax_ratio",1.2)
#            gnu.set_plot_properties("logscale_y",False)
#            gnu.set_plot_properties("ymin",-10)



#        if gnu.get_name().startswith("yH_"):
##            gnu.set_plot_properties("ylabel","d{/Symbol s}/dpt_{H}")
#            gnu.set_plot_properties("yunit","[fb/GeV]")
#            gnu.set_plot_properties("xlabel","y_H")
#            gnu.set_plot_properties("logscale_y",False)
#            gnu.set_plot_properties("ymin_ratio",0.6)
#            gnu.set_plot_properties("ymax_ratio",1.7)
        skip = False
        for name in ["Njet","ptv-yj4","ptj1-yj4","mV","yVubdiff"]:
            if gnu.get_name().startswith(name):
                skip = True
        if skip:
            continue
        if "_atlas_" in plot:
            if gnu.get_name().startswith("pt_l1l2gam_"):
                gnu.set_plot_properties("categoryleft","ATLAS-setup-2")
            else:
                gnu.set_plot_properties("category","ATLAS-setup-2")
            if "j1" in plot or "j2" in plot:
                continue

        # if not gnu.get_name().startswith("m.Z"): 
        #     continue


        if gnu.get_name().startswith("absdy.ZlW"): 
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("xlabel","|{/Symbol \104}{y}_{Z  {/Symbola μ}}|")
            gnu.set_plot_properties("xmax", 5)            
        if gnu.get_name().startswith("absdy.jj"):
            continue
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("xlabel","{|{/Symbol \104}y|}_{j_{1}j_{2}}")
            gnu.set_plot_properties("xmax", 10)            
        if gnu.get_name().startswith("dphi.WZ"): 
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("xlabel","{/Symbol \104}{/Symbol \152}_{WZ}")
            gnu.set_plot_properties("xmax", 3)            
        if gnu.get_name().startswith("dphi.leplep"): 
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("xlabel","{/Symbol \104}{/Symbol \152}_{ℓ_{1}ℓ_{2}}")
            gnu.set_plot_properties("xmax", 3)            
            gnu.set_plot_properties("legend", "left")            
        if gnu.get_name().startswith("dphi.lepleplep_"): 
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("xlabel","{/Symbol \104}{/Symbol \152}_{3ℓ {/Symbol n}}")
            gnu.set_plot_properties("xmax", 3)            
        if gnu.get_name().startswith("dy.ZlW"): 
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("xlabel","{/Symbol \104}{y}_{Z {/Symbola μ}}")
            gnu.set_plot_properties("xmax", 5)            
            gnu.set_plot_properties("xmin", -5)            
        if gnu.get_name().startswith("m.3l"): 
#            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("xlabel","m_{3ℓ}")
            gnu.set_plot_properties("ymin", 0.03)            
            gnu.set_plot_properties("ymax", 0.6)            
            gnu.set_plot_properties("xmin", 90)            
            gnu.set_plot_properties("xmax", 400)            
            gnu.set_plot_properties("rebin", 2)            
        if gnu.get_name().startswith("m.W"): 
#            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("xlabel","m_{{/Symbola μ}{/Courier=24 ν}_{/Symbola μ}}}")
            gnu.set_plot_properties("xmin", 50)
            gnu.set_plot_properties("xmax", 200)            
            gnu.set_plot_properties("rebin_above_x",5)
            gnu.set_plot_properties("min_x_for_rebin",100)
        if gnu.get_name().startswith("m.WZ"): 
#            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("xlabel","m_{WZ}")
            gnu.set_plot_properties("xmin", 120)            
            gnu.set_plot_properties("xmax", 500)            
        if gnu.get_name().startswith("m.Z_1.0"): 
#            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("xmin",80)
            gnu.set_plot_properties("xmax",105)
            gnu.set_plot_properties("xlabel","m_{ee}")
        if gnu.get_name().startswith("m.Z_2.5"): 
#            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("xmin",80)
            gnu.set_plot_properties("xmax",105)
            gnu.set_plot_properties("xlabel","m_{ee(2.5)}")
        if gnu.get_name().startswith("m.jj"):
            continue
#            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("xlabel","m_{j_{1}j_{2}}")
        if gnu.get_name().startswith("mT.W"): 
#            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("xlabel","m_{{/Times=22 T},{/Symbola μ}{/Courier=24 ν}_{/Symbola μ}}}")
        if gnu.get_name().startswith("mT.WZ"): 
            gnu.set_plot_properties("xlabel","m_{{/Times=22 T},WZ}")
        if gnu.get_name().startswith("pT.W"): 
            gnu.set_plot_properties("ymax",2)
            gnu.set_plot_properties("logscale_y",True)
            gnu.set_plot_properties("xlabel","p_{{/Times=22 T},{/Symbola μ}{/Courier=24 ν}_{/Symbola μ}}")
            gnu.set_plot_properties("xmax",400)
        if gnu.get_name().startswith("pT.WZ"): 
            gnu.set_plot_properties("logscale_y",True)
            gnu.set_plot_properties("xmax", 600)            
            gnu.set_plot_properties("xlabel","p_{{/Times=22 T},WZ}")
        if gnu.get_name().startswith("pT.Z"): 
            gnu.set_plot_properties("logscale_y",True)
            gnu.set_plot_properties("xlabel","p_{{/Times=22 T},Z}")
        if gnu.get_name().startswith("pT.lep1"): 
            gnu.set_plot_properties("logscale_y",True)
            gnu.set_plot_properties("xlabel","p_{{/Times=22 T},ℓ_{1}}")
        if gnu.get_name().startswith("pT.lep2"): 
            gnu.set_plot_properties("logscale_y",True)
            gnu.set_plot_properties("xlabel","p_{{/Times=22 T},ℓ_{2}}")
        if gnu.get_name().startswith("pT.lepW"): 
            gnu.set_plot_properties("logscale_y",True)
            gnu.set_plot_properties("xlabel","p_{{/Times=22 T},{/Symbola μ}}")
        if gnu.get_name().startswith("pT.miss"): 
            gnu.set_plot_properties("xmax",300)            
            gnu.set_plot_properties("logscale_y",True)
            gnu.set_plot_properties("xlabel","p_{{/Times=22 T},{miss} }")
        if gnu.get_name().startswith("y.lep1st"): 
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("xlabel","y_{ℓ_1}")
            gnu.set_plot_properties("xmin",-4)
            gnu.set_plot_properties("xmax",4)
            gnu.set_plot_properties("legend", "down")
        if gnu.get_name().startswith("y.lep2nd"): 
            gnu.set_plot_properties("logscale_y",True)
            gnu.set_plot_properties("xlabel","y_{ℓ_2}")
        if gnu.get_name().startswith("y.Z"): 
            gnu.set_plot_properties("logscale_y",True)
            gnu.set_plot_properties("xlabel","y_{ee}")
        if gnu.get_name().startswith("y.WZ"): 
            gnu.set_plot_properties("logscale_y",True)
            gnu.set_plot_properties("xlabel","y_{WZ}")
            gnu.set_plot_properties("xmin",-3)
            gnu.set_plot_properties("xmax",3)
            gnu.set_plot_properties("rebin",2)




            
        if gnu.get_name().startswith("total"):
            gnu.set_plot_properties("logscale_y",False)
#            gnu.set_plot_properties("ymin_ratio",0.9)
#            gnu.set_plot_properties("ymax_ratio",1.1)
#            gnu.set_plot_properties("xlabel","{/Symbol s}")


        # if gnu.get_name().startswith("pt") and "zoom" in gnu.get_name():
        #     gnu.set_plot_properties("rebin",2)

        if gnu.get_name().startswith("n_jet"): # for njets, treat it as special case and combine it with total rate in "-1" bin
            gnu.set_plot_properties("logscale_y",False)
            gnu.set_plot_properties("ylabel","{/Symbol s}")
            gnu.set_plot_properties("xlabel","")
            gnu.set_plot_properties("xtics","(\"total rate\" -0.5,\"0-jet\" 0.5,\"1-jet\" 1.5,\"2-jet\" 2.5)")
#            gnu.set_plot_properties("ytics","")
            gnu.set_plot_properties("xmin",-1)
            gnu.set_plot_properties("ymin_ratio",0.3)
            gnu.set_plot_properties("ymax_ratio",1.2)
            
        elif gnu.get_name().startswith("pTveto"): # treat this later as special case inside the code (with distributiontype)
            continue

#        gnu.set_plot_properties("rebin",1)

#        gnu.set_plot_properties("ylabel","d{/Symbol s}/bin")
#        gnu.set_plot_properties("process","pp{/Symbol \256}W^+Z{/Symbol \256}e^+ e^{\342\210\222} {/Symbola μ}^+ {/Courier=30 ν}_{/Symbola μ}")
        gnu.set_plot_properties("process","t{/b t\u0305}H")
        gnu.set_plot_properties("collider","LHC")
        gnu.set_plot_properties("energy","13 TeV")
#        gnu.set_plot_properties("yunit","[fb]")
        #    gnu.set_plot_properties("reference","1111.1111")
        gnu.plot()
        # try:
        #     gnu.plot()
        # except:
        #     pass
#    time.sleep(1)
    # combine the pdfs in gnuplot folder in one single pdf file
    # get all pdfs in gnuplot folder

#    all_pdfs = sorted(glob.glob("gnuplot_validation_EW_py8/*.pdf"))
#    output_pdf = "gnuplot_validation_EW_py8/all_plots.pdf"
#    command = "gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile={} ".format(output_pdf)
#    command += " ".join(all_pdfs)
# Appending all pdfs
#    for pdf in all_pdfs:
#        command += " \"%s\"" % pdf
#    Writing all the collected pages to a file
#    combined_pdf_file = pjoin("gnuplot_validation_EW_py8","all_plots_py8_HW.pdf")
#    command += " %s" % combined_pdf_file
#    print(subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read())


# Get all PDF files in the directory
#    all_pdfs = sorted(glob.glob("gnuplot_validation_EW_py8/*.pdf"))

# Print the list of all PDFs
#    print("PDF files found:", all_pdfs)

# Initialize a list to track skipped files
#    skipped_files = []

# Command for combining PDFs using Ghostscript
#    command = "gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile=gnuplot_validation_EW_py8/all_plots.pdf "

# Append all PDF file names to the command, checking for size
#    for pdf in all_pdfs:
#        file_size = os.path.getsize(pdf)
    
#        if file_size == 0:
#            print(f"Warning: '{pdf}' is empty and will be skipped.")
#            skipped_files.append(pdf)  # Add to skipped files
#            continue  # Skip this file
    
    # Append the valid PDF file name to the command
#        command += f'"{pdf}" '

# Execute the command and print any output or error message
#    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Print the output and error messages from Ghostscript
#    print(result.stdout)
#    print(result.stderr)

# Print the list of skipped files
#    if skipped_files:
#        print("Skipped files:")
#        for skipped in skipped_files:
#            print(f"  - {skipped}")
#    else:
#        print("No files were skipped.")
