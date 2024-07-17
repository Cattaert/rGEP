# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 2018
This script select a file in a chosen directory
@author: Solene Lambert & Daniel Cattaert
    When a folder is selected (in the saved directory) - > model_dir
    (1) Plot separately Deb, Max, Fin values for each selected chart column
      Each plot represents the values for each const parameter and all trials
      Thee results are plotted in different colors for different mvt durations
      Results for the different angles are on separate sheeet graph
      these graphs are saved in the model_dir
    (2) Plots of the elbow movementfor each template
      Each plot represents the template and all movements obtained with the
      different constant values (for example Ia->MN sunapse strength)
      these graphs are saved in each folder specific to a movement template
      (i.e. angles and mvt duration)
    (3) Plot of superimposed movements of same angles and different durations

    Possibility to choose the constant values to plot results

    Plot relationship between parameters
    (1) Builds graphs of chosen parameter values. Each graph represents
    the adaptation of the parameter value for each value of the constant
    parameter (and for all selected trials). Different mvt durations are
    ploted with different lines. The different angles are plotted on different
    files.
    (2) Draws and saves correlation graphs for each angle_duration condition
    (3) Draws and saves a matrix of correlation graphs with color codes

    New series of procedures added for metrics of optimization methods.
    class GEPGraphsMetrics containing a "grid" method (grid_method) that builts
    a grid on behaviour space (40x40) in order to calculate the number of
    elements of the grid in which a behavior (at least one) was found.
    Then this methods builds the function nbboxes=f(nbRuns) with a step=100
    runs (i.e. for 7500 runs we get 75 points).
    Builts the corresponding graph (and saves it), with the indication of the
    value of span for each run series (numbers on the curve), and the type of
    run (reparam, GEPrand, CMAE) with a color code.

    1) "metrics" has been modified to allow re-use of the present df_parremai
    and df_bhvremain dataframes. A message box is used to ask the user what to
    do either keep these dataframes, or load a new one.
    2)When calling "metrics" the previously present BhvWindow is erased
    3)If the newly selected directory contains only one GepData folder then if
    this directory is the same as the one present in memory, the asim file is
    not red again
    4) When selecting a single directory in which GEPdata folder contains a
    series of runs (GEPdata00.par,GEPdata01.par,... GEPdataii.par) it
    is proposed to choose a given run (in a table, select check button case)

    1) windows are now disposed and ordered on right-up screen corner
    2) the bhv_window is erased and recreated each time a new type of analyze
    is performed.
    3) a new procedure "makes_bhvpar_windows" was created to recreate the
    bhv_window that also actualizes two files used in GEP_GUI procedures:
        self.mafen.source_df_bhvremain = df_bhv.iloc[self.df_glob.index]
        self.mafen.source_df_parremain = df_par.iloc[self.df_glob.index]

    In param_in_blue(self, df_par): all par graphs are built from
        listDicGraphs. This dictionary can be modified from makeGEPMetrics.py
        to choose the params plotted in each graph
            namex = self.listDicGraphs[pargr+1]["abscissa"]
            namey = self.listDicGraphs[pargr+1]["ordinate"]
            parx = self.xparNameDict[namex[0]]
            pary = self.xparNameDict[namey[0]]

    In class GUI_Graph:
        new methods added:
            plot_2D_stability_map(self, df_bhvremain, df_parremain)
                Prepares a dataframe in which for each behavior (duration,
                amplitude) a mean distance is calculated from the distance to
                all behaviors produced by parameters in the vicinyty (dist<0.2)
                of this behavior. When several distances are obtained, the mean
                value is retained. Then call the do_plot_2D_stability_map()
                method to plot the stability map.

            do_plot_2D_stability_map(self, df_cues_dist)

    
    plot_densitymap_metrics(self): it asks to choos a folder with GEPdata
        and builds the corresponding df_bhvremain and df_parremain dataframes
        (if already present in memor, asks if a new folder is to be analysed)
        Then calls the new function do_plot_2D_density_map_metrics

    do_plot_2D_density_map_metrics(df_bhvremain, behav_col,
                                   pathGEP, GEPdataName,
                                   nbruns, col_scale_range):
            Plots and saves a density map that uses the same grid as the grid
            used in metrics to evaluate how the GEP explores the behavior
            space. THe score in metrics is simply the number of cases in the
            grid that contain at least one behavior.
            Here, this gid is used to count the number of behaviors in each
            case, which gives an idea of the density of the behaviors in the
            different regions.

    a new general procedure added:
        plot_2D_graph_from_array(x, pathGEP,  baseName, nameX, nameY, extent)
        x is an array of arrays containing values (typically the number of
        behaviours in each case of the grid defined by the array of arrays, but
        it may be any value that defines a feature of the grid).
        pathGEP is the path to save the graphs (.esp and .pdf)
        baseName is the name of the graph
        nameX and nameY are the X and Y axes legends
        extent is an array [x_min, x_max, y_min, y_max] used to define the
        ranges of x and y axes.

    GEPGraphsMetrics class Contains various methods to build graphs for GEP analysis
        - plot and save behavior and parameter maps
        - plot and save behavior map
        - plot and save behavior map (with chosen number of valid behaviors)
        - plot and save density map of GEP behavior domain
        - plot and save stability map of GEP behavior domain
        - plot and save progression of GEP process with two metric methods

        - plot_densitymaps_contour
        - plot_save_2D_densitymap_contour
        These two methods use contour to draw the density map (continuous way)
Translated in Python 3.8 Jan 2023 (D. Cattaert)

Modified January 27, 2023 (D. Cattaert):
    Saving to xls has beenreplaced by saving in csv format.
    
Modified January 29, 2023 (D. Cattaert):
    New methods added in Graph_Setting class :
        chartgraph_selected_bhv()
        run_selected_bhv()
        These methods used selected Bhv to build graph from charts. To do this
        the corresponding paramsets are run and results saved in graphs/run-0
        or run-1 etc... in incremental manner.
ModifiedFebruary 1, 2023 (D. Cattaert):
    Modification of run_selected_bhv() method that use now the saves_seeds()
    method of GEP_GUI to complete the new directory.
Modified February 3, 2023 (D. Cattaert):
    Modifications of build_newdf() method:
        After selectiion of several folders, the index of df_bhvremain and
        df_parremain are no more set to range(len(self.df_parremain)) but to
        self.lst_valid, the list of valid elements (varmse<1) adapted to take
        into account the origin of elements (i.e. the folder of origin)
        self.df_bhvremain.index = self.lst_valid
        self.df_parremain.index = self.lst_valid
    Accordingly, in run_selected_bhv() method, the concatenated pairs numbers
    (optSet.pairs) are now directly compatible with seeds_selected
    (= list(df_glob.index)). So lst_valid is no more used.
    The call to GEP-GUI.py saves_seeds() is made with the param 
    seedDirCreate=False in order not to create a 0_IDXXX_seeds00 foder.
Modified February 14, 2023 (D. Cattaert):
    In the procedure graphfromchart(), "path" replaced by "chart_path" 
    In the class GUI_Graph, a bug in the method build_newdf() was fixed: when
    only one folder (one experiment) was chosen, the variable "tab_bhv" was not
    defined. It is now defined if one_expe:
        if self.prevListGEPFiles == []:
            tab_bhv = readTablo(self.listGEPFolders[0], "GEPdata00bhv.txt")
            tab_bhv = np.array(tab_bhv)
Modified February 28, 2023 (D. Cattaert):
    in GEPGraphsMetrics class, bug fixed in make_graph_score_evol(method):
        "span = int(tabnewspan[idx])" not accepted for a list. Now replaced
        by series of tests to define span.
Modified Mars 01, 2023 (D. Cattaert):
    graphfromchart() procedure improved. Neuron voltage are no more expressed
    in V but in mV.
Modified April 23, 2023 (D. Cattaert):
    New method plot_abaque_duration() allows to draw abaques of duration values
    in the MaxSpeed vs Amplitude graph. It calls a new prodecure from
    optimization: plot_series_curves_maxspeed_ampl_duration()
Modified April 28, 2023 (D. Cattaert):
    Method chooseChartFromPar() : bug fixed to take into account the new format
    in datastructure. This method builds bhv Plots from the charts of
    datastructure the varme of which is <1.
    New method analyze_triphasic(): 
        Builds a new df_bhv and df_par from a datastructure
        Runs the method chooseChartFromPar() to select charts from the
            datastructure
        From datastructure, builds a new self.df_chart containint:
            chartName, varmse, startangle, ampl, max_speed, dur_mvt2, run_rg
            plus three other columns characterizing triphasic pattern:
                TwoPicks, FlxTo0BetwPicks, ExtOnePick
        Aks if plot is required for each selected chartName (the plot contains
             the movement and EMGs (1FlxPotMuscle, 1ExtPotMuscle)
        The self.df_chart is saved in csv format.
Modified May 10, 2023 (D. Cattaert):
    Bug fixed in chooseChartFromPar() method. The <Max replaced by <=Max
Modified May 16, 2023 (D. cattaert):
    Scalses for bhv plots corrected and set to 0-120 for x , and 0-500 for
    MaxSpeed
    New method: plot_save_density_map_metrics() used when called from
    controlScriptGEP.py to build gaphs with autoscale=True
Modified July 29, 2023 (D. Cattaert):
    Method saveplot_bhvparam() in GEPGraphMetrics class modified so that
    when called from a multipleExpeGraph the complete dataframe is plotted.
Modified September 17, 2023 (D. Cattaert):
    Method make_graph_score_evol() Bug fixed to take into account the type of
    tabnewspan[idx] when red from datastructure and is ['DicSpanVal.txt'],
    Which means that for this series, span values was red from DicSpanVal.txt:
        if type(tabnewspan[idx][0]) is str: ...
Modified Ostober 06, 2023 (D. Cattaert):
    Method saveplot_bhvparam(): bug fixed for multiple expe graph. Start and
    End values missed. Now provided.
    Method plot_densitymap_metrics(): same bug fixed
Modified October 10, 2023 (d. Cattaert):
    Method analyze_triphasic() improved so that multiple experiments are
    allowed. Method build_df_chart() modified accordingly. Nw the df_chart
    contains a new column "origine". A number (0 to nbExpe) indicates the
    origin folder of the chart name. Method chooseChartFromPar() modified
    accordingly. It does not asks anymore for a GEPdata00.par, but gets it
    directly from the self.listGEPFolders list elaborated in build_newdf()
    method called by make_bhvpardf() method.
Modoified October 10, 2023 (D. Cattaert):
    Bug fixed in chooseChartFromPar(). Now the chart directory is obtained from
    self.listGEPFolders, and the chart is red in the good GEPChartFiles,
    according to the experiment folder in the list self.listGEPFolders.
Modified October 17, 2023 (D. Cattaert):
    Method makegr_chart_tcourse() modified to allow two types of graph when the
    names extension is ".txt":
        either an 'EMG'
        or a 'bhvMvt'
Modified February 03, 2024 (D. Cattaert):
    In grid_method() method, derecated writing fixed:
        state_table = np.zeros(dtype=int, shape=(nbcol, nbrow))
        ('dtype=np.int' replaced by 'dtype=int')
Modified April 12, 2024 (D. Cattaert):
    makeGraphs.py  Bug fixed in the selection of behaviors when data
	are from several folders. The behaviors are now selected
	using "orig_rg" and "origine". The index of chart_global_df
	is now compatible with indexes of df_parremain and
	df_bhvremain
Modified April 24, 2024 (D. Cattaert):
	Old methods (used for the old format "experiments series")
	have been suppressed.
	New procedures introduced to Analyze neuron activities and par
	vs bhv. Now it is possible to opena previously saved 
	"df_chart_bhv_neur_param.csv" to make graphs. The new method
	("read_csv_for_df_bhv_neur_par()") relies on a part of the old
	"build_newdf()" method to reconstruct the df_parremain and
	df_bhvremain dataframes.
	To do this, "build_newdf()" has been splitted into four sub methods
Modified May 1st, 2024 (D; Cattaert):
    Bug fixed in method "run_selected_bhv". Selected_seeds are obtained from
    the index of the dataframe "df_glob". This is OK but the corresponding
    parameters were not at those rows, becaus correct rows are indicated in
    rgserie column NOT AT INDEX!!! This is why the correct row of each
    parameter (in optSet.pairs) is calculated :
        rg_pair = int(df_bhvremain.loc[select]["rgserie"])
        The script was chaned accordingly:
            seeds_selected = list(df_glob.index))
            selected_pairs = []
            for select in seeds_selected:
                print(df_parremain.loc[select][:5])
                rg_pair = int(df_bhvremain.loc[select]["rgserie"])
                print(optSet.pairs[rg_pair][:5])
                selected_pairs.append(optSet.pairs[rg_pair])
Modified May 02, 2024 (D. Cattaert):
	Bug in method "run-selected-bhv()' fixed. Now, df-parremain and
    df-bhvremain indexes correspond to seeds-selected = df_glob.rgserie
Modified May 15, 2024 (D. Cattaert):
    Bug in construct_df_par_bhv_remains() and read_csv_for_df_bhv_neur_par()
    methods have been fixedc:
        "sum_precedingTab" variable was added to sum preceeding tables in order
        to get a correct final index
Modified May 17, 2024 (D. Cattaert):
    Suppression of two lines on read_csv_for_df_bhv_neur_par() method:
        self.df_bhvremain.loc[:, "orig_rg"] = self.df_bhvremain["rgserie"]
        self.df_parremain.loc[:, "orig_rg"] = self.df_parremain["rgserie"]
    because self.df_bhvremain and self.df_parremain already got the column
    entitled "orgi-rg" (in construct_df_par_bhv_remains() method)
    in and self.df_parremain already got the column
    
    In order to allow analysis from a different computer, with path
    different from the one used to build the multipleExpeGraph-x folders, the
    method "construct_df_par_bhv_remains()" has been modified so that it works
    with relative folder addresses established from self.ensembleRunDir
    annimatsimdir is rebuilt to make it compatible with the computer paths
Modified June 05, 2024 (D. Cattaert):
    new_run_dir is now created in chartgraph_selected_bhv() method
    This allows the par and bhv csv files of selected behaviors to be saved in
    new_run_dir (run-0, run-1 etc.)
Modified July 5, 2024 (D. Cattaert):
    create_df_for_bhv_neur_par() method modified to allow second peak detection
    at user's demand.
    get_peaks_and_troughs() procedure modified accordingly. Asks the user
    Which neurone to search for a second peak.
Modified July 15, 2024 (D. Cattaert):
    read_csv_for_df_bhv_neur_par() method modified to accept lines containing a
    NaN element
    buildStpDiscretCol() procedure modified to get a single color scale (<50),
    because plotting to legends(plt.legend()) is no more accepted.
Modified July 17, 2024 (D. Cattaert):
    Bug fixed in "save (par+bhv) dataframe to csv". The problem came from the
    variable "self.new_run_dir" that was not defined in the method
    "construct_df_par_bhv_remains" but only in neuron analysis. Therfor, any
    call to "save "par+bhv dataframes to csv" directely after running
    "make/analyze (par+bhv) dataframe" failed. This is now fixed in the method
    "construct_df_par_bhv_remains":
        new line added after the folders have been selected: 
            self.new_run_dir = self.graph_path
"""
import os
from os import listdir
from os.path import isfile, join
import pickle
import copy
import random
import ctypes  # used to create message box
from ctypes import wintypes as w

import matplotlib.pyplot as plt
# import matplotlib.colors as pltcolors
import matplotlib.pylab as pylab
import matplotlib as mpl
# from matplotlib import colors as mcolors
# from matplotlib import cm

import json

from itertools import product
import numpy as np
import pandas as pd
# from openpyxl import Workbook
import seaborn as sns
from scipy.stats import pearsonr
from scipy.signal import find_peaks_cwt
from scipy.signal import find_peaks
from scipy.signal import lfilter
from itertools import groupby
# from mpl_toolkits.mplot3d import axes3d
from mpl_toolkits.mplot3d import Axes3D

from math import log as ln
from math import sqrt as sqrt
from math import isnan
from math import pi

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from pyqtgraph.Qt import QtWidgets
# from PyQt5 import QtWidgets

from optimization import showdialog
from optimization import load_datastructure
from optimization import readTabloTxt
from optimization import readTablo
from optimization import chartToDataFrame
from optimization import getInfoComputer
from optimization import SaveIncrementNb
from optimization import saveListToDir
from optimization import calculate_minjerk_duration
from optimization import copyRenameFilewithExt
from optimization import copyFileDir_ext
from optimization import copyFileDir
from optimization import copyFileWithExt
from optimization import copyFile
from optimization import readGravityfromAsim
from optimization import readCoacPenality
from optimization import testVarMsePlot
from optimization import plot_series_curves_maxspeed_ampl_duration

# import mvt_GUI

from DialogChoose_in_List import ChooseInList
from DialogChoose_in_List import GetText
from DialogChoose_in_List import choose_one_element_in_list
from DialogChoose_in_List import choose_elements_in_list
from DialogChoose_in_List import set_values_in_list
from DialogChoose_in_List import Enter_Values

from optimization import loadParams
from animatlabOptimSetting import OptimizeSimSettings
from FoldersArm import FolderOrg

import class_animatLabModel as AnimatLabModel
import class_projectManager as ProjectManager
from class_animatLabSimulationRunner import AnimatLabSimulationRunner as SimRun

"""
from matplotlib.backends.qt_compat import is_pyqt5
if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
"""
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

global verbose
verbose = 2


# =======  Format a new "MessageBox" function to be used in Python 2.7  =======
# The four folling lines are for python2.7  because Python 2's strings are byte
# strings and marshaled as byte strings (char*). Python 3's strings are Unicode
# strings and marshaled as wide strings (wchar_t*). Without defining .argtypes,
# ctypes won't error check and happily pass the wrong type.
user32 = ctypes.WinDLL('user32')
MessageBox = user32.MessageBoxW
MessageBox.argtypes = w.HWND, w.LPCWSTR, w.LPCWSTR, w.UINT
MessageBox.restype = ctypes.c_int
"""
# to use "MessageBox just type
# MessageBox(None, u'message', u'title', 0)
# it will return the code of answer

# several options (styles) are possible:
##  Styles:
##  0 : OK
##  1 : OK | Cancel
##  2 : Abort | Retry | Ignore
##  3 : Yes | No | Cancel
##  4 : Yes | No
##  5 : Retry | No
##  6 : Cancel | Try Again | Continue
"""
# -----------------------------------------------------------------------------
def dialogWindow(titre, info, details=""):
    rep = showdialog(titre, info, details)
    # print(rep)
    if rep == 1024:
        OK = True
    else:
        OK = False
    return OK


class Form(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        nameLabel = QtWidgets.QLabel("Name:")
        self.nameLine = QtWidgets.QLineEdit()
        self.submitButton = QtWidgets.QPushButton("&Submit")
        self.quitButton = QtWidgets.QPushButton("&Quit")

        buttonLayout1 = QtWidgets.QVBoxLayout()
        buttonLayout1.addWidget(nameLabel)
        buttonLayout1.addWidget(self.nameLine)
        buttonLayout1.addWidget(self.submitButton)
        buttonLayout1.addWidget(self.quitButton)

        self.submitButton.clicked.connect(self.submitContact)
        self.quitButton.clicked.connect(self.closeIt)

        mainLayout = QtWidgets.QGridLayout()
        # mainLayout.addWidget(nameLabel, 0, 0)
        mainLayout.addLayout(buttonLayout1, 0, 1)

        self.setLayout(mainLayout)
        self.setWindowTitle("Hello Qt")

    def submitContact(self):
        name = self.nameLine.text()

        if name == "":
            QtWidgets.QMessageBox.information(self, "Empty Field",
                                          "Please enter a name and address.")
            return
        else:
            QtWidgets.QMessageBox.information(self, "Success!",
                                          "Hello %s!" % name)

    def closeIt(self):
        """
        doc string
        """
        self.close()


def change_key_str_to_int(dic_folder_st):
    rep = {}
    for key in list(dic_folder_st.keys()):
        rep[int(key)] = dic_folder_st[key].replace("\\", "/")
    return rep


def lighten_color(color, amount=0.5):
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.

    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except Exception as e:
        c = color
        print(e)
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])


def getListOfFiles(dirName):
    '''
    For the given path, get the List of all files in the directory tree
    '''
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
    return allFiles


def find_a_file(rootdir=None, fileName=None):
    if rootdir is None:
        from mainOpt import readAnimatLabDir
        animatsimdir = readAnimatLabDir()
        rootdir = animatsimdir

    if fileName is None:
        fileName = "GEPdata00.par"
    # Get the list of all files in directory tree at given path
    # listOfFiles = getListOfFiles(rootdir)
    # Print the files
    # for elem in listOfFiles:
    #    print(elem)
    # print ("****************")

    # Get the list of all files in directory tree at given path
    listOfFiles = list()
    listOfDir = list()
    for (dirpath, dirnames, filenames) in os.walk(rootdir):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]
        listOfDir += [os.path.join(dirpath, file) for file in dirnames]

    listOfSearchedFiles = list()
    listOfSearchedDir = list()
    # Print the files
    for elem in listOfFiles:
        if elem[-len(fileName):] == fileName:
            print(elem)
            listOfSearchedFiles.append(elem)
            listOfSearchedDir.append(os.path.split(elem)[0])
    return listOfSearchedDir


def save_eps_pdf(graph_path, tit, sstit):
    nomfic_eps = r'{0}\{1}{2}.eps'.format(graph_path, tit, sstit)
    nomfic_pdf = r'{0}\{1}{2}.pdf'.format(graph_path, tit, sstit)
    if len(nomfic_eps) > 250:
        nomfic_eps = r'{0}\{1}.eps'.format(graph_path, tit)
        nomfic_pdf = r'{0}\{1}.pdf'.format(graph_path, tit)

    if not os.path.exists(nomfic_eps):
        plt.savefig(nomfic_eps, bbox_inches='tight')
        plt.savefig(nomfic_pdf, bbox_inches='tight')
    else:
        root = nomfic_eps[:nomfic_eps.find(".eps")]
        print(len(root))
        k = 0
        while os.path.exists("{0}({1}){2}".format(root, k, ".eps")):
            k += 1
        nomfic_eps = "{0}({1}){2}".format(root, k, ".eps")
        nomfic_pdf = "{0}({1}){2}".format(root, k, ".pdf")
        plt.savefig(nomfic_eps, bbox_inches='tight')
        plt.savefig(nomfic_pdf, bbox_inches='tight')
    print("files saved under {0}".format(nomfic_eps))


"""
def create_workbook(path):
    workbook = Workbook()
    sheet = workbook.active
    sheet['A1'] = 'Hello'
    sheet['A2'] = 'from'
    sheet['A3'] = 'OpenPyXL'
    workbook.save(path)
"""

def dataframe_to_rows(df, index=False):
    
    rows = []
    if index == True:
        row = [""]
        for col in list(df.columns):
            row.append(col)
        
    else:
        row = list(df.columns)
    rows.append(row)
    indexes = list(df.index)
    for id_row, row in enumerate(df.index):
        # print("row=", id_row, "index=", indexes[id_row])
        if index:
            rowVals = [indexes[id_row]]
        else:
            rowVals = []
        for idx, col in enumerate(df.columns):
            # print("\t {:2.2f}".format(df.loc[row, col]), end=" " )
            rowVals.append(df.loc[row, col])
        # print()
        rows.append(rowVals)
    return rows
       


"""
def save_df_to_xls(df, pathGEP, file_name, typ=None):

    # Although this procedure has been fixed for Python 3.8, we do not use it
    # anymore because dataframe conversion is not straight forward and more
    # over importing xlsx file to built a dataframe is not satisfying. We use
    # csv file instead.

    workbook = Workbook()
    sheet = workbook.active
   
    rows = dataframe_to_rows(df, index=False)
    for r_idx, row in enumerate(rows, 1):
        for c_idx, value in enumerate(row, 1):
            sheet.cell(row=r_idx, column=c_idx, value=value)
    completeName = os.path.join(pathGEP, file_name + '.xlsx')
    workbook.save(completeName)
    print('DataFrame is written successfully to Excel Sheet.')
"""


def save_df_to_csv(df, pathGEP, file_name, typ=None):
    completeName = os.path.join(pathGEP, file_name + '.csv')
    df.to_csv(completeName, sep=",")


def calculate_dist_par(df_parremain, par_names, idx, rg, dist):
    d2 = 0
    for par in par_names:
        x = df_parremain[par][idx] - df_parremain[par][rg]
        if x > dist:
            d = None
            return None
        d2 += x*x
    d = sqrt(d2)
    if d < dist:
        return d
        # print(idx, d)
    return d


def find_close_param(df_parremain, par_names, rg, dist):
    """
    Gets all parameter sets in df_parremain that are close to a given parameter
    set (at distance < dist).
    Returns the list of ranks of such parameters and list of distances¨2
    """
    lst_closepar_rg = []
    lst_closepar_d = []
    for idx in df_parremain.index:
        if idx != rg:
            """
            d2 = 0
            for par in par_names:
                x = df_parremain[par][idx] - df_parremain[par][rg]
                if x > dist:
                d2 += x*x
            d = sqrt(d2)
            """
            d = calculate_dist_par(df_parremain, par_names, idx, rg, dist)
            if d is not None:
                # print idx, d
                lst_closepar_rg.append(idx)
                lst_closepar_d.append(d)
    return lst_closepar_rg, lst_closepar_d


def Calc_disp(df_bhvremain, source_rg, lst_closepar_rg, behav_col):
    """
    """
    behavs_cues = df_bhvremain[df_bhvremain.columns[behav_col]]
    # =========== normalization of endangle => division by 100 ===========
    behav_normalized = copy.deepcopy(behavs_cues)
    behav_normalized[df_bhvremain.columns[behav_col][0]] *= 0.01
    lst_bhv_dist = []
    for idx in lst_closepar_rg:
        if idx != source_rg:
            bhv_d2 = 0
            for bhv in df_bhvremain.columns[behav_col]:
                x = behav_normalized[bhv][idx] -\
                    behav_normalized[bhv][source_rg]
                bhv_d2 += x*x
            bhv_d = sqrt(bhv_d2)
            lst_bhv_dist.append(bhv_d)
    return lst_bhv_dist


def getValuesFromText(txt):
    t2 = txt
    xtab = []
    while t2.find('\t') != -1:
        t1 = t2[:t2.find('\t')]
        t2 = t2[t2.find('\t')+1:]
        xtab.append(t1)
    t1 = t2[:t2.find('\n')]
    xtab.append(t1)
    return xtab


def read_dist_list(pathGEP, baseName):
    """
    Reads a table containing as columns: idx, run, score, nBhvOK, density
    This table was saved as a text file in a previous run of grid_method()
    """
    tabFinal = []
    # idx = 0
    completeName = os.path.join(pathGEP, baseName + '.txt')
    with open(completeName, 'r') as fich:
        columns_txt = fich.readline()
        columns = getValuesFromText(columns_txt)
        while 1:
            # while idx < 9:
            tab1 = []
            tab2 = []
            valid_line = True
            txt = fich.readline()
            if txt == '':
                break
            else:
                tab1 = getValuesFromText(txt)
                # print(tab1)
                try:
                    x = int(tab1[0])
                except Exception as e:
                    x = tab1
                    print(e, "alpha-numeric line", x)
                    valid_line = False
                if valid_line:
                    for k in range(len(columns)):
                        try:
                            if tab1[k].find('.') == -1:  # not a float
                                tab2.append(int(tab1[k]))
                            else:
                                tab2.append(float(tab1[k]))
                            # tab2.append(tab1[k])
                        except Exception as e:
                            if len(tab1) < len(columns):
                                tab2.append(0)
                            else:
                                tab2.append(np.NaN)
                            k = 0
                            if (verbose > 2):
                                print(e)
                    tabFinal.append(tab2)
            # idx += 1
        tab_dist = tabFinal
    fich.close()
    df_dist = pd.DataFrame(tab_dist[:],
                           columns=columns,
                           index=np.arange(len(tab_dist[:])))
    return df_dist


def read_tab_scores(pathGEP, baseName):
    tabFinal = []
    # idx = 0
    completeName = os.path.join(pathGEP, baseName + '.txt')
    with open(completeName, 'r') as fich:
        columns_txt = fich.readline()
        columns = getValuesFromText(columns_txt)
        while 1:
            # while idx < 9:
            tab1 = []
            tab2 = []
            valid_line = True
            txt = fich.readline()
            if txt == '':
                break
            else:
                tab1 = getValuesFromText(txt)
                # print(tab1)
                try:
                    x = int(tab1[0])
                except Exception as e:
                    x = tab1
                    print(e, "alpha-numeric line", x)
                    valid_line = False
                if valid_line:
                    for k in range(len(columns)):
                        try:
                            if tab1[k].find('.') == -1:  # not a float
                                tab2.append(int(tab1[k]))
                            else:
                                tab2.append(float(tab1[k]))
                            # tab2.append(tab1[k])
                        except Exception as e:
                            if len(tab1) < len(columns):
                                tab2.append(0)
                            else:
                                tab2.append(np.NaN)
                            k = 0
                            if (verbose > 2):
                                print(e)
                    tabFinal.append(tab2)
            # idx += 1
        tab_scores = tabFinal
    fich.close()
    return tab_scores


def get_titre(path, baseName):
    titre = "{}/{}".format(path, baseName)
    titre = titre.replace("\\", "/")

    slashPositions = [pos for pos, char in enumerate(titre) if char == "/"]
    end1 = max([x for x in slashPositions[:-1] if x < 100])
    tit1 = titre[: end1+1]
    if end1 < max(slashPositions):
        end2 = max([x for x in slashPositions if x < 160])
        tit2 = titre[end1+1:end2+1]
        if end2 < max(slashPositions):
            end3 = max([x for x in slashPositions if x < 240])
            tit3 = titre[end2+1:end3+1]
            if end3 < max(slashPositions):
                tit4 = titre[end3+1:]
                titr = tit1 + "\n" + tit2 + "\n" + tit3 + "\n" + tit4
            else:
                tit3 = titre[end2+1:]
                titr = tit1 + "\n" + tit2 + "\n" + tit3
        else:
            tit3 = titre[end2+1:]
            titr = tit1 + "\n" + tit2 + "\n" + tit3
    else:
        titr = titre
    return titr


def plot_2D_graph_from_array(x, graph_path,  baseName,
                             nameX, nameY, extent, col_scale_range):
    """
    plot_2D_graph_from_array(x, graph_path,  baseName, nameX, nameY, extent)
    x is an array of arrays containing values (typically the number of
    behaviours in each case of the grid defined by the array of arrays, but
    it may be any value that defines a feature of the grid).
    => graph_path is the path to save the graphs (.esp and .pdf)
    => baseName is the name of the graph
    => nameX and nameY are the X and Y axes legends
    => extent is an array [x_min, x_max, y_min, y_max] used to define the
    ranges of x and y axes.
    """
    path = os.path.split(graph_path)[0]
    titre = get_titre(path, baseName)
    # nameX = df_cues_dist.columns[0]
    # nameY = df_cues_dist.columns[1]
    w = 10
    h = 9
    d = 80
    vmin = col_scale_range[0]
    vmax = col_scale_range[1]
    plt.figure(figsize=(w, h), dpi=d)
    color_map = plt.imshow(x, origin='lower',
                           extent=extent,
                           aspect='auto',
                           vmin=vmin, vmax=vmax)
    # color_map = plt.imshow(x, origin='lower')
    # color_map = plt.imshow(x)

    color_map.set_cmap("nipy_spectral")
    # plt.colorbar()
    cbar = plt.colorbar()
    cbar.ax.tick_params(labelsize=18)
    plt.xlabel(nameX, fontsize=18)
    plt.ylabel(nameY, fontsize=18)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.suptitle(titre, fontsize=12, y=0.97)
    plt.savefig(os.path.join(graph_path, baseName + '.pdf'))
    plt.savefig(os.path.join(graph_path, baseName + '.eps'))
    plt.show()


def do_plot_2D_density_map_metrics(df_bhvremain, behav_col, bhv_names,
                                   graph_path, GEPdataName, nbruns,
                                   min_x=0, max_x=120,
                                   min_y=0, max_y=5,
                                   autoscale=True):
    """
    from df_bhvremain, builds a table 40x40 of number of bhvs contained in each
    frame case.
    """
    nbcol = 40
    nbrow = 40
    """
    min_x = 0
    max_x = 120
    min_y = 0
    max_y = 1.4
    """
    intervalx = (max_x - min_x)/nbcol
    intervaly = round((max_y - min_y)*1000/nbrow)/1000
    extent = [min_x, max_x, min_y, max_y]
    # ================= find rank ond nbruns in orig_rg ===================
    end_rank = df_bhvremain[df_bhvremain["orig_rg"] >= nbruns].index[0]
    behav_cues = df_bhvremain[df_bhvremain.columns[behav_col]]
    df_cues = copy.deepcopy(behav_cues)
    df_cues_sel = df_cues.loc[:][:end_rank]
    tab_nb_bhv = []
    x_name = bhv_names[behav_col[0]]
    y_name = bhv_names[behav_col[1]]
    for i in range(nbrow):
        yi = i*intervaly + min_y
        ys = (i+1)*intervaly + min_y
        row_df = df_cues_sel.loc[(df_cues_sel[y_name] >= yi) &
                                 (df_cues_sel[y_name] < ys)]

        nb_bhv_row = []
        for j in range(nbcol):
            xi = j*intervalx + min_x
            xs = (j+1)*intervalx + min_x
            temp_col_df = row_df.loc[(row_df[x_name] >= xi) &
                                     (row_df[x_name] < xs)]
            # print yi, ys, xi, xs, temp_col_df
            nb_bhv_row.append(len(temp_col_df[x_name]))
        # print nb_bhv_row
        tab_nb_bhv.append(nb_bhv_row)
    tab_nb_bhv = np.array(tab_nb_bhv)

    nameX = df_cues.columns[0]
    nameY = df_cues.columns[1]
    # nb_runs = len(df_cues_sel)

    color_min = 0
    color_max = tab_nb_bhv.max() + 1
    if not autoscale:
        # --------------------------------------------------------------------
        listChoix = ['colorScale_range']
        listDicColScalRange = [{'colorScale_range': ["inf", "sup"]}]
        listDic_Color_range = [{"inf": color_min, "sup": color_max}]
        factorLimits_keys = ["inf", "sup"]
        titleText = "set limits for factor"
        rep = ChooseInList.listTransmit(parent=None,
                                        graphNo=0,
                                        listChoix=listChoix,
                                        items=factorLimits_keys,
                                        listDicItems=listDicColScalRange,
                                        onePerCol=[0],
                                        colNames=["colorScale_range", 'value'],
                                        dicValues=listDic_Color_range[0],
                                        typ="val",
                                        titleText=titleText)
        listDicColScalRange = rep[0]
        if len(rep[1]) > 0:    # No values entered,  ESC button was used
            color_min = float(rep[1]['inf'])
            color_max = float(rep[1]['sup'])
        # --------------------------------------------------------------------
    col_scale_range = (color_min, color_max)

    if behav_col[1] == 8:
        ordTyp = "duration"
    elif behav_col[1] == 6:
        ordTyp = "maxSpeed"
    baseName = "{}_{}_{}_{}{}".format(GEPdataName, ordTyp, "densityMap",
                                      nbruns, "_runs")
    plot_2D_graph_from_array(tab_nb_bhv, graph_path,  baseName,
                             nameX, nameY, extent, col_scale_range)


def build_stability_dataframe(df_bhvremain, df_parremain, graph_path,
                              GEPdataName, behav_col, par_names,
                              search_dist):
    """
    Prepares a dataframe in which, for each behavior (duration,
    amplitude) a mean distance is calculated from
    all behaviors produced by parameters in the vicinyty (dist<search_dist)
    of the parameters of this behavior. When several distances are
    obtained, the mean value is retained.
    """
    if behav_col[1] == 8:
        ordTyp = "duration"
    elif behav_col[1] == 6:
        ordTyp = "maxSpeed"
    baseName = "{}_{}_{}{}".format(GEPdataName[:], ordTyp, "List_stab",
                                   search_dist)
    completeName = os.path.join(graph_path, baseName + '.txt')
    if not os.path.exists(completeName):
        df_dist = []
        lst_dist = []
        print("please wait... building unstability map")
        for source_rg in df_bhvremain.index:
            res = find_close_param(df_parremain, par_names,
                                   source_rg, search_dist)
            lst_closepar_rg = res[0]
            # lst_closepar_d = res[1]
            bhv_dist = Calc_disp(df_bhvremain, source_rg,
                                 lst_closepar_rg, behav_col)
            mean_dist = np.array(bhv_dist).mean()
            # print source_rg, mean_dist
            if source_rg % 10 == 0:
                print("*", end=" ")
            lst_dist.append(mean_dist)
            """"
            df_dist.append(pd.DataFrame({'rg': lst_closepar_rg,
                                        'par_d': lst_closepar_d,
                                        'bhv_d': bhv_dist},
                                        index = range(len(lst_closepar_rg))))
            """
        print()
        # =================         saves lst_dist        ====================
        # baseName = "{}{}{}_{}".format(GEPdataName[:], ordTyp, "_List_stab",
        #                               search_dist)
        # completeName = os.path.join(graph_path, baseName + '.txt')
        with open(completeName, 'w') as fich:
            s = "index\tmeandist\n"
            fich.write(s)
            for idx, dist in enumerate(lst_dist):
                s = "{}\t{:2.3f}\n".format(idx, dist)
                fich.write(s)
        fich.close()
        # =================         reads lst_dist        ====================
        df_dist = read_dist_list(graph_path, baseName)
        print(df_dist)
        behavs_cues = df_bhvremain[df_bhvremain.columns[behav_col]]
        df_cues_dist = copy.deepcopy(behavs_cues)
        df_cues_dist['dist_bhv'] = df_dist["meandist"]
        df_cues_dist['rg'] = df_cues_dist.index

    else:
        # =================         reads lst_dist        ====================
        df_dist = read_dist_list(graph_path, baseName)
        print(df_dist)
        behavs_cues = df_bhvremain[df_bhvremain.columns[behav_col]]
        df_cues_dist = copy.deepcopy(behavs_cues)
        df_cues_dist['dist_bhv'] = df_dist["meandist"]
        df_cues_dist['rg'] = df_cues_dist.index
    return df_cues_dist


def do_plot_2D_stability_map(MyWin, df_cues_dist, search_dist, graph_path,
                             GEPdataName):
    """
    plots the stability map
    """
    nbcol = 40
    nbrow = 40
    """
    min_x = 0
    max_x = 120
    min_y = 0.2
    max_y = 1.4
    """
    behav_col = MyWin.behav_col
    bhv_names = MyWin.bhv_names
    name_x = bhv_names[behav_col[0]]
    name_y = bhv_names[behav_col[1]]
    max_x_bhv = df_cues_dist[name_x].max()
    max_y_bhv = df_cues_dist[name_y].max()
    max_x = float(int(max_x_bhv*10)+1)/10
    max_y = float(int(max_y_bhv*10)+1)/10
    min_x = 0
    min_y = 0
    intervalx = (max_x - min_x)/nbcol
    intervaly = round((max_y - min_y)*1000/nbrow)/1000
    tab_nb_bhv = []
    map_bhv = []
    tab_dist_bhv = []
    name_x = MyWin.bhv_names[MyWin.behav_col[0]]
    name_y = MyWin.bhv_names[MyWin.behav_col[1]]
    for i in range(nbrow):
        yi = i*intervaly + min_y
        ys = (i+1)*intervaly + min_y
        row_df = df_cues_dist.loc[(df_cues_dist[name_y] >= yi) &
                                  (df_cues_dist[name_y] < ys)]
        map_bhv_row = []
        nb_bhv_row = []
        dist_bhv_row = []
        for j in range(nbcol):
            xi = j*intervalx + min_x
            xs = (j+1)*intervalx + min_x
            temp_col_df = row_df.loc[(row_df[name_x] >= xi) &
                                     (row_df[name_x] < xs)]
            # print yi, ys, xi, xs, temp_col_df
            map_bhv_row.append([yi, ys, xi, xs,
                               len(temp_col_df[name_x])])
            nb_bhv_row.append(len(temp_col_df[name_x]))
            try:
                # we cannot use mean() because this will give NaN in
                # temp_col_df["dist_bhv"].mean()
                # ===== elimination of cases without distance (NaN) ======
                tmp_df = copy.deepcopy(temp_col_df["dist_bhv"])
                tmp_ser = pd.Series(tmp_df)
                nan_elems = tmp_ser.isnull()
                remove_nan = tmp_ser[~nan_elems]
                tmpdist = np.array(remove_nan)
                if len(tmpdist) > 0:
                    dist_bhv_row.append(tmpdist.mean())
                else:
                    dist_bhv_row.append(np.NaN)
            except Exception as e:
                if (verbose > 2):
                    print(e)
        # if in the process a case is empty (NaN) -> a negative value
        # is given: -0.01 is small enough for the case to appear in black
        # but not too larg to modify the color scale
        stab_bhv_row = [-0.01 if isnan(x) else x for x in dist_bhv_row]
        # print nb_bhv_row
        tab_nb_bhv.append(nb_bhv_row)
        map_bhv.append(map_bhv_row)
        tab_dist_bhv.append(stab_bhv_row)
    tab_nb_bhv = np.array(tab_nb_bhv)
    map_bhv = np.array(map_bhv)
    tab_dist_bhv = np.array(tab_dist_bhv)
    extent = [min_x, max_x, min_y, max_y]

    nameX = df_cues_dist.columns[0]
    nameY = df_cues_dist.columns[1]
    nb_runs = len(df_cues_dist)

    if behav_col[1] == 8:
        ordTyp = "duration"
    elif behav_col[1] == 6:
        ordTyp = "maxSpeed"
    col_scale_range = (-0.01, tab_nb_bhv.max())
    baseName = "{}_{}_{}_{}".format(GEPdataName, ordTyp, nb_runs, "densityMap")
    plot_2D_graph_from_array(tab_nb_bhv, graph_path,  baseName,
                             nameX, nameY, extent, col_scale_range)

    baseName = "{}_{}_{}_{}_{}".format(GEPdataName, ordTyp, nb_runs,
                                       "stabilityMap", search_dist)
    col_scale_range = (-0.01, tab_dist_bhv.max())
    plot_2D_graph_from_array(tab_dist_bhv, graph_path,  baseName,
                             nameX, nameY, extent, col_scale_range)


def makeDensityMap_contour(rel_behavs_cues, step=0.05,
                           xmin=None, xmax=None, ymin=None, ymax=None):
    """
    builds a matrix containing the number of elements in each unit surface
    (squarre step x step) covering the X and the Y range of behavs_cues
    """
    # xmin = None
    df = copy.deepcopy(rel_behavs_cues)
    if xmin is None:
        xmin = min(df[df.columns[0]]) - step
        xmax = max(df[df.columns[0]])
        ymin = min(df[df.columns[1]]) - step
        ymax = max(df[df.columns[1]])
    else:
        xmin = xmin - step
        ymin = ymin - step

    xmin_gr = int(xmin/step) * step
    xmax_gr = (int(xmax/step) + 1) * step
    print(xmin, xmax)
    ymin_gr = int(ymin/step) * step
    ymax_gr = (int(ymax/step) + 1) * step
    print(ymin, ymax)
    listx = np.linspace(xmin_gr, xmax_gr, int((xmax_gr-xmin_gr)/step)+1)
    listy = np.linspace(ymin_gr, ymax_gr, int((ymax_gr-ymin_gr)/step)+2)

    density_map = []

    # xmin = min(df[df.columns[0]])
    # xmax = max(df[df.columns[0]])
    # print xmin, xmax
    # ymin = min(df[df.columns[1]])
    # ymax = max(df[df.columns[1]])
    # print ymin, ymax
    for yval in listy:
        res = []
        for xval in listx:
            # print x*step, y*step
            tmp_df = copy.deepcopy(df)
            onTheSpotx1 = (tmp_df[tmp_df.columns[0]] > xval)
            tmp_df = tmp_df[onTheSpotx1]
            onTheSpotx2 = (tmp_df[tmp_df.columns[0]] < xval+step)
            tmp_df = tmp_df[onTheSpotx2]
            onTheSpoty1 = (tmp_df[tmp_df.columns[1]] > yval)
            tmp_df = tmp_df[onTheSpoty1]
            onTheSpoty2 = (tmp_df[tmp_df.columns[1]] < yval+step)
            tmp_df = tmp_df[onTheSpoty2]
            # print len(tmp_df)
            res.append(len(tmp_df))
        density_map.append(res)
    return density_map, listx, listy


def plot_3D_density_map_contour(df_bhvremain, behav_col, step=0.02,
                                incline=60, rot=-90,
                                xmin=None, xmax=None, ymin=None, ymax=None):
    """
    Plots a 3D-Graph using the density_map and the listx, listy to build
    a X, Y grid
    """
    behavs_cues = df_bhvremain[df_bhvremain.columns[behav_col]]
    rel_behavs_cues = behavs_cues/[MyWin.scale_x, MyWin.scale_y]
    res = makeDensityMap_contour(rel_behavs_cues, step=step,
                                 xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
    (density_map, listx, listy) = res
    nameX = rel_behavs_cues.columns[0]
    nameY = rel_behavs_cues.columns[1]
    X, Y = np.meshgrid(listx, listy)
    Z = np.array(density_map)
    fig = plt.figure(figsize=(7, 7), dpi=100)
    ax = plt.axes(projection='3d')
    ax.contour3D(X, Y, Z, 50, cmap='cool')
    # ax.contour3D(X, Y, Z, 50, cmap='binary')
    # ax.contour3D(X, Y, Z, 50, cmap='viridis')
    ax.set_xlabel(nameX)
    ax.set_ylabel(nameY)
    ax.set_zlabel("Nb evts")
    ax.view_init(incline, rot)
    fig.show()


def plot_2D_density_map_contour(MyWin, df_bhvremain, behav_col, graph_path,
                                strGEPdataName, nbruns=None,
                                step=0.02, aimbhv=[],
                                xmin=0, xmax=1.2, ymin=0, ymax=1.5,
                                saveDM=False):
    """
    Plots a 2D-Graph using the density_map (contour) and the listx, listy to
    build a X, Y grid. Density_map, listx and listy are obtained from the
    function makeDensityMap_contour()
    """
    behav_cues = df_bhvremain[df_bhvremain.columns[behav_col]]
    if nbruns is None:
        nbruns = df_bhvremain["orig_rg"].max()
    # ================= find rank ond nbruns in orig_rg ===================
    end_rank = df_bhvremain[df_bhvremain["orig_rg"] >= nbruns].index[0]
    df_cues = copy.deepcopy(behav_cues)
    df_cues_sel = df_cues.loc[:][:end_rank]
    rel_behavs_cues = df_cues_sel/[MyWin.scale_x, MyWin.scale_y]
    res = makeDensityMap_contour(rel_behavs_cues, step=step,
                                 xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
    (density_map, listx, listy) = res
    nameX = rel_behavs_cues.columns[0]
    nameY = rel_behavs_cues.columns[1]
    if behav_col[1] == 8:      # if ordonate is duration...
        labelnameX = nameX + "(x 0.01)"
        labelnameY = nameY
    elif behav_col[1] == 6:
        labelnameX = nameX + "(x 0.01)"
        labelnameY = nameY + "(x 0.01)"

    X, Y = np.meshgrid(listx, listy)
    Z = np.array(density_map)
    Z[Z == 1] = 4   # replace all 1 by 4
    Z[Z == 2] = 4   # replace all 1 by 4
    Z[Z == 3] = 4   # replace all 1 by 4
    nbniv = int(np.amax(Z))

    plt.figure(figsize=(10, 9), dpi=80)
    plt.contourf(X, Y, Z, nbniv, cmap='nipy_spectral', vmin=0, vmax=130)
    cbar = plt.colorbar()
    cbar.ax.tick_params(labelsize=18)
    plt.xlabel(labelnameX, fontsize=18)
    plt.ylabel(labelnameY, fontsize=18)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    for point in aimbhv:
        x = point[0]-MyWin.scale_x*step/2
        y = point[1]-MyWin.scale_y*step/2
        relx, rely = x/MyWin.scale_x, y/MyWin.scale_y
        plt.plot(relx, rely, '-p', color='gray',
                 markersize=5, linewidth=4,
                 markerfacecolor='white',
                 markeredgecolor='gray',
                 markeredgewidth=2)
    if saveDM:
        path = os.path.split(graph_path)[0]
        strGEPdataName = os.path.splitext(strGEPdataName)[0]
        if behav_col[1] == 8:
            ordTyp = "duration"
        elif behav_col[1] == 6:
            ordTyp = "maxSpeed"
        baseName = "{}_{}_{}{}{}{}".format(strGEPdataName, ordTyp,
                                           len(df_cues_sel),
                                           "bhv_DensityContour_",
                                           nbruns, "runs")
        titre = get_titre(path, baseName)
        plt.suptitle(titre, fontsize=12, y=0.97)
        plt.savefig(os.path.join(graph_path, baseName + '.pdf'))
        plt.savefig(os.path.join(graph_path, baseName + '.eps'))
    plt.show()


def read_metric_table(graph_path, baseName):
    """
    Reads a table containing as columns: idx, run, score, nBhvOK, density
    This table was saved as a text file in a previous run of grid_method()
    """
    tabFinal = []
    # idx = 0
    completeName = os.path.join(graph_path, baseName + '.txt')
    with open(completeName, 'r') as fich:
        columns_txt = fich.readline()
        colums = getValuesFromText(columns_txt)
        while 1:
            # while idx < 11:
            tab1 = []
            tab2 = []
            valid_line = True
            txt = fich.readline()
            if txt == '':
                break
            else:
                tab1 = getValuesFromText(txt)
                # print(tab1)
                try:
                    x = int(tab1[0])
                except Exception as e:
                    x = tab1
                    print(e, "alpha-numeric line", x)
                    valid_line = False
                if valid_line:
                    for k in range(len(colums)):
                        try:
                            if tab1[k].find('.') == -1:  # not a float
                                tab2.append(int(tab1[k]))
                            else:
                                tab2.append(float(tab1[k]))
                            # tab2.append(tab1[k])
                        except Exception as e:
                            if len(tab1) < len(colums):
                                tab2.append(0)
                            else:
                                tab2.append(1)
                            k = 0
                            if (verbose > 2):
                                print(e)
                    tabFinal.append(tab2)
            # idx += 1
        tab_scores = tabFinal
    fich.close()
    df_score = pd.DataFrame(tab_scores[:],
                            columns=colums,
                            index=np.arange(len(tab_scores[:])))
    return df_score


def FitCourseToDataFrame(completeName):
    """
    Reads a text file (FitCourse.txt). The first line is measured param
    names. There may be several successive sessions (CMAeData-00,
    CMAeData-01...). They are grouped in a single dataframe. Returns the
    nparray of data, the dataframe and the list of parameter names.
    """
    tabFinal = []
    tabnewstart = []
    # idx = 0
    # prevline = ""
    # prevtrial = 0
    with open(completeName, 'r') as fich:
        params = fich.readline()
        params = params[:-2] + "\tsaved\n"
        tabparams = getValuesFromText(params)
        while 1:
            # while idx < 11:
            tab1 = []
            tab2 = []
            valid_line = True
            txt = fich.readline()
            if txt == '':
                break
            else:
                tab1 = getValuesFromText(txt)
                # print(tab1)
                if tab1[0] == "1":
                    # tabnewstart.append(int(prevtrial))
                    # print(prevline)
                    tabnewstart.append(len(tabFinal)+1)
                else:
                    try:
                        x = float(tab1[0])
                    except Exception as e:
                        x = tab1
                        print(e, "alpha-numeric line", x)
                        valid_line = False
                if valid_line:
                    for k in range(len(tabparams)):
                        try:
                            tab2.append(float(tab1[k]))
                            # tab2.append(tab1[k])
                        except Exception as e:
                            if len(tab1) < len(tabparams):
                                tab2.append(0)
                            else:
                                tab2.append(1)
                            k = 0
                            if (verbose > 2):
                                print(e)
                    nptab2 = np.array(tab2)
                    tabFinal.append(nptab2)
            # idx += 1
    print(tabnewstart)
    tabFinal = np.array(tabFinal)
    # tabFinal = np.transpose(tabFinal)
    dataframe = pd.DataFrame(tabFinal, columns=tabparams)
    dataframe.index = np.arange(1, len(dataframe)+1, 1)
    return (tabFinal, dataframe, tabparams, tabnewstart)


def plotdataframe(dataframe, par, Deb, Fin, tabnewstart,
                  unitx="xaxis", unity="yaxis", color="b", ylim=(-5, 50)):
    plt.legend(fontsize=30)
    if Fin-Deb < 20:
        dataframe[Deb:Fin][par].plot(color=color, marker="o")
    else:
        dataframe[Deb:Fin][par].plot(color=color, ylim=ylim)
    for idx, newstart in enumerate(tabnewstart):
        if newstart in range(Deb, Fin):
            plt.axvline(tabnewstart[idx])
    plt.xlabel(unitx, fontsize=20)
    plt.ylabel(unity, fontsize=20)
    plt.legend(loc=0, fontsize=18)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    # plt.rcParams.update({'font.size': 28})


def plotdf_improve(dataframe, par, Deb, Fin, tabnewstart,
                   unitx="xaxis", unity="yaxis", color="b", ylim=(-5, 50)):
    """
    Plots one parameter (par) against time from Deb to Fin. Each time a new
    start is present in tabnewstart, a vertical line is traced.
    """
    if (par == "eval") or (par == "mse"):
        par2 = "bestfit"
    if par == "coactpenality":
        par2 = "bestcoact"
    new_df = copy.deepcopy(dataframe)
    # ======    creates one new column    =================
    lst_bestfit = []
    lst_bestcoact = []
    # bestfit = new_df["eval"][1]
    bestfit = new_df[par][1]
    bestcoact = new_df["coactpenality"][1]
    for idx in range(1, len(new_df)):
        lst_bestfit.append(bestfit)
        lst_bestcoact.append(bestcoact)
        if idx in tabnewstart:
            bestfit = new_df["eval"][idx]
            bestcoact = new_df["coactpenality"][idx]
        """
        # if idx in range(len(new_df)-10, len(new_df)):
        if idx in range(1169, 1200):
            print idx, new_df["eval"][idx], "=>", bestfit,
            print "  \t", new_df["coactpenality"][idx], "=>", bestcoact
        """
        if new_df["eval"][idx+1] < bestfit:
            bestfit = new_df["eval"][idx+1]
        if new_df["coactpenality"][idx+1] < bestcoact:
            bestcoact = new_df["coactpenality"][idx+1]
    lst_bestfit.append(bestfit)
    lst_bestcoact.append(bestcoact)
    new_df.loc[:, 'bestfit'] = lst_bestfit
    new_df.loc[:, 'bestcoact'] = lst_bestcoact
    """
    saved_OK = dataframe['saved'] == 1
    df = dataframe[saved_OK]
    if len(df) > 0:
        print df
    """
    ylimMax = new_df[Deb:Fin][par2].max()*1.2
    ylimMin = -ylimMax/20
    ylim=(ylimMin, ylimMax)
    # plt.legend(fontsize=30)
    if Fin-Deb < 20:
        new_df[Deb:Fin][par2].plot(color=color, marker="o")
    else:
        new_df[Deb:Fin][par2].plot(color=color, ylim=ylim)
    for idx, newstart in enumerate(tabnewstart):
        # if newstart in range(Deb, Fin):
        if newstart in range(new_df.index[Deb], new_df.index[Fin-1]):
            plt.axvline(tabnewstart[idx])
    plt.xlabel(unitx, fontsize=20)
    plt.ylabel(unity, fontsize=20)
    # plt.legend(loc=0, fontsize=18)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    # plt.rcParams.update({'font.size': 28})


def adaptScale(max_valY):
    y = max_valY * 10000
    while (y > 10):
        y = y/10
    # BarreY = int(round((max_valY / y)))
    BarreY = max_valY / y
    if y < 1.1:
        scaleYMax = 1.1 * BarreY
    elif y < 1.2:
        scaleYMax = 1.2 * BarreY
    elif y < 1.5:
        scaleYMax = 1.5 * BarreY
    elif y < 2:
        scaleYMax = 2 * BarreY
    elif y < 5:
        scaleYMax = int(y + 1) * BarreY
    else:
        scaleYMax = int(y + 1) * BarreY
    return scaleYMax


def graphfromFitCourse(path, FitCourseFileName):
    """
    Uses the path to FitCourse to built a plot of the corresponding
    dataframe
    """
    completeName = os.path.join(path, FitCourseFileName)
    baseName = os.path.splitext(FitCourseFileName)[0]
    (tabFinal, dataframe,
     tabparams, tabnewstart) = FitCourseToDataFrame(completeName)
    df = copy.deepcopy(dataframe)
    plt.figure(figsize=(20, 20), dpi=50)

    plt.subplot(331)
    Deb = 0
    Fin = len(df)
    par = "mse"
    max_valY = df[Deb:Fin][par].max()
    min_valY = df[Deb:Fin][par][Fin]
    ylimMax = adaptScale(max_valY)
    if (max_valY - min_valY) < (0.5 * ylimMax):
        ylimMax *= 2
    ylimMin = -ylimMax/20
    plotdataframe(df, "mse", Deb, Fin, tabnewstart,
                  unitx="Trial", unity=par, color="b",
                  ylim=(ylimMin, ylimMax))

    plt.subplot(332)
    Deb = int(len(df)/2)
    Fin = len(df)
    max_valY = df[Deb:Fin][par].max()
    ylimMax = adaptScale(max_valY)
    if (max_valY - min_valY) < (0.5 * ylimMax):
        ylimMax *= 2
    ylimMin = -ylimMax/20
    plotdataframe(df, "mse", Deb, Fin, tabnewstart,
                  unitx="Trial", unity=par, color="b",
                  ylim=(ylimMin, ylimMax))

    plt.subplot(333)
    Deb = int(len(df)*3/4)
    Fin = len(df)
    max_valY = df[Deb:Fin][par].max()
    ylimMax = adaptScale(max_valY)
    # if (max_valY - min_valY) < (0.5 * ylimMax):
    #     ylimMax *= 2
    ylimMin = -ylimMax/20
    plotdataframe(df, "mse", Deb, Fin, tabnewstart,
                  unitx="Trial", unity=par, color="b",
                  ylim=(ylimMin, ylimMax))

    plt.subplot(334)
    Deb = 0
    Fin = len(df)
    par = "coactpenality"
    plotdataframe(df, "coactpenality", Deb, Fin, tabnewstart,
                  unitx="Trial", unity=par, color="orange")

    plt.subplot(335)
    Deb = int(len(df)/2)
    Fin = len(df)
    plotdataframe(df, "coactpenality", Deb, Fin, tabnewstart,
                  unitx="Trial", unity=par, color="orange")

    plt.subplot(336)
    Deb = int(len(df)*3/4)
    Fin = len(df)
    plotdataframe(df, "coactpenality", Deb, Fin, tabnewstart,
                  unitx="Trial", unity=par, color="orange")

    plt.subplot(337)
    Deb = 0
    Fin = len(df)
    par = "mse"
    max_valY = df[Deb:Fin][par][Deb + 1]
    min_valY = df[Deb:Fin][par][Fin]
    ylimMax = adaptScale(max_valY)
    if (max_valY - min_valY) < (0.5 * ylimMax):
        ylimMax *= 2
    ylimMin = -ylimMax/20
    plotdf_improve(df, "mse", Deb, Fin, tabnewstart,
                   unitx="Trial", unity=par, color="b",
                   ylim=(ylimMin, ylimMax))

    plt.subplot(338)
    Deb = int(len(df)/2)
    Fin = len(df)
    max_valY = df[Deb:Fin][par][Deb + 1]
    ylimMax = adaptScale(max_valY)
    if (max_valY - min_valY) < (0.5 * ylimMax):
        ylimMax *= 2
    ylimMin = -ylimMax/20
    plotdf_improve(df, "mse", Deb, Fin, tabnewstart,
                   unitx="Trial", unity=par, color="b",
                   ylim=(ylimMin, ylimMax))

    plt.subplot(339)
    Deb = int(len(df)*3/4)
    Fin = len(df)
    max_valY = df[Deb:Fin][par][Deb + 1]
    ylimMax = adaptScale(max_valY)
    # if (max_valY - min_valY) < (0.5 * ylimMax):
    #     ylimMax *= 2
    ylimMin = -ylimMax/20
    plotdf_improve(df, "mse", Deb, Fin, tabnewstart,
                   unitx="Trial", unity=par, color="b",
                   ylim=(ylimMin, ylimMax))

    plt.gcf().subplots_adjust(left=0.09, right=0.95, top=0.9, bottom=0.1,
                              wspace=0.2, hspace=0.25)
    bestfit = df["mse"].min()
    bestfitline = df.index[df['mse'] == bestfit].values
    if len(bestfitline) > 1:
        bestfitlineVal = bestfitline[0]
    else:
        bestfitlineVal = bestfitline
    titre = get_titre(path, FitCourseFileName)
    # titre = completeName
    titre = titre + "\n" + "bestfit= %3.3f at line %3d" % (bestfit,
                                                           bestfitlineVal)
    plt.suptitle(titre, fontsize=20)
    plt.savefig(os.path.join(path, baseName + '.pdf'))
    plt.savefig(os.path.join(path, baseName + '.eps'))
    plt.show()


def select_chartcol(optSet, colnames):
    list_elem = colnames
    typ = "chart_col"

    print("Select sensory neurons to plot (validate the selection window)")
    selected = optSet.sensColChartNames
    text = "select sensory neurons to plot"
    list_sensory_neur = choose_elements_in_list(list_elem, typ, selected, text)

    print("Select alpha MNs to plot (validate the selection window)")
    selected = optSet.mnColChartNames
    text = "select alpha MNs to plot"
    list_alpha_neur = choose_elements_in_list(list_elem, typ, selected, text)

    print("Select gamma MNs to plot (check and validate selection window)")
    selected = []
    text = "select gamma MN to plot"
    list_gamma_neur = choose_elements_in_list(list_elem, typ, selected, text)
    return list_sensory_neur, list_alpha_neur, list_gamma_neur


def graph_chart_elements(optSet, chart_path, chartName,
                         lstChartColNam=["1FlxPotMuscle", "1ExtPotMuscle"],
                         y_label="EMG (mV)",
                         title="_EMG_Mvt"):
    """
    Uses the path, chartname to built a plot of a dataframe of chart data.
    """
    # EMGsNames = ['1FlxPotMuscle', '1ExtPotMuscle']
    colnames = optSet.chartColNames
    # completeName = os.path.join(chart_path, chartName)
    completeName = chart_path + "/" + chartName
    baseName = os.path.splitext(chartName)[0]
    
    my_palette = sns.color_palette("tab10")
    # Tdf[:0.6]
    (L, df, titre, tabparams) = chartToDataFrame(completeName,
                                                 colnames=colnames)
    df.index = df.Time
    df[:0.6]

    plt.figure(figsize=(20, 8), dpi=50)

    plt.subplot(121)
    plt.rc('xtick', labelsize=14)   # fontsize of the x tick labels
    plt.rc('ytick', labelsize=14)   # fontsize of the x tick labels
    for col in range(len(lstChartColNam)):
        print()
        df_EMG = df[:][lstChartColNam[col]] * 1000
        df_EMG.loc[4:7].plot(color=my_palette[col])
    unitx = "Time (s)"
    # unity = "EMG (mV)"
    unity = y_label
    plt.xlabel(unitx, fontsize=18)
    plt.ylabel(unity, fontsize=18)
    plt.legend(fontsize=12)

    plt.subplot(122)
    df.loc[4:7]["Elbow"].plot(color="c")
    unitx = "Time (s)"
    unity = "Elbow Mvt (degres)"
    plt.xlabel(unitx, fontsize=18)
    plt.ylabel(unity, fontsize=18)
    plt.legend(fontsize=12)

    plt.suptitle(titre, fontsize=20)
    plt.savefig(os.path.join(chart_path, baseName + title + '.pdf'))
    #plt.savefig(os.path.join(chart_path, baseName + title + '.eps'))
    plt.show()

def graph_triphasic(optSet, chart_path, chartName, EMGsNames):
    """
    Uses the path, chartname to built a plot of a dataframe of chart data.
    """
    # EMGsNames = ['1FlxPotMuscle', '1ExtPotMuscle']
    colnames = optSet.chartColNames
    # completeName = os.path.join(chart_path, chartName)
    completeName = chart_path + "/" + chartName
    baseName = os.path.splitext(chartName)[0]
    
    my_palette = sns.color_palette("tab10")
    # Tdf[:0.6]
    (L, df, titre, tabparams) = chartToDataFrame(completeName,
                                                 colnames=colnames)
    df.index = df.Time
    df[:0.6]

    plt.figure(figsize=(20, 8), dpi=50)

    plt.subplot(121)
    plt.rc('xtick', labelsize=14)   # fontsize of the x tick labels
    plt.rc('ytick', labelsize=14)   # fontsize of the x tick labels
    for col in range(2):
        df_EMG = df[:][EMGsNames[col]] * 1000
        df_EMG[4:7].plot(color=my_palette[col])
    unitx = "Time (s)"
    unity = "EMG (mV)"
    plt.xlabel(unitx, fontsize=18)
    plt.ylabel(unity, fontsize=18)
    plt.legend(fontsize=12)

    plt.subplot(122)
    df[4:7]["Elbow"].plot(color="c")
    unitx = "Time (s)"
    unity = "Elbow Mvt (degres)"
    plt.xlabel(unitx, fontsize=18)
    plt.ylabel(unity, fontsize=18)
    plt.legend(fontsize=12)

    plt.suptitle(titre, fontsize=20)
    plt.savefig(os.path.join(chart_path, baseName + '_EMG_Mvt.pdf'))
    plt.savefig(os.path.join(chart_path, baseName + '_EMG_Mvt.eps'))
    plt.show()

def graphfromchart(optSet, chart_path, chartName, templateFileName):
    """
    Uses the path, chartname and corresponding mvt template to
    built a plot of a dataframe of chart data.
    """
    colnames = optSet.chartColNames
    completeName = os.path.join(chart_path, chartName)
    baseName = os.path.splitext(chartName)[0]
    rootname = os.path.split(chart_path)[0]
    result_path = rootname + "/ResultFiles"

    chart_plot_pickle_name = result_path + "/chart_plot.pkl"
    if os.path.exists(chart_plot_pickle_name):
        with open(chart_plot_pickle_name, 'rb') as f1:
            optSet.chart_column_to_plot = pickle.load(f1)
            list_sensory_neur = optSet.chart_column_to_plot[0]
            list_alpha_neur = optSet.chart_column_to_plot[1]
            list_gamma_neur = optSet.chart_column_to_plot[2]
    else:
        rep = select_chartcol(optSet, colnames)
        list_sensory_neur, list_alpha_neur, list_gamma_neur = rep
        if rep is not None:
            optSet.chart_column_to_plot = list(rep)
            with open(chart_plot_pickle_name, 'wb') as f1:
                pickle.dump(list(rep), f1)

    T = np.loadtxt(templateFileName)
    Tdf = pd.DataFrame(T)
    Tdf.index = Tdf[1]
    my_palette = sns.color_palette("tab10")
    # Tdf[:0.6]
    (L, df, titre, tabparams) = chartToDataFrame(completeName,
                                                 colnames=colnames)
    dfsrtTime = df.Time[0]
    # dfendTime = df.Time[len(df)-1]
    dfendTime = 9.99
    df.index = df.Time
    df[:0.6]
    # add two columns to df : TemplateTime and Template
    df.loc[:, 'TemplateTime'] = Tdf[dfsrtTime:dfendTime][1]
    df.loc[:, 'Template'] = Tdf[dfsrtTime:dfendTime][2]
    if verbose > 3:
        print("15 first rows...")
        print(df[dfsrtTime:dfsrtTime+0.15])
        print("15 last rows")
        print(df[dfendTime-0.15:dfendTime])

    plt.figure(figsize=(20, 15), dpi=50)
    plt.subplot(321)
    muscle = ["Triceps1", "Biceps1"]
    plt.rc('xtick', labelsize=14)   # fontsize of the x tick labels
    plt.rc('ytick', labelsize=14)   # fontsize of the x tick labels

    for col in range(2):
        df[:dfendTime][muscle[col]].plot(color=my_palette[col])
    unitx = "Time (s)"
    unity = "Force (N)"
    plt.xlabel(unitx, fontsize=18)
    plt.ylabel(unity, fontsize=18)
    plt.legend(fontsize=12)

    list_alpha_neur.sort()
    plt.subplot(322)
    for col, mn in enumerate(list_alpha_neur):
        df_mn = df[:dfendTime][mn] * 1000
        df_mn.plot(color=my_palette[col])
    # df[:]["1ExtAlpha"].plot(color="b")
    # df[:]['1FlxAlpha'].plot(color="r")
    unitx = "Time (s)"
    unity = "Membrane potentoial (mV)"
    plt.xlabel(unitx, fontsize=18)
    plt.ylabel(unity, fontsize=18)
    plt.legend(fontsize=12)

    list_sensory_neur.sort()
    plt.subplot(323)
    for col, sens in enumerate(list_sensory_neur):
        df_sens = df[:dfendTime][sens] * 1000
        df_sens.plot(color=my_palette[col])
    # df[:]["1ExtIa"].plot(color="b")
    # df[:]["1FlxIa"].plot(color="r")
    unitx = "Time (s)"
    unity = "Membrane potentoial (mV)"
    plt.xlabel(unitx, fontsize=18)
    plt.ylabel(unity, fontsize=18)
    plt.legend(fontsize=12)

    list_gamma_neur.sort()
    plt.subplot(324)
    for col, gamma in enumerate(list_gamma_neur):
        df_gamma = df[:dfendTime][gamma] *1000
        df_gamma.plot(color=my_palette[col])
    # df[:]["1ExtGamma"].plot(color="b")
    # df[:]["1FlxGamma"].plot(color="r")
    unitx = "Time (s)"
    unity = "Membrane potentoial (mV)"
    plt.xlabel(unitx, fontsize=18)
    plt.ylabel(unity, fontsize=18)
    plt.legend(fontsize=12)

    plt.subplot(325)
    df[:dfendTime]["Elbow"].plot(color="c")
    df[:dfendTime]["Template"].plot(color="grey")
    unitx = "Time (s)"
    unity = "Elbow Mvt (degres)"
    plt.xlabel(unitx, fontsize=18)
    plt.ylabel(unity, fontsize=18)
    plt.legend(fontsize=12)

    plt.subplot(326)
    df[4.5:6]["Elbow"].plot(color="c")
    df[4.5:6]["Template"].plot(color="grey")
    unitx = "Time (s)"
    unity = "Elbow Mvt (degres)"
    plt.xlabel(unitx, fontsize=18)
    plt.ylabel(unity, fontsize=18)
    plt.legend(fontsize=12)

    plt.gcf().subplots_adjust(left=0.09, right=0.95, top=0.9, bottom=0.1,
                              wspace=0.2, hspace=0.25)
    plt.suptitle(titre, fontsize=20)
    plt.savefig(os.path.join(chart_path, baseName + '_bhvMvt.pdf'))
    plt.savefig(os.path.join(chart_path, baseName + '_bhvMvt.eps'))
    plt.show()


def choose_title_col(df):
    """
    """
    lst_col_name = list(df.columns)
    listDic_columns = [{'title': lst_col_name[0]}]
    listChoix = list(listDic_columns[0].keys())
    titleText = "select a column for titles"
    rep = ChooseInList.listTransmit(parent=None,
                                    graphNo=0,
                                    listChoix=listChoix,
                                    items=lst_col_name,
                                    listDicItems=listDic_columns,
                                    onePerCol=[1],
                                    colNames=["title"],
                                    typ="chk",
                                    titleText=titleText)
    # Create a series from  dic_params_order
    listDic_columns = rep[0]
    title_col = listDic_columns[0]['title'][0]
    return title_col


def choose_lines(lst_ligns):
    """
    """
    lst_items = [str(title) for title in lst_ligns]
    listDic_limits = [{'first': lst_items[0], 'last': lst_items[1]}]
    """
    listChoix = []
    for key in listDic_limits[0].keys():
        listChoix.append(key)
    """
    listChoix = ["first", "last"]
    titleText = "select start and end of rows for radar"
    rep = ChooseInList.listTransmit(parent=None,
                                    graphNo=0,
                                    listChoix=listChoix,
                                    items=lst_items,
                                    listDicItems=listDic_limits,
                                    onePerCol=[1, 1],
                                    colNames=listChoix,
                                    typ="chk",
                                    titleText=titleText)
    # Create a series from  dic_params_order
    listDic_limits = rep[0]
    first = listDic_limits[0]['first'][0]
    last = listDic_limits[0]['last'][0]
    return (first, last)


def reorder_df(df, prev_column_order=None):
    """
    """
    if prev_column_order is None:
        col_name = list(df.columns)
        listChoix = ['params']
        listDic_params = [{'params': col_name}]
        params_order = list(zip(col_name, list(range(1, len(col_name)+1, 1))))
        dic_params_order = dict(params_order)
        listDic_params_order = [dic_params_order]
        titleText = "set order of parameters"
        rep = ChooseInList.listTransmit(parent=None,
                                        graphNo=0,
                                        listChoix=listChoix,
                                        items=col_name,
                                        listDicItems=listDic_params,
                                        onePerCol=[0],
                                        colNames=["order"],
                                        dicValues=listDic_params_order[0],
                                        typ="val",
                                        titleText=titleText)
        # Create a series from  dic_params_order
        listDic_params = rep[0]
        dic_params_order = rep[1]
        for par in list(dic_params_order.keys()):
            val = dic_params_order[par]
            if int(float(val)) < 10:
                val = "0" + val
                dic_params_order[par] = int(float(val))
            else:
                dic_params_order[par] = int(float(val))

        # print "rep[1]", rep[1]
        s = pd.Series(dic_params_order, name='order')
        s.index.name = 'par_names'
        s = s.reset_index()
        # Create a dataframe from  dic_params_order series
        ordered_df = pd.DataFrame(s)
        ordered_df = ordered_df.sort_values(by='order')
        ordered_df.to_pickle(MyWin.graph_path + "/order_param.pkl")
        # get the ordered paramNames
        ordered_names = list(ordered_df["par_names"])
    else:
        ordered_names = prev_column_order
    # Re-order the original df folloing the new column order
    df_new = df.reindex(columns=ordered_names)
    return df_new


def prepare_spider(df_radar, row, title, overdraw, color, ylim=(-0.2, 1)):
    """
    Procedure used to prepare a radar graph (set position in sheet, polar axes,
                                           names around the radar)
    """
    (ymin, ymax) = ylim
    # number of variable
    categories = list(df_radar)[0:]
    N = len(categories)
    red_categories = [cat[:cat.find(".")] for cat in categories]
    null_categories = ["" for cat in categories]
    # prepares ticks and labels
    # nbstep = (ymax - ymin) * 10
    # ticks = np.arange(ymin, ymax+float(ymax-ymin)/nbstep,
    #                  float(ymax-ymin)/nbstep)
    # strticks = ["{:2.2f}".format(tick) for tick in ticks]

    # calculate the angle of each axis in the plot
    # pi = np.pi
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    # Initialise the spider plot
    if not overdraw:
        ax = plt.subplot(3, 2, row+1, polar=True, )
        plt.subplots_adjust(wspace=0.9, hspace=None)
        labelsize = 9
        offset = (1.08)
        letterscale = 0.036
    else:
        ax = plt.subplot(2, 1, 1, polar=True, )
        plt.gcf().subplots_adjust(left=0.2, bottom=0.2,
                                  right=0.7, top=0.9,
                                  wspace=0, hspace=0.2)
        labelsize = 13
        offset = (1.09)
        letterscale = 0.020
    # In order the first axis to be on top:
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    # Draw one axe per variable + add labels labels yet
    # plt.xticks(angles[:-1], red_categories, color='grey', size=12)
    plt.xticks(angles[:-1], null_categories, color='grey', size=12)

    # Draw ylabels
    ax.set_rlabel_position(0)
    # plt.yticks(ticks, strticks, color="grey", size=10)
    plt.ylim(ymin, ymax)

    # add oriented xlabels
    theta = np.arange(pi/2, -2*pi + pi/2, -2*pi/N)
    rotations = np.rad2deg(theta)
    for x, rotation, label in zip(angles[:-1], rotations, red_categories):
        # offset = (1.1)
        h = offset + (len(label)/2.) * letterscale
        lab = ax.text(x, h, label,
                      transform=ax.get_xaxis_transform(),
                      ha='center', va='center', fontsize=labelsize)
        lab.set_rotation(rotation)

    # Add a title
    plt.title(title, size=16, color=color, y=1.4)

    return ax, angles


def add_spider_values(df_radar, row, color, title, filled, ax, angles):
    # get the values to plot
    values = df_radar.loc[row].values.flatten().tolist()
    values += values[:1]

    ax.plot(angles, values, color=color, linewidth=2, linestyle='solid',
            label=title)
    if filled:
        ax.fill(angles, values, color=color, alpha=0.3)
    return ax


def makeRadarFromExcelPar_csv(df_radar, lst_title, sup_title, sub_title,
                              graph_path, name, ylim):
    """
    Builds the global graph of a series of radars (from df_radar), with a
    global name (sup_title), a sub-title, and the path and name of the figure
    to be saved.
    """
    lst_df_rad = []
    # builts a new index for df_radar
    df_radar.index = np.arange(len(df_radar))
    nb_rad = len(df_radar)
    if len(df_radar.index) < 7:
        lst_df_rad.append(df_radar)
    else:
        k = 0
        last_rad = (k+1) * 6
        while last_rad < nb_rad:
            lst_df_rad.append(df_radar[k*6:last_rad])
            k += 1
            last_rad = (k+1) * 6
        lst_df_rad.append(df_radar[k*6:nb_rad])

    # Create a color palette:
    # my_palette = plt.cm.get_cmap("Set2", len(df_radar.index))
    # my_palette = plt.cm.get_cmap("tab20", len(df_radar.index))
    # my_palette = plt.cm.get_cmap("gist_ncar", len(df_radar.index)+2)
    my_palette = mpl.colormaps["gist_ncar"](len(df_radar.index)+2)
    # my_palette = plt.cm.get_cmap("nipy_spectral", len(df_radar.index)+1)
    filled = True
    overdraw = False

    # Loop to plot
    for idx, df_rad in enumerate(lst_df_rad):
        # initialize the figure
        my_dpi = 60
        plt.figure(figsize=(900/my_dpi, 1800/my_dpi), dpi=my_dpi)
        df_rad.index = list(range(len(df_rad)))
        for row in list(df_rad.index):
            rad = row + idx*6
            print(rad)
            color = my_palette(rad)
            title = lst_title[rad]
            # ylim = (0, 1/float(scale_up))
            ax, angles = prepare_spider(df_radar, row, title, overdraw,
                                        color, ylim)
            add_spider_values(df_radar, row, color, title, filled, ax, angles)

        plt.suptitle(sup_title, fontsize=16)
        plt.figtext(.5, .9, sub_title + str(idx), fontsize=14, ha='center')
        # model_dir = graph_path
        tit = os.path.split(sup_title)[-1]
        sstit = sub_title + str(idx)
        save_eps_pdf(graph_path, tit, sstit)
        # plt.savefig(os.path.join(path, name + sub_title + str(idx) + '.pdf'))
        # plt.savefig(os.path.join(path, name + sub_title + str(idx) + '.eps'))
        plt.show()


def overdrawRadarFromExcelPar_csv(df_radar, lst_title, sup_title, sub_title,
                                  graph_path, name, ylim):
    """
    Builds the global graph of overdran selected params (from df_radar), with a
    global name (sup_title), a sub-title, and the path and name of the figure
    to be saved.
    """

    # builts a new index for df_radar
    df_radar.index = np.arange(len(df_radar))

    # Create a color palette:
    # my_palette = plt.cm.get_cmap("Set2", len(df_radar.index))
    # my_palette = plt.cm.get_cmap("tab20", len(df_radar.index))
    my_palette = mpl.colormaps["gist_ncar"](len(df_radar.index)+2)
    # my_palette = plt.cm.get_cmap("nipy_spectral", len(df_radar.index)+1)
    filled = False

    # initialize the figure
    my_dpi = 60
    plt.figure(figsize=(900/my_dpi, 1800/my_dpi), dpi=my_dpi)
    row = 0
    title = ""
    color = "b"
    overdraw = True
    # ax, angles = prepare_spider(df_radar, row, title,
    #                             overdraw, color, ylim=(-0.2, 1))
    ax, angles = prepare_spider(df_radar, row, title,
                                overdraw, color, ylim=ylim)
    for rad in list(df_radar.index):
        print(rad, color)
        color = my_palette(rad)
        title = lst_title[rad]
        ax = add_spider_values(df_radar, rad, color, title, filled, ax, angles)

    # ax.legend(loc='upper right', bbox_to_anchor=(1.9, 1.1))
    # ax.legend(prop=dict(size=18))
    ax.legend(bbox_to_anchor=(1.55, 1.2), prop=dict(size=14))

    plt.suptitle(sup_title, fontsize=16, y=1.02)
    plt.figtext(.5, 0.98, sub_title, fontsize=14, ha='center')

    # model_dir = graph_path
    tit = os.path.split(sup_title)[-1]
    sstit = sub_title + "_overdraw"
    save_eps_pdf(graph_path, tit, sstit)
    # plt.savefig(os.path.join(path, name + sub_title + str(idx) + '.pdf'))
    # plt.savefig(os.path.join(path, name + sub_title + str(idx) + '.eps'))
    plt.show()


def adaptPaletteTodf(df_glob_sel, factor, step_palette, codeCoul_df_sel):
    """
    From step_palette, creates a set of colors, one for each element in the df.
    """
    colour = [step_palette[i] for i in codeCoul_df_sel['color']]
    if verbose > 2:
        print("... color scale achieved")
        print("len(colour) =", len(colour))
        print("len(df_glob_sel) =", len(df_glob_sel))
    return colour


def buildStpFilledCol(df, factor):
    """
    Creates a palette of colors one for each element in the df. This is not the
    same as "buildStpDiscretCol()" that get only the colors of levels (missing
    steps in codeCoul_df being removed).
    """
    # =============    creates new "color" & factor df    ==============
    codeCoul_df = copy.deepcopy(df[[factor]])
    rg = codeCoul_df.index
    codeCoul_df.loc[:, 'rg'] = rg   # index is now in a new column 'rg'
    codeCoul_df.sort_values(factor, axis=0, ascending=True,
                            inplace=True, na_position='last')
    sort_factor = np.array(codeCoul_df[factor])
    # ----- creates a quantal progressing array for factor values
    mult = 0.1
    nb_levels = 1
    newsortf = copy.deepcopy(sort_factor)
    newsortf = newsortf * mult
    newsortf = newsortf.astype(int)
    mini = newsortf.min()
    maxi = newsortf.max()
    while nb_levels <= 100:
        mult *= 10
        newsortf = copy.deepcopy(sort_factor)
        # newsortf = (newsortf * 10)
        newsortf = newsortf * mult
        newsortf = newsortf.astype(int)
        mini = newsortf.min()
        maxi = newsortf.max()
        nb_levels = maxi-mini + 1
        if verbose > 2:
            print(nb_levels)
    if nb_levels > 100:
        mult = mult/10
        newsortf = copy.deepcopy(sort_factor)
        # newsortf = (newsortf * 10)
        newsortf = newsortf * mult
        newsortf = newsortf.astype(int)
        mini = newsortf.min()
        maxi = newsortf.max()
        nb_levels = maxi-mini + 1
        if verbose > 2:
            print(nb_levels)

    # ==== creates the color palette associated to nb levels
    step_palette = []
    cmap = plt.get_cmap('gist_rainbow')
    for i in range(nb_levels):
        # print cmap(float(i)/nb_levels, float(10)/10)
        step_palette.append(cmap(float(i)/nb_levels, float(10)/10))
    # ==== crates a list of the colors of each data in factor
    color_sort = []
    for idx, val in enumerate(newsortf):
        color_sort.append(step_palette[val-mini])
    # ------    rescale 'seq_factor' to original scale
    newsortf_scale = newsortf/mult
    # ------    adds the new "quantal progressing factor" column
    seq_factor = "seq_{}".format(factor)
    codeCoul_df.loc[:, seq_factor] = newsortf_scale
    # ------    adds the new "quantal progressing factor" column
    coul = newsortf - newsortf.min()
    coul = coul.astype(int)
    codeCoul_df.loc[:, "color"] = coul
    # ------    re-arrange df according to original rg
    codeCoul_df.sort_values("rg", axis=0, ascending=True,
                            inplace=True, na_position='last')
    color = [step_palette[i] for i in codeCoul_df['color']]
    if verbose > 2:
        print("... color scale achieved")
        print("len(color) =", len(color))
        print("len(df) =", len(df))
    return color, codeCoul_df, step_palette


def buildStpDiscretCol(df_glob, factor):
    """
    Creates a palette of colors corresponding to the number of leves in the
    factor column. This column is first copied and transformed in a series of
    level values. Each level corresponds to a color
    """
    # ***********  creates a new rainbow palette n = 20 levels ********
    cmap = plt.get_cmap('gist_rainbow')

    # =============    creates new "color" & factor df    ==============
    codeCoul_df = copy.deepcopy(df_glob[[factor]])
    codeCoul_df.dropna(inplace=True)
    rg = codeCoul_df.index
    codeCoul_df.loc[:, 'rg'] = rg   # index is now in a new column 'rg'
    codeCoul_df.sort_values(factor, axis=0, ascending=True,
                            inplace=True, na_position='last')
    # type(codeCoul_df)
    codeCoul_df.describe()
    sort_factor = codeCoul_df[factor].values
    # sort_factor = codeCoul_df[factor].values.T[0]

    # ----- creates a sequential array for factor values
    mult = 0.1
    nb_levels = 1
    newsortf = copy.deepcopy(sort_factor)
    newsortf = newsortf * mult
    newsortf = newsortf.astype(int)
    mini = newsortf.min()
    maxi = newsortf.max()
    while nb_levels <= 50:
        mult *= 2
        newsortf = copy.deepcopy(sort_factor)
        # newsortf = (newsortf * 10)
        newsortf = newsortf * mult
        newsortf = newsortf.astype(int)
        mini = newsortf.min()
        maxi = newsortf.max()
        nb_levels = maxi-mini + 1
        # print nb_levels
    if nb_levels > 50:
        mult = mult/2
        newsortf = copy.deepcopy(sort_factor)
        # newsortf = (newsortf * 10)
        newsortf = newsortf * mult
        newsortf = newsortf.astype(int)
        mini = newsortf.min()
        maxi = newsortf.max()
        nb_levels = maxi-mini + 1
        # print nb_levels

    print("nb_levels:", nb_levels)
    

    # =========    build the palettte for factor df   ==========
    step_palette = []
    for i in range(nb_levels):
        # print cmap(float(i)/nb_levels, float(10)/10)
        step_palette.append(cmap(float(i)/nb_levels, float(10)/10))

    palette = step_palette
    # the sequential array (newsortf) may contain up to 100 steps
    # So now we limit the superior values of the array
    limsup = mini + len(palette) - 1
    for idx, val in enumerate(newsortf):
        if val > limsup:
            newsortf[idx] = limsup
    mini = newsortf.min()
    maxi = newsortf.max()
    nb_levels = maxi-mini + 1

    # ====  modifies palette for missing levels in 'seq_factor'  =====
    step_color = len(palette) // nb_levels
    nbstep_color = 0
    list_colors = []    # list of index of valid colors in palette
    list_colors.append(0)   # starts with the first color in palette
    prev_val = newsortf[0]  # first value of ordered seq_factor
    for idx, val in enumerate(newsortf):
        if (val - prev_val) < 1:        # same value in successive vals
            None
            # print "-",
        else:     # increment >= 1
            # print '+{}'.format(val - prev_val),
            nbstep_color = nbstep_color + (val - prev_val)
            list_colors.append(nbstep_color * step_color)
        prev_val = val

    adapt_palette = []
    for col in list_colors:
        adapt_palette.append(palette[col])
    step_pal_misRem = adapt_palette
    # ===============================================================

    # ------    rescale 'seq_factor' to original scale
    newsortf = newsortf/mult
    # ------    adds the new "color" column
    seq_factor = "seq_{}".format(factor)
    codeCoul_df.loc[:, seq_factor] = newsortf
    # ------    reagange df according to original rg
    codeCoul_df.sort_values("rg", axis=0, ascending=True,
                            inplace=True, na_position='last')
    print("len(palette) =", len(step_pal_misRem))
    return [step_pal_misRem, codeCoul_df]


def make_3d_plot_subPlots(df_glob, dataSet, selected_dataSets,
                          list_items, faceColItems,
                          xlim, ylim, zlim,
                          factor, select_3_col, titre, ss_titre, graph_path,
                          azim=60, elev=30):
    """
    Draws a 3D scatter plot with a fourth parameter as color scale
    """

    # =======   The following lines are used to debug the plot   =======
    """
    self=MyWin
    df_glob = self.df_glob
    factor = self.factor
    select_3_col = self.select_3_col
    ss_titre = self.ss_titre
    titre = "Fig5_3D_Dots_{}__{}__{}".format(select_3_col[0][:13],
                                                 select_3_col[1][:13],
                                                 select_3_col[2][:13])

    dataSet = self.visu_3d.dataSet
    selected_dataSets = self.visu_3d.selected_dataSets
    list_items = self.visu_3d.setnames

    self.graph_settings.choose_factor()
    factor = self.factor
    print("factor =", factor)


    color, codeCoul_df, step_palette = buildStpFilledCol(df_glob, factor)
    # Gets the first set of dots to apply color scale on it
    gl3d_item = self.visu_3d.listgl3dItems[0]
    self.visu_3d.apply_colors(color, gl3d_item)

    azim = self.visu_3d.axis.azim
    elev = self.visu_3d.axis.elev
    xlim = self.visu_3d.axis.get_xlim()
    ylim = self.visu_3d.axis.get_ylim()
    zlim = self.visu_3d.axis.get_zlim()
    model_dir = self.ensembleRunDir

    color, codeCoul_df, step_palette = buildStpFilledCol(df_glob, factor)
    gl3d_item = self.visu_3d.listgl3dItems[0]
    self.visu_3d.apply_colors(color, gl3d_item)
    faceColItems = self.visu_3d.faceColItems

    """
    [step_pal_misRem, codeCoul_df] = buildStpDiscretCol(df_glob, factor)
    seq_factor = "seq_{}".format(factor)
    # seq_factor_col = codeCoul_df[seq_factor]
    classes = list(set(codeCoul_df[seq_factor]))
    classes.sort(reverse=False)
    color_map = dict(list(zip(classes, step_pal_misRem)))

    # colors = seq_factor_col.apply(lambda group: color_map[group])
    # print(colors[0:10])
    # print()
    # ===============        Creating plot           ==================
    fig = plt.figure(figsize=(8, 8), dpi=100)
    # ax = fig.gca(projection='3d')
    ax = fig.add_axes([0.0, 0.0, 0.8, 0.8], projection='3d')
    ax.view_init(azim=azim, elev=elev)
    ax.set_xlabel(select_3_col[0])
    ax.set_ylabel(select_3_col[1])
    ax.set_zlabel(select_3_col[2])
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_zlim(zlim)
    subset_txt = ""
    for idx, subset in enumerate(list_items):
        colors = faceColItems[idx]
        # print(colors[0:10])
        if subset in selected_dataSets:
            pos = dataSet[idx]
            (x, y, z) = pos
            ax.scatter(x, y, z, alpha=0.8,
                       facecolors=colors,
                       edgecolors=colors,
                       s=10,
                       # label=classes,
                       )
            if subset == "main":
                None
            else:
                subset_txt = "{}_{}".format(subset_txt, subset[7:])
    tit = "{}__color={}".format(titre, factor[:13])
    # tit = "{}({})".format(tit, subset_txt[:10])
    orient = "azim({}) elev({})".format(azim, elev)
    titre_2lines = "{}\n{} {}".format(tit, ss_titre, orient)
    titre_3lines = "{}\n{}{}".format(titre_2lines, factor[:13], subset_txt)
    plt.suptitle(titre_3lines, fontsize=14, y=0.90)

    # ================= building legend for color scale ===============
    labels = copy.deepcopy(classes)
    labels.sort(reverse=True)
    nbcolors = len(classes)
    if nbcolors < 50:
        handles = [plt.plot([], [], color=color_map[labels[i]],
                   ls="", marker='o',
                   markersize=6)[0] for i in range(nbcolors)]
        # In legend order is that of classes (revert order)
        plt.legend(handles, labels, loc=(1.08, 0.00))
        plt.setp(plt.gca().get_legend().get_texts(), fontsize='6')
    else:
        # ------------ 1st set of legend elements  ----------------
        labels1 = labels[:nbcolors/2]
        handles1 = [plt.plot([], [], color=color_map[labels[i]],
                    ls="", marker='o',
                    markersize=6)[0] for i in range(nbcolors/2)]
        # In legend order is that of classes (revert order)
        first_legend = plt.legend(handles1, labels1,
                                  loc=(1.04, 0.00))
        plt.gca().add_artist(first_legend)
        plt.setp(plt.gca().get_legend().get_texts(), fontsize='6')
        # ------------ 2nd set of legend elements  ----------------
        labels2 = labels[nbcolors/2:]
        handles2 = [plt.plot([], [], color=color_map[labels[i]],
                    ls="", marker='o',
                    markersize=6)[0] for i in range(nbcolors/2,
                                                    nbcolors)]
        # In legend order is that of classes (revert order)
        second_legend = plt.legend(handles2, labels2,
                                   loc=(1.12, 0.00))
        plt.gca().add_artist(second_legend)
        plt.setp(plt.gca().get_legend().get_texts(), fontsize='6')

    sstit = ss_titre_to_txt(ss_titre)
    sstit = "{}__az({})_el({})".format(sstit, azim, elev)
    ficname = r'{0}\{1}{2}'.format(graph_path, tit, sstit)
    directory = graph_path
    ext = ".pdf"
    complete_name = SaveIncrementNb(directory, ficname, ext)

    file_name = os.path.splitext(complete_name)[0]

    plt.savefig(r'{}.eps'.format(file_name), bbox_inches='tight')
    plt.savefig(r'{}.pdf'.format(file_name), bbox_inches='tight')
    plt.show()


def saveCSVStructure(self):
    """
    Saves the CSV files sturcture (Angle & Duration, Constants ...)
    """
    structCSVFileName = "CSV_Struct.par"
    complete_structCSVFName = os.path.join(self.graph_path, structCSVFileName)
    csv_structure = [self.graph_path, self.rootdir,
                     self.prevListAngles, self.prevListConsts,
                     self.prevListTrials, self.prevListColNames,
                     self.prevListParams,
                     [self.strtTime, self.endTime]]
    f = open(complete_structCSVFName, 'w')
    for idx in range(len(csv_structure)):
        # s = str(idx) + '\t'
        s = ""
        if idx < 2:
            s = csv_structure[idx] + '\n'
        else:
            for idy in range(len(csv_structure[idx])-1):
                tmpval = csv_structure[idx][idy]
                s += "{}".format(tmpval) + '\t'
            s += "{}".format(csv_structure[idx][idy+1]) + '\n'
        # print(s)
        f.write(s)
    f.close()
    print("data saved to:", complete_structCSVFName)


def getBestParamSet(graph_path, ang, const, trial):
    pathGEP = os.path.join(graph_path, ang, const, trial, "GEPdata")
    fileGEP = os.path.join(pathGEP, "GEPdata00.par")
    datastructure = load_datastructure(fileGEP)
    nbMvtSet = len(datastructure)
    bestChartName = ""
    bestparamset = []
    # print pathGEP,
    if verbose > 2:
        print("NbSets:", nbMvtSet, end=" ")
    if nbMvtSet > 0:
        mvtSet = nbMvtSet - 1
        typ = datastructure[mvtSet][0]
        start = datastructure[mvtSet][1]
        end = datastructure[mvtSet][2]
        # packetsize = datastructure[mvtSet][3]
        if verbose > 2:
            print("{} start={} end={}".format(typ, start, end), end=" ")
        conditions = datastructure[mvtSet][4]
        nbObj = len(conditions)
        chartList = conditions[nbObj-2]
        rangList = conditions[nbObj-1]
        bestChartName = chartList[len(chartList)-1]
        bestParamRg = rangList[len(rangList)-1]
        if verbose > 2:
            print("---> best param set: {}".format(bestParamRg))
        tab = readTablo(pathGEP, "GEPdata00.txt")
        tab = np.array(tab)
        if tab[0][-1] != 0.0:
            # nbparfromtab = len(tab[0]) - 2
            pairs = np.array(tab[:, :])
        else:
            # nbparfromtab = len(tab[0]) - 2 - 1
            pairs = np.array(tab[:, 0:-1])
        bestparamset = pairs[bestParamRg]
    else:
        print("no data to plot")
    return (bestChartName, bestparamset)


def read_pklfile(self, paramFicName):
    try:
        print()
        print("looking paramOpt file:", paramFicName)
        with open(paramFicName, 'rb') as input:
            self.paramVSCDName = pickle.load(input)
            self.paramVSCDValue = pickle.load(input)
            self.paramVSCDType = pickle.load(input)
            self.paramVSCDCoul = pickle.load(input)
            self.paramMarquezName = pickle.load(input)
            self.paramMarquezValue = pickle.load(input)
            self.paramMarquezType = pickle.load(input)
            self.paramMarquezCoul = pickle.load(input)
        print("nb loaded param :", len(self.paramVSCDName))
        # print "nb nb actual param param:", len(listparNameOpt)
        print("nb expected param:", 42)
        # There are 42 VSCD parameters in this version
        nbloadedpar = len(self.paramVSCDName)
        if nbloadedpar == 42:
            if self.paramVSCDName[16] == 'disabledSynNbs':
                # This is the last version that includes "seriesSynNSParam"
                if verbose > 3:
                    print("paramOpt :")
                    for idx, val in enumerate(self.paramVSCDName):
                        print("{0}:\t{1}".format(val,
                                                 self.paramVSCDValue[idx]))
            elif self.paramVSCDName[16] == 'allsyn':
                # This is not the last version that includes "seriesSynNSParam"
                print("this version does not indicate seriesSynNSParam")
            if verbose > 3:
                print("paramMarquez :")
                for idx, val in enumerate(self.paramMarquezName):
                    print("{0}:\t{1}".format(val,
                                             self.paramMarquezValue[idx]))
            print('===================  Param loaded  ====================')
            response = True
        elif nbloadedpar == 41:
            print("paramOpt with only 41 params:")
            pln = ['selectedChart'] + self.paramVSCDName
            self.paramVSCDName = pln
            plv = [0] + self.paramVSCDValue
            paramVSCDValue = plv
            plt = [int] + self.paramVSCDType
            self.paramVSCDType = plt
            plc = ["Magenta"] + self.paramVSCDCoul
            self.paramVSCDCoul = plc
            if verbose > 3:
                print("paramOpt :")
                for idx, val in enumerate(self.paramVSCDName):
                    print("{0}:\t{1}".format(val, paramVSCDValue[idx]))
                print("paramMarquez :")
                for idx, val in enumerate(self.paramMarquezName):
                    print("{0}:\t{1}".format(val, self.paramMarquezValue[idx]))
            print('===================  Param loaded  ====================')
            response = True
        else:
            print("Mismatch between existing and actual parameter files")
            response = False
    except Exception as e:
        if (verbose > 2):
            print(e)
        # print("No parameter file with this name in the directory", end=" ")
        # print("NEEDs to create a new parameter file")
        response = False
    return response


def getOptSetFromAsim(self, animatsimdir):
    rootdir = os.path.dirname(animatsimdir)
    subdir = os.path.split(animatsimdir)[-1]
    animatLabV2ProgDir, nb_procs = getInfoComputer()
    folders = FolderOrg(animatlab_root=rootdir,
                        python27_source_dir=animatLabV2ProgDir,
                        subdir=subdir)
    sims = SimRun("Test Sims",
                  rootFolder=folders.animatlab_rootFolder,
                  commonFiles=folders.animatlab_commonFiles_dir,
                  sourceFiles=folders.python27_source_dir,
                  simFiles=folders.animatlab_simFiles_dir,
                  resultFiles=folders.animatlab_result_dir)
    model = AnimatLabModel.AnimatLabModel(folders.animatlab_commonFiles_dir)
    projMan = ProjectManager.ProjectManager('Test Project')
    # aprojFicName = os.path.split(model.aprojFile)[-1]
    if self.optSet is None:
        optSet = OptimizeSimSettings(folders=folders, model=model,
                                     projMan=projMan, sims=sims)
        fileName = 'paramOpt.pkl'
        if loadParams(os.path.join(folders.animatlab_result_dir, fileName),
                      optSet):
            # optSet was updated from "paramOpt.pkl"
            # we use then optSet to implement the needed variables
            optSet.actualizeparamVSCD()
            optSet.actualizeparamMarquez()
            optSet.ideal_behav = [0, 0]
        else:
            print("paramOpt.pkl MISSING !!, run 'GUI_animatlabOptimization.py'")
            print
        self.stimParName = optSet.stimParName
        self.synParName = optSet.synParName
        self.synNSParName = optSet.synNSParName
        self.synFRParName = optSet.synFRParName
        self.par_names = optSet.xparName
        self.optSet = optSet
    return self.optSet, model


def get_angle_dur(select_angledur_dir):
    mvt_by_angle = []
    angles = []
    durees = []
    for cond in select_angledur_dir:
        if cond[:cond.find("_")] not in angles:
            angles.append(cond[:cond.find("_")])
        if cond[cond.find("_")+1:] not in durees:
            durees.append(cond[cond.find("_")+1:])
    for ang in angles:
        ang_set = []
        for cond in select_angledur_dir:
            if cond[:cond.find("_")] in ang:
                ang_set.append(cond)
        mvt_by_angle.append(ang_set)
    return (mvt_by_angle, angles, durees)


def make_graph_var(graph_path, list_VSCDParam, strtTime, endTime,
                   prevListConsts, prevListTrials,
                   selectLst_const_trial, select_angledur_dir,
                   select_var_names_plt):
    """
    Builds graphs of chosen chart names variables for Deb, Max and Fin
    Each graph represents the values of these variables for each constant
    parameter value (for all selected trials). Different mvt durations are
    ploted with different lines. The different angles are plotted on different
    files.
    """
    list_constVal = ['Time']
    for const in prevListConsts:
        lastConstPar = const
        while lastConstPar.find("=") != -1:
            lastConstPar = lastConstPar[lastConstPar.find("=")+1:]
        # print(lastConstPar)
        for idx, trial in enumerate(prevListTrials):
            list_constVal.append("{0}-{1}".format(lastConstPar, idx+1))

    (mvt_by_angle, angles, durees) = get_angle_dur(select_angledur_dir)

    for ang_idx, ang in enumerate(angles):
        dic_VSCDparam = list_VSCDParam[ang_idx]
        # endMvt1 = dic_VSCDparam["endMvt1"]
        endPos1 = dic_VSCDparam["endPos1"]
        endMvt2 = dic_VSCDparam["endMvt2"]
        endPos2 = dic_VSCDparam["endPos2"]
        titre = "fig_var_{0}".format(ang)
        angle_class = mvt_by_angle[ang_idx]
        ysize = len(select_var_names_plt) * 2
        fig, ax = plt.subplots(nrows=len(select_var_names_plt), ncols=3,
                               figsize=(7, ysize), dpi=150,
                               # subplot_kw={'xticks': [], 'yticks': []},
                               sharex='col', sharey='row')
        for idx, var in enumerate(select_var_names_plt):
            for mvt in angle_class:
                output_path = os.path.join(graph_path, mvt, "output")
                df1 = pd.read_csv(r'{0}\{1}.csv'.format(output_path, var),
                                  delimiter='\t',
                                  index_col='Time',
                                  header=1,
                                  names=list_constVal)
                selectdf1 = df1.loc[:, selectLst_const_trial]
                "Deb_steady part"
                Deb = selectdf1.loc[0.5:endPos1]
                Deb_moy = Deb.mean(axis=0)
                # Deb.describe()
                "Max part"
                MaxVal = selectdf1.max(axis=0)
                "Fin_steady part"
                Fin = selectdf1.loc[endMvt2:endPos2]
                # Fin.describe()
                Fin_moy = Fin.mean(axis=0)

                ax[idx, 0].plot(Deb_moy)
                ax[idx, 0].set_title('Deb_' + var, fontsize=10)  # set title

                ax[idx, 1].plot(MaxVal)
                ax[idx, 1].set_title('Max_' + var, fontsize=10)

                ax[idx, 2].plot(Fin_moy)
                ax[idx, 2].set_title("Fin_" + var, fontsize=10)

                if idx == 0:
                    # plt.legend(angle_class,
                    #           bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                    #           ncol=1, mode="expand", borderaxespad=0.)
                    ax[idx, 2].legend(angle_class,
                                      bbox_to_anchor=(0.05, 1.2),
                                      loc=3, borderaxespad=0.)
                if idx == len(select_var_names_plt) - 1:
                    ax[idx, 0].tick_params(axis='x', rotation=70)
                    ax[idx, 1].tick_params(axis='x', rotation=70)
                    ax[idx, 2].tick_params(axis='x', rotation=70)

        plt.suptitle(titre, fontsize=14, y=1-ysize*0.005)
        plt.savefig(r'{0}\fig_var_{1}.eps'.format(graph_path, ang))
        plt.show()


def make_graph_mvt(graph_path, list_VSCDParam, strtTime, endTime,
                   prevListConsts, prevListTrials,
                   selectLst_const_trial, select_angledur_dir,
                   select_var_names_plt, fname='fig_Elbow.eps'):
    """
    Builds the elbow movement for each angle on a separates files
    (and for all mvt durations).
    """
    list_constVal = ['Time']
    for const in prevListConsts:
        lastConstPar = const
        while lastConstPar.find("=") != -1:
            lastConstPar = lastConstPar[lastConstPar.find("=")+1:]
        # print(lastConstPar)
        for idx, trial in enumerate(prevListTrials):
            list_constVal.append("{0}-{1}".format(lastConstPar, idx+1))
    # movement together
    figmvt, axes = plt.subplots(nrows=len(select_angledur_dir), ncols=2,
                                figsize=(7, 14), dpi=150,
                                sharex='col',
                                sharey='row')

    for idx, angdur in enumerate(select_angledur_dir):
        const = prevListConsts[0]
        trial = prevListTrials[0]
        templateFileName = os.path.join(graph_path, angdur, const, trial,
                                        "ResultFiles", "template.txt")
        T = np.loadtxt(templateFileName)
        Tdf = pd.DataFrame(T)
        Tdf.index = Tdf[1]
        output_path = os.path.join(graph_path, angdur, "output")
        df_move = pd.read_csv(r'{0}\Elbow.csv'.format(output_path),
                              delimiter='\t',
                              index_col='Time',
                              header=1,
                              names=list_constVal)
        select_df_move = df_move.loc[:, selectLst_const_trial]
        # add two columns to df_move : TemplateTime and Template
        select_df_move.loc[:, 'TemplateTime'] = Tdf[strtTime:endTime][1]
        select_df_move.loc[:, 'Template'] = Tdf[strtTime:endTime][2]
        # select_df_move.plot()

        # titre = "{0}".format(angdur)

        for col in selectLst_const_trial:
            data = select_df_move[:][col]
            # data.plot(ax=axes[0])
            axes[idx, 0].plot(data, linewidth=0.2)
        dataT = select_df_move[:]["Template"]
        # dataT.plot(ax=axes[0], color="grey")
        axes[idx, 0].plot(dataT, color="grey")
        unitx = "Time (s)"
        unity = "Elbow Mvt (degres)"
        axes[idx, 0].legend(loc='upper left', fontsize=4)
        axes[idx, 0].set_ylabel(unity, fontsize=10)
        if idx == len(select_angledur_dir) - 1:
            axes[idx, 0].set_xlabel(unitx, fontsize=10)

        for col in selectLst_const_trial:
            data = select_df_move[4.9:6][col]
            # data.plot(ax=axes[1])
            axes[idx, 1].plot(data, linewidth=0.2)
        dataT = select_df_move[4.9:6]["Template"]
        # dataT.plot(ax=axes[1], color="grey")
        axes[idx, 1].plot(dataT, color="grey")
        unitx = "Time (s)"
        unity = "Elbow Mvt (degres)"
        # axes[idx, 1].text(4.25, 35, angdur)
        axes[idx, 1].set_title(angdur)
        axes[idx, 1].legend(loc='upper left', fontsize=4)
        # axes[idx, 1].set_ylabel(unity, fontsize=10)
        if idx == len(select_angledur_dir) - 1:
            axes[idx, 1].set_xlabel(unitx, fontsize=10)

    plt.suptitle("Angles and Durations series", fontsize=14, y=0.91)
    plt.savefig(r'{0}\{1}'.format(graph_path, fname))
    plt.show()


def make_graph_supmvt(graph_path, list_VSCDParam, strtTime, endTime,
                      prevListConsts, prevListTrials,
                      selectLst_const_trial, select_angledur_dir,
                      select_var_names_plt, fname="fig_Elbow2.eps"):
    """
    Builds superimposed movements of same angles and different durations
    """
    list_constVal = ['Time']
    for const in prevListConsts:
        lastConstPar = const
        while lastConstPar.find("=") != -1:
            lastConstPar = lastConstPar[lastConstPar.find("=")+1:]
        # print(lastConstPar)
        for idx, trial in enumerate(prevListTrials):
            list_constVal.append("{0}-{1}".format(lastConstPar, idx+1))

    (mvt_by_angle, angles, durees) = get_angle_dur(select_angledur_dir)

    # superimposed movements
    nbrows = len(angles)
    fig2mvt, axes2 = plt.subplots(nrows=nbrows, ncols=1,
                                  figsize=(7, 7*nbrows), dpi=150)
    for ang_idx, ang in enumerate(angles):
        colors = []
        newHandles = []
        newLabels = []
        # dic_VSCDparam = list_VSCDParam[ang_idx]
        # titre = "{0}".format(ang)
        angle_class = mvt_by_angle[ang_idx]
        for mvt_idx, mvt in enumerate(angle_class):
            const = prevListConsts[0]
            trial = prevListTrials[0]
            templateFileName = os.path.join(graph_path, mvt, const, trial,
                                            "ResultFiles", "template.txt")
            T = np.loadtxt(templateFileName)
            Tdf = pd.DataFrame(T)
            Tdf.index = Tdf[1]
            output_path = os.path.join(graph_path, mvt, "output")
            df_move = pd.read_csv(r'{0}\Elbow.csv'.format(output_path),
                                  delimiter='\t',
                                  index_col='Time',
                                  header=1,
                                  names=list_constVal)
            select_df_move = df_move.loc[:, selectLst_const_trial]
            # add two columns to df_move : TemplateTime and Template
            select_df_move.loc[:, 'TemplateTime'] = Tdf[strtTime:endTime][1]
            select_df_move.loc[:, 'Template'] = Tdf[strtTime:endTime][2]
            # df_move.plot()

            color = "C{}".format(mvt_idx)
            colors.append(color)
            for col in selectLst_const_trial:
                data = select_df_move[4.9:6][col]
                if nbrows > 1:
                    axes2[ang_idx].plot(data, linewidth=0.5,
                                        color=color, label=mvt)
                else:
                    axes2.plot(data, linewidth=0.5, color=color, label=mvt)
            dataT = select_df_move[4.9:6]["Template"]
            unitx = "Time (s)"
            unity = "Elbow Mvt (degres)"
            if nbrows > 1:
                axes2[ang_idx].plot(dataT, color="grey")
                axes2[ang_idx].set_title(ang)
                axes2[ang_idx].legend(angle_class,
                                      loc='upper left', fontsize=18)
                axes2[ang_idx].set_ylabel(unity, fontsize=10)
                if ang_idx == nbrows - 1:
                    axes2[ang_idx].set_xlabel(unitx, fontsize=10)
                # gets the handles and labels of legend for current mvt
                handles, labels = axes2[ang_idx].get_legend_handles_labels()
            else:
                axes2.plot(dataT, color="grey")
                axes2.set_title(ang)
                axes2.legend(angle_class, loc='upper left', fontsize=18)
                axes2.set_ylabel(unity, fontsize=10)
                if ang_idx == nbrows - 1:
                    axes2.set_xlabel(unitx, fontsize=10)
                # gets the handles and labels of legend for current mvt
                handles, labels = axes2.get_legend_handles_labels()
            # gets the first handle & label of each constant list
            # and add it in new Handles & newLabels, respectively
            nbConstTrial = len(selectLst_const_trial)
            newHandles.append(handles[mvt_idx*(nbConstTrial)])
            newLabels.append(labels[mvt_idx*(nbConstTrial)])
        # and now adds the "template" in legend handles and labels
        newHandles.append(handles[(mvt_idx+1)*(nbConstTrial)-1])
        newLabels.append(labels[(mvt_idx+1)*(nbConstTrial)-1])
        # at the end of each angle_class, rewrites the legend using newHandles
        # and newLabels
        if nbrows > 1:
            axes2[ang_idx].legend(newHandles, newLabels)
        else:
            axes2.legend(newHandles, newLabels)
    plt.suptitle("Angles and Superimposed Durations", fontsize=14, y=0.94)
    plt.savefig(r'{0}\{1}'.format(graph_path, fname))
    plt.show()


def make_graph_param(graph_path, select_constVal_dir, select_angledur_dir,
                     selectLst_const_trial, prevLstPltParams):
    """
    Builds graphs of chosen parameter values. Each graph represents
    the adaptation of the parameter value for each value of the constant
    parameter (and for all selected trials). Different mvt durations are
    ploted with different lines. The different angles are plotted on different
    files.
    """
    df1 = pd.read_csv(r'{0}\{1}.csv'.format(graph_path, "output_param"),
                      delimiter='\t',
                      # index_col="param",
                      index_col=0,
                      # header=2,
                      header=[0, 1, 2],
                      # names=column_labels,
                      )
    parnames = df1.index
    nbcol = 3
    nbrow = int(len(parnames)/nbcol)
    if len(parnames) > nbrow*nbcol:
        nbrow += 1
    ysize = nbrow * 2
    (mvt_by_angle, angles, durees) = get_angle_dur(select_angledur_dir)

    for ang_idx, ang in enumerate(angles):
        titre = "fig_par_{0}".format(ang)
        angle_class = mvt_by_angle[ang_idx]
        dfang = df1[angle_class]
        fig, ax = plt.subplots(nrows=nbrow, ncols=nbcol,
                               figsize=(7, ysize), dpi=150,
                               # subplot_kw={'xticks': [], 'yticks': []},
                               sharex='col', sharey='row')
        lastrow = (len(parnames) - len(parnames) % 3) // 3
        for par_idx, par in enumerate(parnames):
            col = par_idx % 3   # modulo function -> 0 1 2 0 1 2 etc.
            row = (par_idx - col) / 3
            # print row, col
            for dur_idx, dur in enumerate(angle_class):
                dfdur = dfang[dur]
                dfconst = dfdur[select_constVal_dir]
                dfconst.columns = selectLst_const_trial
                ax[row, col].plot(dfconst.loc[par])
                ax[row, col].set_title(par, fontsize=9)
                if row == 0 and col == 2:
                    # plt.legend(angle_class,
                    #           bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                    #           ncol=1, mode="expand", borderaxespad=0.)
                    ax[0, 2].legend(angle_class,
                                    bbox_to_anchor=(0.05, 1.2),
                                    loc=3, borderaxespad=0.)
                if row == lastrow:
                    ax[row, col].tick_params(axis='x', rotation=70)

        plt.suptitle(titre, fontsize=14, y=1-ysize*0.005)
        plt.savefig(r'{0}\fig_par_{1}.eps'.format(graph_path, ang))
        plt.show()


def analyse_const_dir(const):
    list_cstes = []
    fini = False
    while not fini:
        res = const.find("_")
        if res != -1:
            prevconst = const[:const.find("_")]
            # print prevconst
            if prevconst != "const":
                list_cstes.append(prevconst)
            const = const[const.find("_")+1:]
        else:
            # print const
            list_cstes.append(const)
            fini = True
    return list_cstes


def factor_scatter_matrix(df, factor, graph_name,
                          plt_factor=False, palette=None):
    '''
    Create a scatter matrix of the variables in df, with differently colored
    points depending on the value of df[factor].
    inputs:
        df: pandas.DataFrame containing the columns to be plotted, as well
            as factor.
        factor: string or pandas.Series. The column indicating which group
            each row belongs to.
        palette: A list of hex codes, at least as long as the number of groups.
            If omitted, a predefined palette will be used, but it only includes
            9 groups.
    '''
    from pandas.plotting import scatter_matrix
    from scipy.stats import gaussian_kde
    import seaborn as sns

    if isinstance(factor, str):
        factor_name = factor                # save off the name
        factor_col = df.loc[:, factor]      # extract column
        if plt_factor is False:
            df = df.drop(factor_name, axis=1)   # remove from df, so it
        # doesn't get a row and col in the plot.

    classes = list(set(factor_col))
    classes.sort(reverse=False)
    nbcolors = len(classes)
    if palette is None:
        palette = colors = sns.color_palette()
        """
        palette = ['#e41a1c', '#377eb8', '#4eae4b',
                   '#994fa1', '#ff8101', '#fdfc33',
                   '#a8572c', '#f482be', '#999999']
        """
    color_map = dict(list(zip(classes, palette)))

    if len(classes) > len(palette):
        message1 = 'Too many groups for the number of colors provided.'
        message2 = ' We only have {} colors in the palette, for {} groups.'
        message = message1 + message2
        raise ValueError(message.format(len(palette), len(classes)))

    plt.rcParams['axes.labelsize'] = 8
    plt.rcParams['ytick.labelsize'] = 6
    colors = factor_col.apply(lambda group: color_map[group])
    axarr = scatter_matrix(df, figsize=(15, 15),
                           alpha=1,
                           marker='.',
                           c=colors,
                           diagonal=None)

    for rc in range(len(df.columns)):
        for group in classes:
            try:
                y = df[factor_col == group].iloc[:, rc].values
                gkde = gaussian_kde(y)
                ind = np.linspace(y.min(), y.max(), 1000)
                axarr[rc][rc].plot(ind, gkde.evaluate(ind),
                                   c=color_map[group])
                # in the color process colors are associated to values in
                # value order (i.e. 1st value 0.01 -> first color)
            except Exception as e:
                None
                if verbose > 2:
                    print(e)

    title = "{0} colors by {1}".format(graph_name, factor)
    plt.suptitle(title, fontsize=14, y=0.90)
    labels = copy.deepcopy(classes)
    labels.sort(reverse=True)
    if nbcolors < 50:
        handles = [plt.plot([], [], color=color_map[labels[i]],
                            ls="", marker='o',
                            markersize=8)[0] for i in range(nbcolors)]
        # In legend the order is that of classes (revert order) so all is OK
        plt.legend(handles, labels, loc=(1.02, 0))
        plt.setp(plt.gca().get_legend().get_texts(), fontsize='10')
    else:
        labels1 = labels[:nbcolors/2]
        handles1 = [plt.plot([], [], color=color_map[labels[i]],
                             ls="", marker='o',
                             markersize=8)[0] for i in range(nbcolors/2)]
        # In legend the order is that of classes (revert order) so all is OK
        first_legend = plt.legend(handles1, labels1, loc=(1.02, 0))
        plt.gca().add_artist(first_legend)
        plt.setp(plt.gca().get_legend().get_texts(), fontsize='10')

        labels2 = labels[nbcolors/2:]
        handles2 = [plt.plot([], [], color=color_map[labels[i]],
                             ls="", marker='o',
                             markersize=8)[0] for i in range(nbcolors/2,
                                                             nbcolors)]
        # In legend the order is that of classes (revert order) so all is OK
        second_legend = plt.legend(handles2, labels2, loc=(1.25, 0))
        plt.gca().add_artist(second_legend)
        plt.setp(plt.gca().get_legend().get_texts(), fontsize='10')

    return axarr, color_map


# ======================================================================
#                    functions to plot GEP graphs
# ======================================================================
def do_plot_bhv_param(MyWin, df_bhvremain, df_parremain, behav_col, graph_path,
                      baseName, listDicGraphs, xparNameDict, xparName,
                      max_x_bhv=1.2, max_y_bhv=5):
    nbpargraphs = len(listDicGraphs)
    nbgraphs = nbpargraphs + 1  # the bhvGraph is added on 1st line
    nblines = int(float(nbgraphs+1)/3)
    reste = nbgraphs % 3
    if reste > 0:
        nblines += 1

    if nblines % 5 != 0:
        nbpages = int(nblines / 5) + 1
        # nbLinesLastPage = nblines % 5
    else:
        nbpages = int(nblines / 5)
        # nbLinesLastPage = 5
    # nbLinesPerPage = []
    nbparGr1stPage = min(14, nbpargraphs)
    grlist = [list(range(0, nbparGr1stPage))]   # list of pargraphs of 1st page
    rg1stGrNextPage = nbparGr1stPage
    if nbpages > 1:
        for pag in range(1, nbpages-1):
            # nbLinesPerPage.append(5)
            grlist.append(list(range(rg1stGrNextPage, rg1stGrNextPage+14)))
            rg1stGrNextPage = rg1stGrNextPage+14
    # nbLinesPerPage.append(nbLinesLastPage)
    grlist.append(list(range(rg1stGrNextPage, nbpargraphs)))

    for page in range(nbpages):
        plotGrOnPage(MyWin, df_bhvremain, df_parremain, behav_col, graph_path,
                     baseName, listDicGraphs, xparNameDict, xparName, page,
                     grlist, max_x_bhv=max_x_bhv, max_y_bhv=max_y_bhv)


def plotGrOnPage(MyWin, df_bhvremain, df_parremain, behav_col, graph_path,
                 baseName, listDicGraphs, xparNameDict, xparName, page,
                 grlist, max_x_bhv=1.2, max_y_bhv=1.4):
    listcolors = ['blue', 'orange', 'green', 'red', 'purple',
                  'brown', 'pink', 'gray', 'olive', 'cyan']
    fig = plt.figure(figsize=(10, 18), dpi=90)
    # plt.subplots_adjust(bottom=0, left=0.1, top=0.9, right=0.9)
    grid = plt.GridSpec(5, 3, wspace=0.4, hspace=0.3)
    path = os.path.split(graph_path)[0]
    # baseName = strGEPdataName[:] + "/ bhv_par_graphs"
    baseNamePage = baseName + "_p" + str(page+1)
    titre = get_titre(path, baseNamePage)
    # titre = titre + "_p" + str(page+1)
    plt.suptitle(titre, fontsize=12, y=0.95)
    row = -1
    if page == 0:
        #  ===================== plots the behavior map =======================
        behavs_cues = df_bhvremain[df_bhvremain.columns[behav_col]]
        rel_behavs_cues = behavs_cues/[MyWin.scale_x, MyWin.scale_y]
        nameX = rel_behavs_cues.columns[0]
        nameY = rel_behavs_cues.columns[1]
        valX = rel_behavs_cues[nameX]
        valY = rel_behavs_cues[nameY]
        # figure, ax = plt.subplots(figsize=(7, 7))
        # figure, ax = plt.subplots()
        # ax3 = fig.add_subplot(337)
        ax3 = fig.add_subplot(grid[0, 0])
        selectedROI = MyWin.mafen.selectedROI
        if selectedROI == []:
            # ===========================================================
            ax3.scatter(valX, valY, marker='o', s=4, c="r")
            # ===========================================================
        else:
            for idxROI, listdata in enumerate(selectedROI):
                valX_s = valX[listdata]
                valY_s = valY[listdata]
                color = listcolors[idxROI]
                # ---------------------------------------------------
                ax3.scatter(valX_s, valY_s, marker='o', s=4, c=color)
                # ---------------------------------------------------
        if behav_col[1] == 8:      # if ordonate is duration...
            labelnameX = nameX + " (x 0.01)"
            labelnameY = nameY
        elif behav_col[1] == 6:
            labelnameX = nameX + " (x 0.01)"
            labelnameY = nameY + " (x 0.01)"
        ax3.set_xlabel(labelnameX, fontsize=11)
        ax3.set_ylabel(labelnameY, fontsize=11)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        ax3.set_axisbelow(True)
        ax3.set_xlim(0, max_x_bhv)
        ax3.set_ylim(0, max_y_bhv)
        ax3.grid(linestyle='-', linewidth='0.5', color='green')
        row = 0
        # =====================================================================

    #  =================== plots the parameter maps =======================
    axpar = []
    # row = 0
    line = 0
    for idx, pargr in enumerate(grlist[page]):
        abscissName = listDicGraphs[pargr]['abscissa'][0]
        ordinateName = listDicGraphs[pargr]['ordinate'][0]
        if abscissName[abscissName.find(".")+1:] == "SynAmp":
            xmin = 0
            xmax = 0.05
        if ordinateName[ordinateName.find(".")+1:] == "SynAmp":
            ymin = 0
            ymax = 0.05
        if abscissName[abscissName.find(".")+1:] == "CurrentOn":
            xmin = 0
            xmax = 1
        if ordinateName[ordinateName.find(".")+1:] == "CurrentOn":
            ymin = 0
            ymax = 1
        row = row + 1
        if row > 2:
            row = 0
            line = line + 1
        # axpar.append(fig.add_subplot(3, nblines+1, 8+pargr))
        axpar.append(fig.add_subplot(grid[line, row]))
        namex = listDicGraphs[pargr]["abscissa"]
        namey = listDicGraphs[pargr]["ordinate"]
        parx = xparNameDict[namex[0]]
        pary = xparNameDict[namey[0]]
        dflist_x = df_parremain[xparName[parx]]
        dflist_y = df_parremain[xparName[pary]]
        if dflist_x.max() > xmax:
            xmax = dflist_x.max()
        if dflist_x.min() < xmin:
            xmin = dflist_x.min()
        """
        if (dflist_y.max() > ymax) or dflist_y.min() < ymin:
            if dflist_y.max() - dflist_y.min() < 2:
                ymax = (dflist_y.max() + dflist_y.min())/2 + 1
                ymin = (dflist_y.max() + dflist_y.min())/2 - 1
        """
        if dflist_y.max() > ymax:
            ymax = dflist_y.max()
        if dflist_y.min() < ymin:
            ymin = dflist_y.min()

        print(namex[0], parx, namey[0], pary)
        selectedROI = MyWin.mafen.selectedROI
        if selectedROI == []:
            # ===========================================================
            axpar[idx].scatter(list(dflist_x), list(dflist_y),
                               marker='o', s=4, c="b")
            # ===========================================================

        else:
            for idxROI, listdata in enumerate(selectedROI):
                dflist_x_s = dflist_x[listdata]
                dflist_y_s = dflist_y[listdata]
                color = listcolors[idxROI]
                # ---------------------------------------------------
                axpar[idx].scatter(list(dflist_x_s), list(dflist_y_s),
                                   marker='o', s=4, c=color)
                # ---------------------------------------------------

        axpar[idx].set_xlabel(namex[0], fontsize=11)
        axpar[idx].set_ylabel(namey[0], fontsize=11)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        axpar[idx].set_axisbelow(True)
        """
        xmin = -4
        xmax = 2
        ymin = -3
        ymax = 3
        """
        axpar[idx].set_xlim(xmin, xmax)
        axpar[idx].set_ylim(ymin, ymax)
        axpar[idx].grid(linestyle='-', linewidth='0.5', color='gray')
    # =====================================================================

    plt.savefig(os.path.join(graph_path, baseNamePage + '.pdf'))
    plt.savefig(os.path.join(graph_path, baseNamePage + '.eps'))
    plt.show()


def ss_titre_to_txt(ss_titre):
    txt = "{}".format(ss_titre)
    txt = txt.replace(" ", "")
    txt = txt.replace("[", "(")
    txt = txt.replace("]", ")")
    txt = txt.replace("_", "")
    return "_{}".format(txt)


def look_for_peaks(data):
    start = 0
    sequence = []
    for key, group in groupby(data):
        sequence.append((key, start))
        start += sum(1 for _ in group)

    for (b, bi), (m, mi), (a, ai) in zip(sequence, sequence[1:], sequence[2:]):
        if b < m and a < m:
            yield m, mi


class Ui_Visu3D(object):
    def setupUi(self, Visu3D):
        self.Visu3D = Visu3D
        self.Visu3D.setObjectName("Visu3D")
        self.Visu3D.resize(400, 400)

        btn_color_per_set = QtWidgets.QPushButton('Color Points per set')
        btn_color_per_set.clicked.connect(self.colors_per_set)
        btn_create_subset = QtWidgets.QPushButton('create subset')
        btn_create_subset.clicked.connect(self.restrain_visible_factor)
        btn_choose_subset = QtWidgets.QPushButton('choose subset')
        btn_choose_subset.clicked.connect(self.choose_subset)
        btn_remove_subset = QtWidgets.QPushButton('remove subset')
        btn_remove_subset.clicked.connect(self.remove_subset)
        btn_chge_colorPar = QtWidgets.QPushButton('Change Colored param')
        btn_chge_colorPar.clicked.connect(self.chge_colorPar)
        btn_set_orient = QtWidgets.QPushButton('set orientation')
        btn_set_orient.clicked.connect(self.set_orient)
        btn_clear = QtWidgets.QPushButton('clear graph')
        btn_clear.clicked.connect(self.clearData)
        btn_save = QtWidgets.QPushButton('save graph')
        btn_save.clicked.connect(self.saveGraph)
        btn_quit = QtWidgets.QPushButton('QUIT')
        btn_quit.clicked.connect(self.closeWindows)

        # ==============================================
        # Add QHBoxlayout to place the buttons
        self.buttonHLayout1 = QtWidgets.QHBoxLayout()
        self.buttonHLayout1.setObjectName("ButtonHLayout")
        # self.buttonHLayout1.addWidget(btn_color_per_set)
        self.buttonHLayout1.addWidget(btn_create_subset)
        self.buttonHLayout1.addWidget(btn_choose_subset)
        self.buttonHLayout1.addWidget(btn_remove_subset)
        self.buttonHLayout1.addWidget(btn_chge_colorPar)
        self.buttonHLayout1.addWidget(btn_set_orient)
        self.buttonHLayout1.addWidget(btn_save)
        # self.buttonHLayout1.addWidget(btn_clear)
        self.buttonHLayout1.addWidget(btn_quit)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        # Add widgets to the layout in their proper positions
        # self.verticalLayout.addWidget(self.gl3d)
        self.verticalLayout.addLayout(self.buttonHLayout1)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.Visu3D.setLayout(self.horizontalLayout)
        # self.centralwidget.setLayout(self.horizontalLayout)
        self.setWindowTitle("Make 3d graph")
        QtCore.QMetaObject.connectSlotsByName(self.Visu3D)


#   TODO    ...
class Visualizer3D(QtWidgets.QDialog, Ui_Visu3D):
    def __init__(self, graph_path,  GUI_Gr_obj):
        super(Visualizer3D, self).__init__()
        self.setupUi(self)      # le 2eme self est pour l'argument Visualizer3D
        self.graph_path = graph_path
        self.GUI_Gr_obj = GUI_Gr_obj
        self.rootdir = ""
        self.ficname = ""
        self.dataSet = []
        self.listgl3dItems = []
        self.faceColItems = []
        self.setnames = []
        self.listDic_dataSet = [{'data_sets': ["main"]}]
        self.selected_dataSets = ['main']

        plt.ion()
        # self.figure, self.axis = plt.subplots(figsize=(10, 10), dpi=100)
        self.figure = plt.figure(figsize=(10, 10), dpi=100)
        self.canvas = FigureCanvas(self.figure)

        # self.canvas.mpl_connect('pick_event', self.onpick)

        self.verticalLayout.addWidget(self.canvas)
        # self.visu_3d.gridLayout.addWidget(self.canvas)
        self.axis = self.figure.add_subplot(1, 1, 1, projection='3d')
        # self.axis = self.figure.gca(projection='3d')
        # self.figure.set_size_inches(18.5, 10.5)
        self.axis.set_xlabel("xlabel")
        self.axis.set_ylabel("ylabel")
        self.axis.set_zlabel("zlabel")
        self.axis.view_init(60, 30)
        print(" ========== execution in Vizualizer ON ==========")

        # self.show()
    """
    def newData(self):
        pos = np.random.randint(-10, 10, size=(100, 3))
        pos[:, 2] = np.abs(pos[:, 2])
        color = np.zeros((pos.shape[0], 4), dtype=np.float32)
        color[:, 0] = 0.5
        color[:, 1] = 0.2
        color[:, 2] = 0.5
        color[:, 3] = 1
        x = pos[:, 0]
        y = pos[:, 1]
        z = pos[:, 2]
        self.addData(pos=(x, y, z), size=10, pxMode=True, color=color)
        # color = np.roll(color, 1, axis=0)

    def origin_colors(self):
        for idx, gl3d_item in enumerate(self.listgl3dItems):
            color = self.faceColItems[idx]
            gl3d_item._facecolor3d = color
            gl3d_item._edgecolor3d = color
        plt._auto_draw_if_interactive(self.figure, 1)
    """
    """
    def plot_curves(self, indexes):
        for idx, gl3d_item in enumerate(self.listgl3dItems):
            for i in indexes:  # might be more than 1 point if ambiguous click
                new_fc = self.fc.copy()
                new_fc[i,:] = (1, 0, 0, 1)
                gl3d_item._facecolor3d = new_fc
                gl3d_item._edgecolor3d = new_fc
            self.figure.canvas.draw_idle()

    def onpick(self, event):
        ind = event.ind
        print ind
        self.plot_curves(list(ind))
    """

    def addData(self, pos=None, names=["xlabel", "ylabel", "zlabel"],
                fourth="fourthlabel", size=10, pxMode=True, color=None,
                setname="", ficname=""):
        factor = fourth
        self.ficname = ficname
        (x, y, z) = pos
        self.axis.set_xlabel(names[0])
        self.axis.set_ylabel(names[1])
        self.axis.set_zlabel(names[2])

        # ========  tests if bvh name (bhv_names[behav_col[i]]) is in names
        #    (if so, sets the limits to original (before restraining bhv)
        x_bhvname = self.GUI_Gr_obj.bhv_names[self.GUI_Gr_obj.behav_col[0]]
        y_bhvname = self.GUI_Gr_obj.bhv_names[self.GUI_Gr_obj.behav_col[1]]
        rank_x = list
        rank_y = list
        if x_bhvname in names:
            # print x_bhvname,
            rank_x = [i for i in range(len(names)) if names[i] == x_bhvname]
            # print rank_x
            if rank_x[0] == 0:
                self.axis.set_xlim(self.GUI_Gr_obj.bhv_xmin,
                                   self.GUI_Gr_obj.bhv_xmax)
            elif rank_x[0] == 1:
                self.axis.set_ylim(self.GUI_Gr_obj.bhv_xmin,
                                   self.GUI_Gr_obj.bhv_xmax)
            elif rank_x[0] == 2:
                self.axis.set_zlim(self.GUI_Gr_obj.bhv_xmin,
                                   self.GUI_Gr_obj.bhv_xmax)

        if y_bhvname in names:
            # print(y_bhvname, end=" ")
            rank_y = [i for i in range(len(names)) if names[i] == y_bhvname]
            # print(rank_y)
            if rank_y[0] == 0:
                self.axis.set_xlim(self.GUI_Gr_obj.bhv_ymin,
                                   self.GUI_Gr_obj.bhv_ymax)
            elif rank_y[0] == 1:
                self.axis.set_ylim(self.GUI_Gr_obj.bhv_ymin,
                                   self.GUI_Gr_obj.bhv_ymax)
            elif rank_y[0] == 2:
                self.axis.set_zlim(self.GUI_Gr_obj.bhv_ymin,
                                   self.GUI_Gr_obj.bhv_ymax)

        if color is None:
            print("no color scale")
            gl3d_item = self.axis.scatter(x, y, z, s=size,
                                          facecolors=["C5"]*len(x),
                                          edgecolors=["C5"]*len(x),
                                          picker=True)
        else:
            # print("apllying color scale")
            gl3d_item = self.axis.scatter(x, y, z, s=size,
                                          facecolors=color,
                                          edgecolors=color,
                                          picker=True)
        fc = gl3d_item.get_facecolors()
        self.faceColItems.append(fc)
        self.dataSet.append(pos)
        self.setnames.append(setname)
        self.listgl3dItems.append(gl3d_item)
        plt._auto_draw_if_interactive(self.figure, 1)
        self.setWindowTitle("color={}".format(factor))
        print("new data {} added to 3d_graph".format(gl3d_item))
        return gl3d_item

    def chge_colorPar(self):
        self.GUI_Gr_obj.graph_settings.choose_factor()
        factor = self.GUI_Gr_obj.factor
        print("factor =", factor)
        df_glob = self.GUI_Gr_obj.df_glob
        # print(df_glob)
        color, codeCoul_df, step_palette = buildStpFilledCol(df_glob, factor)
        # Gets the first set of dots to apply color scale on it
        gl3d_item = self.listgl3dItems[0]
        self.apply_colors(color, gl3d_item)

        # =====================================================================
#   TODO    Part not Finished...
        fc = gl3d_item.get_facecolors()
        self.faceColItems[0] = fc
        # =====================================================================
        self.setWindowTitle("color={}".format(factor))

    def apply_colors(self, color, gl3d_item):
        # for idx, gl3d_item in enumerate(self.listgl3dItems):
        gl3d_item._facecolor3d = color
        gl3d_item._edgecolor3d = color
        plt._auto_draw_if_interactive(self.figure, 1)
        # print("new_color for gl3d_item")
        # print("len(color) =", len(color))

    def restrain_visible_factor(self):
        factor = self.GUI_Gr_obj.factor
        df_glob = self.GUI_Gr_obj.df_glob
        color, codeCoul_df, step_palette = buildStpFilledCol(df_glob, factor)
        seq_factor = "seq_{}".format(factor)
        # seq_factor_col = copy.deepcopy(codeCoul_df[seq_factor])
        list_sort_seq_factor = np.array(codeCoul_df[seq_factor])
        list_sort_seq_factor.sort()
        if verbose > 2:
            print("seq_factor:", list_sort_seq_factor)
            print("sorted seq_factor:",  list_sort_seq_factor)
        step = list_sort_seq_factor[1] - list_sort_seq_factor[0]
        i = 0
        while step == 0:
            step = list_sort_seq_factor[i+1] - list_sort_seq_factor[0]
            i += 1
        # print(step)
        step = step / 100
        # print(step)
        k = 0
        while step < 1:
            step *= 10
            k += 1
            # print(step)
        # print round(step)
        step = round(step) / (10**k)
        # print(step)
        step *= 100
        print("step in color scale: {}".format(step))

        factor_min = min(codeCoul_df[seq_factor])
        factor_max = max(codeCoul_df[seq_factor])
        listChoix = ['factor_limits']
        listDicFactorLimNam = [{'factor_limits': ["inf", "sup"]}]
        listDic_factorLimVal = [{"inf": factor_min, "sup": factor_max}]
        factorLimits_keys = ["inf", "sup"]
        titleText = "set limits for factor"
        rep = ChooseInList.listTransmit(parent=None,
                                        graphNo=0,
                                        listChoix=listChoix,
                                        items=factorLimits_keys,
                                        listDicItems=listDicFactorLimNam,
                                        onePerCol=[0],
                                        colNames=["Factor_limits", 'value'],
                                        dicValues=listDic_factorLimVal[0],
                                        typ="val",
                                        titleText=titleText)
        listDicFactorLimNam = rep[0]
        if len(rep[1]) == 0:    # No values entered,  ESC button was used
            return
        factLim_names = []
        # print("rep[1]", rep[1])
        for i in range(len(listDicFactorLimNam[0][listChoix[0]])):
            itemName = listDicFactorLimNam[0][listChoix[0]][i]
            factLim_names.append(itemName)
            listDic_factorLimVal[0][itemName] = float(rep[1][itemName])
            # print itemName, rep[1][itemName]
        factor_inf = listDic_factorLimVal[0]['inf']
        factor_sup = listDic_factorLimVal[0]['sup']
        # print('factor_inf={} ; factor_sup={}'.format(factor_inf, factor_sup))

        # get the ranks of factor_inf and factor_sup in codeCoul_df
        idx_inf = codeCoul_df.loc[codeCoul_df[seq_factor] == factor_inf]
        if len(idx_inf) > 0:
            rg_inf = idx_inf.index[0]
        else:       # this means that factor_inf does not exist in seq_factor
            while len(idx_inf) < 1:     # then lokk for the immediately larger
                if factor_inf - step > factor_min:
                    factor_inf -= step
                    factor_inf = round(factor_inf/step)*step
                else:
                    factor_inf = factor_min
                idx_inf = codeCoul_df.loc[codeCoul_df[seq_factor] ==
                                          factor_inf]
                if len(idx_inf) > 0:
                    rg_inf = idx_inf.index[0]
                # rg = np.searchsorted(list_sort_seq_factor, factor_inf)

        idx_sup = codeCoul_df.loc[codeCoul_df[seq_factor] == factor_sup]
        if len(idx_sup) > 0:
            rg_sup = idx_sup.index[0]
        else:       # this means that factor_inf does not exist in seq_factor
            while len(idx_sup) < 1:     # then lokk for the immediately larger
                if factor_sup + step < factor_max:
                    factor_sup += step
                    factor_sup = round(factor_sup/step)*step
                else:
                    factor_sup = factor_max
                idx_sup = codeCoul_df.loc[codeCoul_df[seq_factor] ==
                                          factor_sup]
                if len(idx_sup) > 0:
                    print(factor_sup, idx_sup)
                if len(idx_sup) > 0:
                    rg_sup = idx_sup.index[0]

        print('factor_inf={} ; factor_sup={}'.format(factor_inf, factor_sup))

        # and gets the corresponding color ranks in "color"
        color_inf = int(codeCoul_df.loc[rg_inf]["color"])
        color_sup = int(codeCoul_df.loc[rg_sup]["color"])
        if verbose > 2:
            print('color_inf={} ; color_sup={}'.format(color_inf, color_sup))
        setname = "factor_{}-{}".format(factor_inf, factor_sup)
        # ========== defines transparent colors for df_glob dots =============
        col_trans = copy.deepcopy(color)
        color_tr = [[col_trans[i][j] for j in range(4)]
                    for i in range(len(col_trans))]
        color_t = [tuple([color_tr[i][j] if j < 3 else 0.02 for j in range(4)])
                   for i in range(len(col_trans))]
        # and applies it to the main 3D scatter graph
        gl3d_item = self.listgl3dItems[0]
        self.apply_colors(color_t, gl3d_item)

        # prepares a new df for plot data corresponding to selected factor
        df_glob_sel = copy.deepcopy(df_glob)
        factor_OK = df_glob_sel[factor] > factor_inf
        df_glob_sel = df_glob_sel[factor_OK]
        factor_OK = df_glob_sel[factor] < factor_sup
        df_glob_sel = df_glob_sel[factor_OK]
        codeCoul_df_sel = codeCoul_df.loc[df_glob_sel.index][:]

        # colour = step_palette[color_inf]
        # sel_pal = step_palette[color_inf:color_sup]
        colour = adaptPaletteTodf(df_glob_sel, factor,
                                  step_palette, codeCoul_df_sel)

        x = np.array(df_glob_sel[self.GUI_Gr_obj.select_3_col[0]])
        y = np.array(df_glob_sel[self.GUI_Gr_obj.select_3_col[1]])
        z = np.array(df_glob_sel[self.GUI_Gr_obj.select_3_col[2]])
        self.addData(pos=(x, y, z),
                     names=self.GUI_Gr_obj.select_3_col, fourth=factor,
                     size=4, pxMode=True, color=colour,
                     setname=setname, ficname=self.ficname)
        # nb ficname is not used so far
        self.setWindowTitle("color={} -> restricted to {} - {}".format(factor,
                            factor_inf, factor_sup))
        # plt._auto_draw_if_interactive(self.figure, 1)

    def choose_subset(self):
        listChoix = ['data_sets']
        # self.listDic_dataSet = [{'data_sets': ["main"]}]
        titleText = "choose set to plot"
        list_items = self.setnames
        listDic_dataSet = self.listDic_dataSet
        rep = ChooseInList.listTransmit(parent=None,
                                        graphNo=0,
                                        listChoix=listChoix,
                                        items=list_items,
                                        listDicItems=listDic_dataSet,
                                        onePerCol=[0],
                                        colNames=["data sets"],
                                        typ="chk",
                                        titleText=titleText)
        self.listDic_dataSet = rep[0]
        self.selected_dataSets = self.listDic_dataSet[0][listChoix[0]]
        unselected_dataSets = []
        for idx, gl3d_item in enumerate(self.listgl3dItems):
            color = self.faceColItems[idx]
            sub_set = list_items[idx]
            if sub_set in self.selected_dataSets:
                gl3d_item._facecolor3d = color
                gl3d_item._edgecolor3d = color
            else:
                unselected_dataSets.append(sub_set)
                gl3d_item._facecolor3d = (0, 0, 0, 0)
                gl3d_item._edgecolor3d = (0, 0, 0, 0)
        plt._auto_draw_if_interactive(self.figure, 1)

    def remove_subset(self):
        listChoix = ['data_sets']
        titleText = "choose set to remove from list"
        list_remove = []
        list_items = self.setnames
        listDic_remSet = [{'data_sets': []}]
        rep = ChooseInList.listTransmit(parent=None,
                                        graphNo=0,
                                        listChoix=listChoix,
                                        items=list_items,
                                        listDicItems=listDic_remSet,
                                        onePerCol=[0],
                                        colNames=["data sets"],
                                        typ="chk",
                                        titleText=titleText)
        listDic_remSet = rep[0]
        dataSetsToRemove = listDic_remSet[0][listChoix[0]]
        print("dataSets To Remove:", dataSetsToRemove)
        # for idx, subset in enumerate(list_items):
        for idx, gl3d_item in enumerate(self.listgl3dItems):
            sub_set = list_items[idx]
            if sub_set in dataSetsToRemove:
                list_remove.append(idx)
            if sub_set in self.selected_dataSets:
                gl3d_item._facecolor3d = (0, 0, 0, 0)
                gl3d_item._edgecolor3d = (0, 0, 0, 0)
                plt._auto_draw_if_interactive(self.figure, 1)

        unwanted = set(list_remove)
        faceColItems = self.faceColItems
        listgl3dItems = self.listgl3dItems
        dataSet = self.dataSet
        list_items = [list_items[idx] for idx in range(len(list_items))
                      if idx not in unwanted]
        faceColItems = [faceColItems[idx] for idx in range(len(list_items))
                        if idx not in unwanted]
        listgl3dItems = [listgl3dItems[idx] for idx in range(len(list_items))
                         if idx not in unwanted]
        dataSet = [dataSet[idx] for idx in range(len(list_items))
                   if idx not in unwanted]
        self.setnames = list_items
        self.faceColItems = faceColItems
        self.listgl3dItems = listgl3dItems
        self.dataSet = dataSet

    def colors_per_set(self):
        for idx, gl3d_item in enumerate(self.listgl3dItems):
            # --------  One color for all dots  --------
            color = [random.uniform(0, 1), random.uniform(0, 1),
                     random.uniform(0, 1), 1]
            gl3d_item._facecolor3d = color
            gl3d_item._edgecolor3d = color
        plt._auto_draw_if_interactive(self.figure, 1)
        print("one color per gl3d_item")

    def set_orient(self):
        azim = self.axis.azim
        elev = self.axis.elev
        azim = float("{0:.2f}".format(round(azim, 2)))
        elev = float("{0:.2f}".format(round(elev, 2)))
        print("azim={}  elev={}".format(azim, elev))
        listChoix = ['orientation']
        listDicOrientNames = [{'orientation': ["azim", "elev"]}]
        listDic_orient_val = [{"azim": azim, "elev": elev}]
        self.orient_keys = ["azim", "elev"]
        titleText = "set orientation 3D graph"
        rep = ChooseInList.listTransmit(parent=None,
                                        graphNo=0,
                                        listChoix=listChoix,
                                        items=self.orient_keys,
                                        listDicItems=listDicOrientNames,
                                        onePerCol=[0],
                                        colNames=["orientation", 'value'],
                                        dicValues=listDic_orient_val[0],
                                        typ="val",
                                        titleText=titleText)

        listDicOrientNames = rep[0]
        self.orient_names = []
        self.dic_orient_val = rep[1]
        # print "rep[1]", rep[1]
        for i in range(len(listDicOrientNames[0][listChoix[0]])):
            itemName = listDicOrientNames[0][listChoix[0]][i]
            self.orient_names.append(itemName)
            listDic_orient_val[0][itemName] = float(rep[1][itemName])
            # print itemName, rep[1][itemName]
        azim = listDic_orient_val[0]['azim']
        elev = listDic_orient_val[0]['elev']
        print('azim={} ; elev={}'.format(azim, elev))
        self.axis.view_init(azim=azim, elev=elev)
        plt._auto_draw_if_interactive(self.figure, 1)

    def clearData(self):
        for idx, gl3d_item in enumerate(self.listgl3dItems):
            print(gl3d_item)
            gl3d_item.remove()
        self.dataSet = []
        self.listgl3dItems = []
        plt._auto_draw_if_interactive(self.figure, 1)
        print("all gl3d_item supressed")

    def saveGraph(self):
        azim = self.axis.azim
        elev = self.axis.elev
        """
        xlim = self.axis.get_xlim()
        ylim = self.axis.get_ylim()
        zlim = self.axis.get_zlim()
        """
        azim = float("{0:.2f}".format(round(azim, 2)))
        elev = float("{0:.2f}".format(round(elev, 2)))
        print("azim={}  elev={}".format(azim, elev))

        self.graph_path = QtWidgets.QFileDialog.\
            getExistingDirectory(self, "folder in which to save figure",
                                 self.rootdir)
        self.rootdir = os.path.split(self.graph_path)[0]
        print(r'{0}\{1}.pdf'.format(self.graph_path, self.ficname))
        df_glob = self.GUI_Gr_obj.df_glob
        select_3_col = self.GUI_Gr_obj.select_3_col
        factor = self.GUI_Gr_obj.factor
        ss_titre = self.GUI_Gr_obj.ss_titre
        titre = "Fig5_3D_Dots_{}__{}__{}".format(select_3_col[0][:13],
                                                 select_3_col[1][:13],
                                                 select_3_col[2][:13])
        # self.GUI_Gr_obj.make_3d_plot(df_glob, select_3_col,
        #                              titre, ss_titre, factor,
        #                              azim=azim, elev=elev)
        """
        dataSet = self.dataSet
        selected_dataSets = self.selected_dataSets
        list_items = self.setnames
        faceColItems = self.faceColItems
        graph_path = self.graph_path

        make_3d_plot_subPlots(df_glob, dataSet, selected_dataSets,
                              list_items, faceColItems,
                              xlim, ylim, zlim,
                              factor, select_3_col, titre, ss_titre,
                              graph_path,
                              azim=azim, elev=elev)
        """
        self.GUI_Gr_obj.make_3d_plot(df_glob, select_3_col, titre, ss_titre,
                                     factor, azim=azim, elev=elev)

    def closeWindows(self):
        # self.gl3d.removeItem(self.sp2)
        self.close()

    def closeEvent(self, event):
        """
        code exécuté quand l'interface est fermée
        """
        # ajoute une boite de dialogue pour confirmation de fermeture
        result = QtWidgets.QMessageBox.question(self,
                                            "Confirm Exit...",
                                            "Do you want to exit ?",
                                            (QtWidgets.QMessageBox.Yes |
                                             QtWidgets.QMessageBox.No))
        if result == QtWidgets.QMessageBox.Yes:
            # permet d'ajouter du code pour fermer proprement
            print(" ========== execution in Vizualizer OFF ==========")
            event.accept()

        else:
            event.ignore()


class InputDialogWin(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(InputDialogWin, self).__init__(parent)
        layout = QtWidgets.QFormLayout()
        self.btn2 = QtWidgets.QPushButton("Enter an integer")
        self.btn2.clicked.connect(self.getint)
        self.le2 = QtWidgets.QLineEdit()
        layout.addRow(self.btn2, self.le2)
        self.setLayout(layout)

    def getint(self, dialog_title, question, val):
        num, ok = QtWidgets.QInputDialog.getInt(self, dialog_title, question, val)
        if ok:
            self.le2.setText(str(num))
        return num


#   TODO    to be Finished..
class GEPGraphsMetrics(QtWidgets.QDialog):   # top-level widget to hold everything
    """
    class containing various methods to build graphs for GEP analysis
        - plot and save behavior and parameter maps
        - plot and save behavior map
        - plot and save behavior map (with chosen number of valid behaviors)
        - plot and save density map of GEP behavior domain
        - plot and save stability map of GEP behavior domain
        - plot and save progression of GEP process with two metric methods
            Two procedures can be used to estimate the "efficacy" of an
            optimisation process:
                1) Build an array that covers the behavior space with a given
                step and count the number of behaviours that are present in
                each box.
                Then give the number of boxes with at least one behaviour.
                2) Generate random targets inb the behaviour space and find for
                each target the closest behaviour. Then calculate the mean of
                distances from targets to closest behaviours.
    """
    def __init__(self, GUI_Gr_obj, parent=None):
        super(GEPGraphsMetrics, self).__init__(parent)
        self.resize(300, 150)
        self.GUI_Gr_obj = GUI_Gr_obj
        # self.scale_x = self.GUI_Gr_obj.scale_x
        # Create some widgets to be placed inside
        self.saveplotbhv_btn = QtWidgets.QPushButton('saveplot bhv map')
        self.saveplotbhv_btn.clicked.connect(self.saveplot_bhv)
        self.saveplobhvtparam_btn = QtWidgets.QPushButton('saveplot bhvparam maps')
        self.saveplobhvtparam_btn.clicked.connect(self.saveplot_bhvparam)

        self.behavior_map_btn = QtWidgets.QPushButton("&Behavior Map GEP")
        self.behavior_map_btn.clicked.connect(self.plot_bhvmap_nbBhvOK)

        self.MSp_ampl_Abaque_btn = QtWidgets.QPushButton("Abaque MaxSpeed/dur")
        self.MSp_ampl_Abaque_btn.clicked.connect(self.plot_abaque_duration)

        self.plot_density_btn = QtWidgets.QPushButton('plot bhv DensityMapContour')
        self.plot_density_btn.clicked.connect(self.plot_densitymaps_contour)
        self.density_map_btn = QtWidgets.QPushButton("&Density Map GEP")
        self.density_map_btn.clicked.connect(self.plot_densitymap_metrics)

        self.stability_map_btn = QtWidgets.QPushButton("&stability Map GEP")
        self.stability_map_btn.clicked.connect(self.plot_save_2D_stabilitymap)

        self.grid_method_btn = QtWidgets.QPushButton('metrics with grid method')
        self.grid_method_btn.clicked.connect(self.grid_method)
        self.dist_to_rand_goal_btn = QtWidgets.QPushButton('random goal method')
        self.dist_to_rand_goal_btn.clicked.connect(self.rand_goal_method)
        self.btn_quit = QtWidgets.QPushButton('QUIT')
        self.btn_quit.clicked.connect(self.closeIt)

        # text = QtWidgets.QLineEdit('enter text')
        self.listw = QtWidgets.QListWidget()
        # self.plot = pg.PlotWidget()
        # self.gl3d = gl.GLViewWidget()

        # Create a grid layout to manage the widgets size and position
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)
        # layout = QtWidgets..QVBoxLayout()

        # Add widgets to the layout in their proper positions
        layout.addWidget(self.saveplotbhv_btn, 0, 0)        # goes 1st row-left
        layout.addWidget(self.saveplobhvtparam_btn, 1, 0)   # goes 2nd row-left
        layout.addWidget(self.behavior_map_btn, 2, 0)       # goes 3d row-left
        layout.addWidget(self.MSp_ampl_Abaque_btn, 3, 0)    # goes 4th row-left
        layout.addWidget(self.plot_density_btn, 4, 0)       # goes 5th row-left
        layout.addWidget(self.density_map_btn, 5, 0)
        layout.addWidget(self.stability_map_btn, 6, 0)
        layout.addWidget(self.grid_method_btn, 7, 0)
        layout.addWidget(self.dist_to_rand_goal_btn, 8, 0)

        layout.addWidget(self.btn_quit, 9, 0)      # goes in bottom-left
        # layout.addWidget(self.plot, 0, 1, 3, 1)  # plot goes on right side,
        #                                          # spanning 3 rows
        self.setWindowTitle("GEP Metrics and Graphs")
        self.to_init()

    def screen_loc(self, xshift=0, yshift=0):
        ag = QtWidgets.QDesktopWidget().availableGeometry()
        # sg = QtWidgets.QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = ag.width() - widget.width() - xshift
        # y = 2 * ag.height() - sg.height() - widget.height()
        y = ag.height() - widget.height() - yshift
        self.move(x, y)

    def to_init(self):
        """
        doc string
        """
        self.autoscale = False
        self.scale_x = self.GUI_Gr_obj.scale_x
        self.scale_y = self.GUI_Gr_obj.scale_y
        self.behav_col = self.GUI_Gr_obj.behav_col
        self.bhv_names = self.GUI_Gr_obj.bhv_names

    def saveplot_bhv(self):
        """
        Saves a plot of behavior domain using a method of the class MaFenetre
        """
        df_bhv = self.GUI_Gr_obj.df_bhvremain
        # pathGEP = self.GUI_Gr_obj.listGEPFolders[0]
        # root_path = os.path.split(pathGEP)[0]
        # graph_path = os.path.join(root_path, "graphs")
        # graph_path = root_path + "/graphs"
        graph_path = self.GUI_Gr_obj.graph_path
        if not os.path.exists(graph_path):
            os.makedirs(graph_path)
        behav_col = self.behav_col
        if behav_col[1] == 8:
            ordTyp = "duration"
        elif behav_col[1] == 6:
            ordTyp = "maxSpeed"
        name = "{}_{}".format("GEPdata00", ordTyp)
        behav_col = self.behav_col
        max_x_bhv = df_bhv[df_bhv.columns[behav_col[0]]].max()/self.scale_x
        max_y_bhv = df_bhv[df_bhv.columns[behav_col[1]]].max()/self.scale_y
        self.GUI_Gr_obj.mafen.save_map_behav(df_bhv, graph_path, name,
                                             max_x=max_x_bhv, max_y=max_y_bhv)
        print("bvh plot saved to: " + graph_path)

    def saveplot_bhvparam(self):
        """
        Plots and saves in pdf and eps format, a series of x-y scatter graphs
        representing the behaviors (from df_bhvremain) and the corresponding
        parameter sets presented by pairs of parameters (from df_parremain).
        It s possible to restraindf_bhvremain and df_parremain to lines that
        are between start and end
        """
        optSet = self.GUI_Gr_obj.optSet
        xparName = optSet.xparName
        graph_path = self.GUI_Gr_obj.graph_path
        graph_name = os.path.split(graph_path)[-1]
        df_bhv = copy.deepcopy(self.GUI_Gr_obj.df_bhvremain)
        df_par = copy.deepcopy(self.GUI_Gr_obj.df_parremain)
        if graph_name[:15] == 'mltpleExpeGraph':
            print("This is a multipleExpeGraph ==> plot totality of _bhv")
            start = 0
            end = df_bhv["rgserie"].max()
        else: 
            if self.autoscale is not True:
                self.dialog = InputDialogWin()
                start = 0
                end = len(self.GUI_Gr_obj.df_bhvremain)
                dialog_title = "plot range"
                start = self.dialog.getint(dialog_title, "start row", start)
                end = self.dialog.getint(dialog_title, "end row", end)
            else:
                start = 0
                end = df_bhv["rgserie"].max()
            df_bhv = df_bhv.loc[start:end]
            df_par = df_par.loc[start:end]
        behav_col = self.GUI_Gr_obj.behav_col
        listDicGraphs = self.GUI_Gr_obj.mafen.listDicGraphs
        xparNameDict = self.GUI_Gr_obj.mafen.xparNameDict
        # pathGEP = self.GUI_Gr_obj.listGEPFolders[0]
        # root_path = os.path.split(pathGEP)[0]
        # graph_path = os.path.join(root_path, "graphs")
        # graph_path = root_path + "/graphs"
        graph_path = self.GUI_Gr_obj.graph_path
        if not os.path.exists(graph_path):
            os.makedirs(graph_path)
        strGEPdataName = self.GUI_Gr_obj.prevListGEPFiles[0]
        strGEPdataName = os.path.splitext(strGEPdataName)[0]

        if behav_col[1] == 8:
            ordTyp = "duration"
            max_x_bhv = 1.2
            max_y_bhv = 2.0
        elif behav_col[1] == 6:
            ordTyp = "maxSpeed"
            max_x_bhv = 1.2
            max_y_bhv = 5.0
        baseName = "{}_{}_{}_{}_{}".format(strGEPdataName[:], ordTyp,
                                           "bhv_par_graphs", start, end)
        """
        max_x_bhv = df_bhv[df_bhv.columns[behav_col[0]]].max()/self.scale_x
        max_y_bhv = df_bhv[df_bhv.columns[behav_col[1]]].max()/self.scale_y
        max_x = float(int(max_x_bhv*10)+1)/10
        max_y = float(int(max_y_bhv*10)+1)/10
        """
        do_plot_bhv_param(self.GUI_Gr_obj, df_bhv, df_par, behav_col,
                          graph_path, baseName, listDicGraphs, xparNameDict,
                          xparName,  max_x_bhv=max_x_bhv, max_y_bhv=max_y_bhv)
        print("bvh & parameter plot saved to: " + graph_path)

    def plot_bhvmap_nbBhvOK(self):
        """
        plots and saves the df_bhvremain dataframe for index < nbBhvOK
        """
        # self.GUI_Gr_obj.close_otherwin()
        """
        df_bhvremain = self.GUI_Gr_obj.df_bhvremain
        ret = 7
        if df_bhvremain is not None:
            msg = "A previous dataframe is present \n Use Same dataframe?"
            ret = MessageBox(None, msg, 'Previous dataframe detected', 3)
            print ret
            if ret == 2:
                print "ESC"
            elif ret == 6:
                print "YES --> Keep the previous dataframe"
                print "df_bhvremain size : {}\n".format(len(df_bhvremain))
            elif ret == 7:
                print "NO: --> Look for another dierctory"
        if ret == 7:
            self.GUI_Gr_obj.make_bhvpardf_bhvparwins()
        """
        listcolors = ['blue', 'orange', 'green', 'red', 'purple',
                      'brown', 'pink', 'gray', 'olive', 'cyan']

        # self.GUI_Gr_obj.make_bhvpardf_bhvparwins()
        df_bhvremain = self.GUI_Gr_obj.df_bhvremain
        # pathGEP = self.GUI_Gr_obj.listGEPFolders[0]
        # root_path = os.path.split(pathGEP)[0]
        # graph_path = os.path.join(root_path, "graphs")
        # graph_path = root_path + "/graphs"
        graph_path = self.GUI_Gr_obj.graph_path
        if not os.path.exists(graph_path):
            os.makedirs(graph_path)
        strGEPdataName = self.GUI_Gr_obj.prevListGEPFiles[0]
        GEPdataName = os.path.splitext(strGEPdataName)[0]
        df = copy.deepcopy(df_bhvremain)
        # ==============================================================
        list_entry_name = ["nbBhvOKs", "X_min", "X_max", "Y_min", "Y_max"]
        nbBhvOKs = len(df)
        behav_col = self.GUI_Gr_obj.behav_col
        # max_x = df_bhvremain[df_bhvremain.columns[behav_col[0]]].max()/100
        # max_y_bhv = df_bhvremain[df_bhvremain.columns[behav_col[1]]].max()
        list_entry_value = [str(nbBhvOKs), str(0), str(1.2), str(0), str(1.4)]
        list_value_max = [nbBhvOKs, 1.5, 1.5, 5, 5]
        window_name = "Enter nbBhvOK to Plot"
        self.list_bhvmap_value = list_entry_value
        self.get_nbBhvOKs = Enter_Values(self,
                                         list_entry_name,
                                         list_entry_value,
                                         list_value_max,
                                         window_name)
        self.get_nbBhvOKs.show()
        self.get_nbBhvOKs.exec_()  # Stops further processes
        #                                           until executed
        self.list_bhvmap_value = self.list_value
        # QtWidgets.QApplication.processEvents()
        # ==============================================================

        nbBhvOK = int(self.list_bhvmap_value[0])
        x_min = float(self.list_bhvmap_value[1])
        x_max = float(self.list_bhvmap_value[2])
        y_min = float(self.list_bhvmap_value[3])
        y_max = float(self.list_bhvmap_value[4])
        df = df[:nbBhvOK]
        rate = 100
        lstdurMvt2T = []  
        behav_col = self.GUI_Gr_obj.behav_col
        if behav_col[1] == 8:
            ordTyp = "duration"
            # ======== add a new column with durMvt2T from template ===========
            for idx in df.index:
                amplitude = df.endangle[idx]
                max_speed = df.max_speed[idx]
                rep = calculate_minjerk_duration(amplitude, max_speed, rate)
                durMvt2T = rep[0]
                lstdurMvt2T.append(durMvt2T)
            df.loc[:, 'durMvt2T'] = lstdurMvt2T  
            # =================================================================
            name = "{}_{}_bhvPlot_{}".format(GEPdataName, "durationT", nbBhvOK)
        elif behav_col[1] == 6:
            ordTyp = "maxSpeed"
            name = "{}_{}_bhvPlot_{}".format(GEPdataName, ordTyp, nbBhvOK)
        # name = GEPdataName + "bhvPlot_{}".format(nbBhvOK)
        # path = os.path.split(pathGEP)[0]
        if os.path.split(graph_path)[1] == "graphs":
            path = os.path.split(graph_path)[0]
        else:
            path = graph_path
        # titre = "{}/{}".format(path, name)
        baseName = name
        titre = get_titre(path, baseName)
        # ===========================================================
        fig = plt.figure(figsize=(10, 10), dpi=90)
        # plt.subplots_adjust(bottom=0, left=0.1, top=0.9, right=0.9)
        grid = plt.GridSpec(1, 1, wspace=0.4, hspace=0.3)
        ax1 = fig.add_subplot(grid[0, 0])
        if ordTyp == "duration":
            bhv_col = [3, 13]
        else:
            bhv_col = [3, 6]
        behavs_cues = df[df.columns[bhv_col]]
        rel_behavs_cues = behavs_cues/[self.scale_x, self.scale_y]
        nameX = rel_behavs_cues.columns[0]
        nameY = rel_behavs_cues.columns[1]
        valX = rel_behavs_cues[nameX]
        valY = rel_behavs_cues[nameY]

        if self.behav_col[1] == 8:      # if ordonate is duration...
            labelnameX = nameX + "(x 0.01)"
            labelnameY = nameY
        elif self.behav_col[1] == 6:
            labelnameX = nameX + "(x 0.01)"
            labelnameY = nameY + "(x 0.01)"

        ax1 = fig.add_subplot(grid[0, 0])
        selectedROI = self.GUI_Gr_obj.mafen.selectedROI
        if selectedROI == []:
            # ---------------------------------------------------
            ax1.scatter(valX, valY, marker='o', s=4, c="r")
            # ---------------------------------------------------
        else:
            for idxROI, listdata in enumerate(selectedROI):
                dflist_x = rel_behavs_cues[nameX][listdata]
                dflist_y = rel_behavs_cues[nameY][listdata]
                color = listcolors[idxROI]
                # ---------------------------------------------------
                ax1.scatter(dflist_x, dflist_y, marker='o', s=4, c=color)
                # ---------------------------------------------------
        ax1.set_xlabel(labelnameX, fontsize=11)
        ax1.set_ylabel(labelnameY, fontsize=11)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        ax1.set_axisbelow(True)
        ax1.set_xlim(x_min, x_max)
        ax1.set_ylim(y_min, y_max)
        ax1.grid(linestyle='-', linewidth='0.5', color='green')
        plt.suptitle(titre, fontsize=12, y=0.95)
        plt.savefig(os.path.join(graph_path, name + '.pdf'))
        plt.savefig(os.path.join(graph_path, name + '.eps'))
        plt.show()
        # self.mafen.save_map_behav(df, pathGEP, name)

    def plot_abaque_duration(self):
        """
        Plots a series of curves Maxspeed=f(amplitude)  for a series of
        duration values
        INPUT: graph_path, graph_name, mindur, maxdur, stepdur
            in which mindur and max dur are the minimum and maximum values of
            duration, and stepdur is the step used to define the varius values
            of duration between mindur and maxdur
        OUTPUT: a plot that will be saved in the graph folder (graph_path)
            under the names : graph_name + '.pdf' and graph_name + '.eps'
        """
        graph_path = self.GUI_Gr_obj.graph_path
        graph_name = "abaques_duration"
        nomfic_eps = graph_path + '/' + graph_name + '.eps'
        nomfic_pdf = graph_path + '/' + graph_name + '.pdf'
        if not os.path.exists(nomfic_eps):
            plt.savefig(nomfic_eps, bbox_inches='tight')
            plt.savefig(nomfic_pdf, bbox_inches='tight')
        else:
            root = nomfic_eps[:nomfic_eps.find(".eps")]
            print(len(root))
            k = 0
            while os.path.exists("{0}({1}){2}".format(root, k, ".eps")):
                k += 1
            nomfic_eps = "{0}({1}){2}".format(root, k, ".eps")
            nomfic_pdf = "{0}({1}){2}".format(root, k, ".pdf")
        graph_name_with_ext = os.path.split(nomfic_eps)[-1]
        graph_name = os.path.splitext(graph_name_with_ext)[0]
        # ==============================================================
        list_entry_name = ["mindur", "maxdur", "stepdur"]
        list_entry_value = [0.2, 5, 0.25]
        #list_value_max = [0.2, 5, 5]
        window_name = "Enter min, max, step for durations"
        dicValues = {}
        for idx, nam in enumerate(list_entry_name):
            dicValues[nam] = list_entry_value[idx]
        selected, typ, text = "sel", "typ", window_name
        dicValues = set_values_in_list(dicValues, selected, typ, text)
        # QtWidgets.QApplication.processEvents()
        # ==============================================================
        mindur = float(dicValues["mindur"])
        maxdur = float(dicValues["maxdur"])
        stepdur = float(dicValues["stepdur"])
        plot_series_curves_maxspeed_ampl_duration(graph_path, graph_name,
                                                  mindur, maxdur, stepdur)
        

    def plot_densitymap_metrics(self):
        """
        Plots and saves a density map that uses the same grid as the grid
        used in metrics to evaluate how the GEP explores the behavior
        space. The score in metrics is simply the number of cases in the
        grid that contain at least one behavior.
        Here, this gid is used to count the number of behaviors in each
        case, which gives an idea of the density of the behaviors in the
        different regions.
        It is possible to restrain the graph for runs between 0 and nbruns
        """
        # self.GUI_Gr_obj.close_otherwin()
        # self.GUI_Gr_obj.make_bhvpardf_bhvparwins()
        df_bhvremain = self.GUI_Gr_obj.df_bhvremain
        # pathGEP = self.GUI_Gr_obj.listGEPFolders[0]
        # root_path = os.path.split(pathGEP)[0]
        # graph_path = os.path.join(root_path, "graphs")
        # graph_path = root_path + "/graphs"
        graph_path = self.GUI_Gr_obj.graph_path
        if not os.path.exists(graph_path):
            os.makedirs(graph_path)
        strGEPdataName = self.GUI_Gr_obj.prevListGEPFiles[0]
        behav_col = self.GUI_Gr_obj.behav_col
        GEPdataName = os.path.splitext(strGEPdataName)[0]

        
        nbruns = df_bhvremain["orig_rg"].max()
        # ==============================================================
        max_x_bhv = df_bhvremain[df_bhvremain.columns[behav_col[0]]].max()
        max_y_bhv = df_bhvremain[df_bhvremain.columns[behav_col[1]]].max()
        max_x = float(int(max_x_bhv*10)+1)/10
        max_y = float(int(max_y_bhv*10)+1)/10
        
        list_entry_value = [str(nbruns), str(0), str(max_x),
                            str(0), str(max_y)]
        list_value_max = [nbruns, 150, 150, 200, 500]
        list_entry_name = ["nbRunOK", "X_min", "X_max", "Y_min", "Y_max"]
        window_name = "Enter x_Y range to Plot"
        self.list_range_value_densitymap_metrics = list_entry_value
        self.get_plot_range = Enter_Values(self,
                                           list_entry_name,
                                           list_entry_value,
                                           list_value_max,
                                           window_name)
        self.get_plot_range.show()
        self.get_plot_range.exec_()  # Stops further processes
        #                                           until executed
        self.list_range_value_densitymap_metrics = self.list_value
        # QtWidgets.QApplication.processEvents()
        
        # ==============================================================

        nbRunOK = int(self.list_range_value_densitymap_metrics[0])
        x_min = float(self.list_range_value_densitymap_metrics[1])
        x_max = float(self.list_range_value_densitymap_metrics[2])
        y_min = float(self.list_range_value_densitymap_metrics[3])
        y_max = float(self.list_range_value_densitymap_metrics[4])

        print(nbRunOK)
        bhv_names = self.bhv_names
        # #####################################################################
        do_plot_2D_density_map_metrics(df_bhvremain, behav_col, bhv_names,
                                       graph_path, GEPdataName, nbRunOK,
                                       min_x=x_min, max_x=x_max,
                                       min_y=y_min, max_y=y_max,
                                       autoscale=False)
        # #####################################################################

    def plot_save_density_map_metrics(self):
        # ==============================================================
        QtWidgets.QApplication.processEvents()
        # ==============================================================
        df_bhvremain = self.GUI_Gr_obj.df_bhvremain
        behav_col = self.GUI_Gr_obj.behav_col
        bhv_names = self.bhv_names
        strGEPdataName = self.GUI_Gr_obj.prevListGEPFiles[0]
        GEPdataName = os.path.splitext(strGEPdataName)[0]
        graph_path = self.GUI_Gr_obj.graph_path
        bhvOK = df_bhvremain["varmse"]<1
        df_OK = df_bhvremain[bhvOK]
        nbRunOK = len(df_OK)
        x_min = 0
        x_max = 120
        y_min = 0
        y_max = 500
        # #####################################################################
        do_plot_2D_density_map_metrics(df_bhvremain, behav_col, bhv_names,
                                       graph_path, GEPdataName, nbRunOK,
                                       min_x=x_min, max_x=x_max,
                                       min_y=y_min, max_y=y_max,
                                       autoscale=True)
        # #####################################################################
        
        

    def plot_save_2D_densitymap_contour(self):
        # self.GUI_Gr_obj.close_otherwin()
        # self.GUI_Gr_obj.make_bhvpardf_bhvparwins()
        # ==============================================================
        QtWidgets.QApplication.processEvents()
        # ==============================================================
        behav_col = self.GUI_Gr_obj.behav_col
        df_bhv = copy.deepcopy(self.GUI_Gr_obj.df_bhvremain)
        max_x_bhv = df_bhv[df_bhv.columns[behav_col[0]]].max()/self.scale_x
        max_y_bhv = df_bhv[df_bhv.columns[behav_col[1]]].max()/self.scale_y
        max_x = float(int(max_x_bhv*10)+1)/10
        max_y = float(int(max_y_bhv*10)+1)/10

        nbruns = df_bhv["orig_rg"].max()
        if self.autoscale is not True:
            # ==============================================================
            list_entry_name = ["nbBhvOKs", "X_min", "X_max", "Y_min", "Y_max"]
            list_entry_value = [str(nbruns), str(0), str(max_x),
                                str(0), str(max_y)]
            list_value_max = [nbruns, 5, 5, 5, 5]
            window_name = "densitymap_contour settings"
            self.list_densitymap_contour_value = list_entry_value
            self.get_densitymapContour = Enter_Values(self,
                                                      list_entry_name,
                                                      list_entry_value,
                                                      list_value_max,
                                                      window_name)
            self.get_densitymapContour.show()
            self.get_densitymapContour.exec_()  # Stops further processes
            self.list_densitymap_contour_value = self.list_value

            nbRunOK = int(self.list_densitymap_contour_value[0])
            xmin = float(self.list_densitymap_contour_value[1])
            xmax = float(self.list_densitymap_contour_value[2])
            ymin = float(self.list_densitymap_contour_value[3])
            ymax = float(self.list_densitymap_contour_value[4])
            #                                           until executed
            # QtWidgets.QApplication.processEvents()
            # ==============================================================
        else:
            nbRunOK = nbruns
            xmin = 0
            xmax = max_x
            ymin = 0
            ymax = max_y
        # pathGEP = self.GUI_Gr_obj.listGEPFolders[0]
        # root_path = os.path.split(pathGEP)[0]
        # graph_path = os.path.join(root_path, "graphs")
        # graph_path = root_path + "/graphs"
        graph_path = self.GUI_Gr_obj.graph_path
        if not os.path.exists(graph_path):
            os.makedirs(graph_path)

        strGEPdataName = self.GUI_Gr_obj.prevListGEPFiles[0]
        # #####################################################################
        plot_2D_density_map_contour(self.GUI_Gr_obj, df_bhv, behav_col,
                                    graph_path,
                                    strGEPdataName, nbRunOK,
                                    step=0.025,
                                    xmin=xmin, xmax=xmax,
                                    ymin=ymin, ymax=ymax, saveDM=True)
        # ==============================================================
        QtWidgets.QApplication.processEvents()
        # ==============================================================
        """
        df_bhv.iloc[[4000]]
        """


    def plot_densitymaps_contour(self):
        df_bhv = self.GUI_Gr_obj.df_bhvremain
        behav_col = self.GUI_Gr_obj.behav_col
        # pathGEP = self.GUI_Gr_obj.listGEPFolders[0]
        # root_path = os.path.split(pathGEP)[0]
        # graph_path = os.path.join(root_path, "graphs")
        # graph_path = root_path + "/graphs"
        graph_path = self.GUI_Gr_obj.graph_path
        if not os.path.exists(graph_path):
            os.makedirs(graph_path)
        strGEPdataName = self.GUI_Gr_obj.prevListGEPFiles[0]
        max_x_bhv = df_bhv[df_bhv.columns[behav_col[0]]].max()/self.scale_x
        max_y_bhv = df_bhv[df_bhv.columns[behav_col[1]]].max()/self.scale_y
        max_x = float(int(max_x_bhv*10)+1)/10
        max_y = float(int(max_y_bhv*10)+1)/10

        xmin = 0
        xmax = max_x
        ymin = 0
        ymax = max_y

        # #####################################################################
        plot_2D_density_map_contour(self.GUI_Gr_obj, df_bhv, behav_col,
                                    graph_path,
                                    strGEPdataName,
                                    step=0.025,
                                    xmin=xmin, xmax=xmax,
                                    ymin=ymin, ymax=ymax, saveDM=True)
        # ==============================================================
        QtWidgets.QApplication.processEvents()
        # ==============================================================
        plot_3D_density_map_contour(df_bhv, behav_col, step=0.025,
                                    incline=60, rot=-30,
                                    xmin=xmin, xmax=xmax,
                                    ymin=ymin, ymax=ymax)
        # ==============================================================
        QtWidgets.QApplication.processEvents()
        # ==============================================================
        # #####################################################################
        print("2D denity plot saved to: ", graph_path)

    def plot_save_2D_stabilitymap(self):
        """
        """
        """
        self.GUI_Gr_obj.close_otherwin()
        # ==============================================================
        QtWidgets.QApplication.processEvents()
        # ==============================================================

        ret = 7
        df_bhvremain = self.GUI_Gr_obj.df_bhvremain
        if df_bhvremain is not None:
            msg = "A previous dataframe is present \n Use Same dataframe?"
            ret = MessageBox(None, msg, 'Previous dataframe detected', 3)
            print ret
            if ret == 2:
                print "ESC"
            elif ret == 6:
                print("YES --> Keep the previous dataframe")
                print("df_bhvremain size : {}\n".format(len(df_bhvremain)))
            elif ret == 7:
                print("NO: --> Look for another dierctory")
        if ret == 7:
            self.GUI_Gr_obj.make_bhvpardf_bhvparwins()

        self.GUI_Gr_obj.make_bhvpardf_bhvparwins()
        """
        df_bhvremain = self.GUI_Gr_obj.df_bhvremain
        df_parremain = self.GUI_Gr_obj.df_parremain
        # #####################################################################
        self.GUI_Gr_obj.plot_2D_stability_map(df_bhvremain, df_parremain)
        # #####################################################################
        QtWidgets.QApplication.processEvents()
        # ==============================================================

    def grid_method(self):
        """
        This methods builds a grid on the behaviour space (40row x 40 columns)
        on a behav space limits: endangle in [0, 120]; dur_mvt2 in [0.2, 1.4]
        Every 100 runs, the number of cases in which at least one behavior was
        found are counted. A plot of these numbers along time is then built.
        """

        print("build a grid on behaviour space to count nb of occupied boxes ")
        # creates a df with only two columns (for behaviour)
        bhv_names = self.bhv_names
        behav_col = self.behav_col
        name_x = bhv_names[behav_col[0]]
        name_y = bhv_names[behav_col[1]]
        df = copy.deepcopy(self.GUI_Gr_obj.df_bhvremain[[name_x,
                                                         name_y,
                                                         'orig_rg']])
        optSet = self.GUI_Gr_obj.optSet
        nbr_trials = len(optSet.pairs)
        tab_scores = []
        # nbFilledBox = []
        # nbrun = []
        # bhv_OK = []
        # density = []
        nbcol = 40
        nbrow = 40
        max_x_bhv = df[name_x].max()
        max_y_bhv = df[name_y].max()
        min_x = 0
        max_x = max_x_bhv
        min_y = 0
        max_y = max_y_bhv
        intervalx = (max_x - min_x)/nbcol
        intervaly = round((max_y - min_y)*1000/nbrow)/1000

        # pathGEP = self.GUI_Gr_obj.listGEPFolders[0]
        # root_path = os.path.split(pathGEP)[0]
        # graph_path = os.path.join(root_path, "graphs")
        # graph_path = root_path + "/graphs"
        graph_path = self.GUI_Gr_obj.graph_path
        if not os.path.exists(graph_path):
            os.makedirs(graph_path)
        if behav_col[1] == 8:
            ordTyp = "duration"
        elif behav_col[1] == 6:
            ordTyp = "maxSpeed"
        strGEPdataName = self.GUI_Gr_obj.prevListGEPFiles[0]
        strGEPdataName = os.path.splitext(strGEPdataName)[0]
        baseName = "{}_{}_{}".format(strGEPdataName[:], ordTyp,
                                     "Grid_Metrics")
        completeName = os.path.join(graph_path, baseName + '.txt')
        nBhvOK = 0
        if not os.path.exists(completeName):
            if nbr_trials > 100:
                state_table = np.zeros(dtype=int, shape=(nbcol, nbrow))
                lst_bn_bhv = []
                for run in range(int(round(nbr_trials/100))+1):
                    start = run * 100
                    end = start + 100
                    df_run = df.loc[(df['orig_rg'] >= start) &
                                    (df['orig_rg'] < end)]
                    nBhvOK += len(df_run)
                    nb_bhv = []
                    for i in range(nbrow):
                        yi = i*intervaly + min_y
                        ys = (i+1)*intervaly + min_y
                        row_df = df_run.loc[(df_run[name_y] >= yi) &
                                            (df_run[name_y] < ys)]
                        nb_bhv_row = []
                        for j in range(nbcol):
                            xi = j*intervalx + min_x
                            xs = (j+1)*intervalx + min_x
                            temp_col_df = row_df.loc[(row_df[name_x] >= xi) &
                                                     (row_df[name_x] < xs)]
                            nb_bhv_row.append(len(temp_col_df[name_x]))
                        # print(nb_bhv_row)
                        nb_bhv.append(nb_bhv_row)
                    nb_bhv = np.array(nb_bhv)
                    lst_bn_bhv.append(nb_bhv)
                    state_table = nb_bhv + state_table
                    score = np.count_nonzero(state_table)
                    if score > 0:
                        density = float(nBhvOK)/score
                        tab_scores.append([(run+1) * 100, score, nBhvOK,
                                           density])
                        print("{:5d} {:4d} {:3.2f}\t".format(run, score,
                                                             density), end=" ")
                    else:
                        print("{:5d} {:4d} {:3.2f}\t".format(run, score, 0), end=" ")
                    """
                    nbFilledBox.append(score)
                    nbrun.append((run+1) * 100)
                    bhv_OK.append(nBhvOK)
                    density.append(nBhvOK/score)
                """
                if score > 0:
                    with open(completeName, 'w') as fich:
                        s = "index\tnb_runs\t score\t nBhvOK\t density\n"
                        fich.write(s)
                        for idx in range(len(tab_scores)):
                            [run, score, nBhvOK, density] = tab_scores[idx]
                            tmptxt = "{}\t{:5d}\t{:4d}\t{:4d}\t{:3.2f}\n"
                            s = tmptxt.format(idx, run, score, nBhvOK, density)
                            fich.write(s)
                    fich.close()
                    print("metrics data saved to: ", completeName)
                    print()
        else:
            print("Tab_scores already exists... Build graph from it")

        if os.path.exists(completeName):
            tab_scores = read_tab_scores(graph_path, baseName)
            index = np.arange(len(tab_scores[:]))
            self.df_score = pd.DataFrame(tab_scores[:],
                                         columns=['index', 'nb_runs',
                                                  'score',
                                                  'nBhvOK', 'density'],
                                         index=index)

            """
            d = {'nb_runs': pd.Series(nbrun),
                 'score': pd.Series(nbFilledBox),
                 'bhv_OK': pd.Series(bhv_OK),
                 'density': pd.Series(density)}
            score_evol_df = pd.DataFrame(d)
            score_evol_df.index = nbrun
            self.GUI_Gr_obj.score_evol_df = score_evol_df
            """
            self.GUI_Gr_obj.score_evol_df = self.df_score
            self.make_graph_score_evol()

    def make_graph_score_evol(self):
        """
        Builds the graph to be saved in eps and pdf formats of score_evol_df
        along time (one dot every 100 trials). On the second graph row the
        bhvplot is placed and all paramplots are placed to finish the row and
        on following rows if necessary.

        """
        # =====================================================================
        #   The following lines allow to make the graphs from table in debug
        # =====================================================================
        """
        self = MyWin
        self.make_bhvpardf_bhvparwins()
        self.makeGEPMetrics = GEPGraphsMetrics(self)

        self = MyWin.makeGEPMetrics
        pathGEP = self.GUI_Gr_obj.listGEPFolders[0]
        strGEPdataName = self.GUI_Gr_obj.prevListGEPFiles[0]
        strGEPdataName = os.path.splitext(strGEPdataName)[0]
        baseName = baseName = strGEPdataName[:] + "_Grid_Metrics"
        self.df_score = read_metric_table(pathGEP, baseName)
        self.GUI_Gr_obj.score_evol_df = self.df_score
        """

        # optSet = self.GUI_Gr_obj.optSet
        score_evol_df = self.GUI_Gr_obj.score_evol_df
        datastructure = self.GUI_Gr_obj.datastructure
        df_bhvremain = copy.deepcopy(self.GUI_Gr_obj.df_bhvremain)
        # df_parremain = copy.deepcopy(self.GUI_Gr_obj.df_parremain)
        behav_col = self.GUI_Gr_obj.behav_col
        # listDicGraphs = self.GUI_Gr_obj.mafen.listDicGraphs
        # xparNameDict = self.GUI_Gr_obj.mafen.xparNameDict

        tabnewstart_typ = []
        tabnewstart = []
        tabnewend = []
        tabnewspan = []
        tabcolors = []
        tabtexts = []
        for i in range(len(datastructure)):
            tabnewstart_typ.append(datastructure[i][0])
            tabnewstart.append(datastructure[i][1])
            tabnewend.append(datastructure[i][2])
            tabnewspan.append(datastructure[i][4][0])

        # pathGEP = self.GUI_Gr_obj.listGEPFolders[0]
        # root_path = os.path.split(pathGEP)[0]
        # graph_path = os.path.join(root_path, "graphs")
        # graph_path = root_path + "/graphs"
        graph_path = self.GUI_Gr_obj.graph_path
        if not os.path.exists(graph_path):
            os.makedirs(graph_path)

        strGEPdataName = self.GUI_Gr_obj.prevListGEPFiles[0]
        strGEPdataName = os.path.splitext(strGEPdataName)[0]
        #  =================  sets the vertical bands for typ  ================
        prev_span = 0
        prev_typ = "0"
        for idx, start in enumerate(tabnewstart):
            # print(idx, start, tabnewstart_typ[idx])
            if idx < len(tabnewstart):
                if type(tabnewspan[idx]) is list:
                    if len(tabnewspan[idx]) > 2:
                        span = "spanlist"
                    elif len(tabnewspan[idx]) == 2:
                        span = tabnewspan[idx]
                    elif len(tabnewspan[idx]) == 1:
                        if type(tabnewspan[idx][0]) is str:
                            span = "spanlist"
                        else:
                            span = int(tabnewspan[idx])
                new_typ = tabnewstart_typ[idx]
                # print(new_typ)
                # lighten = 0.5 + (float(span)/100) * 5
                if type(span) is int:
                    lighten = ln(1 + (float(span)/100) * 5)
                    if lighten > 1:
                        lighten = 1
                else:
                    lighten = 1
                # tp = int(tabnewstart[idx]/100)*100    # round 100multiple
                # labY = score_evol_df.loc[(score_evol_df['nb_runs'] == tp)]
                if tabnewstart_typ[idx] == "rdparam":
                    color = lighten_color('green', lighten)
                elif tabnewstart_typ[idx] == 'rdparam_MSE':
                    color = lighten_color('green', lighten)
                elif tabnewstart_typ[idx] == 'rdparam_varmse':
                    color = lighten_color('green', lighten)
                elif tabnewstart_typ[idx] == 'rdparam_noEvol':
                    color = lighten_color('green', lighten)
                elif tabnewstart_typ[idx] == "GEPrand":
                    color = lighten_color('yellow', lighten)
                elif tabnewstart_typ[idx] == "CMAE":
                    color = lighten_color('red', lighten)
                else:
                    color = "w"
                tabcolors.append(color)
                # -------------------- sets the span values -----------------
                if new_typ not in (prev_typ, "GEPrand", "CMAE"):
                    typ = new_typ
                else:
                    typ = ""

                if span != prev_span or tabnewstart_typ[idx] != prev_typ:
                    txt = "{} \n {}".format(typ, span)
                else:
                    txt = ""
                tabtexts.append(txt)
                prev_span = span
                prev_typ = tabnewstart_typ[idx]
        # pathGEP = self.listGEPFolders[0]
        # path = os.path.split(pathGEP)[0]
        if os.path.split(graph_path)[1] == "graphs":
            path = os.path.split(graph_path)[0]
        else:
            path = graph_path
        if behav_col[1] == 8:
            ordTyp = "duration"
        elif behav_col[1] == 6:
            ordTyp = "maxSpeed"

        baseName = "{}_{}_{}".format(strGEPdataName[:], ordTyp, "Grid Metrics")
        titre = get_titre(path, baseName)

        max_score = score_evol_df[:]["score"].max()
        max_density = score_evol_df[:]["density"].max()
        # =====================================================================
        fig = plt.figure(figsize=(10, 18), dpi=90)
        # plt.subplots_adjust(bottom=0, left=0.1, top=0.9, right=0.9)
        grid = plt.GridSpec(5, 3, wspace=0.4, hspace=0.3)
        # plt.subplots_adjust(hspace=.3)
        # plt.subplots_adjust(wspace=.4)
        # ax1 = fig.add_subplot(311)
        ax1 = fig.add_subplot(grid[0, :3])
        #  ================= plots the evolution of filled boxes ==============
        ax1.plot(score_evol_df[:]["nb_runs"],
                 score_evol_df[:]["score"], color="b")

        """
        maxi = float(score_evol_df[:]["score"].max())
        prev_typ = "0"
        for idx, start in enumerate(tabnewstart):
            ax1.axvspan(tabnewstart[idx], tabnewend[idx],
                        alpha=0.5, color=tabcolors[idx], lw=1)
            tp = int(tabnewstart[idx]/100)*100    # round 100multiple
            labY = score_evol_df.loc[(score_evol_df['nb_runs'] == tp)]
            if tabnewstart_typ[idx] == prev_typ:
                ax1.text(tabnewstart[idx], labY["score"]+20*maxi/600,
                         tabtexts[idx], fontsize=8)
                # ------ print vertical line / span changed ---------
                # ax.axvline(tabnewstart[idx])
            else:
                ax1.text(tabnewstart[idx], labY["score"]+40*maxi/600,
                         tabtexts[idx], fontsize=8)
            prev_typ = tabnewstart_typ[idx]
        """
        # =====================================================================
        plt.suptitle(titre, fontsize=12, y=0.95)
        plt.xlabel("nb runs", fontsize=11)
        plt.ylabel("Nb filled boxes", fontsize=11)
        # plt.legend(loc=0, fontsize=18)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        ax1.set_ylim(0, max_score*1.1)

        # =======================   plot the legend   =========================
        # Here we create a legend:
        # we'll plot empty lists with the desired size and label
        # for typ in ["rdparam", "GEPrand", "CMAE"]:
        ax1.scatter([], [], c='green', alpha=0.3, label=str("rdparam"))
        ax1.scatter([], [], c='yellow', alpha=0.3, label=str("GEPrand"))
        ax1.scatter([], [], c='red', alpha=0.3, label=str("CMAE"))
        ax1.legend(shadow=True, facecolor='white', framealpha=1, borderpad=1,
                   scatterpoints=1, frameon=False,
                   labelspacing=1, loc=1, bbox_to_anchor=(1.11, 0.8),
                   title='', fontsize=10)

        # ===================  plots the density evolution ====================
        # ax2 = fig.add_subplot(312)
        ax2 = fig.add_subplot(grid[1, :3])
        ax2.plot(score_evol_df[:]["nb_runs"],
                 score_evol_df[:]["density"], color="g")
        plt.suptitle(titre, fontsize=12, y=0.95)
        plt.xlabel("nb runs", fontsize=11)
        plt.ylabel("Density", fontsize=11)
        # plt.legend(loc=0, fontsize=18)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        ax2.set_ylim(0, max_density*1.1)

        #  ===================== plots the behavior map =======================
        behavs_cues = df_bhvremain[df_bhvremain.columns[behav_col]]
        rel_behavs_cues = behavs_cues/[self.scale_x, self.scale_y]
        nameX = rel_behavs_cues.columns[0]
        nameY = rel_behavs_cues.columns[1]
        valX = rel_behavs_cues[nameX]
        valY = rel_behavs_cues[nameY]
        max_x_bhv = df_bhvremain[df_bhvremain.columns[behav_col[0]]].max()
        max_x_bhv_rel = max_x_bhv / self.scale_x
        max_y_bhv = df_bhvremain[df_bhvremain.columns[behav_col[1]]].max()
        max_y_bhv_rel = max_y_bhv / self.scale_y
        max_x = float(int(max_x_bhv_rel*10)+1)/10
        max_y = float(int(max_y_bhv_rel*10)+1)/10
        bhv_xmin = 0
        bhv_xmax = max_x
        bhv_ymin = 0
        bhv_ymax = max_y
        if self.scale_x == 1:
            labelnamex = nameX
        else:
            labelnamex = nameX + " (x{})".format(1.0/self.scale_x)
        if self.scale_y == 1:
            labelnamey = nameY
        else:
            labelnamey = nameY + " (x{})".format(1.0/self.scale_y)
        # figure, ax = plt.subplots(figsize=(7, 7))
        # figure, ax = plt.subplots()
        # ax3 = fig.add_subplot(337)
        ax3 = fig.add_subplot(grid[2, 0])
        # ---------------------------------------------------
        ax3.scatter(valX, valY, marker='o', s=4, c="r")
        # ---------------------------------------------------
        ax3.set_xlabel(labelnamex, fontsize=11)
        ax3.set_ylabel(labelnamey, fontsize=11)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        ax3.set_axisbelow(True)
        ax3.set_xlim(bhv_xmin, bhv_xmax)
        ax3.set_ylim(bhv_ymin, bhv_ymax)
        ax3.grid(linestyle='-', linewidth='0.5', color='green')
        # =====================================================================
        """
        #  =================== plots the parameter maps =======================
        axpar = []
        nbpargraphs = len(listDicGraphs)
        nblines = int(float(nbpargraphs+1)/3)
        if nbpargraphs % 3 > 0:
            nblines += 1
            row = 0
            line = 2
        for pargr in range(nbpargraphs):
            xmin = -1
            xmax = 1
            ymin = -1
            ymax = 1
            row = row + 1
            if row > 2:
                row = 0
                line = line + 1
            # axpar.append(fig.add_subplot(3, nblines+1, 8+pargr))
            axpar.append(fig.add_subplot(grid[line, row]))
            namex = listDicGraphs[pargr]["abscissa"]
            namey = listDicGraphs[pargr]["ordinate"]
            parx = xparNameDict[namex[0]]
            pary = xparNameDict[namey[0]]
            dflist_x = df_parremain[optSet.xparName[parx]]
            dflist_y = df_parremain[optSet.xparName[pary]]
            if dflist_x.max() > xmax:
                xmax = dflist_x.max()
            if dflist_x.min() < xmin:
                xmin = dflist_x.min()
            if (dflist_y.max() > ymax) or dflist_y.min() < ymin:
                if dflist_y.max() - dflist_y.min() < 2:
                    ymax = (dflist_y.max() + dflist_y.min())/2 + 1
                    ymin = (dflist_y.max() + dflist_y.min())/2 - 1
            if dflist_y.min() < ymin:
                ymin = dflist_y.min()

            print(namex[0], parx, namey[0], pary)
            axpar[pargr].scatter(list(dflist_x), list(dflist_y),
                                 marker='o', s=4, c="b")
            axpar[pargr].set_xlabel(namex[0], fontsize=11)
            axpar[pargr].set_ylabel(namey[0], fontsize=11)
            plt.xticks(fontsize=10)
            plt.yticks(fontsize=10)
            axpar[pargr].set_axisbelow(True)

            # xmin = -4
            # xmax = 2
            # ymin = -3
            # ymax = 3

            axpar[pargr].set_xlim(xmin, xmax)
            axpar[pargr].set_ylim(ymin, ymax)
            axpar[pargr].grid(linestyle='-', linewidth='0.5', color='gray')
        # =====================================================================
        """
        plt.savefig(os.path.join(graph_path, baseName + '.pdf'))
        plt.savefig(os.path.join(graph_path, baseName + '.eps'))
        plt.show()

    def rand_goal_method(self):
        """
        """
        print("distance to random goals in behaviour space")

    def closeIt(self):
        """
        doc string
        """
        self.GUI_Gr_obj.close_otherwin()
        self.close()





#   TODO
class Graph_Setting(QtWidgets.QDialog):   # top-level widget to hold everything
    def __init__(self, listpar, listbhv, df, GUI_Gr_obj, parent=None):
        super(Graph_Setting, self).__init__(parent)
        self.GUI_Gr_obj = GUI_Gr_obj
        self.df = df
        self.listpar = listpar
        self.listbhv = listbhv
        self.resize(300, 280)
        # Create some widgets to be placed inside
        """
        self.show_par_clusters_btn = QtWidgets.QPushButton('analyze param cluster')
        self.show_par_clusters_btn.clicked.connect(self.create_param_wins)
        """
        # self.choose_var_btn = QtWidgets.QPushButton('choose variables to plot')
        # self.choose_var_btn.clicked.connect(self.choose_variables_to_plot)
        self.set_bhv_limits_btn = QtWidgets.QPushButton('select bhv in limits')
        self.set_bhv_limits_btn.clicked.connect(self.set_bhv_limits)
        self.run_selected_btn = QtWidgets.QPushButton(
            'Run and Build charts of selected bhv')
        self.run_selected_btn.clicked.connect(self.chartgraph_selected_bhv)
        self.make_graphs_btn = QtWidgets.QPushButton("make graph'series")
        self.make_graphs_btn.clicked.connect(self.make_graphs_series)
        self.make_single_graph_btn = QtWidgets.QPushButton('make single graph')
        self.make_single_graph_btn.clicked.connect(self.make_single_graph)
        self.make_matrix_graph_btn = QtWidgets.QPushButton('make matrix graph')
        self.make_matrix_graph_btn.clicked.connect(self.make_matrix_graph)
        self.make_3d_graph_btn = QtWidgets.QPushButton('make 3d graph')
        self.make_3d_graph_btn.clicked.connect(self.make_3d_graph)

        self.btn_quit = QtWidgets.QPushButton('QUIT')
        self.btn_quit.clicked.connect(self.closeIt)

        if self.df is not None:
            self.run_selected_btn.setEnabled(False)
        """
        buttonLayout1 = QtWidgets.QHBoxLayout()
        self.check1 = QtWidgets.QCheckBox("Checkbox1")
        self.check1.setChecked(True)
        self.check1.stateChanged.connect(lambda: self.btnstate(self.check1))
        # check1.setText("Checkbox 1")
        spacerItem = QtWidgets.QSpacerItem(40, 20,
                                       QtWidgets.QSizePolicy.Expanding,
                                       QtWidgets.QSizePolicy.Minimum)
        self.check2 = QtWidgets.QCheckBox("Checkbox2")
        # self.check2.setChecked(True)
        self.check2.stateChanged.connect(lambda: self.btnstate(self.check2))
        # check2.setText("Checkbox 2")
        
        self.bg = QtWidgets.QButtonGroup()
        self.bg.addButton(self.check1, 1)
        self.bg.addButton(self.check2, 2)
        self.bg.buttonClicked[QtWidgets.QAbstractButton].connect(self.btngroup)
        
        # ------------------------------------------------
        buttonLayout1.addWidget(self.check1)
        buttonLayout1.addItem(spacerItem)    # allows line expansion
        buttonLayout1.addWidget(self.check2)
        # ------------------------------------------------
        """
        # text = QtWidgets.QLineEdit('enter text')
        self.listw = QtWidgets.QListWidget()
        # self.plot = pg.PlotWidget()
        # self.gl3d = gl.GLViewWidget()

        # Create a grid layout to manage the widgets size and position
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)
        # layout = QtWidgets..QVBoxLayout()

        # Add widgets to the layout in their proper positions
        # layout.addWidget(self.plot_density_btn, 0, 0)   # goes 1st row-left
        # layout.addWidget(self.show_par_clusters_btn, 1, 0)
        layout.addWidget(self.set_bhv_limits_btn, 2, 0)     # 3rd row-left
        layout.addWidget(self.run_selected_btn, 3, 0)       # 4th row-left
        # layout.addWidget(self.choose_var_btn, 3, 0)
        layout.addWidget(self.make_graphs_btn, 5, 0)
        layout.addWidget(self.make_single_graph_btn, 6, 0)
        layout.addWidget(self.make_matrix_graph_btn, 7, 0)
        layout.addWidget(self.make_3d_graph_btn, 8, 0)
        """
        layout.addLayout(buttonLayout1, 8, 0, 1, 1)
        """
        layout.addWidget(self.btn_quit, 9, 0)      # goes in bottom(3)-left
        # layout.addWidget(self.plot, 0, 1, 3, 1)  # plot goes on right side,
        #                                          # spanning 3 rows
        if self.df is None:
            self.setWindowTitle("Global df (par and bhv) analysis")
        else:
            self.setWindowTitle("Global chart df (bhv, par and neur) analysis")
        self.to_init()

    def screen_loc(self, xshift=0, yshift=0):
        ag = QtWidgets.QDesktopWidget().availableGeometry()
        # sg = QtWidgets.QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = ag.width() - widget.width() - xshift
        y = ag.height() - widget.height() - yshift
        self.move(x, y)

    def to_init(self):
        # self=MyWin.graph_settings
        self.rootdir = ""
        self.scale_x = self.GUI_Gr_obj.scale_x
        self.scale_y = self.GUI_Gr_obj.scale_y
        self.behav_col = self.GUI_Gr_obj.behav_col
        self.bhv_names = self.GUI_Gr_obj.bhv_names
        xmin = self.GUI_Gr_obj.xmin
        xmax = self.GUI_Gr_obj.xmax
        ymin = self.GUI_Gr_obj.ymin
        ymax = self.GUI_Gr_obj.ymax

        #xmin = 0
        #xmax = 120
        #ymin = 0
        #ymax = 450

        bhv_names = self.GUI_Gr_obj.bhv_names
        # print(self.GUI_Gr_obj)
        # print(bhv_names)
        x_axis_bhv_name = bhv_names[self.GUI_Gr_obj.behav_col[0]]
        y_axis_bhv_name = bhv_names[self.GUI_Gr_obj.behav_col[1]]
        print("x_axis_bhv_name : ", x_axis_bhv_name)
        print("y_axis_bhv_name : ", y_axis_bhv_name)
        inf_x_axis_key = "{}.min".format(x_axis_bhv_name)
        sup_x_axis_key = "{}.max".format(x_axis_bhv_name)
        inf_y_axis_key = "{}.min".format(y_axis_bhv_name)
        sup_y_axis_key = "{}.max".format(y_axis_bhv_name)
        self.limits = [inf_x_axis_key, sup_x_axis_key,
                       inf_y_axis_key, sup_y_axis_key]
        print("bhv_set keys (=self.items)", self.limits)

        self.listDic_bhv_lim_val = [{inf_x_axis_key:  xmin,
                                     sup_x_axis_key:  xmax,
                                     inf_y_axis_key:  ymin,
                                     sup_y_axis_key:  ymax}]
        self.listDicLimits_bhv = [{'bhv_limits': [inf_x_axis_key,
                                                  sup_x_axis_key,
                                                  inf_y_axis_key,
                                                  sup_y_axis_key]}]
        self.listDicSelectedPar = [{'parameters': []}]
        self.selected_par = []
        self.listDicSelectedPar2 = [{'parameters': []}, {'factor': []}]
        self.selected_par2 = []
        self.selected_factorpar = []

        self.listDicSelectedBhv = [{'behaviours': []}]
        self.selected_bhv = []
        self.listDicSelectedBhv2 = [{'behaviours': []}, {'factor': []}]
        self.selected_bhv2 = []
        self.selected_factorbhv = []
        
        self.listDicSelectedNeurAct = [{'neural activities': []}]
        self.selected_neurAct = []
        self.listDicSelectedNeurAct2 = [{'neural activities': []},
                                        {'factor': []}]
        self.selected_neurAct2 = []
        self.selected_factoNeurAct = []
        
        self.listDicSelSingleCol = [{'selectedCol': []}]
        self.listDicSelCols = [{'selectedCols': []}]
        self.lstDicSelcXY = [{'X': [], "Y": []}]
        self.lstDicSelcXYZ = [{'X': [], "Y": [],  "Z": []}]
        self.selected_factor = []
        self.selected_two = []
        self.selected_three = []
        self.selectedCols = []
        
        if self.df is not None:
            # self.set_bhv_limits()
            self.df_glob = self.df
            self.index = list(self.df["rg_in_whole"])
            # self.GUI_Gr_obj.df_glob = self.df_glob


    """
    def btnstate(self, b):
        if b.text() == "Checkbox1":
            if b.isChecked() is True:
                print(b.text() + " Do its stuff")
            else:
                print(b.text() + " is deselected")

        if b.text() == "Checkbox2":
            if b.isChecked() is True:
                print(b.text() + " Do its stuff")
            else:
                print(b.text() + " is deselected")

    def btngroup(self, btn):
        print(btn.text() + " is selected")
        if btn.text() == "Checkbox1":
            print(btn.text() + " Do its stuff -> action 1")
        else:
            print(btn.text() + " Do its stuff -> action 2")
    """
    def affich(self):
        x = np.random.normal(size=1000)
        y = np.random.normal(size=1000)
        self.plot.plot(x, y, pen=10)

    """
    def create_param_wins(self):
        self.GUI_Gr_obj.mafen.showAllParGraphs()
        print self.GUI_Gr_obj.mafen.listDicGraphs
        # ============  re-draw bhv and param windows =============
        rep2 = self.GUI_Gr_obj.restrain_to_bhv_set()
        self.GUI_Gr_obj.df_glob, self.GUI_Gr_obj.ss_titre = rep2
    """

    def set_bhv_limits(self):
        """
        Call ChooseInList() to change behaviour limit values.
        If the "unselect all" key is pressed, then come back to original
        limits (i.e. all bhv data are selected)
        bhv limits are stored in bhv_set
        """
        listChoix = list(self.listDicLimits_bhv[0].keys())
        if verbose > 2:
            print(self.listDicLimits_bhv)
            print(self.limits)
            print(self.listDic_bhv_lim_val)
            print(listChoix)
        titleText = "set min/max values for bhv_graph"
        rep = ChooseInList.listTransmit(parent=None,
                                        graphNo=0,
                                        listChoix=listChoix,
                                        items=self.limits,
                                        listDicItems=self.listDicLimits_bhv,
                                        onePerCol=[0],
                                        colNames=["bhv_limits", "Value"],
                                        dicValues=self.listDic_bhv_lim_val[0],
                                        typ="val",
                                        titleText=titleText)

        self.listDicLimits_bhv = rep[0]
        if rep[1] == {}:
            print("Set limits back to original")
            self.to_init()
            self.bhv_set = self.listDic_bhv_lim_val[0]
        else:
            self.listbhv_limit_names = []
            self.bhv_set = rep[1]
            if verbose > 2:
                print("rep[1]", rep[1])
            for i in range(len(self.listDicLimits_bhv[0][listChoix[0]])):
                itemName = self.listDicLimits_bhv[0][listChoix[0]][i]
                self.listbhv_limit_names.append(itemName)
                self.listDic_bhv_lim_val[0][itemName] = float(rep[1][itemName])
                print(itemName, rep[1][itemName])
        if verbose > 2:
            print("self.listDicLimits_bhv", self.listDicLimits_bhv)
            print("bhv_set: ", self.bhv_set)
        self.GUI_Gr_obj.bhv_set = self.bhv_set

        # ========  adjust df_glob and plot bhv_win   ===========
        rep2 = self.restrain_to_bhv_set()
        self.GUI_Gr_obj.df_glob, self.GUI_Gr_obj.ss_titre = rep2
        namex = self.GUI_Gr_obj.bhv_names[self.GUI_Gr_obj.behav_col[0]]
        namey = self.GUI_Gr_obj.bhv_names[self.GUI_Gr_obj.behav_col[1]]
        self.GUI_Gr_obj.bhv_ymin = float(self.bhv_set[namey + ".min"])
        self.GUI_Gr_obj.bhv_ymax = float(self.bhv_set[namey + ".max"])
        self.GUI_Gr_obj.bhv_xmin = float(self.bhv_set[namex + ".min"])
        self.GUI_Gr_obj.bhv_xmax = float(self.bhv_set[namex + ".max"])

        """
        bhv_set = {'endangle.min': 0, 'endangle.max': 100,
                   "dur_mvt2.min": 0.100, "dur_mvt2.max": 1.400}
        """

    def restrain_to_bhv_set(self):
        """
        Select bhV that are in the limits of bhv_set.
        If self.df is None :
            Uses the indexes of those bhv data (df_bhvremain) to also select
            corresponding parameters (df_parremain). Then uses these new
            df_bhvremain and df_parremain to build the new df_glob (with a
            call to extract_new_df function). Finally re-plots the selected
            parameters in param windows.
        If self.df is not None (call to Graph_Setting included chart_df_glob):
            directly restrict a copy of df to the limits of bhv_set and
            re-plots the selected bhv and param windows.
        """
        df_bhv = copy.deepcopy(self.GUI_Gr_obj.df_bhvremain)
        df_par = copy.deepcopy(self.GUI_Gr_obj.df_parremain)

        # -------   bhv_set is given by Graph_Setting window    ------
        """
        self.bhv_set = {'endangle.min': 0, 'endangle.max': 100,
                        "dur_mvt2.min": 0.100, "dur_mvt2.max": 1.400}
        """

        res = self.GUI_Gr_obj.extract_new_df(df_par, df_bhv,
                                             self.GUI_Gr_obj.bhv_set)
        df_glob, ss_titre = res[0], res[1]
        index = list(df_glob.index)
        if self.df is not None:
            df_glob = self.df.loc[index]
            # index = list(self.df["rg_in_whole"])
        else:
            index = df_glob.index
        """
        self.behav_col = self.GUI_Gr_obj.behav_col
        bhv_xmin = df_bhv[df_bhv.columns[self.behav_col[0]]].min()/self.scale_x
        bhv_xmax = df_bhv[df_bhv.columns[self.behav_col[0]]].max()/self.scale_x
        bhv_ymin = df_bhv[df_bhv.columns[self.behav_col[1]]].min()/self.scale_y
        bhv_ymax = df_bhv[df_bhv.columns[self.behav_col[1]]].max()/self.scale_y
        """
        xmin = float(self.GUI_Gr_obj.bhv_set['endangle.min'])
        xmax = float(self.GUI_Gr_obj.bhv_set['endangle.max'])
        ymin = float(self.GUI_Gr_obj.bhv_set['max_speed.min'])
        ymax = float(self.GUI_Gr_obj.bhv_set['max_speed.max'])

        bhv_xmin = xmin / self.scale_x
        bhv_xmax = xmax / self.scale_x
        bhv_ymin = ymin / self.scale_y
        bhv_ymax = ymax / self.scale_y

        self.GUI_Gr_obj.plot_map_behav(df_bhv.loc[index],
                                       xmin=bhv_xmin, xmax=bhv_xmax,
                                       ymin=bhv_ymin, ymax=bhv_ymax)

        self.GUI_Gr_obj.mafen.df_bhvremain = df_bhv.loc[index]
        self.GUI_Gr_obj.mafen.df_parremain = df_par.loc[index]
        self.GUI_Gr_obj.mafen.source_df_bhvremain = df_bhv.loc[index]
        self.GUI_Gr_obj.mafen.source_df_parremain = df_par.loc[index]
        self.GUI_Gr_obj.mafen.bhvPlot.plot_item.clearPlots()
        """
        self.GUI_Gr_obj.plot_df_bhv(df_bhv.loc[index],
                                    xmin=bhv_xmin*self.scale_x,
                                    xmax=bhv_xmax*self.scale_x,
                                    ymin=bhv_ymin*self.scale_y,
                                    ymax=bhv_ymax*self.scale_y)
        """
        
        self.GUI_Gr_obj.plot_df_bhv(df_bhv.loc[index],
                                    xmin=xmin, xmax=xmax,
                                    ymin=ymin, ymax=ymax)

        self.GUI_Gr_obj.mafen.clearParam()
        self.GUI_Gr_obj.mafen.param_in_blue(df_par.loc[index])
        return df_glob, ss_titre

    def chartgraph_selected_bhv(self):
        """
        """
        df_glob = self.GUI_Gr_obj.df_glob
        NbSelectedBhv = len(df_glob)
        print("{} selected bhv".format(NbSelectedBhv))
        msg = "Save restrained dataframes with graphs?"
        msg2 = "New selection contains {} bhvs".format(NbSelectedBhv)
        ret = MessageBox(None, msg, msg2, 3)

        animatsimdir = self.GUI_Gr_obj.animatsimdir
        print(animatsimdir)
        graph_path = self.GUI_Gr_obj.graph_path
        graph_path = graph_path.replace("\\", "/")
        listdir = os.listdir(graph_path)
        lst_subdir = [sd for sd in listdir
                      if os.path.isdir(graph_path + "/" + sd)]
        ix = 0
        for sdir in lst_subdir:
            if sdir[:4] == "run-":
                ix += 1
        newrundirname = "run" + '-{0:d}'.format(ix)
        new_run_dir = graph_path + "/" + newrundirname
        
        print(ret)
        if ret == 2:
            print("ESC")
        elif ret == 6:
            print("YES --> Saves the bhv, par dataframes of selected data")
        elif ret == 7:
            print("NO: --> Do Not Save restrained dataframes")
        if ret == 6:
            self.new_run_dir = new_run_dir
            self.GUI_Gr_obj.new_run_dir = new_run_dir
            if not os.path.exists(new_run_dir):
                os.makedirs(new_run_dir)
            file_name = self.GUI_Gr_obj.save_bhvpar_df_to_csv()
            self.run_selected_bhv(file_name)

    def run_selected_bhv(self, file_name):
        """
        """
        # self=MyWin.graph_settings
        optSet = self.GUI_Gr_obj.optSet
        gravity = readGravityfromAsim(optSet.model)
        optSet.gravity = gravity

        # ============== get df_parremain from GUI_graph =================
        # the two following commented lines are from restrain_to_bhv_set()
        # self.GUI_Gr_obj.mafen.df_bhvremain = df_bhv.iloc[df_glob.index]
        # self.GUI_Gr_obj.mafen.df_parremain = df_par.iloc[df_glob.index]
        # This means that GEP_GUI has already the good df_parremain
        # In GEP_GUI, the restrained df was saved --> df_glob
        df_parremain = self.GUI_Gr_obj.mafen.df_parremain
        df_bhvremain = self.GUI_Gr_obj.mafen.df_bhvremain
        self.GUI_Gr_obj.mafen.select_df_bhvremain = df_bhvremain
        df_glob = self.GUI_Gr_obj.df_glob
        # lst_valid = self.GUI_Gr_obj.lst_valid
        seeds_selected = list(df_glob.rgserie)
        df_parremain.index = seeds_selected
        df_bhvremain.index = seeds_selected
        nbpar = self.GUI_Gr_obj.mafen.nbpar
        # seeds_selected = list(df_glob.rgserie)
        selected_pairs = []
        old_selected_pairs = []
        for select in seeds_selected:
            print(df_parremain.loc[select][:5])
            rg_pair = int(df_bhvremain.loc[select]["rgserie"])
            print(optSet.pairs[rg_pair][:5])
            old_selected_pairs.append(optSet.pairs[rg_pair])
            selected_pairs.append(np.array(
                df_parremain.loc[select][:nbpar+2]))
            print()
        self.GUI_Gr_obj.mafen.selected_pairs = selected_pairs

        # datastructure = self.GUI_Gr_obj.datastructure
        datastructure = optSet.datastructure
        xCoactPenality = readCoacPenality(datastructure)
        xCoactPenality1, xCoactPenality2 = xCoactPenality
        optSet.xCoactPenality1 = xCoactPenality1
        optSet.xCoactPenality2 = xCoactPenality2
        # rootdir = self.GUI_Gr_obj.rootdir======
        
        # ======== create new_run_dir folder with incremental name ============
        animatsimdir = self.GUI_Gr_obj.animatsimdir
        print(animatsimdir)
        """
        graph_path = self.GUI_Gr_obj.graph_path
        graph_path = graph_path.replace("\\", "/")
        listdir = os.listdir(graph_path)
        lst_subdir = [sd for sd in listdir
                      if os.path.isdir(graph_path + "/" + sd)]
        ix = 0
        for sdir in lst_subdir:
            if sdir[:4] == "run-":
                ix += 1
        newrundirname = "run" + '-{0:d}'.format(ix)
        new_run_dir = graph_path + "/" + newrundirname
        self.GUI_Gr_obj.new_run_dir = new_run_dir
        if not os.path.exists(new_run_dir):
            os.makedirs(new_run_dir)
        """
        new_run_dir = self.new_run_dir
        ficname = "file_name.txt"
        complete_fname = new_run_dir + "/" + ficname
        with open(complete_fname, 'w') as fich:
            fich.write(file_name)
        fich.close()

        list_ext = [".aproj", ".asim", ".aform"]
        copyFileDir_ext(animatsimdir, new_run_dir, list_ext, copy_dir=0)
        aprojSaveDir = new_run_dir + "/AprojFiles"
        copyFileDir(new_run_dir, aprojSaveDir, copy_dir=0)

        # ====== the index of df_glob is used to create seeds_selected =======
        # variable in GEP_GUI. We will use "run_selected_param" from GEP_GUI to
        # run the restrained parameter sets.
        # To do this we copy anmatsimdir to GEP_GUI
        # and we copy new_run_dir to GEP_GUI.newSeedFolder variable
        """
        self.GUI_Gr_obj.mafen.seeds_selected = [lst_valid[sel] \
                                                for sel in seeds_selected]
        """
        self.GUI_Gr_obj.mafen.seeds_selected = seeds_selected
        self.GUI_Gr_obj.mafen.rg_bhv_selected = seeds_selected
        self.GUI_Gr_obj.mafen.animatsimdir = animatsimdir
        self.GUI_Gr_obj.mafen.newDestFolder = new_run_dir
        gepdatadir = new_run_dir + "/GEPdata"
        if not os.path.exists(gepdatadir):
            os.makedirs(gepdatadir)
        # ===================  run selected paramsets ====================
        self.GUI_Gr_obj.mafen.run_selected_param()
        """
        self=MyWin.graph_settings
        for idOK in range(10):
            idx = self.GUI_Gr_obj.lst_valid[idOK]
            print(idOK, idx)
            print(self.GUI_Gr_obj.df_parremain.rgserie[idOK])
            print(self.GUI_Gr_obj.df_parremain.loc[idOK][:5])
            print(self.GUI_Gr_obj.optSet.pairs[idx][:5])
        """
        # ================== make graphs for each selected bhv ============
        chart_glob_name = self.GUI_Gr_obj.mafen.procName + "_chart"
        chartdir = new_run_dir + "/GEPChartFiles"
        resultdir = new_run_dir + "/ResultFiles"
        if not os.path.exists(resultdir):
            os.makedirs(resultdir)
        src = os.path.join(animatsimdir, "ResultFiles")
        dst = os.path.join(new_run_dir, "ResultFiles")
        # copyFile("paramOpt.pkl", src, dst)
        copyFile("template.txt", src, dst)
        copyFileWithExt(src, dst, ".pkl")  
        # templateFileName = resultdir + "/template.txt"
        
        self.GUI_Gr_obj.mafen.seeds_selected = seeds_selected
        self.GUI_Gr_obj.mafen.optSet.spanStim = 5
        self.GUI_Gr_obj.mafen.optSet.spanSyn = 5
        self.GUI_Gr_obj.mafen.saves_newGEPdata(seedDirCreate=False)
        
        for idx in range(len(df_bhvremain)):
            print(idx)
            if idx < 10:
                zero = "0"
            else:
                zero = ""
            dstfile = chart_glob_name + zero + str(idx)
            chartName = dstfile + ".txt"
            self.GUI_Gr_obj.mafen.checkChartComment(chartdir, chartName, idx)
            # graphfromchart(optSet, chartdir, chartName, templateFileName)
            chartFullName = chartdir + "/" + chartName
            try:
                testVarMsePlot(optSet, chartFullName, interval=1./6)
            except Exception as e:
                None
                if verbose > 2:
                    print(e)


    def choose_variables_to_plot(self):
        """
        Select a set of parameter variables and a set of behaviour cues to plot
        par-par scatter plots in which all selected parameters are plotted
        against a single parameter in the selected list,
        and par-bhv plots in which allselected  parameters are plotted against
        a behaviour cue in the selected list
        """
        listChoix = ["parameters"]
        self.items = self.GUI_Gr_obj.par_names
        titleText = "Select paramters for analysis"
        rep = ChooseInList.listTransmit(parent=None,
                                        graphNo=0,
                                        listChoix=listChoix,
                                        items=self.items,
                                        listDicItems=self.listDicSelectedPar,
                                        onePerCol=[0],
                                        colNames=["parameters"],
                                        typ="chk",
                                        titleText=titleText)

        self.listDicSelectedPar = rep[0]
        self.selected_par = self.listDicSelectedPar[0][listChoix[0]]

        listChoix = ["behaviours"]
        bhv_names = self.GUI_Gr_obj.list_bhvVar
        self.items = bhv_names
        # self.items = self.GUI_Gr_obj.bhv_names
        titleText = "Select behaviour cues for analysis"
        rep = ChooseInList.listTransmit(parent=None,
                                        graphNo=0,
                                        listChoix=listChoix,
                                        items=self.items,
                                        listDicItems=self.listDicSelectedBhv,
                                        onePerCol=[0],
                                        colNames=["behaviours"],
                                        typ="chk",
                                        titleText=titleText)

        self.listDicSelectedBhv = rep[0]
        self.selected_bhv = self.listDicSelectedBhv[0][listChoix[0]]

        if self.df is not None:
            listChoix = ["neural activities"]
            neur_act_names =self.GUI_Gr_obj.neur_act_names
            self.items = neur_act_names
            titleText = "Select neural activities for analysis"
            rep = ChooseInList.listTransmit(
                parent=None,
                graphNo=0,
                listChoix=listChoix,
                items=self.items,
                listDicItems=self.listDicSelectedNeurAct,
                onePerCol=[0],
                colNames=["neural activities"],
                typ="chk",
                titleText=titleText)

            self.listDicSelectedNeurAct = rep[0]
            self.selected_neurAct=self.listDicSelectedNeurAct[0][listChoix[0]]
            

        listChoix = ["selectedCol"]
        par_names = self.GUI_Gr_obj.par_names
        if self.df is not None:
            bhv_names = self.GUI_Gr_obj.list_bhvVar \
                      + self.GUI_Gr_obj.neur_act_names
        else:
            bhv_names = self.GUI_Gr_obj.bhv_names
        self.items = bhv_names + par_names
        # self.items = self.selected_par + self.selected_bhv
        titleText = "Select variable displayed as color scale"
        rep = ChooseInList.listTransmit(parent=None,
                                        graphNo=0,
                                        listChoix=listChoix,
                                        items=self.items,
                                        listDicItems=self.listDicSelSingleCol,
                                        onePerCol=[1],
                                        colNames=["selectedCol"],
                                        typ="chk",
                                        titleText=titleText)

        self.listDicSelSingleCol = rep[0]
        self.selected_factor = self.listDicSelSingleCol[0][listChoix[0]]

        # Save var lists to MyWin (= self.GUI_Gr_obj)
        self.GUI_Gr_obj.list_bhv = self.selected_bhv
        self.GUI_Gr_obj.list_par = self.selected_par
        self.GUI_Gr_obj.factor = self.selected_factor[0]
        if self.df is not None:
            self.GUI_Gr_obj.list_neurAct = self.selected_neurAct

    def choose_scatterMatrix_variables(self):
        """
        choose a set of variables (bhv and par) to plor a scatterMattrix.
        Select also a single variale for the color scale
        """
        listChoix = ["selectedCols"]
        par_names = self.GUI_Gr_obj.par_names
        if self.df is not None:
            bhv_names = self.GUI_Gr_obj.list_bhvVar \
                      + self.GUI_Gr_obj.neur_act_names
        else:
            bhv_names =self.GUI_Gr_obj.bhv_names
        self.items = bhv_names + par_names
        # self.items = self.GUI_Gr_obj.par_names + self.GUI_Gr_obj.bhv_names
        titleText = "Select variables for matrix scatter plot"
        rep = ChooseInList.listTransmit(parent=None,
                                        graphNo=0,
                                        listChoix=listChoix,
                                        items=self.items,
                                        listDicItems=self.listDicSelCols,
                                        onePerCol=[0],
                                        colNames=["selectedVars"],
                                        typ="chk",
                                        titleText=titleText)

        self.listDicSelCols = rep[0]
        self.selectedCols = self.listDicSelCols[0][listChoix[0]]

        listChoix = ["selectedCol"]
        par_names = self.GUI_Gr_obj.par_names
        if self.df is not None:
            bhv_names = self.GUI_Gr_obj.list_bhvVar \
                      + self.GUI_Gr_obj.neur_act_names
        else:
            bhv_names =self.GUI_Gr_obj.bhv_names
        self.items = bhv_names + par_names
        # self.items = self.GUI_Gr_obj.par_names + self.GUI_Gr_obj.bhv_names
        titleText = "Select variable displayed as color scale"
        rep = ChooseInList.listTransmit(parent=None,
                                        graphNo=0,
                                        listChoix=listChoix,
                                        items=self.items,
                                        listDicItems=self.listDicSelSingleCol,
                                        onePerCol=[1],
                                        colNames=["selectedColor"],
                                        typ="chk",
                                        titleText=titleText)

        self.listDicSelSingleCol = rep[0]
        self.selected_factor = self.listDicSelSingleCol[0][listChoix[0]]

        # Save var lists to MyWin (= self.GUI_Gr_obj)
        self.GUI_Gr_obj.factor = self.selected_factor[0]
        self.GUI_Gr_obj.selected_col = self.selectedCols



    def choose_two_params(self):
        """
        Choose X and Y variables and variable for color to plot a scatterplot
        """
        par_names = self.GUI_Gr_obj.par_names
        if self.df is not None:
            bhv_names = self.GUI_Gr_obj.list_bhvVar \
                      + self.GUI_Gr_obj.neur_act_names
        else:
            bhv_names =self.GUI_Gr_obj.bhv_names
        self.items = bhv_names + par_names
        # self.items = self.GUI_Gr_obj.par_names + self.GUI_Gr_obj.bhv_names
        listChoix = ["X", "Y"]
        titleText = "Select two variables for plot"
        while ((self.lstDicSelcXY[0][listChoix[0]] == [])
               or (self.lstDicSelcXY[0][listChoix[1]] == [])
               or (self.first_time)):
            rep = ChooseInList.listTransmit(parent=None,
                                            graphNo=0,
                                            listChoix=listChoix,
                                            items=self.items,
                                            listDicItems=self.lstDicSelcXY,
                                            onePerCol=[1, 1],
                                            colNames=["X", "Y"],
                                            typ="chk",
                                            titleText=titleText)
            print(rep)
            self.lstDicSelcXY = rep[0]
            print(self.lstDicSelcXY)
            self.first_time = False

        varX = self.lstDicSelcXY[0][listChoix[0]][0]
        varY = self.lstDicSelcXY[0][listChoix[1]][0]
        self.selected_two = [varX, varY]
        print(self.selected_two)

        listChoix = ["selectedCol"]
        par_names = self.GUI_Gr_obj.par_names
        if self.df is not None:
            bhv_names = self.GUI_Gr_obj.list_bhvVar \
                      + self.GUI_Gr_obj.neur_act_names
        else:
            bhv_names =self.GUI_Gr_obj.bhv_names
        self.items = bhv_names + par_names
        # self.items = self.GUI_Gr_obj.par_names + self.GUI_Gr_obj.bhv_names
        titleText = "Select variable displayed as color scale"
        rep = ChooseInList.listTransmit(parent=None,
                                        graphNo=0,
                                        listChoix=listChoix,
                                        items=self.items,
                                        listDicItems=self.listDicSelSingleCol,
                                        onePerCol=[1],
                                        colNames=["behaviours"],
                                        typ="chk",
                                        titleText=titleText)

        self.listDicSelSingleCol = rep[0]
        self.selected_factor = self.listDicSelSingleCol[0][listChoix[0]]

        # Save var lists to MyWin (= self.GUI_Gr_obj)
        self.GUI_Gr_obj.two_selected_var = self.selected_two
        self.GUI_Gr_obj.factor = self.selected_factor[0]

    def choose_factor(self):
        """
        select a variable name in self.df_glob for color scale
        """
        listChoix = ["selectedCol"]
        par_names = self.GUI_Gr_obj.par_names
        if self.df is not None:
            bhv_names = self.GUI_Gr_obj.list_bhvVar \
                      + self.GUI_Gr_obj.neur_act_names
        else:
            bhv_names =self.GUI_Gr_obj.bhv_names
        self.items = bhv_names + par_names
        # self.items = self.GUI_Gr_obj.par_names + self.GUI_Gr_obj.bhv_names
        titleText = "Select variable displayed as color scale"
        rep = ChooseInList.listTransmit(parent=None,
                                        graphNo=0,
                                        listChoix=listChoix,
                                        items=self.items,
                                        listDicItems=self.listDicSelSingleCol,
                                        onePerCol=[1],
                                        colNames=["behaviours"],
                                        typ="chk",
                                        titleText=titleText)

        self.listDicSelSingleCol = rep[0]
        self.selected_factor = self.listDicSelSingleCol[0][listChoix[0]]
        self.GUI_Gr_obj.factor = self.selected_factor[0]

    def choose_three_params(self):
        """
        Choose X Y and Z variables for 3d_plot and variable for color scale
        """
        listChoix = ["X", "Y", "Z"]
        par_names = self.GUI_Gr_obj.par_names
        if self.df is not None:
            bhv_names = self.GUI_Gr_obj.list_bhvVar \
                      + self.GUI_Gr_obj.neur_act_names
        else:
            bhv_names =self.GUI_Gr_obj.bhv_names
        self.items = bhv_names + par_names
        # self.items = self.GUI_Gr_obj.par_names + self.GUI_Gr_obj.bhv_names
        titleText = "Select three variables for plot"
        """
        while ((self.lstDicSelcXYZ[0][listChoix[0]] == [])
               or (self.lstDicSelcXYZ[0][listChoix[1]] == [])
               or (self.lstDicSelcXYZ[0][listChoix[2]] == [])
               or (self.first_time)):
        """
        rep = ChooseInList.listTransmit(parent=None,
                                        graphNo=0,
                                        listChoix=listChoix,
                                        items=self.items,
                                        listDicItems=self.lstDicSelcXYZ,
                                        onePerCol=[1, 1, 1],
                                        colNames=["X", "Y", "Z"],
                                        typ="chk",
                                        titleText=titleText)
        print(rep)
        self.lstDicSelcXYZ = rep[0]
        print(self.lstDicSelcXYZ)
        self.first_time = False

        varX = self.lstDicSelcXYZ[0][listChoix[0]][0]
        varY = self.lstDicSelcXYZ[0][listChoix[1]][0]
        varZ = self.lstDicSelcXYZ[0][listChoix[2]][0]
        self.selected_three = [varX, varY, varZ]
        print(self.selected_three)

        listChoix = ["selectedCol"]
        par_names = self.GUI_Gr_obj.par_names
        if self.df is not None:
            bhv_names = self.GUI_Gr_obj.list_bhvVar \
                      + self.GUI_Gr_obj.neur_act_names
        else:
            bhv_names =self.GUI_Gr_obj.bhv_names
        self.items = bhv_names + par_names
        # self.items = self.GUI_Gr_obj.par_names + self.GUI_Gr_obj.bhv_names
        titleText = "Select variable displayed as color scale"
        rep = ChooseInList.listTransmit(parent=None,
                                        graphNo=0,
                                        listChoix=listChoix,
                                        items=self.items,
                                        listDicItems=self.listDicSelSingleCol,
                                        onePerCol=[1],
                                        colNames=["behaviours"],
                                        typ="chk",
                                        titleText=titleText)

        self.listDicSelSingleCol = rep[0]
        self.selected_factor = self.listDicSelSingleCol[0][listChoix[0]]

        # Save var lists to MyWin (= self.GUI_Gr_obj)
        self.GUI_Gr_obj.three_selected_var = self.selected_three
        self.GUI_Gr_obj.factor = self.selected_factor[0]

    def make_graphs_series(self):
        """
        doc string
        """
        self.choose_variables_to_plot()
        # Launches the plots in MyWin (= self.GUI_Gr_obj)
        if self.selected_factor != []:
            self.GUI_Gr_obj.plot_par_bhv()
            self.GUI_Gr_obj.plot_par_par()
            if self.df is not None:
                self.GUI_Gr_obj.plot_bhv_neur()
                self.GUI_Gr_obj.plot_par_neur()
        else:
            print("Select variables first!!")

    def make_matrix_graph(self):
        self.choose_scatterMatrix_variables()
        self.GUI_Gr_obj.plot_scatterMatrix()

    def make_single_graph(self):
        self.first_time = True
        self.choose_two_params()
        # Launches the plot in MyWin (= self.GUI_Gr_obj)
        self.GUI_Gr_obj.plot_single()

    def make_3d_graph(self):
        self.choose_three_params()
        self.GUI_Gr_obj.plot_3d_graph_with_colorScale()

    def open_paramGraphs(self):
        """
        doc string
        """

    def closeIt(self):
        """
        doc string
        """
        self.GUI_Gr_obj.close_otherwin()
        self.close()


class Ui_GrChart(object):
    def setupUi(self, GUI_Gr):
        self.GUI_Gr = GUI_Gr
        self.GUI_Gr.setObjectName("GUI_Gr")
        self.GUI_Gr.resize(300, 220)
        self.centralwidget = QtWidgets.QWidget(self.GUI_Gr)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        # Create a series of button widgets to be placed inside
        self.make_pardf_bhvdf_btn = \
            QtWidgets.QPushButton("&Make/Analyze (par+bhv) dataframe")
        self.save_pardf_bhvdf_btn = \
            QtWidgets.QPushButton("&save (par+bhv) dataframe to csv")
        self.gr_chart_tcourse_btn = \
            QtWidgets.QPushButton("&Make graph (chart, timeCourse)")
        self.gr_chart_btn = \
            QtWidgets.QPushButton("&Make graphs (chartDir)")
        self.analyze_bhv_neur_par_chart_btn = \
            QtWidgets.QPushButton("&Analyze neurons_activity/bhv from charts")
        self.analyze_triphasic_btn = \
            QtWidgets.QPushButton("&Analyze triphasic")
        self.radar_Button = QtWidgets.QPushButton("&Make Radar from .csv")
        self.GEPgraphMetric_button = QtWidgets.QPushButton("&GEP graphs & Metrics")
        self.quit_Button = QtWidgets.QPushButton("&Quit")

        # Add QHBoxlayout to place the buttons
        buttonLayout1 = QtWidgets.QVBoxLayout()

        # Add widgets to the layout in their proper positions
        buttonLayout1.addWidget(self.make_pardf_bhvdf_btn)
        buttonLayout1.addWidget(self.save_pardf_bhvdf_btn)
        buttonLayout1.addWidget(self.radar_Button)
        buttonLayout1.addWidget(self.gr_chart_tcourse_btn)
        buttonLayout1.addWidget(self.gr_chart_btn)
        buttonLayout1.addWidget(self.analyze_bhv_neur_par_chart_btn)
        buttonLayout1.addWidget(self.analyze_triphasic_btn)
        buttonLayout1.addWidget(self.GEPgraphMetric_button)

        buttonLayout1.addWidget(self.quit_Button)

        self.gridLayout.addLayout(buttonLayout1, 0, 1)

        self.GUI_Gr.setCentralWidget(self.centralwidget)
        self.setLayout(self.gridLayout)
        self.setWindowTitle("Data Analysis")
        QtCore.QMetaObject.connectSlotsByName(self.GUI_Gr)


#   TODO    to be Finished..
class GUI_Graph(QtWidgets.QMainWindow, Ui_GrChart):
    def __init__(self):
        super(GUI_Graph, self).__init__()
        self.setupUi(self)      # le 2eme self est pour l'argument GUI_Graph
        #                       qui est la fenetre elle-meme -> donc self
        self.to_init()
        self.show()

    def screen_loc(self, xshift=0, yshift=0):
        ag = QtWidgets.QDesktopWidget().availableGeometry()
        # sg = QtWidgets.QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = ag.width() - widget.width() - xshift
        # y = 2 * ag.height() - sg.height() - widget.height()
        y = ag.height() - widget.height() - yshift
        self.move(x, y+1)

    def to_init(self):
        self.rootdir = ""
        self.graph_path = ""
        self.ensembleRunDir = ""
        self.mydir = ""
        self.fname = ""
        self.prevListColNames = []
        self.prevListAngles = []
        self.prevListConsts = []
        self.prevListTrials = []
        self.prevListParams = []
        self.prevLstPltColNames = []
        self.prevLsAnglesDur_dir = []
        self.prevLstConstVal_dir = []
        self.prevLstPltTrials = []
        self.prevLstPltParams = []
        self.ordered_par_columns = None
        self.n_rows = 0
        self.strtTime = 0
        self.endTime = 10
        self.strtMvt = 5
        self.endMvt = 5.8

        self.listFold = []
        self.prevListFolders = []
        self.listFoldersNbBhv7 = []
        self.listGEPFolders = []
        self.singleDirectory = ""

        self.listGEPFiles = []
        self.prevListGEPFiles = []

        self.bhv_names = ["mse", "coactpen", "startangle", "endangle",
                          "oscil1", "oscil2", "max_speed", "end_mvt2",
                          "dur_mvt2", "varmse"]

        self.df_bhvremain = None
        self.df_parremain = None
        self.dic_df_origine = {}
        self.listAngle = []
        self.listConst = []
        self.listTrial = []
        self.list_constVal = []
        self.stimParName = []
        self.synParName = []
        self.synNSParName = []
        self.synFRParName = []
        self.par_names = []
        self.best_xparVals = []

        self.optSet = None
        self.mafen = None
        self.df_glob = None
        self.list_bhv = []
        self.list_par = []
        self.listY = []
        self.listX = []
        self.factor = None
        self.ss_titre = ""
        self.behav_col = None
        self.original_limits = None

        """
        self.xmin = 0
        self.xmax = 100
        self.ymin = 0
        self.ymax = 1.5
        """
        self.two_selected_var = []
        self.three_selected_var = []
        self.selected_col = []
        self.select_3_col = []
        self.make_pardf_bhvdf_btn.clicked.connect(self.build_analyze_bhvpar_df)
        self.save_pardf_bhvdf_btn.clicked.connect(self.save_bhvpar_df_to_csv)
        self.gr_chart_tcourse_btn.clicked.connect(self.makegr_chart_tcourse)
        self.gr_chart_btn.clicked.connect(self.make_all_chart)
        self.analyze_bhv_neur_par_chart_btn.clicked.connect(
            self.analyze_bhv_neur_par_chart)
        self.analyze_triphasic_btn.clicked.connect(self.analyze_triphasic)
        self.radar_Button.clicked.connect(self.make_radar_from_csv)
        self.GEPgraphMetric_button.clicked.connect(self.graphMetrics_GEP)

        self.quit_Button.clicked.connect(self.closeIt)

        self.allfiletypes = "All Files (*);;Text Files (*.txt, *.asc, *.par)"
        self.initialfiletypes = "Text Files (*.txt, *.asc, *.par)"
        # nameLabel = QtWidgets.QLabel("Name:")
        # self.nameLine = QtWidgets.QLineEdit()

        self.datastructure = {}
        # self.show()

    def actualize_mafen(self, GEP_GUI_win, aprojFicName, optSet):
        if GEP_GUI_win is None:
            self.mafen = MaFenetre(aprojFicName, optSet)
            self.mafen.hide()
            self.mafen.bhvPlot.hide()
            self.mafen.mvtPlot.hide()
            self.mafen.main_mode = False
        else:
            self.mafen = GEP_GUI_win
            self.mafen.optSet = optSet
        self.mafen.df_parremain = self.df_parremain
        # self.mafen.showAllParGraphs()
        # print self.mafen.listDicGraphs
        list_elem = ["duration", "maxSpeed"]
        typ = "ordinate"
        title = "Choose ordinate for bhv Window"
        behav_ord = choose_one_element_in_list(title, list_elem, typ)
        if behav_ord == "duration":
            self.mafen.chkBx_bhv_duration.setChecked(True)
            self.mafen.chkBx_bhv_maxSpeed.setChecked(False)
            self.mafen.mvt_ord_duration = 1
            self.mafen.mvt_ord_maxSpeed = 0
        else:
            self.mafen.chkBx_bhv_duration.setChecked(False)
            self.mafen.chkBx_bhv_maxSpeed.setChecked(True)
            self.mafen.mvt_ord_duration = 0
            self.mafen.mvt_ord_maxSpeed = 1
        self.mafen.configureforbhvcriteria()

    def plot_df_bhv(self, df_bhvremain, xmin=0, xmax=1,
                    ymin=0, ymax=1.5):
        listcolors = []
        for i in range(20):
            listcolors.append(pg.intColor(i, 6, maxValue=128))
        color = listcolors[0]
        behav_val_array = np.array(df_bhvremain)[:, self.behav_col]
        self.mafen.bhvPlot.plot_item.setXRange(xmin, xmax)
        self.mafen.bhvPlot.plot_item.setYRange(ymin, ymax)
        self.mafen.bhvPlot.plot_item.plot(behav_val_array[:, 0],
                                          behav_val_array[:, 1],
                                          pen=None, symbol='o',
                                          symbolBrush=color)
        self.mafen.bhvPlot.show()
        # ==============================================================
        QtWidgets.QApplication.processEvents()
        # ==============================================================

    def plot_mvt(self, xmin=0, xmax=10, ymin=0, ymax=150):
        self.mafen.mvtPlot.pw_mvt.setXRange(xmin, xmax)
        self.mafen.mvtPlot.pw_mvt.setYRange(ymin, ymax)
        self.mvtTemplate = np.array(self.optSet.mvtTemplate)
        self.mafen.mvtPlot.pw_mvt.plot(self.mvtTemplate[:, 1],
                                       self.mvtTemplate[:, 2],
                                       pen='k')
        # self.mafen.plotmvt(self, chart)
        self.mafen.mvtPlot.show()
        # ==============================================================
        QtWidgets.QApplication.processEvents()
        # ==============================================================

    def build_analyze_bhvpar_df(self):
        self.close_otherwin()
        """
        ret = 7
        df_bhvremain = self.GUI_Gr_obj.df_bhvremain
        if df_bhvremain is not None:
            msg = "A previous dataframe is present \n Use Same dataframe?"
            ret = MessageBox(None, msg, 'Previous dataframe detected', 3)
            print ret
            if ret == 2:
                print "ESC"
            elif ret == 6:
                print "YES --> Keep the previous dataframe"
                print "df_bhvremain size : {}\n".format(len(df_bhvremain))
            elif ret == 7:
                print "NO: --> Look for another dierctory"
        if ret == 7:
            self.make_bhvpardf_bhvparwins()
        """
        self.make_bhvpardf_bhvparwins()
        listpar = self.par_names
        listbhv = self.bhv_names
        # =====================================================================
        self.graph_settings = Graph_Setting(listpar, listbhv, None, self)
        self.graph_settings.show()

        # ========= positionning the Graph_Setting window on screen ===========
        sg = QtWidgets.QDesktopWidget().screenGeometry()
        mywin_height = self.geometry().height()
        graphSet_height = self.graph_settings.geometry().height()
        # graphSet_width = self.graph_settings.geometry().width()
        xshift = 10
        yshift = sg.height() - graphSet_height - mywin_height - 40
        self.graph_settings.screen_loc(xshift=xshift, yshift=yshift)
        # =====================================================================

    def make_bhvpardf_bhvparwins(self):
        """
        Builds behavior and prameter dataframes (df_parremain and
        df_bhvrelmain)
        shows the param graphs
        shows the bhv graph
        """
        ret = self.make_bhvpardf()
        df_parremain = self.df_parremain
        df_bhvremain = self.df_bhvremain
        """
        behav_col = self.behav_col
        max_x_bhv = df_bhvremain[df_bhvremain.columns[behav_col[0]]].max()
        max_x_bhv_rel = max_x_bhv / self.scale_x
        max_y_bhv = df_bhvremain[df_bhvremain.columns[behav_col[1]]].max()
        max_y_bhv_rel = max_y_bhv / self.scale_y
        max_x = float(int(max_x_bhv_rel*10)+1)/10
        max_y = float(int(max_y_bhv_rel*10)+1)/10
        bhv_xmin = 0
        bhv_xmax = max_x
        bhv_ymin = 0
        bhv_ymax = max_y
        """
        bhv_xmin = self.bhv_xmin
        bhv_xmax = self.bhv_xmax
        bhv_ymin = self.bhv_ymin
        bhv_ymax = self.bhv_ymax
        self.makes_bhvpar_windows(df_bhvremain, df_parremain,
                                  bhv_xmin, bhv_xmax, bhv_ymin, bhv_ymax)
        return ret

    def make_bhvpardf(self):
        ret = 7
        df_bhvremain = self.df_bhvremain
        if df_bhvremain is not None:
            msg = "A previous dataframe is present \n Use Same dataframe?"
            ret = MessageBox(None, msg, 'Previous dataframe detected', 3)
            print(ret)
            if ret == 2:
                print("ESC")
            elif ret == 6:
                print("YES --> Keep the previous dataframe")
                print("df_bhvremain size : {}\n".format(len(df_bhvremain)))
            elif ret == 7:
                print("NO: --> Look for another dierctory")
        if ret == 7:
            self.build_newdf()
        return ret
    
    
    def build_bhv_par_df(self, idx, gepdataFold, parName, bhvName,
                         concatpairs, concatbehavs, lst_lenTab,
                         lst_df_parremain, lst_df_bhvremain):

        tab_par = readTablo(gepdataFold, parName)
        tab_par = np.array(tab_par)
        tab_bhv = readTablo(gepdataFold, bhvName)
        tab_bhv = np.array(tab_bhv)
        lst_lenTab. append(len(tab_par))
        print(gepdataFold, end=" ")
        if tab_par[0][-1] != 0.0:   # last column must be 0, 1, 2...., n
            # nbparfromtab = len(tab[0]) - 2
            pairs = np.array(tab_par[:, :])
        else:
            # nbparfromtab = len(tab[0]) - 2 - 1
            pairs = np.array(tab_par[:, 0:-1])
            behavs = np.array(tab_bhv[:, 0:-1])
            print("nbcol in pairs : {}".format(len(pairs[0])), end=" ")
            print("nbcol in behavs : {}".format(len(behavs[0])))
            # print(concatpairs)
            # print(pairs[0])
            if concatpairs[0][0] != 0:
                concatpairs = np.concatenate((concatpairs, pairs))
                concatbehavs = np.concatenate((concatbehavs, behavs))
            else:
                concatpairs = pairs
                concatbehavs =behavs
            start = 0
            end = len(tab_bhv)
            # =============================================================
            res = self.selctValidBehav(behavs, pairs, start, end,
                                       stangl=0, st_err=1,
                                       minampl=10,
                                       max_coactpenalty=0.01)
            (df_bhvOK, df_parOK) = res
            # creates a new column with the idx value og the origine df
            origine = np.ones(len(df_bhvOK))*idx
            df_bhvOK.loc[:, 'origine'] = origine
            df_parOK.loc[:, 'origine'] = origine
            # =============================================================
            default = True
            mseThr = 1
            lst_df_bhvremain.append(copy.deepcopy(df_bhvOK))
            lst_df_parremain.append(copy.deepcopy(df_parOK))
            varmse_OK = lst_df_bhvremain[idx]['varmse'] <= mseThr
            lst_df_bhvremain[idx] = lst_df_bhvremain[idx][varmse_OK]
            lst_df_parremain[idx] = lst_df_parremain[idx][varmse_OK]
            if default is True:
                bhvframes = [self.df_bhvremain, lst_df_bhvremain[idx]]
                self.df_bhvremain = pd.concat(bhvframes)
                parframes = [self.df_parremain, lst_df_parremain[idx]]
                self.df_parremain = pd.concat(parframes)
                self.dic_df_origine[idx] = gepdataFold
        return (concatpairs, concatbehavs,
                lst_df_parremain, lst_df_bhvremain, lst_lenTab)

    def build_newdf(self):
        """
        From a selected directory, reads all subdirectories and allows to
        select the ones to be included in the process.
        Finds all "GEPdata" folders in subdirectories (whatever the level).
        Takes GEPdata00bhv.txt file present in each "GEPdata" folder to
        build a dataframe only if nb of columns == 10.
        Takes only data with a varmse < 1.
        Dataframes are appended in a list of dataframes (df_bhvremain[idx]). A
        global dataframe is built with a new last column indicating the origin
        (integers) of the appended dataframe (self.df_bhvremain).
        The same is made with GEPdata00.txt for the  df_parremain[idx] and a
        global dataframe self.df_parremain.
        """
        self.explore_subfolders()
        nb_folders = len(self.listGEPFolders)
        self.read_GEPdata_infos()
        self.construct_df_par_bhv_remains()


    def explore_subfolders(self):
        """
        From a selected directory, reads all subdirectories and allows to
        select the ones to be included in the process
        Actualize
            self.one_expe = one_expe
            self.directory = directory
            self.listOfSearchedDir = listOfSearchedDir 
        """

        self.original_limits = None
        one_expe = False    # indicates if only one experiment is analyzed
        text = "Pick the Root Folder containing directories you want to select"
        self.ensembleRunDir = QtWidgets.QFileDialog.\
            getExistingDirectory(self, text, self.rootdir)
        self.rootdir = os.path.split(self.ensembleRunDir)[0]
        print(self.ensembleRunDir)
        listOfSearchedDir = find_a_file(rootdir=self.ensembleRunDir,
                                        fileName="GEPdata00.par")
        self.listGEPFolders = []
        self.listFold = []
        if len(listOfSearchedDir) == 1:
            singleGEPdataRep = listOfSearchedDir[0]
            directory = os.path.split(singleGEPdataRep)[0]
            # directory = singleGEPdataRep
            if directory == self.ensembleRunDir:
                singleDirectory = directory
                print("Only One Experiment chosen:", singleDirectory)
                one_expe = True
                self.listGEPFolders = listOfSearchedDir
                gepdataFold = self.listGEPFolders[0]
                animatsimdir = os.path.split(gepdataFold)[0]
                self.graph_path = animatsimdir + "/graphs"

        if not one_expe:
            self.prevListGEPFiles = ["GEPdata00.par"]
            for rep in listOfSearchedDir:
                directory = os.path.split(rep)[0]
                # print(directory[len(self.ensembleRunDir)+1:])
                self.listFold.append(directory[len(self.ensembleRunDir)+1:])
            # the "+1" excludes the "\" from the directory name to avoid
            # the problem of overriding the path before it in the join process

            # self.prevListFolders = self.listFold
            listDicItems = [{"selectedFolders": self.prevListFolders}]
            titleText = "SelectFolders to build bhv and par dataframes"
            folders = ChooseInList.listTransmit(parent=None,
                                                graphNo=0,
                                                listChoix=["selectedFolders"],
                                                items=self.listFold,
                                                listDicItems=listDicItems,
                                                onePerCol=[0],
                                                colNames=["Dir Names"],
                                                typ="chk",
                                                titleText=titleText)
            self.prevListFolders = folders[0][0]["selectedFolders"]
            for exp in self.prevListFolders:
                expPath = os.path.join(self.ensembleRunDir, exp)
                # print(expPath)
                for fold1 in os.listdir(expPath):
                    if fold1 == "GEPdata":
                        gepFold = os.path.join(expPath, fold1)
                        self.listGEPFolders.append(gepFold)
                        # print(gepFold)
            if len(self.listGEPFolders) == 1:
                print("Only One Experiment chosen")
                one_expe = True
                listOfSearchedDir = self.listGEPFolders
                gepdataFold = self.listGEPFolders[0]
                animatsimdir = os.path.split(gepdataFold)[0]
                self.graph_path = animatsimdir + "/graphs"
            else:
                self.nbExpe = len(self.listGEPFolders)
                print("Number of experiments in graph :", self.nbExpe)
        # self.listGEPFolders.sort()  # do not work (duplicate folders ???)
        self.one_expe = one_expe
        self.directory = directory
        self.listOfSearchedDir = listOfSearchedDir
        
        
    def read_GEPdata_infos(self):
        """
        Finds all "GEPdata" folders in subdirectories (whatever the level).
        Takes GEPdata00bhv.txt file present in each "GEPdata" folder only
        if nb of columns == 10.
        Takes only data with a varmse < 1.
        """
        one_expe = self.one_expe
        # print self.listGEPFolders
        self.listFoldersNbBhv7 = []

        # =========== Take bhv only if nb of columns == 10 ============
        if one_expe:
            print('Single Experiment')
            if self.prevListGEPFiles == []:
                tab_bhv = readTablo(self.listGEPFolders[0], "GEPdata00bhv.txt")
                tab_bhv = np.array(tab_bhv)
            else:
                for idx, gepdataFile in enumerate(self.prevListGEPFiles):
                    ficBasename = gepdataFile[:-4]  # name without ext
                    tab_bhv = readTablo(self.listGEPFolders[0],
                                        ficBasename + "bhv.txt")
                    tab_bhv = np.array(tab_bhv)
                    if len(tab_bhv) > 0:
                        behavs = np.array(tab_bhv[:, 0:-1])
                        if len(behavs[0]) != 10:
                            # fold = os.path.split(gepdataFold)[0]
                            # foldName = os.path.split(fold)[-1]
                            self.listFoldersNbBhv7.append(self.listGEPFolders[0])
                            # print gepdataFold
                    else:    # empty table
                        self.listFoldersNbBhv7.append(self.listGEPFolders[0])
        if not one_expe:
            for idx, gepdataFold in enumerate(self.listGEPFolders):
                tab_bhv = readTablo(gepdataFold, "GEPdata00bhv.txt")
                tab_bhv = np.array(tab_bhv)
                if len(tab_bhv) > 0:
                    behavs = np.array(tab_bhv[:, 0:-1])
                    if len(behavs[0]) != 10:
                        # fold = os.path.split(gepdataFold)[0]
                        # foldName = os.path.split(fold)[-1]
                        self.listFoldersNbBhv7.append(gepdataFold)
                        # print gepdataFold
                else:
                    self.listFoldersNbBhv7.append(gepdataFold)    # empty table
                if idx % 10 == 0:
                    print("*", end=" ")
        self.tab_bhv = tab_bhv
        print()
        nbpbs = len(self.listFoldersNbBhv7)
        print(nbpbs)
        if nbpbs > 0:
            print("#### ALARM!!!", end=" ")
            print(nbpbs, "bhv data with less that 10 columns ####")
            print()
            tmpFoldList = []
            for gepdataFold in self.listGEPFolders:
                if gepdataFold not in self.listFoldersNbBhv7:
                    tmpFoldList.append(gepdataFold)
            self.listGEPFolders = tmpFoldList
        self.listGEPFolders.sort()
        print(self.listGEPFolders)
        print()
        # if len(self.listGEPFolders) == 0:
        #    print("######### No data to process #########")
        #    return



    def construct_df_par_bhv_remains(self):
        """
        Dataframes are appended in a list of dataframes (df_bhvremain[idx]). A
        global dataframe is built with a new last column indicating the origin
        (integers) of the appended dataframe (self.df_bhvremain).
        The same is made with GEPdata00.txt for the  df_parremain[idx] and a
        global dataframe self.df_parremain.
        self.ensembleRunDir is the folder from which the sub-folders selection
        was made
        """
        self.df_bhvremain = None
        self.df_parremain = None
        self.dic_df_origine = {}

        # directory = self.directory
        directory = self.ensembleRunDir
        one_expe = self.one_expe
        # listOfSearchedDir = self.listOfSearchedDir
        tab_bhv = self.tab_bhv
        
        rootdir = os.path.split(directory)[0]
        self.rootdir = rootdir
        rootfolder = os.path.split(rootdir)[-1]
        self.rootfolder = rootfolder
        lenrootfld = len(rootfolder) 
        # if self.optSet is None:
        getInfoAsim = True
        if one_expe:
            if directory == self.singleDirectory:
                getInfoAsim = False
        
        gepdataFold = self.listGEPFolders[0]
        gepdataFold = gepdataFold.replace('\\', '/')
        start_gepFolder = gepdataFold.find(rootfolder)+lenrootfld
        self.start_gepFolder = start_gepFolder
        rel_gepfataFold = gepdataFold[self.start_gepFolder:]
        animatsimdir = os.path.split(self.rootdir + rel_gepfataFold)[0]
        
        self.animatsimdir = animatsimdir
        if getInfoAsim is True:
            # ============ Get informations from the .asim file
            self.optSet, model = getOptSetFromAsim(self, animatsimdir)
            self.aprojFicName = os.path.split(model.aprojFile)[-1]
            self.singleDirectory = directory    # to avoid reload asim next...
        # ============ Build the dataframes
        lst_df_bhvremain = []
        lst_df_parremain = []
        parName = "GEPdata00.txt"
        bhvName = "GEPdata00bhv.txt"

        concatpairs = [np.zeros(len(self.optSet.x0) + 2)]
        concatbehavs = [np.zeros(10)]

        # =====================================================================
        nb_folders = len(self.listGEPFolders)
        if not one_expe:
            print()
            text = " # PLEASE WAIT! PROCESSING {} folders ... "
            print(text.format(nb_folders))
            parName = "GEPdata00.txt"
            bhvName = "GEPdata00bhv.txt"
            # lst_lenTab = [len(tab_bhv)]
            lst_lenTab = []
            for idx, gepdataFold in enumerate(self.listGEPFolders):
                gepdataFold = gepdataFold.replace('\\', '/')
                rel_gepfataFold = gepdataFold[self.start_gepFolder:]
                gepdataFold = self.rootdir + rel_gepfataFold
                res = self.build_bhv_par_df(idx, gepdataFold, parName, bhvName,
                                            concatpairs, concatbehavs,
                                            lst_lenTab,
                                            lst_df_parremain, lst_df_bhvremain)
                (concatpairs, concatbehavs,
                 lst_df_parremain, lst_df_bhvremain, lst_lenTab) = res
            print(lst_df_bhvremain)
            listsubdir = os.listdir(self.ensembleRunDir)
            ix = 0
            for idx, sdir in enumerate(listsubdir):
                # print(sdir, end=" ")
                if sdir[:6] == "mltple":
                    if os.path.isdir(os.path.join(self.ensembleRunDir,
                                                  sdir)):
                        ix += 1
            folderExist = False
            if ix > 0:
                for mltple in range(ix):
                    mltpleDirName = "mltpleExpeGraph-" + str(mltple+1)
                    mltpleDirPath = os.path.join(self.ensembleRunDir,
                                                 mltpleDirName)
                    print(mltpleDirPath, end=" ")
                    with open(mltpleDirPath+'/dic_folds.json') as f:
                        dic_folder_st = json.load(f)
                        dic_folder = change_key_str_to_int(dic_folder_st)
                        print(dic_folder)
                        for ky in dic_folder.keys():
                            gepdataFold = dic_folder[ky]
                            rel_gepfataFold=gepdataFold[self.start_gepFolder:]
                            gepdatafold = self.rootdir + rel_gepfataFold
                            dic_folder[ky] = gepdatafold
                        print(dic_folder)    
                        if self.dic_df_origine == dic_folder:
                            print("already created for these folders")
                            folderExist = True
                            folderName = mltpleDirPath
                            self.graph_path = folderName
                        else:
                            print("do not contain these folders")
            else:
                print("No mltpleExpeGraph folder found -> create: ", end=" ")

            if not folderExist:
                if ix > 0:
                    print("creating a new mltpleExpeGraph folder:", end=" ")
                newGrname = "mltpleExpeGraph" + '-{0:d}'.format(ix+1)
                self.graph_path = os.path.join(self.ensembleRunDir,
                                               newGrname)
                print(newGrname)
                if not os.path.exists(self.graph_path):
                    os.makedirs(self.graph_path)
                    # save dictionary of folders with their ID number
                    jsondicfile_name = os.path.join(self.graph_path,
                                                    'dic_folds.json')
                    with open(jsondicfile_name, 'w+') as f:
                        # this would place the entire output on one line
                        json.dump(self.dic_df_origine, f, indent=4)
                else:
                    self.graph_path = folderName
            saveListToDir(self.prevListFolders,
                          "listFolders.txt", self.graph_path)

        else:   # only one_expe
            gepdataFold = self.listGEPFolders[0]
            gepdataFold = gepdataFold.replace('\\', '/')
            rel_gepfataFold = gepdataFold[self.start_gepFolder:]
            gepdataFold = self.rootdir + rel_gepfataFold            
            listOfSearchedDir = [gepdataFold]
            lst_lenTab = [len(tab_bhv)]
            onlyfiles = [f for f in listdir(listOfSearchedDir[0])
                         if isfile(join(listOfSearchedDir[0], f))
                         and f.endswith(".par")]
            onlyfiles.sort()
            self.listGEPFiles = onlyfiles
            print(onlyfiles)
            if len(self.listGEPFiles) > 1:
                listDicItems = [{"selectedFiles": self.prevListGEPFiles}]
                titleText = "SelectGEPFiles to build bhv and par dataframes"
                files = ChooseInList.listTransmit(parent=None,
                                                  graphNo=0,
                                                  listChoix=["selectedFiles"],
                                                  items=self.listGEPFiles,
                                                  listDicItems=listDicItems,
                                                  onePerCol=[0],
                                                  colNames=["FIle Names"],
                                                  typ="chk",
                                                  titleText=titleText)
                self.prevListGEPFiles = files[0][0]["selectedFiles"]
            elif len(self.listGEPFiles) == 1:
                self.prevListGEPFiles = ["GEPdata00.par"]
            
            for idx, gepdataFile in enumerate(self.prevListGEPFiles):
                parName = gepdataFile[:-4] + ".txt"
                bhvName = gepdataFile[:-4] + "bhv.txt"
                res = self.build_bhv_par_df(idx, gepdataFold, parName, bhvName,
                                            concatpairs, concatbehavs,
                                            lst_lenTab,
                                            lst_df_parremain, lst_df_bhvremain)
                (concatpairs, concatbehavs,
                 lst_df_parremain, lst_df_bhvremain, lst_lenTab) = res
        self.new_run_dir = self.graph_path
        self.lst_df_parremain = lst_df_parremain
        self.lst_df_bhvremain = lst_df_bhvremain
        self.lst_lenTab = lst_lenTab
        # =====================================================================
        """
        self = MyWin
        for idx in list(lst_df_parremain[0].index)[:10]:
            print(idx)
            print(lst_df_parremain[0].rgserie[idx])
            print(lst_df_parremain[0].loc[idx][:5])
            print(concatpairs[idx][:5])
        """
        self.optSet.pairs = concatpairs
        self.optSet.behavs = concatbehavs

        lst_valid = []
        lst_rgserie = []
        sum_precedingTab = 0
        if one_expe:
            self.lst_valid = list(lst_df_parremain[0].index)
        else:
            for idy, df_bhv in enumerate(lst_df_bhvremain):
                if idy > 0:
                    sum_precedingTab += lst_lenTab[idy-1]
                    arr_rgserie = np.array(df_bhv.rgserie) + sum_precedingTab
                else:
                    arr_rgserie = np.array(df_bhv.rgserie)
                lst_rgserie = list(arr_rgserie)
                print(lst_rgserie)
                lst_valid = lst_valid + lst_rgserie
            print(lst_valid)
            self.lst_valid = lst_valid
                
        # =============  recreates the index of the global df   ===============
        self.df_bhvremain.index = self.lst_valid
        self.df_parremain.index = self.lst_valid
        self.df_bhvremain = self.df_bhvremain.astype({"origine": int})
        self.df_parremain = self.df_parremain.astype({"origine": int})
        # === adds a new column "orig_rg" for the ranks in each source df ===
        self.df_bhvremain.loc[:, "orig_rg"] = self.df_bhvremain["rgserie"]
        self.df_parremain.loc[:, "orig_rg"] = self.df_parremain["rgserie"]
        # === writes the new global index in the column "rgserie"
        self.df_bhvremain.loc[:, "rgserie"] = self.df_bhvremain.index
        self.df_parremain.loc[:, "rgserie"] = self.df_parremain.index
        
        self.df_parremain.index = np.arange(len(self.df_parremain))
        self.df_bhvremain.index = np.arange(len(self.df_bhvremain))

        """
#   TODO    to remind commands
        for idOK in range(10):
            idx = self.lst_valid[idOK]
            print(idOK, idx)
            print(self.df_parremain.rgserie[idOK])
            print(self.df_parremain.loc[idOK][:5])
            print(self.optSet.pairs[idx][:5])
        """

        # #####################################################################
        #                    plots the  behav map
        # self.behav_col = [3, 8]
        df_parremain = self.df_parremain
        df_bhvremain = self.df_bhvremain
        self.optSet.df_parremain = df_parremain
        self.optSet.df_bhvremain = df_bhvremain
        if len(self.listGEPFolders) == 1:
            pathGEP = self.listGEPFolders[0]
            parName = self.prevListGEPFiles[0]
            fileGEP = os.path.join(pathGEP, parName)
            self.datastructure = load_datastructure(fileGEP)
        # next line is needed for mafen to get access to datastructure
        self.optSet.datastructure = self.datastructure
        self.actualize_mafen(self.GEP_GUI_win, self.aprojFicName, self.optSet)
        self.behav_col = self.mafen.behav_col
        self.bhv_names = self.mafen.bhv_names
        df_bhv = self.df_bhvremain
        self.scale_x, self.scale_y = self.mafen.scale_x, self.mafen.scale_y
        if len(df_bhv) > 0:
            max_x_bhv = df_bhv[df_bhv.columns[self.behav_col[0]]].max()
            max_y_bhv = df_bhv[df_bhv.columns[self.behav_col[1]]].max()
            max_x = float(int(max_x_bhv*10)+1)/10
            max_y = float(int(max_y_bhv*10)+1)/10
            self.xmin = 0
            self.xmax = max_x
            self.ymin = 0
            self.ymax = max_y
            bhv_xmin = 0
            bhv_xmax = max_x/self.scale_x
            bhv_ymin = 0
            bhv_ymax = max_y/self.scale_y
            self.bhv_xmin = bhv_xmin*self.scale_x   # for Graph_Setting window
            self.bhv_xmax = bhv_xmax*self.scale_x   # for Graph_Setting window
            self.bhv_ymin = bhv_ymin*self.scale_y
            self.bhv_ymax = bhv_ymax*self.scale_y

            namex = self.bhv_names[self.behav_col[0]]
            namey = self.bhv_names[self.behav_col[1]]
            self.bhv_set = {}
            keys = [namex+'.min', namex+'.max', namey+'.min', namey+'.max']
            values = [0, self.bhv_xmax, 0, self.bhv_ymax]
            for idx, key in enumerate(keys):
                self.bhv_set[key] = values[idx]
            """
            self.bhv_set = {'endangle.min': 0, 'endangle.max': 120,
                            "dur_mvt2.min": 0.200, "dur_mvt2.max": 1.400}
            """
        else:
            print("NO VALID DATA TO ANALYZE")


    def auto_par_bhv(self, win, animatsimdir):
        """
        Method used in controlScriptGEP to build df_parremain and df_bhvremain
        and get all param windows and bhv windows
        """
        GEPdataDir = os.path.join(animatsimdir, "GEPdata")
        fileGEP = os.path.join(GEPdataDir, "GEPdata00.par")
        self.datastructure = load_datastructure(fileGEP)
        GEP_GUI_win = win
        self.mafen = GEP_GUI_win
        self.mafen.optSet = self.optSet
        self.mafen.hide()
        self.mafen.bhvPlot.hide()
        self.mafen.mvtPlot.hide()
        self.mafen.main_mode = False

        self.behav_col = self.mafen.behav_col
        self.bhv_names = self.mafen.bhv_names
        parName = "GEPdata00.txt"
        bhvName = "GEPdata00bhv.txt"
        tab_par = readTablo(GEPdataDir, parName)
        tab_par = np.array(tab_par)
        tab_bhv = readTablo(GEPdataDir, bhvName)
        tab_bhv = np.array(tab_bhv)
        if tab_par[0][-1] != 0.0:   # last column must be 0, 1, 2...., n
            pairs = np.array(tab_par[:, :])
        else:
            pairs = np.array(tab_par[:, 0:-1])
            behavs = np.array(tab_bhv[:, 0:-1])
            print("nbcol in pairs : {}".format(len(pairs[0])), end=" ")
            print("nbcol in behavs : {}".format(len(behavs[0])))
        win.optSet.pairs = pairs
        win.optSet.behavs = behavs
        start = 0
        end = len(win.optSet.behavs)
        tup = win.get_df_remain(win.optSet.behavs, win.optSet.pairs,
                                start, end)
        listdf_bhv, listdf_par = tup
        df_bhvremain = copy.deepcopy(listdf_bhv[0])
        df_parremain = copy.deepcopy(listdf_par[0])
        self.df_bhvremain = df_bhvremain
        self.df_parremain = df_parremain
        df_bhv = df_bhvremain
        self.scale_x, self.scale_y = self.mafen.scale_x, self.mafen.scale_y
        max_x_bhv = df_bhv[df_bhv.columns[self.behav_col[0]]].max()
        max_y_bhv = df_bhv[df_bhv.columns[self.behav_col[1]]].max()
        max_x = float(int(max_x_bhv*10)+1)/10
        max_y = float(int(max_y_bhv*10)+1)/10
        self.xmin = 0
        self.xmax = max_x
        self.ymin = 0
        self.ymax = max_y
        bhv_xmin = 0
        bhv_xmax = max_x/self.scale_x
        bhv_ymin = 0
        bhv_ymax = max_y/self.scale_y
        self.bhv_xmin = bhv_xmin*self.scale_x   # for the Graph_Setting window
        self.bhv_xmax = bhv_xmax*self.scale_x   # for the Graph_Setting window
        self.bhv_ymin = bhv_ymin*self.scale_y
        self.bhv_ymax = bhv_ymax*self.scale_y
        namex = self.bhv_names[self.behav_col[0]]
        namey = self.bhv_names[self.behav_col[1]]
        self.bhv_set = {}
        keys = [namex+'.min', namex+'.max', namey+'.min', namey+'.max']
        values = [0, self.bhv_xmax, 0, self.bhv_ymax]
        for idx, key in enumerate(keys):
            self.bhv_set[key] = values[idx]

        bhv_xmin = self.bhv_xmin
        bhv_xmax = self.bhv_xmax
        bhv_ymin = self.bhv_ymin
        bhv_ymax = self.bhv_ymax

        self.makes_bhvpar_windows(df_bhvremain, df_parremain,
                                  bhv_xmin, bhv_xmax, bhv_ymin, bhv_ymax,
                                  auto=True, hide=True)

    def save_bhvpar_df_to_csv(self):
        """
        """
        NbSelectedBhv = len(self.mafen.source_df_bhvremain)
        if NbSelectedBhv > 0:
            # pathGEP = self.listGEPFolders[0]
            # root_path = os.path.split(pathGEP)[0]
            # graph_path = os.path.join(root_path, "graphs")
            # graph_path = root_path + "/graphs"
            graph_path = self.graph_path
            if not os.path.exists(graph_path):
                os.makedirs(graph_path)
            new_run_dir = self.new_run_dir
            if self.bhv_names[self.behav_col[0]] == 'endangle':
                nomx = "amp"
            if self.bhv_names[self.behav_col[1]] == 'dur_mvt2':
                nomy = "dur"
            if self.bhv_names[self.behav_col[1]] in ('max_speed',
                                                     'speed_mvt2'):
                nomy = "vit"

            str_bhvSet = "{}{}-{}_{}{}-{}".format(nomx, self.bhv_xmin,
                                                  self.bhv_xmax,
                                                  nomy, self.bhv_ymin,
                                                  self.bhv_ymax)
            file_name = "{}_bhv{}".format(str_bhvSet, NbSelectedBhv)
            ret = 7

            msg = "Save restrained dataframes?"
            msg2 = "New selection contains {} bhvs".format(NbSelectedBhv)
            ret = MessageBox(None, msg, msg2, 3)
            print(ret)
            if ret == 2:
                print("ESC")
            elif ret == 6:
                print("YES --> Saves the bhv, par dataframes of selected data")
            elif ret == 7:
                print("NO: --> Do Not Save restrained dataframes")
            if ret == 6:
                file_name = "{}_bhv{}".format(str_bhvSet, NbSelectedBhv)
                save_df_to_csv(self.mafen.source_df_bhvremain, new_run_dir,
                               file_name, typ='bhv')
                file_name = "{}_par{}".format(str_bhvSet, NbSelectedBhv)
                save_df_to_csv(self.mafen.source_df_parremain, new_run_dir,
                               file_name, typ='par')
        return file_name

    def makes_bhvpar_windows(self, df_bhvremain, df_parremain,
                             bhv_xmin, bhv_xmax, bhv_ymin, bhv_ymax,
                             auto=False, hide=False):
        self.plot_map_behav(df_bhvremain,
                            xmin=bhv_xmin/self.scale_x,
                            xmax=bhv_xmax/self.scale_x,
                            ymin=bhv_ymin/self.scale_y,
                            ymax=bhv_ymax/self.scale_y)
        self.plot_df_bhv(df_bhvremain,
                         xmin=bhv_xmin,
                         xmax=bhv_xmax,
                         ymin=bhv_ymin,
                         ymax=bhv_ymax)
        # ============ positionning the bhvPlot window on screen ==============
        sg = QtWidgets.QDesktopWidget().screenGeometry()
        # MyWin_height = self.geometry().height()
        MyWin_width = self.geometry().width()
        bhvPlot_width = self.mafen.bhvPlot.geometry().width()
        bhvPlot_height = self.mafen.bhvPlot.geometry().height()
        bhvPlot_height = bhvPlot_height - 50
        self.mafen.bhvPlot.resize(bhvPlot_width, bhvPlot_height)
        # self.mafen.bhvPlot.show()
        xshift = MyWin_width + 15
        yshift = sg.height() - bhvPlot_height - 1
        self.mafen.bhvPlot.location_on_the_screen(xshift=xshift, yshift=yshift)
        if hide:
            self.mafen.bhvPlot.hide()
        # =====================================================================
        """
        self.bhv_set = {'endangle.min': 0, 'endangle.max': 120,
                        "dur_mvt2.min": 0.200, "dur_mvt2.max": 1.400}
        """
        df_bhv = copy.deepcopy(self.df_bhvremain)
        df_par = copy.deepcopy(self.df_parremain)
        res = self.extract_new_df(df_par, df_bhv, self.bhv_set)
        self.df_glob, self.ss_titre = res[0], res[1]
        self.mafen.df_bhvremain = df_bhv.loc[self.df_glob.index]
        self.mafen.df_parremain = df_par.loc[self.df_glob.index]
        self.mafen.source_df_bhvremain = df_bhv.loc[self.df_glob.index]
        self.mafen.source_df_parremain = df_par.loc[self.df_glob.index]

        self.plot_mvt(xmin=0, xmax=10, ymin=0, ymax=150)
        # ============ positionning the mvtPlot window on screen ==============
        sg = QtWidgets.QDesktopWidget().screenGeometry()
        # MyWin_height = self.geometry().height()
        MyWin_width = self.geometry().width()
        mvtPlot_width = bhvPlot_width
        mvtPlot_height = sg.height() - (bhvPlot_height + 50) - 256 - 85
        self.mafen.bhvPlot.resize(mvtPlot_width, mvtPlot_height)
        mvtPlot_height = self.mafen.mvtPlot.geometry().height()
        xshift = MyWin_width + 15
        yshift = sg.height() - bhvPlot_height - (mvtPlot_height + 50) - 12
        self.mafen.mvtPlot.location_on_the_screen(xshift=xshift, yshift=yshift)
        if hide:
            self.mafen.mvtPlot.hide()
        # =====================================================================
        for gr in enumerate(self.mafen.listDicGraphs):
            print(gr)
        print()
        self.mafen.showAllParGraphs()
        for gr in enumerate(self.mafen.listDicGraphs):
            print(gr)
        print
        if not auto:
            msg = "Change params in param plot windows (and graphs)?"
            ret = MessageBox(None, msg, 'Setting params in each param plot', 3)
            if verbose > 2:
                print(ret)
            if ret == 2:
                print("ESC")
            elif ret == 6:
                print("YES --> change params in param plots")
            elif ret == 7:
                print("NO: --> keep default params in param plots")

            if ret == 6:
                self.mafen.chooseParam()
        else:
            ret = 7
        self.mafen.clearParam()
        self.mafen.param_in_blue(df_par)

        if verbose > 2:
            print(self.mafen.listDicGraphs)
        # self.plot_map_params(df_parremain)
        # ============ positionning the paramPlot windows on screen ===========
        nb_pargraphs = len(self.mafen.listDicGraphs)
        parwin_width = int((sg.width()-100)/nb_pargraphs)
        """
        if parwin_width > 256:
            parwin_width = 256
            nbcol = nb_pargraphs
        elif parwin_width < 256:
            parwin_width = 256
            nbcol = int(sg.width()/256)
        """
        parwin_height = parwin_width
        nbcol = nb_pargraphs
        row = 0
        col = 0
        for pargr, parwin in enumerate(self.mafen.screen):
            parwin.resize(parwin_width, parwin_height)
            col = pargr % nbcol
            print(pargr % nbcol)

            """
            if pargr % nbcol == 0:
                col = 0
                row += 1
            if pargr % nbcol == 1:
                col = 1
            """
            print("col={}; row={}".format(col, row))
            # ============ positionning the parPlot window on screen ==========
            # parwin are disposed in 2 columns on the right side of the screen
            # mywin_height = self.geometry().height()
            parwin_height = parwin.geometry().height()
            parwin_width = parwin.geometry().width()
            xshift = (nbcol - 1) * parwin_width - (col * parwin_width) + 10
            # yshift = sg.height() - 50 - bhvPlot_height - mywin_height
            # yshift = yshift - parwin_height*row
            yshift = 20
            parwin.screen_loc(xshift=xshift, yshift=yshift)
            if hide:
                parwin.hide()
            # =================================================================
            if col == nbcol-1:
                row += 1
        parwin.resize(parwin_width, parwin_height+30)
        parwin.screen_loc(xshift=xshift, yshift=30)

    def plot_par_bhv(self):
        """
        Plots a series of bhv=f(par) graphs plus a 3rd variable with colorscale
        """
        df_glob = self.df_glob
        list_bhv = self.list_bhv
        list_par = self.list_par
        ss_titre = self.ss_titre
        factor = self.factor
        titre = "Fig0_parbhv"
        MyWin.make_graph_lsty_lstx(df_glob, list_bhv, list_par,
                                   titre, ss_titre, factor)

    def plot_par_par(self):
        """
        Plots a series of par=f(par) graphs for a focus of bhvs  plus a 3rd
        variable with color scale
        """
        df_glob = self.df_glob
        list_par = self.list_par
        ss_titre = self.ss_titre
        factor = self.factor
        titre = "Fig1_parpar"
        MyWin.make_graph_lsty_lstx(df_glob, list_par, list_par,
                                   titre, ss_titre, factor)


    def plot_bhv_neur(self):
        """
        Plots a series of bhv=f(par) graphs plus a 3rd variable with colorscale
        """
        df_glob = self.df_glob
        list_bhv = self.list_bhv
        list_neurAct = self.list_neurAct
        ss_titre = self.ss_titre
        factor = self.factor
        titre = "Fig0_bhvneur"
        MyWin.make_graph_lsty_lstx(df_glob, list_neurAct, list_bhv, 
                                   titre, ss_titre, factor)

    def plot_par_neur(self):
        """
        Plots a series of par=f(par) graphs for a focus of bhvs  plus a 3rd
        variable with color scale
        """
        df_glob = self.df_glob
        list_par = self.list_par
        list_neurAct = self.list_neurAct
        ss_titre = self.ss_titre
        factor = self.factor
        titre = "Fig1_parneur"
        MyWin.make_graph_lsty_lstx(df_glob, list_neurAct, list_par,
                                   titre, ss_titre, factor)

    def plot_single(self):
        """
        Plots a single scatter graph for two variables plus a 3rd with color
        scale
        """
        df_glob = self.df_glob
        two_selected_var = self.two_selected_var
        factor = self.factor
        ss_titre = self.ss_titre
        titre = "Fig3_Single"
        self.make_graph_single(df_glob, two_selected_var,
                               titre, ss_titre, factor)

    def plot_scatterMatrix(self):
        """
        Plots a 2D+colorscale Matrix of scatter plots with all given variabl
        names given in selected_col
        """
        df_glob = self.df_glob
        selected_col = self.selected_col
        factor = self.factor
        graph_name = "Fig4_scatter_mtx_Color"
        ss_titre = self.ss_titre
        """
        selected_col = ['1ExtAlpha_St1.CurrentOn',
                        '1FlxGamma_St1.CurrentOn',
                        'NS1_IaFlx-FlxAlMn.SynAmp',
                        'NS1_IaExt-ExtAlMn.SynAmp']

        factor = 'endangle'
        """
        # #####################################################################
        self.make_scatter_matrix_df_2DplusColor(df_glob, selected_col,
                                                graph_name, ss_titre, factor)
        # #####################################################################

    def plot_3d_graph_with_colorScale(self):
        # #####################################################################
        # plots a 3D+colorscale graph in a interactive window for
        # a focus of bhvs
        """
        select_3_col = ['1FlxGamma_St1.CurrentOn',
                        'NS1_IaFlx-FlxAlMn.SynAmp',
                        'endangle',
                        ]
        factor = "dur_mvt2"
        """
        df_glob = self.df_glob
        self.select_3_col = self.three_selected_var
        select_3_col = self.select_3_col
        print(select_3_col)
        factor = self.factor
        ss_titre = self.ss_titre
        titre = "Fig5_3D_Dots_{}__{}__{}".format(select_3_col[0][:13],
                                                 select_3_col[1][:13],
                                                 select_3_col[2][:13])
        self.make_3d_plot(df_glob, select_3_col, titre, ss_titre, factor)

        self.make_3d_plot_window(df_glob, select_3_col,
                                 titre, ss_titre, factor)
        # #####################################################################

    def selctValidBehav(self, behavs, pairs, start, end,
                        stangl=0, st_err=1,
                        minampl=10, max_coactpenalty=0.01):
        if len(behavs) > 1:
            df_behav = pd.DataFrame(behavs[start:end], columns=self.bhv_names,
                                    index=np.arange(len(behavs[start:end])))
        elif len(behavs) == 1:
            df_behav = pd.DataFrame(behavs[:], columns=self.bhv_names,
                                    index=np.arange(len(behavs[:])))
        else:
            return (None, None)
        list_names = copy.deepcopy(self.optSet.xparName)
        list_names.append("mse")
        list_names.append("coactpen")
        df_param = pd.DataFrame(pairs[start:end],
                                columns=list_names,
                                index=np.arange(len(pairs[start:end])))
        """
        if len(optSet.pairs) > 1:
            df_param = pd.DataFrame(optSet.pairs[start:end],
                                    columns=list_names,
                                    index=np.arange(len(optSet.pairs[start:end])))
        elif len(optSet.pairs) == 1:
            df_param = pd.DataFrame(optSet.pairs[:],
                                    columns=list_names,
                                    index=np.arange(len(optSet.pairs[:])))
        else:
            df_param =  None
        """
        # ======    creates one new column    =================
        rgserie = df_behav.index
        df_behav.loc[:, 'rgserie'] = rgserie
        rgseriepar = df_param.index
        df_param.loc[:, 'rgserie'] = rgseriepar

        pd.set_option('display.precision', 4)
        pd.set_option('expand_frame_repr', True)

        # ========    selection of data by start angle   =========
        # print df_behav
        startang_OK = abs(stangl - df_behav['startangle']) < st_err
        df_behav = df_behav[startang_OK]
        df_param = df_param[startang_OK]

        # =====    selection of data by minimum amplitude   ======
        # print(df_behav)
        ampl_OK = df_behav['endangle'] - df_behav['startangle'] > minampl
        df_behav = df_behav[ampl_OK]
        df_param = df_param[ampl_OK]

        # ========    selection of data by coact level   =========
        # print(df_behav)
        coact_OK = df_behav['coactpen'] < max_coactpenalty
        df_behav = df_behav[coact_OK]
        df_param = df_param[coact_OK]
        # print('coactpen < 0.01')

        # ========    selection of data with SynAmp >= 0   ========
        # print(df_behav)
        for syn in self.optSet.synNSParName:
            syn_OK = df_param[syn] >= 0
            df_behav = df_behav[syn_OK]
            df_param = df_param[syn_OK]
        return (df_behav, df_param)

    def plot_2D_stability_map(self, df_bhvremain, df_parremain):
        """
        Then call the do_plot_2D_stability_map()
        method to plot the stability map.
        """
        # pathGEP = self.listGEPFolders[0]
        # root_path = os.path.split(pathGEP)[0]
        # graph_path = os.path.join(root_path, "graphs")
        # graph_path = root_path + "/graphs"
        graph_path = self.graph_path
        if not os.path.exists(graph_path):
            os.makedirs(graph_path)

        strGEPdataName = self.prevListGEPFiles[0]
        GEPdataName = os.path.splitext(strGEPdataName)[0]
        behav_col = self.behav_col
        par_names = self.par_names
        search_dist = 0.005
        df_cues_dist = build_stability_dataframe(df_bhvremain, df_parremain,
                                                 graph_path, GEPdataName,
                                                 behav_col, par_names,
                                                 search_dist)
        do_plot_2D_stability_map(self, df_cues_dist, search_dist, graph_path,
                                 GEPdataName)

    def plot_map_behav(self, df_bhvremain, aimbhv=[],
                       xmin=0, xmax=1.2, ymin=0, ymax=1.5):
        """
        plots the df_bhvremain dataframe with an additional possible point
        aimbhv (if != [])
        """
        # scale x and y values
        behavs_cues = df_bhvremain[df_bhvremain.columns[self.behav_col]]
        rel_behavs_cues = behavs_cues/[self.scale_x, self.scale_y]
        nameX = rel_behavs_cues.columns[0]
        nameY = rel_behavs_cues.columns[1]
        valX = rel_behavs_cues[nameX]
        valY = rel_behavs_cues[nameY]
        figure, ax = plt.subplots(figsize=(7, 7))
        # figure, ax = plt.subplots()
        plt.scatter(valX, valY, marker='o', s=4)
        plt.xlim(xmin, xmax)
        plt.ylim(ymin, ymax)
        if self.scale_x == 1:
            labelnamex = nameX
        else:
            labelnamex = nameX + " (x{})".format(1.0/self.scale_x)
        if self.scale_y == 1:
            labelnamey = nameY
        else:
            labelnamey = nameY + " (x{})".format(1.0/self.scale_y)

        ax.set_xlabel(labelnamex)
        ax.set_ylabel(labelnamey)
        ax.set_axisbelow(True)
        ax.grid(linestyle='-', linewidth='0.5', color='red')

        for point in aimbhv:
            x = point[0]
            y = point[1]
            relx, rely = x/self.scale_x, y/self.scale_y
            plt.plot(relx, rely, '-p', color='gray',
                     markersize=8, linewidth=2,
                     markerfacecolor='white',
                     markeredgecolor='gray',
                     markeredgewidth=2)
        plt.show()

    def plot_map_params(self, df_parremain):
        """
        plots the df_parremain dataframe with a series of XY 2D graphs
        """
        for pargr in range(self.mafen.nbactivepargraphs):
            parx = 2 + int(2*pargr) + self.mafen.parx
            pary = 2 + int(2*pargr) + self.mafen.pary
            if pary > self.mafen.nbpar:
                pary = 2 + self.mafen.pary
            if parx > self.mafen.nbpar:
                parx = 2 + self.mafen.parx
            print(self.mafen.optSet.xparName[parx], end=" ")
            print(self.mafen.optSet.xparName[pary])
            """
            self.plotParBlue(self.screen[pargr].plot_item, df_par, parx, pary)
            """
        print(self.mafen.parx, self.mafen.optSet.xparName[self.mafen.parx])
        print(self.mafen.pary, self.mafen.optSet.xparName[self.mafen.pary])
        """
        self.plotParBlue(self.screen[pargr+1].plot_item, df_par,
                         self.parx, self.pary)
        """

    def extract_new_df(self, df_par, df_bhv, bhv_set):
        """
        Build the new df_glob by concatenation of df_par and df_bhv. Uses
        bhv_set information to filter the df_glob (retain only values with bhv
        data in the limits of bhv_data. Build also an information text about
        the dataframe, ss_titre. Returns [df_glob, ss_titre]
        """
        bhv_keys = list(bhv_set.keys())
        bhv_keys.sort()
        bhv1max = bhv_keys[0]
        bhv1min = bhv_keys[1]
        bhv2max = bhv_keys[2]
        bhv2min = bhv_keys[3]
        bvh1_name = bhv1min[:bhv1min.find(".")]
        # bvh1_name_short = bvh1_name[:-2]
        bvh1_name_short = bvh1_name[:]
        bvh2_name = bhv2min[:bhv2min.find(".")]
        bvh2_name_short = bvh2_name[:-3]
        # sd_bhv = bhv_set["sd"]
        min_bhv1 = float(bhv_set[bhv1min])
        max_bhv1 = float(bhv_set[bhv1max])
        min_bhv2 = float(bhv_set[bhv2min])
        max_bhv2 = float(bhv_set[bhv2max])

        df_glob = pd.concat([df_par, df_bhv], axis=1)

        span_bhv1 = df_glob[bvh1_name] >= min_bhv1
        df_glob = df_glob[span_bhv1]
        span_bhv1 = df_glob[bvh1_name] <= max_bhv1
        df_glob = df_glob[span_bhv1]

        span_bhv2 = df_glob[bvh2_name] >= min_bhv2
        df_glob = df_glob[span_bhv2]
        span_bhv2 = df_glob[bvh2_name] <= max_bhv2
        df_glob = df_glob[span_bhv2]
        df_glob = df_glob.loc[:, ~df_glob.columns.duplicated()]
        ss_titre = "{}[{},{}]{}[{},{}]".format(bvh1_name_short,
                                               min_bhv1, max_bhv1,
                                               bvh2_name_short,
                                               min_bhv2, max_bhv2)
        return [df_glob, ss_titre]

    def make_graph_single(self, df_glob, two_selected_var,
                          titre="", ss_titre="", factor=None):
        """
        Produces a pdf plot of the two parameters plus color code for the third
        """

        codeCoul_df = copy.deepcopy(df_glob[[factor]])
        sort_factor = codeCoul_df[factor].values
        min_coul = min(sort_factor)
        max_coul = max(sort_factor)
        if min_coul == max_coul:
            factor = None

        var1 = two_selected_var[0]
        var2 = two_selected_var[1]
        graph_path = self.graph_path
        figure, ax = plt.subplots(figsize=(7, 7), dpi=100)
        size = figure.get_size_inches()*figure.dpi  # size in pixels
        glob_df = copy.deepcopy(df_glob)

        if factor is None:
            self.palette = sns.color_palette("Set1")
            palette = self.palette
            ax.plot(glob_df.loc[:, var1].values,
                    glob_df.loc[:, var2].values,
                    color=palette[0],
                    marker='o', markersize=5, linewidth=0)
            ax.set_xlabel(var1, labelpad=18, fontsize=10)
            ax.set_ylabel(var2, labelpad=18, fontsize=10)

        else:
            [step_pal_misRem, codeCoul_df] = buildStpDiscretCol(df_glob,
                                                                factor)
            seq_factor = "seq_{}".format(factor)
            seq_factor_col = codeCoul_df[seq_factor]
            classes = list(set(codeCoul_df[seq_factor]))
            classes.sort(reverse=False)
            color_map = dict(zip(classes, step_pal_misRem))
            colors = seq_factor_col.apply(lambda group: color_map[group])
            # =====  creation of a new 'seq_factor' column in new glob_df =====
            glob_df.loc[:, seq_factor] = codeCoul_df.loc[:, seq_factor]

            ax.scatter(np.array(glob_df.loc[:, var1]),
                       np.array(glob_df.loc[:, var2]),
                       alpha=0.70, s=10, c=colors, linewidth=0)
            ax.set_xlabel(var1, labelpad=18, fontsize=10)
            ax.set_ylabel(var2, labelpad=18, fontsize=10)

            # if factor is not None:
            labels = copy.deepcopy(classes)
            labels.sort(reverse=True)
            nbcolors = len(classes)
            """
            if nbcolors < 50:
            # the double colorscale is no more accepted...
            """
            handles = [plt.plot([], [], color=color_map[labels[i]],
                                ls="", marker='o',
                                markersize=6)[0] for i in range(nbcolors)]
            # In legend order is that of classes (revert order)
            plt.legend(handles, labels, loc=(1.02, 0))
            plt.setp(plt.gca().get_legend().get_texts(), fontsize='6')
            """
            else:
                # ------------ 1st set of legend elements  ----------------
                labels1 = labels[:int(nbcolors/2)]
                handles1 = [plt.plot([], [], color=color_map[labels[i]],
                            ls="", marker='o',
                            markersize=6)[0] for i in range(int(nbcolors/2))]
                # In legend order is that of classes (revert order)
                first_legend = plt.legend(handles1, labels1, loc=(1.02, 0))
                plt.gca().add_artist(first_legend)
                plt.setp(plt.gca().get_legend().get_texts(), fontsize='6')
                # ------------ 2nd set of legend elements  ----------------
                labels2 = labels[int(nbcolors/2):]
                handles2 = [plt.plot([], [], color=color_map[labels[i]],
                            ls="", marker='o',
                            markersize=6)[0] for i in range(int(nbcolors/2),
                                                            nbcolors)]
                # In legend order is that of classes (revert order)
                posx_legend2 = 1 + 80/size[0]
                # second_legend = plt.legend(handles2, labels2,
                #                            loc=(1.25, 0))

                second_legend = plt.legend(handles2, labels2,
                                           loc=(posx_legend2, 0))
                plt.gca().add_artist(second_legend)
                plt.setp(plt.gca().get_legend().get_texts(), fontsize='6')
            """
        var1_st = var1[:var1.find(".")]
        var2_st = var2[:var2.find(".")]
        tit = "{}{}-{}col={}".format(titre, var1_st, var2_st, factor)
        titre_2lines = "{}\n{}".format(tit, ss_titre)
        plt.suptitle(titre_2lines, fontsize=14)

        sstit = ss_titre_to_txt(ss_titre)
        """
        plt.savefig(r'{0}/{1} {2}.eps'.format(graph_path, tit, sstit),
                    bbox_inches='tight')
        plt.savefig(r'{0}/{1} {2}.pdf'.format(graph_path, tit, sstit),
                    bbox_inches='tight')
        """
        if two_selected_var == ['ampl', 'max_speed'] \
            or two_selected_var == ['endangle', 'max_speed']:
            xmin = float(self.bhv_set['endangle.min']) #/self.scale_x
            xmax = float(self.bhv_set['endangle.max']) #/self.scale_x
            ymin = float(self.bhv_set['max_speed.min']) #/self.scale_y
            ymax = float(self.bhv_set['max_speed.max']) #/self.scale_y
            
            plt.xlim(xmin, xmax)
            plt.ylim(ymin, ymax)
        save_eps_pdf(graph_path, tit, sstit)
        plt.show()


    def plot_color_scale(self, factor, classes, color_map):
        if factor is not None:
            labels = copy.deepcopy(classes)
            labels.sort(reverse=True)
            nbcolors = len(classes)
            if nbcolors < 50:
                handles = [plt.plot([], [], color=color_map[labels[i]],
                           ls="", marker='o',
                           markersize=6)[0] for i in range(nbcolors)]
                # In legend order is that of classes (revert order)
                plt.legend(handles, labels, loc=(1.02, 0))
                plt.setp(plt.gca().get_legend().get_texts(), fontsize='6')
            else:
                # ------------ 1st set of legend elements  ----------------
                labels1 = labels[:nbcolors/2]
                handles1 = [plt.plot([], [], color=color_map[labels[i]],
                            ls="", marker='o',
                            markersize=6)[0] for i in range(nbcolors/2)]
                # In legend order is that of classes (revert order)
                first_legend = plt.legend(handles1, labels1, loc=(1.02, 0))
                plt.gca().add_artist(first_legend)
                plt.setp(plt.gca().get_legend().get_texts(), fontsize='6')
                # ------------ 2nd set of legend elements  ----------------
                labels2 = labels[nbcolors/2:]
                handles2 = [plt.plot([], [], color=color_map[labels[i]],
                            ls="", marker='o',
                            markersize=6)[0] for i in range(nbcolors/2,
                                                            nbcolors)]
                # In legend order is that of classes (revert order)
                second_legend = plt.legend(handles2, labels2,
                                           loc=(1.25, 0))
                plt.gca().add_artist(second_legend)
                plt.setp(plt.gca().get_legend().get_texts(), fontsize='6')


    def do_single(self, listX, listY, glob_df, idy, y, ysize, setY,
                  colors, palette, classes, color_map,
                  titre, tit, titre_2lines, ss_titre, factor):
        
        figure, (ax1, ax2, ax3) = \
            plt.subplots(nrows=1, ncols=3, figsize=(8, 3), dpi=100,
                         # sharex='col',
                         sharey='row'
                         )
        # x = np.array(df_glob.loc[:, listX[0]])
        if factor is not None:
            ax1.scatter(np.array(glob_df.loc[:, listX[0]]), y,
                        alpha=0.70, s=10, c=colors, linewidth=0)
        else:
            ax1.plot(np.array(glob_df.loc[:, listX[0]]), y,
                     color=palette[idy],
                     marker='o', markersize=1, linewidth=0)
        ax1.set_xlabel(listX[0], labelpad=18, fontsize=10)
        ax1.set_ylabel(setY, labelpad=18, fontsize=10)
        if len(listX) > 1:
            if factor is not None:
                ax2.scatter(np.array(glob_df.loc[:, listX[1]]), y,
                            alpha=0.70, s=10, c=colors, linewidth=0)
            else:
                ax2.plot(np.array(glob_df.loc[:, listX[1]]), y,
                         color=palette[idy],
                         marker='o', markersize=1, linewidth=0)
            ax2.set_xlabel(listX[1], labelpad=18, fontsize=10)
            # ax2.set_ylabel(setY, labelpad=18, fontsize=14)
        elif len(listX) > 2:
            if factor is not None:
                ax3.scatter(np.array(glob_df.loc[:, listX[2]]), y,
                            alpha=0.70, s=10, c=colors, linewidth=0)
            else:
                ax3.plot(np.array(glob_df.loc[:, listX[2]]), y,
                         color=palette[idy],
                         marker='o', markersize=1, linewidth=0)
            ax3.set_xlabel(listX[2], labelpad=18, fontsize=10)
            # ax3.set_ylabel(setY, labelpad=18, fontsize=14) 
        plt.suptitle(titre_2lines, fontsize=11, y=1.05-ysize*0.005)
        self.plot_color_scale(factor, classes, color_map)
        figure.text(0.04, 0.5, setY, va='center', rotation='vertical')
        sstit = ss_titre_to_txt(ss_titre)
        """
        plt.savefig(r'{0}/{1} {2}.eps'.format(graph_path, tit, sstit),
                    bbox_inches='tight')
        plt.savefig(r'{0}/{1} {2}.pdf'.format(graph_path, tit, sstit),
                    bbox_inches='tight')
        """
        save_eps_pdf(self.graph_path, tit, sstit)
        plt.show()


    def make_graph_lsty_lstx(self, df_glob, listY, listX,
                             titre="", ss_titre="", factor=None):
        """
        Produces a pdf of subplots for each parameter and bhv selected
        """
        codeCoul_df = copy.deepcopy(df_glob[[factor]])
        sort_factor = codeCoul_df[factor].values
        min_coul = min(sort_factor)
        max_coul = max(sort_factor)
        if min_coul == max_coul:
            factor = None

        if factor is not None:
            [palette, codeCoul_df] = buildStpDiscretCol(df_glob, factor)
            seq_factor = "seq_{}".format(factor)
            seq_factor_col = codeCoul_df[seq_factor]
            classes = list(set(codeCoul_df[seq_factor]))
            classes.sort(reverse=False)
            color_map = dict(zip(classes, palette))
            colors = seq_factor_col.apply(lambda group: color_map[group])
            # =====  creation of a new 'seq_factor' column in new glob_df =====
            glob_df = copy.deepcopy(df_glob)
            glob_df.loc[:, seq_factor] = codeCoul_df.loc[:, seq_factor]
        else:
            self.palette = sns.color_palette("Set1")
            palette = self.palette

        # model_dir = self.ensembleRunDir
        graph_path = self. graph_path
        ncols = 3
        nrows = len(listX) // ncols
        if nrows < len(listX) / ncols:
            nrows += 1
        rowperpage = 3
        nb_pages = nrows // rowperpage
        if nb_pages * rowperpage < nrows:
            nb_pages += 1
        print("listY = ", listY)
        for idy, setY in enumerate(listY):
            print(setY, end=" ")
            y = glob_df[setY].values
            print(y)
            if setY.find(".") == -1:
                setY_short = setY
            else:
                setY_short = setY[:setY.find(".")]
            tit = "{}-{}-col={}".format(titre, setY_short, factor)
            titre_2lines = "{}\n{}".format(tit, ss_titre)

            if nrows == 1:
                ysize = len(listX) * 2
                self.do_single(listX, listY, glob_df, idy, y, ysize, setY,
                               colors, palette, classes, color_map,
                               titre, tit, titre_2lines, ss_titre, factor)

            else:
                for page in range(nb_pages):
                    print(page)
# TODO     to be continued...
                
                figure, ax = plt.subplots(nrows=nrows, ncols=ncols,
                                          figsize=(8, 9), dpi=100,
                                          gridspec_kw={'hspace': 0.3,
                                                       'wspace': 0.05},
                                          # gridspec_kw={'vspace': 2},
                                          # sharex='col',
                                          sharey='row')
                lastrow = (len(listX) - len(listX) % 3) // 3
                for par_idx, setX in enumerate(listX):
                    col = par_idx % 3   # modulo function -> 0 1 2 0 1 2 etc.
                    row = int((par_idx - col) / 3)
                    print(row, col)
                    x = np.array(glob_df.loc[:, setX])
                    if factor is not None:
                        ax[row, col].scatter(x, y, alpha=0.70,
                                             s=10,
                                             # color=palette,
                                             c=colors,
                                             linewidth=0)
                    else:
                        ax[row, col].plot(x, y, color=palette[idy],
                                          marker='o', markersize=1,
                                          linewidth=0)

                    ax[row, col].set_xlabel(setX, fontsize=8)
                    ax[row, col].xaxis.set_label_coords(0.5, 1.09)
                    # ax[row, col].set_title(setX, fontsize=9)
                    if col == 0:
                        None
                        # ax[row, col].set_ylabel(setY, fontsize=8)
                    if row == 0 and col == 2:
                        None
                    if row == lastrow:
                        ax[row, col].tick_params(axis='x', rotation=70)
            
                if setY.find(".") == -1:
                    setY_short = setY
                else:
                    setY_short = setY[:setY.find(".")]
                tit = "{}-{}-col={}".format(titre, setY_short, factor)
                titre_2lines = "{}\n{}".format(tit, ss_titre)
                ysize = len(listX) * 2
                plt.suptitle(titre_2lines, fontsize=11, y=1.05-ysize*0.005)

                self.plot_color_scale(factor, classes, color_map)
                figure.text(0.04, 0.5, setY, va='center', rotation='vertical')
                sstit = ss_titre_to_txt(ss_titre)
                """
                plt.savefig(r'{0}/{1} {2}.eps'.format(graph_path, tit, sstit),
                            bbox_inches='tight')
                plt.savefig(r'{0}/{1} {2}.pdf'.format(graph_path, tit, sstit),
                            bbox_inches='tight')
                """
                save_eps_pdf(graph_path, tit, sstit)
                plt.show()

    def make_scatter_matrix_df_2DplusColor(self, df_glob, selected_col,
                                           graph_name, ss_titre, factor):
        """
        """

        # select_col = self.par_names
        # factor = 'endangle'
        # factor = 'dur_mvt2'
        # factor = 'NS1_IaExt-ExtAlMn.SynAmp'

        codeCoul_df = copy.deepcopy(df_glob[[factor]])
        sort_factor = codeCoul_df[factor].values
        min_coul = min(sort_factor)
        max_coul = max(sort_factor)
        if min_coul == max_coul:
            factor = None

        if factor is not None:
            [step_pal_misRem, codeCoul_df] = buildStpDiscretCol(df_glob,
                                                                factor)
            seq_factor = "seq_{}".format(factor)
            glob_df = copy.deepcopy(df_glob[selected_col])

            graph_name = "{}_{}".format(graph_name, ss_titre_to_txt(ss_titre))

            # palette = sns.color_palette("tab20b") +\
            #    sns.color_palette("tab20c")
            # palette = sns.color_palette("'hsv'")

            # graph_path = self.ensembleRunDir
            graph_path = self.graph_path

            # =======  creation of a new 'seq_factor' column  =======
            glob_df.loc[:, seq_factor] = codeCoul_df.loc[:, seq_factor]
            # glob_df[seq_factor] = glob_df[seq_factor].astype(int)
            # glob_df = glob_df.drop([factor], axis=1)

            axarr, color_map = factor_scatter_matrix(glob_df,
                                                     seq_factor,
                                                     graph_name,
                                                     plt_factor=False,
                                                     palette=step_pal_misRem)
            """
            plt.savefig(r'{0}/{1}_{2}.eps'.format(graph_path,
                                                  graph_name,
                                                  seq_factor))
            plt.savefig(r'{0}/{1}_{2}.pdf'.format(graph_path,
                                                  graph_name,
                                                  seq_factor))
            """
            save_eps_pdf(graph_path, graph_name, seq_factor)
            plt.show()

    def make_3d_plot(self, df_glob, select_3_col, titre, ss_titre, factor,
                     azim=60, elev=30):
        """
        Draws a 3D scatter plot with a fourth parameter as color scale
        """
        # model_dir = self.ensembleRunDir
        graph_path = self.graph_path
        print("getting palette")

        codeCoul_df = copy.deepcopy(df_glob[[factor]])
        sort_factor = codeCoul_df[factor].values
        min_coul = min(sort_factor)
        max_coul = max(sort_factor)
        if min_coul == max_coul:
            factor = None

        if factor is not None:
            [step_pal_misRem, codeCoul_df] = buildStpDiscretCol(df_glob,
                                                                factor)
            seq_factor = "seq_{}".format(factor)
            seq_factor_col = codeCoul_df[seq_factor]
            classes = list(set(codeCoul_df[seq_factor]))
            classes.sort(reverse=False)
            color_map = dict(zip(classes, step_pal_misRem))

            colors = seq_factor_col.apply(lambda group: color_map[group])
            # =====  creation of a new 'seq_factor' column in new glob_df =====
            glob_df = copy.deepcopy(df_glob[select_3_col])
            glob_df.loc[:, seq_factor] = codeCoul_df.loc[:, seq_factor]
            x = df_glob[select_3_col[0]]
            y = df_glob[select_3_col[1]]
            z = df_glob[select_3_col[2]]

            # ===============        Creating plot           ==================
            fig = plt.figure(figsize=(8, 8), dpi=100)
            ax = fig.add_axes([0.0, 0.0, 0.8, 0.8], projection='3d')
            # ax = fig.gca(projection='3d')
            ax.view_init(azim=azim, elev=elev)
            ax.scatter(x, y, z, alpha=0.8, c=colors,
                       # edgecolors='none',
                       s=10,
                       # label=classes,
                       )
            ax.set_xlabel(select_3_col[0])
            ax.set_ylabel(select_3_col[1])
            ax.set_zlabel(select_3_col[2])
            orient = "azim({}) elev({})".format(azim, elev)
            tit = "{}__color={}".format(titre, factor[:13])
            titre_2lines = "{}\n{} {}".format(tit, ss_titre, orient)
            plt.suptitle(titre_2lines, fontsize=14, y=0.90)
            # plt.title('Matplot 3d scatter plot')

            # ================= building legend for color scale ===============
            if factor is not None:
                labels = copy.deepcopy(classes)
                labels.sort(reverse=True)
                nbcolors = len(classes)
                if nbcolors < 50:
                    handles = [plt.plot([], [], color=color_map[labels[i]],
                               ls="", marker='o',
                               markersize=6)[0] for i in range(nbcolors)]
                    # In legend order is that of classes (revert order)
                    plt.legend(handles, labels, loc=(1.08, 0))
                    plt.setp(plt.gca().get_legend().get_texts(), fontsize='6')
                else:
                    nbcol = int(nbcolors/2)
                    # ------------ 1st set of legend elements  ----------------
                    labels1 = labels[:nbcol]
                    handles1 = [plt.plot([], [], color=color_map[labels[i]],
                                ls="", marker='o',
                                markersize=6)[0] for i in range(nbcol)]
                    # In legend order is that of classes (revert order)
                    first_legend = plt.legend(handles1, labels1,
                                              loc=(1.04, 0.0))
                    plt.gca().add_artist(first_legend)
                    plt.setp(plt.gca().get_legend().get_texts(), fontsize='6')
                    # ------------ 2nd set of legend elements  ----------------
                    labels2 = labels[nbcol:]
                    handles2 = [plt.plot([], [], color=color_map[labels[i]],
                                ls="", marker='o',
                                markersize=6)[0] for i in range(nbcol,
                                                                nbcolors)]
                    # In legend order is that of classes (revert order)
                    second_legend = plt.legend(handles2, labels2,
                                               loc=(1.12, 0.0))
                    plt.gca().add_artist(second_legend)
                    plt.setp(plt.gca().get_legend().get_texts(), fontsize='6')
            sstit = ss_titre_to_txt(ss_titre)
            sstit = "{}__az({})_el({})".format(sstit, azim, elev)
            save_eps_pdf(graph_path, tit, sstit)
            plt.show()

    def make_3d_plot_window(self, df_glob, select_3_col,
                            titre, ss_titre, factor):
        """
        """
        plt.ion()
        print("getting palette")
        # ==== creates a list of quantal progressing values for factor
        color, codeCoul_df, step_palette = buildStpFilledCol(df_glob, factor)
        x = np.array(df_glob[select_3_col[0]])
        y = np.array(df_glob[select_3_col[1]])
        z = np.array(df_glob[select_3_col[2]])
        # pos = pd.concat([x, y, z], axis=1)
        # print(len(pos))
        tit = "{}__col={}".format(titre, factor)
        sstit = ss_titre_to_txt(ss_titre)
        ficname = "{}{}".format(tit, sstit)
        # ====================   activation of win3D   ====================
        print("##########  Creation of visu_3d from   ##########")
        self.visu_3d = Visualizer3D(self.graph_path, self)
        self.visu_3d.resize(800, 800)
        self.visu_3d.show()

        self.visu_3d.addData(pos=(x, y, z), names=select_3_col, fourth=factor,
                             size=4, pxMode=True, color=color, setname="main",
                             ficname=ficname)
        # self.visu_3d.apply_rainbow_colors(color)


# TODO
    def makegr_chart_tcourse(self):
        """
        doc string
        """
        self.make_bhvpardf()
        print(self.optSet.chartColNames)
        res = (QtWidgets.QFileDialog.
               getOpenFileName(self, "Choose a dataFile to plot",
                               self.mydir, "Chart Files (*.txt *.par)"))
        if type(res) == tuple:
            self.fname, __tmp = res
        else:
            self.fname = res
        print(self.fname)
        self.mydir = os.path.split(self.fname)[0]
        ficname = os.path.split(self.fname)[-1]
        name = os.path.splitext(ficname)[0]
        ext = os.path.splitext(ficname)[1]
        if ext == '.par':
            self.chooseChartFromPar()
        elif ext == '.txt':
            if name[-13:] == "CMAeFitCourse" or name[-13:] == "VSCDFitCourse":
                self.makeGraphfromFitCourse(self.fname)
            else:
                list_elem = ["EMG", "bhvMvt"]
                typ = "graph"
                title = "Choose type of graph"
                gr_typ = choose_one_element_in_list(title, list_elem, typ)
                if gr_typ == "EMG":
                    self.makeGraphFromChart(self.fname,
                                            lstChartColNam=['1FlxPotMuscle',
                                                              '1ExtPotMuscle'])
                else:
                    self.makeGraphFromChart(self.fname)

    def make_all_chart(self):
        self.make_bhvpardf()
        res = (QtWidgets.QFileDialog.
               getOpenFileName(self, "Choose a chartFile to plot",
                               self.mydir, "Chart Files (*.txt)"))
        if type(res) == tuple:
            self.fname, __tmp = res
        else:
            self.fname = res
        print(self.fname)
        self.mydir = os.path.split(self.fname)[0]
        mypath = self.mydir
        from os import listdir
        from os.path import isfile, join
        onlyfiles = [str(f) for f in listdir(mypath) if isfile(join(mypath, f))
                     and os.path.splitext(f)[-1] == ".txt"]
        sorted_chart_list = ["GEP_chart" + "0" + str(idx) + ".txt" if idx < 10
                             else "GEP_chart" + str(idx) + ".txt"
                             for idx in range(len(onlyfiles))]
        for fic in sorted_chart_list[:]:
            fname = mypath + "/" + fic
            print(fname)
            self.makeGraphFromChart(fname)


    def analyze_bhv_neur_par_chart(self):
        list_elem = ["Create a new chart bhv_par_neur_dataframe",
                     "Read a previous chart bhv_par_neur_dataframe"]
        typ = "Choose"
        title = "choose what top do"
        choice = choose_one_element_in_list(title, list_elem, typ)
        print(choice)
        if choice == "Create a new chart bhv_par_neur_dataframe":
            self.create_df_for_bhv_neur_par()
        else:
            self.read_csv_for_df_bhv_neur_par()
        
        """
        ======================================================================
        Creates an instance of Graph_setting command window
        ======================================================================
        """
        list_bhvVar = [u'varmse', u'startangle', u'ampl',
                    u'max_speed', u'dur_mvt2']
        self.list_bhvVar = list_bhvVar
        listpar = self.par_names
        # listbhv = self.bhv_names
        listbhv = self.list_bhvVar
        
        self.graph_settings = Graph_Setting(listpar, listbhv,
                                            self.chart_glob_df, self)
        self.graph_settings.show()
        # ========= positionning the Graph_Setting window on screen ===========
        sg = QtWidgets.QDesktopWidget().screenGeometry()
        mywin_height = self.geometry().height()
        graphSet_height = self.graph_settings.geometry().height()
        # graphSet_width = self.graph_settings.geometry().width()
        xshift = 10
        yshift = sg.height() - graphSet_height - mywin_height - 40
        self.graph_settings.screen_loc(xshift=xshift, yshift=yshift)
        # =====================================================================


# TODO: to be continued... activate mltpleExpeGraph                   

    def read_csv_for_df_bhv_neur_par(self):
        res = (QtWidgets.QFileDialog.
               getOpenFileName(self, "Choose bhv_df_csv file to analyse",
                               self.mydir, "Files (*csv)"))
        if type(res) == tuple:
            self.fname, __tmp = res
        else:
            self.fname = res
        print(self.fname)
        if self.fname is not None:
            self.mydir = os.path.split(self.fname)[0]
            self.chart_glob_df = pd.read_csv(self.fname)
            self.chart_glob_df = self.chart_glob_df.drop(['Unnamed: 0'],
                                                         axis=1)
            """
            # Suppression of all row containing a Nan
             self.chart_glob_df.dropna(inplace=True)
            """
            print(self.chart_glob_df)
            lst_glob_df_colNames = list(self.chart_glob_df.columns)
            self.neur_act_names = [nam for nam in lst_glob_df_colNames
                                   if nam not in self.bhv_names
                                   and nam not in self.par_names
                                   and nam not in ['chart', 'ampl',
                                                   'rgserie', 'origine',
                                                   'orig_rg', 'rg_in_whole']]
            if os.path.split(self.mydir)[-1] != "GEPdata":
                one_expe = False
                mltpleDirPath = self.mydir 
                with open(mltpleDirPath+'/dic_folds.json') as f:
                    dic_folder_st = json.load(f)
                    dic_folder = change_key_str_to_int(dic_folder_st)
                self.listGEPFolders = []
                for idx in list(dic_folder.keys()):
                    self.listGEPFolders.append(dic_folder[idx])
            else:
                one_expe = True
                self.listGEPFolders = [self.mydir]

                self.graph_path = os.path.split(self.mydir)[0] + "/graphs"
            """ 
            ==============================================================
            #      building of the global df_bhvremain and df_parremain
            ==============================================================
            """
            self.directory = self.mydir
            self.ensembleRunDir = os.path.split(self.directory)[0]
            self.prevListFolders = self.listGEPFolders
            tab_bhv = readTablo(self.listGEPFolders[0], "GEPdata00bhv.txt")
            tab_bhv = np.array(tab_bhv)
            self.tab_bhv = tab_bhv
            self.one_expe = one_expe

            # ================================================================
            self.construct_df_par_bhv_remains()    
            # ================================================================
            lst_df_parremain = self.lst_df_parremain
            lst_df_bhvremain = self.lst_df_bhvremain
            lst_lenTab = self.lst_lenTab
            """ 
            ==============================================================
            """
            """
            lst_valid = []
            lst_rgserie = []
            sum_precedingTab = 0
            if one_expe:
                self.df_parremain = lst_df_parremain[0]
                self.df_bhvremain = lst_df_bhvremain[0]
                self.lst_valid = list(lst_df_bhvremain[0].index)
            else:
                self.graph_path = self.mydir
                for idy, df_bhv in enumerate(lst_df_bhvremain):
                    if idy > 0:
                        sum_precedingTab += lst_lenTab[idy-1]
                        arr_rgserie = np.array(df_bhv.rgserie) \
                            + sum_precedingTab
                    else:
                        arr_rgserie = np.array(df_bhv.rgserie)
                    lst_rgserie = list(arr_rgserie)
                    print(lst_rgserie)
                    lst_valid = lst_valid + lst_rgserie
                print(lst_valid)
                self.lst_valid = lst_valid
                    
            # ====  Creates df_parremain compatible with global df index  ====
            self.df_bhvremain = self.df_bhvremain.astype({"origine": int})
            self.df_parremain = self.df_parremain.astype({"origine": int})
            #self.df_bhvremain.loc[:, "orig_rg"] = self.df_bhvremain["rgserie"]
            self.df_bhvremain.loc[:, "rgserie"] = self.lst_valid
            #self.df_parremain.loc[:, "orig_rg"] = self.df_parremain["rgserie"]
            self.df_parremain.loc[:, "rgserie"] = self.lst_valid
            """
            lst_valid_chart = list(self.chart_glob_df["rgserie"])

            self.df_parremain_OK = \
                self.df_parremain["rgserie"].isin(lst_valid_chart)
            self.df_parremain = self.df_parremain[self.df_parremain_OK]
            self.df_bhvremain_OK = \
                self.df_bhvremain["rgserie"].isin(lst_valid_chart)          
            self.df_bhvremain = self.df_bhvremain[self.df_bhvremain_OK]
            index = list(self.chart_glob_df["rg_in_whole"])
            #self.df_parremain.index = np.arange(len(self.df_parremain))
            #self.df_bhvremain.index = np.arange(len(self.df_bhvremain))
            self.df_parremain.index = index
            self.df_bhvremain.index = index
            self.chart_glob_df.index = index
            self.df_glob = self.chart_glob_df
            df_bhv = self.df_bhvremain

            #self.actualize_mafen(self.GEP_GUI_win,
            #                     self.aprojFicName, self.optSet)
            if self.mafen.mvt_ord_maxSpeed == 1: # ord is "maxSpeed"
                self.behav_col = [3, 6]
            else:
                self.behav_col = [3, 8]
            if self.behav_col[1] == 8:
                self.scale_x, self.scale_y = 100, 1
            elif self.behav_col[1] == 6:
                self.scale_x, self.scale_y = 100, 100
            max_x_bhv = df_bhv[df_bhv.columns[self.behav_col[0]]].max()
            max_y_bhv = df_bhv[df_bhv.columns[self.behav_col[1]]].max()
            max_x = float(int(max_x_bhv*10)+1)/10
            max_y = float(int(max_y_bhv*10)+1)/10
            self.xmin = 0
            self.xmax = max_x
            self.ymin = 0
            self.ymax = max_y
            bhv_xmin = 0
            bhv_xmax = max_x/self.scale_x
            bhv_ymin = 0
            bhv_ymax = max_y/self.scale_y
            self.bhv_xmin = bhv_xmin*self.scale_x   # for Graph_Setting window
            self.bhv_xmax = bhv_xmax*self.scale_x   # for Graph_Setting window
            self.bhv_ymin = bhv_ymin*self.scale_y
            self.bhv_ymax = bhv_ymax*self.scale_y
            namex = self.bhv_names[self.behav_col[0]]
            namey = self.bhv_names[self.behav_col[1]]
            self.bhv_set = {}
            keys = [namex+'.min', namex+'.max', namey+'.min', namey+'.max']
            values = [0, self.bhv_xmax, 0, self.bhv_ymax]
            for idx, key in enumerate(keys):
                self.bhv_set[key] = values[idx]

    def create_df_for_bhv_neur_par(self):
        """
        Parameters
        ----------
        [el1, el2,...] = list of chart column names
        el1 : chart element_1 (for example "1FlxAlpha")
            this is one of the elements of the txt chart file.
        el2 : chart element_2 (for example "1ExtAlpha")
            this is one of the elements of the txt chart file.
         ...
        eln : chart element_n (for example "1FlxGamma")
            this is one of the elements of the txt chart file.

        Returns
        -------
        self.df_chart_elements dataframe with columns:
            chartnames, varmse, statangle, ampl, max_speed,
            dur_mvt2, origine, run-rg, el1, el2,... eln

        """


        """
        =====================================================================
        creates a new self.df_parremain and a new df_bhvremain
        =====================================================================
        """
        self.make_bhvpardf()
        optSet = self.optSet
        # list_neur = ["1FlxIa", "1ExtIa"]
        # list_neur = ["1FlxAlpha", "1ExtAlpha"]
        # list_neur = ["1FlxIa", "1ExtIa", "1FlxAlpha", "1ExtAlpha"]
        self.scale_x, self.scale_y = self.mafen.scale_x, self.mafen.scale_y
        """
        =====================================================================
        creates new_sub_df_chart with selected neurons present in the chart
        =====================================================================
        """
        print("Select neurons to analyse (validate the selection window)")
        selected = optSet.sensColChartNames
        list_elem = optSet.chartColNames
        typ = "chart_col"
        text = "select neurons to plot and analyse"
        list_neur = choose_elements_in_list(list_elem, typ, selected, text)
        
        print("Select neurons for a second peak analysis")
        selected = list_neur
        typ = "second peak"
        text = "select neurons for 2nd peak analysis"
        list_neur_2nd_peak = choose_elements_in_list(list_elem,
                                                     typ, selected, text)
        
        print(self.listGEPFolders)
        self.nbExpe = len(self.listGEPFolders)
        if self.nbExpe == 1:
            save_path = self.listGEPFolders[0]
        else:
            save_path = self.graph_path
        
        # Buid the self.df_chart by calling self.chooseChartFromPar() method
        self.chooseChartFromPar(lstChartColNam=list_neur,
                                y_label="Neurons pot (mV)",
                                title='_NeurVsBhv')
        print(self.list_bhvVar)
        # self.newdf_chart = copy.deepcopy(self.df_chart)
        self.new_sub_df_chart = copy.deepcopy(self.sub_df_chart)
        # exit()
        
        """
        ======================================================================
        Extraction of elements from each selected neuron in each chart
        ======================================================================
        """
        elem = {}
        lst_df_par = []
        lst_df_par_index = []
        list_calc = ["_startval", "_endval", "_1stmax", "_1stmax_t"]
        list_2nd_peak_calc = ["_2ndmax", "_2ndmax_t"]
        for colname in list_neur:
            for idx, calc in enumerate(list_calc):
                elem[colname + list_calc[idx]] = []
            if colname in list_neur_2nd_peak:
                for idx, calc in enumerate(list_2nd_peak_calc):
                    elem[colname + list_2nd_peak_calc[idx]] = []
        
        for fold_idx, GEPfold in enumerate(self.listGEPFolders):
            df_chart_fold = self.new_sub_df_chart["origine"] == fold_idx
            sub_df_chart = self.new_sub_df_chart[df_chart_fold]

            df_par_fold_OK = self.df_parremain["origine"] == fold_idx 
            tmp_df_par = self.df_parremain[df_par_fold_OK]
            arr = [x for x in list(tmp_df_par.index)
                   if tmp_df_par.loc[x]["orig_rg"]
                   in list(sub_df_chart.run_rg)]
            lst_df_par.append(tmp_df_par.loc[arr])
            lst_df_par_index.append(tmp_df_par.loc[arr].index)
        
            for chartName in sub_df_chart["chart"]:
                print(chartName, end="")
                colnames = self.optSet.chartColNames
                chart_path = os.path.split(GEPfold)[0] + '/GEPChartFiles'
                completeName = os.path.join(chart_path, chartName)
                (L, df, titre, tabparams) = chartToDataFrame(completeName,
                                                             colnames=colnames)
                df.index = df.Time
                df_n = copy.deepcopy(df.loc[4.5:9][list_neur] * 1000)
                df_n["rg"] = np.arange(len(df_n))
                # get activity value0, value1, etc.. of selected neurons
                # and add each of these global values to the corresponding
                # element:
                for neur in list_neur:
                    list_rg_pk, list_rg_min = get_peaks_and_troughs(df_n, neur,
                                                                    chartName)
                    
                    for idx, calc in enumerate(list_calc):
                        if list_calc[idx] == "_startval":
                            list_val = elem[neur + list_calc[idx]]
                            list_val.append(df_n.iloc[0][neur])
                            elem[neur+list_calc[idx]] = list_val
                        elif list_calc[idx] == "_endval":
                            list_val = elem[neur + list_calc[idx]]
                            list_val.append(df_n.iloc[len(df_n)-1][neur])
                            elem[neur+list_calc[idx]] = list_val
                        elif list_calc[idx] == "_1stmax":
                            list_val = elem[neur + list_calc[idx]]
                            if list_rg_pk != []:                            
                                list_val.append(df_n.iloc[list_rg_pk[0]][neur])
                            else:
                                list_val.append("nan")
                            elem[neur+list_calc[idx]] = list_val
                        elif list_calc[idx] == "_1stmax_t":
                            list_val = elem[neur + list_calc[idx]]
                            if list_rg_pk != []:                            
                                list_val.append(df_n.index[list_rg_pk[0]])
                            else:
                                list_val.append("nan")
                            elem[neur+list_calc[idx]] = list_val

                    if neur in list_neur_2nd_peak:
                        for idx, calc in enumerate(list_2nd_peak_calc):
                            if list_2nd_peak_calc[idx] == "_2ndmax":
                                list_val = elem[neur + list_2nd_peak_calc[idx]]
                                if len(list_rg_pk) >1:
                                    Peak2Val = df_n.iloc[list_rg_pk[1]][neur]
                                    list_val.append(Peak2Val)
                                else:
                                    list_val.append("nan")
                                elem[neur+list_2nd_peak_calc[idx]] = list_val
                            elif list_2nd_peak_calc[idx] == "_2ndmax_t":
                                list_val = elem[neur + list_2nd_peak_calc[idx]]
                                if len(list_rg_pk) > 1:                            
                                    list_val.append(df_n.index[list_rg_pk[1]])
                                else:
                                    list_val.append("nan")
                                elem[neur+list_2nd_peak_calc[idx]] = list_val
                            
        self.lst_df_par = lst_df_par
        self.lst_df_par_index = lst_df_par_index
        df_par_index = []
        for idx in lst_df_par_index:
            df_par_index += list(idx)
        """
        ======================================================================
        creates a neur_df for activities of selected neurons
        ======================================================================
        """
        
        neur_df = pd.DataFrame(elem)
        self.neur_df = neur_df
        neur_act_names = list(neur_df.columns)
        self.neur_act_names = neur_act_names
        neur_df.index = df_par_index
        

        """
        ======================================================================
        creates a chart_df_glob including bhv, neur and params
        ======================================================================
        """
        # self.df_parremain.index = self.df_parremain.orig_rg
        # ===== change fdataframe indexes 
        df_par = self.df_parremain.loc[df_par_index]
        self.new_sub_df_chart.index = df_par_index
        
        self.df_chart_par = copy.deepcopy(df_par)
        # self.df_chart_par.index = np.arange(len(self.df_chart_par))
        self.clean_sub_df_chart = self.new_sub_df_chart.drop(
            ['origine', 'run_rg'], axis=1)
        chart_glob_df = pd.concat([self.clean_sub_df_chart,
                                   self.neur_df,
                                   self.df_chart_par], axis=1)
        chart_glob_df["rg_in_whole"] = df_par_index
        self.chart_glob_df = chart_glob_df
        self.chart_glob_df.to_csv(save_path + "/df_chart_bhv_neur_param.csv")
        self.chart_glob_df = pd.read_csv(
            save_path + "/df_chart_bhv_neur_param.csv"
            )
        self.chart_glob_df = self.chart_glob_df.drop(['Unnamed: 0'], axis=1)
        self.chart_glob_df.dropna(inplace=True)
        self.df_glob = self.chart_glob_df


    def analyze_triphasic(self):
        self.make_bhvpardf()
        print(self.listGEPFolders)
        self.nbExpe = len(self.listGEPFolders)
        if self.nbExpe == 1:
            save_path = self.listGEPFolders[0]
        else:
            save_path = self.graph_path
        self.chooseChartFromPar()
        self.triphasicCriteria = [["FlxTwoPicks", "FlxTo0BetwPicks",
                                  "ExtOnePick"]]
        crit1 = []
        crit2 = []
        crit3 = []
        # print(self.chartdir)
        print(self.df_chart)
        EMGsNames = ['1FlxPotMuscle', '1ExtPotMuscle']

        for fold_idx, GEPfold in enumerate(self.listGEPFolders):
            df_chart_fold = self.df_chart["origine"] == fold_idx
            df_chart = self.df_chart[df_chart_fold]
        
            for chartName in df_chart["chart"]:
                print(chartName, end="")
                colnames = self.optSet.chartColNames
                chart_path = os.path.split(GEPfold)[0] + '/GEPChartFiles'
                completeName = os.path.join(chart_path, chartName)
                (L, df, titre, tabparams) = chartToDataFrame(completeName,
                                                             colnames=colnames)
                df.index = df.Time
                df_EMG = df.loc[5:7][EMGsNames] * 1000
                firstmaxEMG0 = df_EMG[5:5.2][EMGsNames[0]].max()
                firstt0max = df_EMG[5:5.2][EMGsNames[0]].idxmax()
                minEMG0 = df_EMG[firstt0max:7][EMGsNames[0]].min()
                t0min = df_EMG[5.2:7][EMGsNames[0]].idxmin()
                # secondmaxEMG0 = df_EMG[t0min:7][EMGsNames[0]].max()
                secondt0max = df_EMG[t0min:7][EMGsNames[0]].idxmax()
                # maxEMG1 = df_EMG[firstt0max:secondt0max][EMGsNames[1]].max()
                t1maxEMG1 = df_EMG[firstt0max:secondt0max][EMGsNames[1]].idxmax()
                if secondt0max - firstt0max > 0.3 \
                    and secondt0max - firstt0max < 2\
                    and t0min < secondt0max:
                    crit = [1]
                    crit1.append(1)
                else:
                    crit = [0]
                    crit1.append(0)
                betwPeackActi = 1 - (minEMG0  + 60)/(firstmaxEMG0 + 60)
                crit.append("{:2.4f}".format(betwPeackActi))
                crit2.append("{:2.4f}".format(betwPeackActi))
                if t1maxEMG1 > firstt0max and t1maxEMG1 < secondt0max:
                    crit.append(1)
                    crit3.append(1)
                else:
                    crit.append(0)
                    crit3.append(0)
                self.triphasicCriteria.append(crit)
                print(crit)

        self.df_chart["FlxTwoPeaks"] = crit1
        self.df_chart["FlxTo0BetwPeaks"] = crit2
        self.df_chart["ExtOnePeak"] = crit3
        self.df_chart.to_csv(save_path + "/df_chart_tri.csv")
        
        """
        res = (QtWidgets.QFileDialog.
               getOpenFileName(self, "Open csv file",
                               self.mydir, "GEPdata (*.csv)"))
        if type(res) == tuple:
            self.fname, __tmp = res
        else:
            self.fname = res
        print(self.fname)
        df_chart_name = self.fname
        root_name = os.path.split(self.fname)[0]
        self.df_chart = pd.read_csv(df_chart_name) 
        nb_0_betwFlxPeaks = len(self.df_chart[
            self.df_chart["FlxTo0BetwPicks"] == 1])
        print("nb elts with absolute stop between peaks: ", nb_0_betwFlxPeaks)
        print("Total nb of events: ", len(self.df_chart))
        print("percentage = ", nb_0_betwFlxPeaks / len(self.df_chart))
        txtFileName = "Triphasic_summary.txt"
        txtFileCompleteName = root_name + "/" + txtFileName
        with open(txtFileCompleteName, 'w') as fich:
            txt = "number of good mvt wiht absolute Flx stop: {}\n"
            s = txt.format(nb_0_betwFlxPeaks)
            fich.write(s)
            s = "tltal number of good mvts: {}\n". format(len(self.df_chart))
            fich.write(s)
            s = "percentage = {}v".format(nb_0_betwFlxPeaks/len(self.df_chart))
            fich.write(s)
        fich.close()
        """
        
    def chooseChartFromGEPChartFiles(self):
        res = (QtWidgets.QFileDialog.
               getOpenFileName(self, "Open a chart file",
                               self.mydir, "GEPChartFiles (*.txt)"))
        if type(res) == tuple:
            self.fname, __tmp = res
        else:
            self.fname = res
        print(self.fname)
        self.makeGraphFromChart(self.fname,
                                lstChartColNam=['1FlxPotMuscle',
                                                '1ExtPotMuscle'])

    def chooseChartFromPar(self, lstChartColNam=['1FlxPotMuscle',
                                                 '1ExtPotMuscle'],
                           y_label="EMG (mV)", title='_EMG_Mvt'):
        """
        This method is called from makegr_chart_tcourse() method when a .par
        file is selected. It allows the user to select among the charts whose
        names are in the GEPdata00.par file (and hence in self.datastructure)
        1) opens the datastructure;
        2) calls build_df_chart() new method that will build a dataframe
            containing all chartnames, varmse, startangle, ampl, maxs_peed and
            dur_mvt2 and the original rg of of the run. This database is saved
            to charts_infos.csv in GEPdata directory;
        3) Open dialog boxes asking for which parameters to use for selecting
            the chart (ampl, max_speed, etc...)
        4) The charts are then selected in the dataframe
        """
        # self.datastructure = load_datastructure(fname)
        # print(self.datastructure)
        self.df_chart = self.build_df_chart()
        df_chart = self.df_chart
        list_bhvVar = [u'varmse', u'startangle', u'ampl',
                    u'max_speed', u'dur_mvt2']
        self.list_bhvVar = list_bhvVar
        typ = "chart_col"
        selected = ["ampl"]
        text = "selection on which Behavior feature(s)?"
        selected_par = choose_elements_in_list(list_bhvVar,
                                               typ, selected, text)
        sub_df_chart = copy.deepcopy(df_chart)
        for par in selected_par:
            min_par = min(df_chart[par])
            max_par = max(df_chart[par])
            text = "min {} = {:06.2f};  max {} = {:06.2f}".format(par, min_par,
                                                                  par, max_par)
            window_name = "select charts"
            X_min = "min{} {:04.2f}".format(par, min_par)
            x_max = "max{} {:04.2f}".format(par, max_par)
            list_entry_name = [X_min, x_max]
            list_entry_value = ["{:04.2f}".format(min_par),
                                "{:04.2f}".format(max_par)]
            list_value_max = [max_par, max_par]
            self.get_chartToPlot = Enter_Values(self,
                                                list_entry_name,
                                                list_entry_value,
                                                list_value_max,
                                                window_name)
            self.get_chartToPlot.show()
            self.get_chartToPlot.exec_()  # Stops further processes
            #                                           until executed
            self.range_chartplot = self.list_value
            sel_df_chart = sub_df_chart[par] > float(self.range_chartplot[0])
            sub_df_chart = sub_df_chart[sel_df_chart]
            sel_df_chart = sub_df_chart[par] <= float(self.range_chartplot[1])
            sub_df_chart = sub_df_chart[sel_df_chart]
            print(sub_df_chart)
        self.sub_df_chart = sub_df_chart
        titre = "Plot from Charts"
        info = "Do you want to plot charts?"
        rep = dialogWindow(titre, info, details="")
        
        for fold_idx, GEPfold in enumerate(self.listGEPFolders):
            df_chart_fold = sub_df_chart["origine"] == fold_idx
            sub_df_chart_fold = sub_df_chart[df_chart_fold]
            chart_path = os.path.split(GEPfold)[0] + '/GEPChartFiles'
            for chartname in sub_df_chart_fold['chart']:
                print(chartname, end=" ")
                """
                self.mydir = os.path.split(self.fname)[0]
                self.chartdir = os.path.split(self.mydir)[0] + "/GEPChartFiles"
                """
                full_chartname = chart_path + "/" + chartname
                print(full_chartname)
                if rep:
                    self.makeGraphFromChart(full_chartname,
                                            lstChartColNam=lstChartColNam,
                                            y_label=y_label,
                                            title=title)


    def build_df_chart(self):
        """
        method that builds a dataframe from self.datastructure infos. It uses
        also self.df_bhvremain dataframe to get infos on ampl, max_speed...
        The dataframe is then saved to charts_infos.csv in the GEPdata
        directory.
        """
        lst_chart = []
        lst_par_rg = []
        lst_origine = []
        lst_varmse = []
        lst_startangle = []
        lst_amp = []
        lst_maxspeed = []
        lst_duration = []
        self.nbexpe = len(self.listGEPFolders)
        if self.nbexpe > 1:
            print(self.nbexpe,"folders")
        else:
            print("Single folder")

        for fold_idx, GEPfold in enumerate(self.listGEPFolders):
            fname = GEPfold + "/GEPdata00.par"
            print(fname)
            datastructure = load_datastructure(fname)
            df_bhvremain_fold_idx = self.df_bhvremain["origine"] == fold_idx
            df_bhvremain = self.df_bhvremain[df_bhvremain_fold_idx]
            for idx in list(range(len(datastructure))):
                # print(idx)
                if datastructure[idx][0] == "selected_seeds":
                    conditions = datastructure[idx][4]
                    if type(conditions[0]) is list:
                        # this is the new span list format
                        vmse_rg = 2
                    else:   # this is the old format with spanStim and spanSyn
                        vmse_rg = 3
                    chrtnm = vmse_rg + 1
                    par_rg = vmse_rg + 2
                elif datastructure[idx][0] == 'CMAES':
                    vmse_rg = 4
                    chrtnm = 5
                    par_rg = 6
                elif datastructure[idx][0] == 'GEPrand_varmse':
                    conditions = datastructure[idx][4]
                    if type(conditions[0]) is list:
                        # this is the new span list format
                        vmse_rg = 2
                    else:   # this is the old format with spanStim and spanSyn
                        vmse_rg = 3
                    chrtnm = vmse_rg + 1
                    par_rg = vmse_rg + 2
                else:
                    vmse_rg = 3
                    chrtnm = 4
                    par_rg = 5
                idy = 0
                for vmse in datastructure[idx][4][vmse_rg]:
                    print(idy, end=" ")
                    if vmse <= 1:
                        rg = datastructure[idx][4][par_rg][idy]
                        select_rg = df_bhvremain['orig_rg'] == rg
                        if len(df_bhvremain[select_rg]['orig_rg']) > 0:
                            ser_endang = df_bhvremain[select_rg]['endangle']
                            endangle = ser_endang.item()
                            ser_stang = df_bhvremain[select_rg]['startangle']
                            startangle = ser_stang.item()
                            amp = endangle-startangle
                            ser_maxspd = df_bhvremain[select_rg]['max_speed']
                            maxspeed = ser_maxspd.item()
                            ser_dur = df_bhvremain[select_rg]['dur_mvt2']
                            duration = ser_dur.item()
    
                            lst_par_rg.append(rg)
                            lst_origine.append(fold_idx)
                            lst_startangle.append(startangle)
                            lst_amp.append(amp)
                            lst_maxspeed.append(maxspeed)
                            lst_duration.append(duration)
                            # lst_varmse.append(vmse)
    
                            chartname = datastructure[idx][4][chrtnm][idy]
                            lst_chart.append(chartname)
                            vmse = datastructure[idx][4][vmse_rg][idy]
                            lst_varmse.append(vmse)
                    idy += 1

        df_chart = pd.DataFrame(list(zip(lst_chart, lst_varmse,
                                         lst_startangle, lst_amp,
                                         lst_maxspeed, lst_duration,
                                         lst_origine, lst_par_rg)),
                                columns=['chart', 'varmse', 'startangle',
                                         'ampl', 'max_speed', 'dur_mvt2',
                                         'origine', 'run_rg'])
        df_chart.to_csv(self.mydir + '/charts_infos.csv')
        print(df_chart)
        return df_chart

    def makeGraphfromFitCourse(self, fname):
        # fname = self.fname
        name = os.path.split(fname)[-1]
        path = os.path.split(fname)[0:-1][0]
        graphfromFitCourse(path, name)

    def makeGraphFromChart(self, fname,
                           lstChartColNam=[],
                           y_label="EMG (mV)",
                           title="_EMG_Mvt"):
        # fname = self.fname
        chartName = os.path.split(fname)[-1]
        path = os.path.split(fname)[0:-1][0]
        animatsimdir = os.path.split(path)[0:-1][0]
        templateFileName = os.path.join(animatsimdir,
                                        "ResultFiles", "template.txt")
        optSet = self.optSet
        if lstChartColNam == []:
            graphfromchart(optSet, path, chartName, templateFileName)
        else:
            # lstChartColNam = ['1FlxPotMuscle', '1ExtPotMuscle']
            graph_chart_elements(optSet, path, chartName,
                                 lstChartColNam, y_label=y_label,
                                 title=title)

    def make_radar_from_csv(self):
        """
        doc string
        """
        res = (QtWidgets.QFileDialog.
               getOpenFileName(self, "Choose a param excel file to plot",
                               self.mydir, "Files (*csv)"))
        if type(res) == tuple:
            self.fname, __tmp = res
        else:
            self.fname = res
        print(self.fname)
        if self.fname is not None:
            self.mydir = os.path.split(self.fname)[0]
            ficname = os.path.split(self.fname)[-1]
            name = os.path.splitext(ficname)[0]
            # ext = os.path.splitext(ficname)[1]
            path = os.path.split(self.fname)[0]
            folderName = os.path.split(path)[1]
            if folderName[:15] == "mltpleExpeGraph":
                graph_path = path
            else:
                root_path = os.path.split(path)[0]
                # graph_path = os.path.join(root_path, "graphs")
                graph_path = root_path + "/graphs"
            if not os.path.exists(graph_path):
                os.makedirs(graph_path)
            df = pd.read_csv(self.fname, sep=",", skiprows=0, header=0)
            indexes = list(df.iloc[:, 0])
            df.index = indexes
            df = df.drop(df.columns[0], axis=1)
            print(df)
            """
            # suppress unused columns
            df = df.drop(["Unnamed: 0", "mse", "coactpen",
                          "rgserie", "origine", "orig_rg"], axis=1)
            """
            df.index = range(len(df))
            (startline, endline) = choose_lines(list(df.index))
            if int(endline) == len(df)-1:
                df = df[:][int(startline):]
            else:
                df = df[:][int(startline):int(endline)+1]

            # List of titles for each of the radar graphs
            colName = choose_title_col(df)
            lst_title = list(df[colName])
            lst_title = ["{}{}".format(colName,
                                       int(float(x))) for x in lst_title]
            # constructs the sup_title
            titre = "{}/{}".format(graph_path, name)
            titre = titre.replace("\\", "/")
            tit1 = titre[:titre.find("/", int(len(titre)/3)+1)]
            tit2 = titre[titre.find("/", int(len(titre)/3)+1):]
            if len(tit1) < 70:
                tit1tmp = titre[:titre.find("/", int(len(titre)/3)+1)]
                tit2tmp = titre[titre.find("/", int(len(titre)/3)+1):]
                tit1sup = tit2tmp[:tit2tmp.find("/")+1]
                tit2 = titre[len(tit1)+len(tit1sup):]
                tit1 = "{}{}".format(tit1tmp, tit1sup)
            sup_title = "{}\n{}".format(tit1, tit2)

            # enter a sub_title for the chosen serie
            sub_title = GetText(inputDialog="Enter sub-title",
                                inputWindow_name="Sub_title").getInput()

            if self.par_names == []:
                self.par_names = list(df.columns)[0:-5]
            df = df[self.par_names]
            for par in list(df.columns):
                print("{}\t{}\t{}".format(par, df[par].min(), df[par].max()))

            order_pickel_name = graph_path + "/order_param.pkl"
            if os.path.exists(order_pickel_name):
                ordered_df = pd.read_pickle(order_pickel_name)
                ordered_names = list(ordered_df["par_names"])
                self.ordered_par_columns = ordered_names

            ret = 7
            if self.ordered_par_columns is not None:
                for nam in self.ordered_par_columns:
                    print(nam)
                msg = "params have already been ordered \n Use Same order?"
                ret = MessageBox(None, msg, 'Previous param order detected', 3)
                print(ret)
                if ret == 2:
                    print("ESC")
                elif ret == 6:
                    print("YES --> Keep the previous order")
                    df_new = reorder_df(df, self.ordered_par_columns)
                elif ret == 7:
                    print("NO: --> get a new order")

            if ret == 7:
                df_new = reorder_df(df)
                order_param_filename = "{}_{}.order_param".format(name,
                                        sub_title)
                sourcedir = MyWin.graph_path
                destdir = MyWin.graph_path + "/orderedparam"
                filesource = "order_param.pkl"
                filedest = order_param_filename
                ext = ".pkl"
                copyRenameFilewithExt(sourcedir, filesource,
                                      destdir, filedest,
                                      ext, "", replace=0)
                
            col_name = list(df_new.columns)
            self.ordered_par_columns = col_name
            col_syn = [coln for coln in col_name if coln[-6:] == "SynAmp"]
            col_stim = [coln for coln in col_name if coln[-9:] == "CurrentOn"]

            df_radar = copy.deepcopy(df_new)
            """
            for colnam in col_syn:
                df_radar[colnam] *= 10
            """
            df_radar_syn = df_radar.filter(col_syn, axis=1)
            df_radar_stim = df_radar.filter(col_stim, axis=1)
                               
            ylim = (-0.2, 1)
            sub_title_stim = sub_title + "\nSTIM"
            makeRadarFromExcelPar_csv(df_radar_stim, lst_title, sup_title,
                                      sub_title_stim, graph_path, name,
                                      ylim)
            overdrawRadarFromExcelPar_csv(df_radar_stim, lst_title, sup_title,
                                          sub_title_stim, graph_path, name,
                                          ylim)

            # ============================================================
            #                Scale up df_radar_syn
            # ============================================================
            maxsyn = max(df_radar_syn.max())
            max_scale_up = int(1/maxsyn)
            k = 0
            sc_up = 1
            if max_scale_up > 9:
                sc_up = max_scale_up / 10
                k = 1
                while sc_up > 9:
                    sc_up = sc_up / 10
                    k = k + 1
            # scale_up = sc_up * 10 **k
            ymax = 1
            if sc_up > 2:
                ymax = float((sc_up + 1)) / 10 **(k+1)
            elif sc_up > 1:
                ymax = float((sc_up + 0.2)) / 10 **(k+1)
            ylim =  (0, ymax)
            sub_title_syn = sub_title + "\nSYN"
            makeRadarFromExcelPar_csv(df_radar_syn, lst_title, sup_title,
                                      sub_title_syn, graph_path, name,
                                      ylim)
            overdrawRadarFromExcelPar_csv(df_radar_syn, lst_title, sup_title,
                                          sub_title_syn, graph_path, name,
                                          ylim)

    def graphMetrics_GEP(self):
        """
        This method get df_parremain and df_bhvremain dataframes and calls a
        class containing various methods to build graphs for GEP analysis
        - plot and save behavior map
        - plot and save density map of GEP behavior domain
        - plot and save stability map of GEP behavior domain
        - plot and save progression of GEP process with two metric methods
        """
        self.close_otherwin()
        """
        ret = 7
        if self.df_bhvremain is not None:
            msg = "A previous dataframe is present \n Use Same dataframe?"
            ret = MessageBox(None, msg, 'Previous dataframe detected', 3)
            print ret
            if ret == 2:
                print "ESC"
            elif ret == 6:
                print "YES --> Keep the previous dataframe"
                print "df_bhvremain size : {}\n".format(len(self.df_bhvremain))
            elif ret == 7:
                print "NO: --> Look for another dierctory"
        if ret == 7:
            self.make_bhvpardf_bhvparwins()
        """
        ret = self.make_bhvpardf_bhvparwins()
        if ret == 6:
            bhv_xmin = 0
            bhv_xmax = 1.2
            bhv_ymin = 0.0
            bhv_ymax = 1.4
            self.makes_bhvpar_windows(self.df_bhvremain, self.df_parremain,
                                      bhv_xmin, bhv_xmax, bhv_ymin, bhv_ymax)
        if ret in (6, 7):
            if len(self.listGEPFolders) == 1:
                pathGEP = self.listGEPFolders[0]
                parName = self.prevListGEPFiles[0]
                fileGEP = os.path.join(pathGEP, parName)
                self.datastructure = load_datastructure(fileGEP)
            # =============================================================
            self.makeGEPMetrics = GEPGraphsMetrics(self)
            self.makeGEPMetrics.show()
            # =============================================================
            # ============ positionning the Metrics window on screen ==========
            sg = QtWidgets.QDesktopWidget().screenGeometry()
            mywin_height = self.geometry().height()
            metrics_height = self.makeGEPMetrics.geometry().height()
            # graphSet_width = self.graph_settings.geometry().width()
            xshift = 10
            yshift = sg.height() - metrics_height - mywin_height - 40
            self.makeGEPMetrics.screen_loc(xshift=xshift, yshift=yshift)
            # =================================================================

    def closeIt(self):
        """
        doc string
        """
        self.close_otherwin()
        self.close()

    def close_otherwin(self):
        try:
            self.mafen.closeWindows()    # Closes the self.plot_df_bhv window
            self.mafen.nbactivepargraphs = 0
        except Exception as e:
            None
            if verbose > 2:
                print(e)


def get_peaks_and_troughs(df_n, neur, chartName):
    dataY = np.array(df_n[neur])
    # dataX = np.array(df_n.index)
    end = len(df_n) - 1

    n = 2  # the larger n is, the smoother curve will be
    b = [1.0 / n] * n
    a = 1
    dataYY = lfilter(b, a, dataY)
    """
    peaks = find_peaks_cwt(dataY,
                           widths=np.ones(dataY.shape)*2)-1
   
    maxim = df_n[neur].max()
    minim = df_n[neur].min()
    height = (maxim + minim)/2
    peaks, _ = find_peaks(data, height=height)
    """
    res = list(look_for_peaks(dataYY))
    # print(res)
    list_rg = [pk[1] for pk in res]
    if list_rg == []:
        peak_time = df_n.iloc[:][neur].idxmax()
        list_rg = [int(df_n.loc[peak_time]["rg"])]
    if len(list_rg) > 1:
        corrected_list_rg = \
            [list_rg[i]
            for i in range(len(list_rg))
            if (abs(dataYY[list_rg[i]] - dataYY[1]) > 0.01)
            and (dataYY[list_rg[i]] - dataYY[list_rg[i] - 10] > 0.01)]
        if corrected_list_rg == []:
            peak_time = df_n.iloc[list_rg][neur].idxmax()
            corrected_list_rg = [int(df_n.loc[peak_time]["rg"])]
        list_rg_pk = corrected_list_rg
    else:
        list_rg_pk = list_rg

    """
    for i in range(len(list_rg)-1):
        print(abs(dataYY[list_rg[i+1]] - dataYY[list_rg[i]]))
    """
    # print(df_n.index[list_rg])
    # print(dataY[list_rg])
    # plt.plot(dataYY)
    list_rg_min = []
    plt.plot(df_n[neur], "-b", label=neur + "_" + chartName)
    # =============  get the first value ==============
    rg0 = 0
    start_time = df_n.index[0]
    start_value = df_n.iloc[0][neur]
    plt.plot(start_time, start_value, "s")

    # ===========  get the first  minimum value =======
    rg0 = 0
    rg1 = list_rg_pk[0]
    if rg1 <= rg0:
        rg1 = rg0 + 1
    mini_time = df_n.iloc[rg0:rg1][neur].idxmin()
    mini_value = df_n.iloc[rg0:rg1][neur].min()
    if abs(mini_value - start_value) > 0.15:
        mini_rg = int(df_n.loc[mini_time]["rg"])
        list_rg_min.append(mini_rg)
        plt.plot(mini_time, mini_value, "o")
    
    if len(list_rg_pk) > 1:
        idx = 0
        while idx < len(list_rg_pk) -1:
            rg0 = list_rg_pk[idx]
            rg1 = list_rg_pk[idx+1]
            mini_time = df_n.iloc[rg0:rg1][neur].idxmin()
            mini_value = df_n.iloc[rg0:rg1][neur].min()
            mini_rg = int(df_n.loc[mini_time]["rg"])
            list_rg_min.append(mini_rg)
            plt.plot(mini_time, mini_value, "o")
            idx += 1
    else:
        rg1 = list_rg_pk[0]
        
    #============= looks for a trough after last peak ================    
    if df_n.iloc[end][neur] - df_n.iloc[rg1:][neur].min() > 0.05:
            mini_time = df_n.iloc[rg1:][neur].idxmin()
            mini_value = df_n.iloc[rg1:][neur].min()
            mini_rg = int(df_n.loc[mini_time]["rg"])
            list_rg_min.append(mini_rg)
            plt.plot(mini_time, mini_value, "o")
    else:
        list_rg_min.append(end)
        plt.plot(9, df_n.iloc[end][neur], "o")
    
    #plt.plot(dataX, dataYY)
    plt.plot(df_n.index[list_rg_pk], dataY[list_rg_pk], "x")
    plt.legend(loc="lower right", fontsize=14)
    plt.show()

    if (list_rg_min[0], list_rg_pk[0]) == (450, 450):
         valid_lst_rg_pk, valid_lst_rg_min = [],[]
         
    elif list_rg_min[0] < list_rg_pk[0]: # probably started from a plateau
        x = 0
        while abs(df_n.iloc[x][neur] - df_n.iloc[0][neur]) < 0.1:
            x += 1
        firstpeak_idx = x
        start_val = df_n.iloc[0][neur]
        start_time = df_n.index[0]
        n_list_rg_pk = [firstpeak_idx]
        for pk_idx in list_rg_pk:
            n_list_rg_pk.append(pk_idx)
    else:
        n_list_rg_pk = list_rg_pk

    if (list_rg_min[0], list_rg_pk[0]) != (450, 450):
        valid_lst_rg_pk = []
        valid_lst_rg_min = []
        for pk in np.arange(len(n_list_rg_pk)):
            """
            print(pk,"peak:",
                  "{:04.2f}".format(df_n.iloc[n_list_rg_pk[pk]][neur]),
                  end=" ")
            print("trough:",
                  "{:04.2f}".format(df_n.iloc[list_rg_min[pk]][neur]),
                  end=" ")   
            """
            peakval = df_n.iloc[n_list_rg_pk[pk]][neur]
            # preced_minval = df_n.iloc[list_rg_min[pk]][neur]
            next_minval =  df_n.iloc[list_rg_min[pk]][neur]
                
            # if (peakval - preced_minval) > 0.5 and (peakval - next_minval) > 0.5:
            if (peakval - next_minval) > 0.1:
                valid_lst_rg_pk.append(n_list_rg_pk[pk])
                valid_lst_rg_min.append(list_rg_min[pk])
                # print("OK")
            else:
                None
                # print("Rejected")
    return valid_lst_rg_pk, valid_lst_rg_min

"""
Code lines usefull to make bhvplot(), bhnparamplot, densitycontourplot
with a portion of the dataframe (here from lin0 to line 88780)

self=MyWin
bhvremain_cut = self.df_bhvremain.orig_rg < 88780
parremain_cut = self.df_parremain.orig_rg < 88780
self.df_bhvremaintmp = self.df_bhvremain[bhvremain_cut]
self.df_parremaintmp = self.df_parremain[parremain_cut]
self.df_bhvremain = self.df_bhvremaintmp
self.df_parremain = self.df_parremaintmp

self=MyWin.makeGEPMetrics

"""

# ==========================================================================
#                                   MAIN
# ==========================================================================
if __name__ == '__main__':
    # from GEP_GUI import BhvWin
    from GEP_GUI import MaFenetre
    GEP_GUI_win = None
    graphparams = {'legend.fontsize': 'xx-small',
                   'figure.figsize': (15, 5),
                   'axes.labelsize': 'x-small',
                   'axes.titlesize': 'small',
                   'xtick.labelsize': 'x-small',
                   'ytick.labelsize': 'x-small'}
    pylab.rcParams.update(graphparams)
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create("Windows"))
    ag = QtWidgets.QDesktopWidget().availableGeometry()
    sg = QtWidgets.QDesktopWidget().screenGeometry()
    MyWin = GUI_Graph()
    MyWin_height = MyWin.geometry().height()
    MyWin_width = MyWin.geometry().width()
    MyWin.screen_loc(xshift=10, yshift=sg.height()-MyWin_height)

    MyWin.GEP_GUI_win = None  # MyWin.GEP_GUI_win is used when makeGEPMetrics
    #                           is called from GEP_GUI to hold the object name

    MyWin.show()   # Show the form
    app.exec_()     # and execute the app
