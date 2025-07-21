# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 10:22:26 2025
(D. Cattaert)
This script allows to transfert valid parameters from a simple model to a more
complex one that is an extension of the simple one (for example from model
50 parameters to model 52 parameters). The scripts needs the dictonary of
[parameter : value] of the source and destination models.
These dictionaries are created in the subdirectory "Test" by the script
SeekValidParameters.py.
The unmatched names are indicated anf the user is invited to transfer manually
 the values or to give other values.

"""

import os
import tkinter
import tkinter.filedialog as filedialog
import csv
import pickle
import json

import seaborn as sns

import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
from pyqtgraph.Qt import QtCore
from pyqtgraph.Qt import QtGui

import numpy as np

from optimization import readAnimatLabDir
from optimization import getInfoComputer
from optimization import setMotorStimsOff
from optimization import readTabloTxt
from optimization import readTablo
from optimization import findTxtFileName
from optimization import getbehavElts
from optimization import normToRealVal
from optimization import chartToDataFrame

from optimization import load_datastructure
from optimization import save_datastructure
from optimization import mise_a_jour
from optimization import copyRenameFilewithExt
from optimization import copyFileDir_ext
from optimization import copyDirectory
from optimization import actualiseSaveAprojFromAsimFile
from optimization import savechartfile


from makeGraphs import select_chartcol
from makeGraphs import graphfromchart

from SaveInfoComputer import SetComputerInfo

from DialogChoose_in_List import choose_one_element_in_list
from DialogChoose_in_List import choose_elements_in_list
from DialogChoose_in_List import set_values_in_list

from GUI_AnimatPar import saveAnimatLabSimDir

from GEP_GUI import MaFenetre, initAnimatLab

from FoldersArm import FolderOrg
from animatlabOptimSetting import OptimizeSimSettings
import class_animatLabModel as AnimatLabModel
import class_animatLabSimulationRunner as AnimatLabSimRunner
import class_simulationSet as SimulationSet
import class_projectManager as ProjectManager


verbose = 0

def choose_csvFile(animatsimdir, title):
    root = tkinter.Tk()
    root.withdraw()
    csvName = filedialog.askopenfilename(initialdir=animatsimdir,
                                          title=title,
                                          filetypes=(("csv", "*.csv"),
                                                     ("all files", "*.*")))
    csvFileName = csvName
    root.destroy()

    return csvFileName


def read_csvFile(csv_name):   
    with open(csv_name, mode='r') as infile:
        for line in csv.DictReader(infile):
            print(line)
            mydict = line
    for key in mydict.keys():
        val = float(mydict[key])
        mydict[key] = float("{:3.5f}".format(val))
    return mydict

def transfer_values_srcTodest(src_dic, dst_dic):
    for srckey in src_dic.keys():
        if srckey in dst_dic.keys():
            dst_dic[srckey] = src_dic[srckey]
    list_unfound_dstkeys = [key for key in dst_dic
                            if key not in src_dic]
    list_unfound_srckeys = [key for key in src_dic 
                            if key not in dst_dic]
    return  dst_dic, list_unfound_srckeys, list_unfound_dstkeys
    
 
def transfer_remaining(list_unfound_srckeys, list_unfound_dstkeys,
                       typ="ext_stimuli", title="select value to transfer"):
     list_elem = list_unfound_srckeys
     selected = choose_one_element_in_list(title, list_elem, typ)
     return selected
 
def sort_dic(dic):
    sorted_list = sorted(dic.items())
    sorted_dic = {}
    [sorted_dic.update({k:v}) for k,v in sorted_list] 
    names = list(sorted_dic.keys())
    dicValues = sorted_dic
    selected = list(dicValues.keys())
    return sorted_dic
 
    
def get_row_by_name(table, name, column_index=0):
    """
    Retourne le rang (ligne) d'un élément dans une QTableWidget en cherchant par nom.
    :param table: instance de QTableWidget
    :param name: nom à rechercher
    :param column_index: index de la colonne où chercher le nom (par défaut 1)
    :return: numéro de ligne si trouvé, sinon -1
    """
    for row in range(table.rowCount()):
        item = table.item(row, column_index)
        #print(row, item.text())
        if item is not None:
            if item.text() == name:
                return row
    return -1  # si non trouvé 


def selectStimToChange(dic_stim, selected_stim="all"):
    sorted_stim_list = sorted(dic_stim.items())
    sorted_dic_stim = {}
    [sorted_dic_stim.update({k:v}) for k,v in sorted_stim_list] 
    stim_names = list(sorted_dic_stim.keys())
    if selected_stim == "all":
        dicValues = sorted_dic_stim
        selected_stim = list(dicValues.keys())
    else:
        selected_stim = selected_stim
    typ = "ext_stimuli"
    text = "select ext_stimuli to modifiy"
    selected_stim_names = choose_elements_in_list(stim_names, typ,
                                                  selected_stim, text)
    return selected_stim_names, sorted_dic_stim


def selectSynToChange(dic_syn, selected_syn="all"):
    sorted_syn_list = sorted(dic_syn.items())
    sorted_dic_syn = {}
    [sorted_dic_syn.update({k:v}) for k,v in sorted_syn_list]
    syn_names = list(sorted_dic_syn.keys())
    if selected_syn == "all":
        dicValues = sorted_dic_syn
        selected = list(dicValues.keys())
    else:
        selected = selected_syn
    typ = "synapses"
    text = "select synapses to modifiy"
    selected_syn_names = choose_elements_in_list(syn_names, typ, 
                                               selected, text)
    return selected_syn_names, sorted_dic_syn


def selectparam(dic_stim, dic_syn, selected_stim="all", selected_syn="all"):
    # sorted_dic_stim = optSet.sorted_dic_stim
    selected_stim_names, sorted_dic_stims = selectStimToChange(dic_stim,
                                                              selected_stim)
    # sorted_dic_syn = optSet.sorted_dic_syn
    selected_syn_names, sorted_dic_syn = selectSynToChange(dic_syn,
                                                           selected_syn)
    return selected_stim_names, selected_syn_names, sorted_dic_stims, sorted_dic_syn
    

def changeparam(selected_stim_names, selected_syn_names,
                dic_stim, dic_syn):
    dic_stim2 = change_stim_val(selected_stim_names, dic_stim)
    dic_syn2 = change_syn_val(selected_syn_names, dic_syn)
    return dic_stim2, dic_syn2, 


def change_stim_val(selected_stim_names, dic_stim):
    dicValues = {}
    for key in selected_stim_names:
        dicValues[key] = dic_stim[key]
    # selected = list(dicValues.keys())
    selected = selected_stim_names
    typ = "stim settings"
    text = "set settings values"
    dic_stim2 = set_values_in_list(dicValues, selected, typ, text)
    return dic_stim2


def change_syn_val(selected_syn_names, dic_syn):
    dicValues = {}
    for key in selected_syn_names:
        dicValues[key] = dic_syn[key]
    # selected = list(dicValues.keys())
    selected = selected_syn_names
    typ = "syn settings"
    text = "set settings values"
    dic_syn2 = set_values_in_list(dicValues, selected, typ, text)
    return dic_syn2


def getChartListfromDatastructure(datastructure):
    chartList = []
    for sim in datastructure:
        # print(datastructure[sim])
        listchart = datastructure[sim][4][4]
        for chart in listchart:
            chartList.append(chart)
    return chartList


def geterrListfromDatastructure(datastructure):
    errList = []
    for sim in datastructure:
        # print(datastructure[sim])
        listerr = datastructure[sim][4][3]
        for err in listerr:
            errList.append(err)
    return errList

  
def run_parameterSet(optSet, dic_stim2, dic_syn2):
    folders = optSet.folders
    model = optSet.model
    projMan = optSet.projMan
    simSet = SimulationSet.SimulationSet()

    stimParName = optSet.stimParName
    synParName = optSet.synParName
    synNSParName = optSet.synNSParName
    synFRParName = optSet.synFRParName
    
    #sourceAsimFile = optSet.model.asimFile
    #sourceAsimFile = optSet,asimFileName
    
    dic_st = {}
    for key in dic_stim2.keys():
        dic_st[key] = dic_stim2[key]

    vals = []
    simSet.samplePts = []
    for st in stimParName:
        short_st = st[ :st.find(".")]
        val = dic_stim2[short_st] * 1e-9
        vals.append(val)
        simSet.set_by_range({st: [val]})
            
    for sy in synParName:
        short_sy = sy[ :sy.find(".")]
        val = dic_syn2[short_sy]
        vals.append(val)
        simSet.set_by_range({sy: [val]})
    
    for syNS in synNSParName:
        short_syNS = syNS[ :syNS.find(".")]
        val = dic_syn2[short_syNS]
        vals.append(val)
        simSet.set_by_range({syNS: [val]})
    
    for syFR in synFRParName:
        short_syFR = syFR[ :syFR.find(".")]
        val = dic_syn2[short_syFR]
        vals.append(val)
        # print(synFRParName[syFR], val)
        simSet.set_by_range({synFRParName[syFR]: [val]})
    xreal = vals
    
    projMan.make_asims(simSet)
    projMan.run(cores=-1)
    tab = readTabloTxt(folders.animatlab_result_dir,
                       findTxtFileName(model, optSet, "", 1))
    behavElts = getbehavElts(optSet, tab, affich=1)
    [startangle, endangle, oscil1, oscil2, max_speed, endMvt2T, duration,
     varmse, coactpenality, otherpenality, res1, res2] = behavElts
    return behavElts


def saves_test_asim_from_aproj(paramset, sourceAsimFile, optSet, folders, model):
    # bestParamSet = optSet.pairs[pairs_rg, 0:win.nbpar]
    procName = ''
    typ = ""
    simSet = SimulationSet.SimulationSet()
    simSet.samplePts = []
    stimParName = optSet.stimParName
    synParName = optSet.synParName
    synNSParName = optSet.synNSParName
    synFRParName = optSet.synFRParName
    [simSet, vals] = normToRealVal(paramset, optSet, simSet, stimParName,
                                   synParName, synNSParName, synFRParName)
    asim_savedir = "AsimFiles"
    destAsimdir = folders.animatlab_rootFolder + "/Test/" + asim_savedir
    sourceAsimdir = os.path.join(folders.animatlab_result_dir, "tmpBestChart")
    # sourceAsimFile = srcasim
    destName = os.path.splitext(os.path.split(model.asimFile)[-1])[0]
    copyRenameFilewithExt(sourceAsimdir, sourceAsimFile, destAsimdir, destName,
                          ".asim", "", replace=0)
    aproj_savedir = "AprojFiles"
    aprojSaveDir = folders.animatlab_rootFolder + "/Test/" + aproj_savedir
    asimFileName = os.path.join(sourceAsimdir, sourceAsimFile)
    aprojFicName = os.path.split(model.aprojFile)[-1]
    name = os.path.splitext(aprojFicName)[0]
    ext = os.path.splitext(aprojFicName)[1]
    projficName = name + procName + typ + ext
    aprojFileName = os.path.join(aprojSaveDir, projficName)
    complete_name = actualiseSaveAprojFromAsimFile(optSet,
                                                   asimFileName,
                                                   aprojFileName,
                                                   simSet=simSet,
                                                   overwrite=0,
                                                   createSimSet=0,
                                                   affiche=0)
    return complete_name


def saves_chart_asim_aproj(optSet, simulNb, mse, coactP, paramSet):
    folders = optSet.folders
    animatsimdir = folders.animatlab_rootFolder
    resultdir = folders.animatlab_result_dir
    chartdir = animatsimdir + "/Test/ChartFiles"
    if not os.path.exists(chartdir):
        os.makedirs(chartdir)
    aprojdir = animatsimdir + "/Test/AprojFiles"
    if not os.path.exists(aprojdir):
        os.makedirs(aprojdir)
    print(simulNb, "-> rang dans le databhv:", end=' ')
    print(simulNb + len(optSet.pairs))
    if simulNb < 10:
        zero = "0"
    else:
        zero = ""
    comment = "mse:{:.4f}; coactP:{:.4}".format(mse, coactP)
    chart_glob_name = "Test_chart" 
    preTot = ""
    # ======= read the values contained in the last simulation =========
    txtchart = readTabloTxt(resultdir, findTxtFileName(model, optSet,
                            preTot, simulNb + 1))
    comment = "mse:{:.4f}; coactP:{:.4}".format(mse, coactP)

    #===================================================================
    chartName = savechartfile(chart_glob_name,
                              chartdir, txtchart, comment)
    #===================================================================
    
    sourceAsimFile = optSet.model.asimFile
    complete_name = saves_test_asim_from_aproj(paramSet, sourceAsimFile,
                                               optSet, folders, model)
    """
    lst_simulNb.append(simulNb)
    lst_err.append(err)
    win.lst_bestParNb.append(len(optSet.pairs) + simulNb)
    """
    return chartName, complete_name  

    
def load_pairs(testDir):
    """
    Reads a textFile (fname) containing previous pairs (parameters, behav)
    """
    fname = testDir + "/GEPdata/GEPdata00.par"
    GEPdataDir = os.path.split(fname)[0:-1][0]

    print(fname)
    fname = str(fname).format()
    ficname = os.path.split(fname)[-1]
    nomparfic = os.path.splitext(ficname)[0] + ".txt"
    nombhvfic = os.path.splitext(ficname)[0] + "bhv.txt"
    GEPdataDir = os.path.split(fname)[0:-1][0]

    tab_bhv = readTablo(GEPdataDir, nombhvfic)
    tab_bhv = np.array(tab_bhv)
    if len(tab_bhv) == 0:
        print("no other behaviour elements than MSE and coactivation")
    tab_par = readTablo(GEPdataDir, nomparfic)
    tab_par = np.array(tab_par)
    if len(tab_par) > 0:
        optSet.pairs = np.array(tab_par[:, 0:-1])
        optSet.behavs = np.array(tab_bhv[:, 0:-1])
        

def add_pair(optSet, pair, behav):
    """
    add a new numpy array vector to the numpy matrix
    """
    optSet.nbMaxPairs = 500000
    # print(pair)
    if verbose > 3:
        if pair[0] > 1:
            print("params >1 :", end=" ")
            print(pair[0])
            # quit()
        if pair[1] > 1:
            print("params >1 :", end=" ")
            print(pair[1])
            # quit()

    if len(optSet.pairs) == 0:   # this is the 1st addition to optSet.pairs
        optSet.pairs = []
        optSet.pairs.append(pair)
        optSet.pairs = np.array(optSet.pairs)
        optSet.behavs = []
        optSet.behavs.append(behav)
        optSet.behavs = np.array(optSet.behavs)
    elif len(optSet.pairs) < optSet.nbMaxPairs:
        # print(optSet.pairs[-1], end=" ")
        optSet.pairs = np.vstack((optSet.pairs, pair))
        # print(pair)
        # print(optSet.behavs[-1], end=" ")
        if len(optSet.behavs) == 0:   # 1st addition to self.behavs
            optSet.behavs = behav
        else:
            optSet.behavs = np.vstack((optSet.behavs, behav))


def save_pairs(optSet, chartName):
    nam = chartName[:chartName.find(".")]
    lastrun = int(nam[nam.find("chart"):][5:])
    folders = optSet.folders
    parfilename = "GEPdata00.txt"
    animatsimdir = folders.animatlab_rootFolder
    GEPdatadir = animatsimdir + "/Test/GEPdata"
    if not os.path.exists(GEPdatadir):
        os.makedirs(GEPdatadir)
    completeparname = GEPdatadir + "/" + parfilename
    bhvfilename =  "GEPdata00bhv.txt"
    completebhvname =  GEPdatadir + "/" + bhvfilename
    fpar = open(completeparname, 'a')
    # startSerie = 0
    endSerie = len(optSet.datastructure) - 1
    fbhv = open(completebhvname, 'a')
    # ==================== saves GEPdata00.txt ===========================
    idx = len(optSet.pairs) - 1
    pair = optSet.pairs[idx]
    s = ""
    for idy, tmpval in enumerate(pair):
        s += "{:4.8f}".format(tmpval) + '\t'
    s += str(endSerie + 1) + '\n'
    # print(s, end=" ")
    fpar.write(s)
    fpar.close()
    # ================== saves GEPdata00bhv.txt ==========================
    idx = len(optSet.behavs) - 1
    behav = optSet.behavs[idx]
    s = ""
    for idy, tmpval in enumerate(behav):
        s += "{:4.8f}".format(tmpval) + '\t'
    s += str(endSerie + 1) + '\n'
    # print(s, end=" ")
    fbhv.write(s)
    fbhv.close()
    # =================== saves GEPdata00.par ============================
    parfilename = "GEPdata00.par"
    completeparfilename = GEPdatadir + "/" + parfilename
    err = pair[-2] + pair[-1]
    datastructure = optSet.datastructure
    conditions = [optSet.spanStim, optSet.spanSyn,
                  [optSet.xCoactPenality1, optSet.xCoactPenality2],
                  [err], [chartName], [lastrun],
                  [optSet.gravity]]
    mise_a_jour(optSet, datastructure, lastrun, "Test_varmse",
            lastrun+1, lastrun + 1, 1, conditions)
    save_datastructure(datastructure, completeparfilename)
    print("data saved to:", completeparfilename)


def real_to_norm(optSet, dic_stim2, dic_syn2):
    paramSet = []
    for stim in dic_stim2.keys():
        stim_name = stim + ".CurrentOn"
        stim_val = dic_stim2[stim]
        parName = stim_name
        rval = stim_val * 1e-9
        norm = int(optSet.normFromReal(parName, rval) * 100000) / 100000
        paramSet.append(norm)
    for idx, syn in enumerate(dic_syn2.keys()):
        if syn + ".G" in optSet.synParName:
            syn_name = syn + ".G"
            syn_val = dic_syn2[syn]
            parName = syn_name
            rval = syn_val
            norm = int(optSet.normFromReal(parName, rval) * 100000) / 100000
            paramSet.append(norm)
        elif syn + ".SynAmp" in optSet.synNSParName:
            synNS_name = syn + ".SynAmp"
            synNS_val = dic_syn2[syn]
            parName = synNS_name
            rval = synNS_val
            norm = int(optSet.normFromReal(parName, rval) * 100000) / 100000
            paramSet.append(norm)
        elif syn + ".Weight" in optSet.synFRParName:
            synFR_name = syn + ".Weight"
            synFR_val = dic_syn2[syn]
            parName = synFR_name
            rval = synFR_val
            norm = int(optSet.normFromReal(parName, rval) * 100000) / 100000
            paramSet.append(norm)
    return paramSet


def norm_to_real(optSet, paramset, dic_stim, dic_syn):
    simSet = SimulationSet.SimulationSet()
    simSet.samplePts = []
    stimParName = optSet.stimParName
    synParName = optSet.synParName
    synNSParName = optSet.synNSParName
    synFRParName = optSet.synFRParName
    [simSet, vals] = normToRealVal(paramset, optSet, simSet,
                                   stimParName, synParName,
                                   synNSParName, synFRParName)
    stim_vals = vals[: len(dic_stim)]
    syn_vals = vals[len(dic_stim):]
    dic_stim_temp = {}
    for idx, stimName in enumerate(list(dic_stim.keys())):
        dic_stim_temp[stimName] = float(int(stim_vals[idx]*1e9 *100000))/100000 
    dic_syn_temp = {}
    for idx, synName in enumerate(list(dic_syn.keys())):
        dic_syn_temp[synName] = syn_vals[idx]
    return dic_stim_temp, dic_syn_temp


def df_from_chart(optSet, chart_path, chartName, comment=""):
    colnames = optSet.chartColNames
    completeName = os.path.join(chart_path, chartName)
    baseName = os.path.splitext(chartName)[0]
    rootname = os.path.split(chart_path)[0]
    result_path = rootname
    expename2 = os.path.split(rootname)[1]
    split2 = os.path.split(rootname)[0]
    expename1 = os.path.split(split2)[1]
    split1 = os.path.split(split2)[0]
    expename0 = os.path.split(split1)[1]
    experoot = expename0 + "/" + expename1 + "/" + expename2 
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
    my_palette = sns.color_palette("tab10")
    (L, df, tit, tabparams) = chartToDataFrame(completeName, colnames=colnames)
        
    dfsrtTime = df.Time[0]
    # dfendTime = df.Time[len(df)-1]
    dfendTime = 9.99
    df.index = df.Time
    df[:0.6]
    return df, dfsrtTime, dfendTime

  
    
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, optSet, src_dic_stim, src_dic_syn,
                 dst_dic_stim, dst_dic_syn, parent=None):
        super(MainWindow, self).__init__(parent)
        self.optSet = optSet
        self.src_dic_stim2 = sort_dic(src_dic_stim)
        self.src_dic_syn2 = sort_dic(src_dic_syn)
        self.dst_dic_stim2 = sort_dic(dst_dic_stim)
        self.dst_dic_syn2 = sort_dic(dst_dic_syn)
        self.simulNb = 0
        if optSet.errList == []:
            self.minerr = 100000
        else:
            self.minerr = min(optSet.errList)
        self.behavElements = optSet.behavElts
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Dictionnaires & Graphiques")
        
        # Configuration du layout principal
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        layout = QtWidgets.QVBoxLayout(main_widget)
        
        # Section supérieure (tableaux + graphiques)
        top_layout = QtWidgets.QHBoxLayout()
        
        """
            ==============================================
                 Left part : dictionary tables
            ==============================================
        """ 
        self.srcExtStim = QtWidgets.QLabel("       Source Ext Stimuli    ")
        self.srcExtStim.setMinimumSize(QtCore.QSize(0, 27))
        self.srcConnexions = QtWidgets.QLabel("              Source Connexions               ")
        self.srcConnexions.setMinimumSize(QtCore.QSize(0, 27))
        self.dstExtStim = QtWidgets.QLabel("   Destination Ext Stimuli   ")
        self.dstExtStim.setMinimumSize(QtCore.QSize(0, 27))
        self.dstConnexions = QtWidgets.QLabel("            Destination Connexions            ")
        self.dstConnexions.setMinimumSize(QtCore.QSize(0, 27))

        tables_widget = QtWidgets.QWidget()
        tables_layout = QtWidgets.QHBoxLayout(tables_widget)
        tabsrc_stim_vertical_with_title = QtWidgets.QVBoxLayout(tables_widget)
        tabsrc_syn_vertical_with_title = QtWidgets.QVBoxLayout(tables_widget)
        tabdst_stim_vertical_with_title = QtWidgets.QVBoxLayout(tables_widget)
        tabdst_syn_vertical_with_title = QtWidgets.QVBoxLayout(tables_widget)
        self.src_stimTable = self.create_dict_table(self.src_dic_stim2,
                                                    "Extl Stimuli",
                                                    ['Clé', 'Valeur (nA)'])
        self.src_stimTable.setMinimumWidth(100)
        self.src_synTable = self.create_dict_table(self.src_dic_syn2,
                                                   "Connexions",
                                                   ['Clé', 'Valeur (nS)'])
        self.src_synTable.setMinimumWidth(250)
        self.dst_stimTable = self.create_dict_table(self.dst_dic_stim2,
                                                    "Extl Stimuli",
                                                    ['Clé', 'Valeur (nA)'])
        self.dst_stimTable.setMinimumWidth(100)
        self.dst_synTable = self.create_dict_table(self.dst_dic_syn2,
                                                   "Connexions",
                                                   ['Clé', 'Valeur (nS)'])
        self.dst_synTable.setMinimumWidth(250)
        tabsrc_stim_vertical_with_title.addWidget(self.srcExtStim)
        tabsrc_stim_vertical_with_title.addWidget(self.src_stimTable)
        tabsrc_syn_vertical_with_title.addWidget(self.srcConnexions)
        tabsrc_syn_vertical_with_title.addWidget(self.src_synTable)
        tabdst_stim_vertical_with_title.addWidget(self.dstExtStim)
        tabdst_stim_vertical_with_title.addWidget(self.dst_stimTable)
        tabdst_syn_vertical_with_title.addWidget(self.dstConnexions)
        tabdst_syn_vertical_with_title.addWidget(self.dst_synTable)
        tables_layout.addLayout(tabsrc_stim_vertical_with_title)
        tables_layout.addLayout(tabsrc_syn_vertical_with_title)
        tables_layout.addLayout(tabdst_stim_vertical_with_title)
        tables_layout.addLayout(tabdst_syn_vertical_with_title)

        # ================================================
        top_layout.addWidget(tables_widget, 40)
        # ================================================
        
        
        """
            ==============================================
                 Right part : Graphs from chart
            ==============================================
        """   
        graph_widget = QtWidgets.QWidget()
        graph_container = QtWidgets.QWidget()
        graph_layout =  QtWidgets.QGridLayout(graph_container)
        graph_vertival_with_comment = QtWidgets.QVBoxLayout(graph_widget)
        otherpenality = self.behavElements[9]
        text2 = ""
        varmse = self.behavElements[7]
        coact = self.behavElements[8]
        text2 += "varmse:{:.4f}   coact:{:.4f}     ".format(varmse, coact)
        for key in otherpenality:
            text2 += key + ":{:.4f}    ".format(otherpenality[key])
        durMvt2 = self.behavElements[6]
        text2 += "mvt duration: {:.3f}".format(durMvt2) 
        self.graph_comment = QtWidgets.QLabel(text2)
        graph_vertival_with_comment.addWidget(self.graph_comment)
        
        optSet = self.optSet
        colnames = optSet.chartColNames
        folders = optSet.folders
        chart_path = folders.animatlab_result_dir
        chartName = findTxtFileName(optSet.model, optSet, "", 1)    
        self.build_df_chart(chart_path, chartName)
        sens = optSet.chart_column_to_plot[0]
        alpha = optSet.chart_column_to_plot[1]
        other = optSet.chart_column_to_plot[2]
        self.dic_col = {}
        self.dic_color = {sens[0]: 'magenta', sens[1]: 'cyan',
                          sens[3]: 'pink', sens[2]: 'lightblue',
                          alpha[0]: 'red', alpha[1]: 'blue',
                          '1FlxPotMuscle': 'brown', '1ExtPotMuscle': "darkgreen",
                          '1FlxPN': 'orange', '1ExtPN': 'lightgreen',
                          'Biceps1' : 'red', 'Triceps1': "blue",
                          'Elbow': "darkgreen"}

        self.graph1 = self.create_plot_widget(["Elbow"], self.dic_color,
                                              "Time (sec)",
                                              "Angle (deg)")
        self.dic_col[self.graph1] = ["Elbow"]

        self.muscle = ["Triceps1", "Biceps1"]
        self.graph2 = self.create_plot_widget(self.muscle, self.dic_color,
                                              "Time (sec)",
                                              "Force (N)")
        self.dic_col[self.graph2] = ["Triceps1", "Biceps1"]

        list_col0 = optSet.chart_column_to_plot[0]
        self.list_col0 = list_col0
        self.graph3 = self.create_plot_widget(list_col0, self.dic_color,
                                              "Time (sec)",
                                              "Membrane potentia (mV)")
        self.dic_col[self.graph3] = list_col0

        list_col1 = optSet.chart_column_to_plot[1]
        self.list_col1 = list_col1
        self.graph4 = self.create_plot_widget(list_col1, self.dic_color,
                                              "Time (sec)",
                                              "Membrane potential (mV)")                                              
        self.dic_col[self.graph4] = list_col1
           
        list_col2 = optSet.chart_column_to_plot[2]
        self.list_col2 = list_col2    
        self.graph5 = self.create_plot_widget(list_col2, self.dic_color,
                                              "Time (sec)",
                                              "Membrane potential (mV)")
        self.dic_col[self.graph5] = list_col2
        
        list_col = optSet.chart_column_to_plot[0] +\
                   optSet.chart_column_to_plot[1] +\
                   optSet.chart_column_to_plot[2]    
        self.list_col = list_col   
        self.graph6 = self.create_plot_widget(list_col, self.dic_color,
                                              "Time (sec)",
                                              "Membrane potential (mV)")
        self.dic_col[self.graph6] = list_col
        
        self.list_graphs = list(self.dic_col.keys())

        graph_layout.addWidget(self.graph1, 0, 0, 1, 1)
        graph_layout.addWidget(self.graph2, 0, 1, 1, 1)
        graph_layout.addWidget(self.graph3, 0, 2, 1, 1)
        graph_layout.addWidget(self.graph4, 1, 0, 1, 1)
        graph_layout.addWidget(self.graph5, 1, 1, 1, 1)
        graph_layout.addWidget(self.graph6, 1, 2, 1, 1)
        
        graph_vertival_with_comment.addWidget(graph_container, 6)
        
        # ================================================
        top_layout.addWidget(graph_widget, 60)
        # ================================================
        
        
        """
            ==============================================
                 lower part : series of buttons
            ==============================================
        """           
        button_layout =  QtWidgets.QHBoxLayout()
        self.btn_copy_from_src =  QtWidgets.QPushButton("copy from source")
        self.btn_run_dst_param =  QtWidgets.QPushButton("run dst param")
        self.btnSave = QtWidgets.QPushButton("Save dst asim_aproj_chart")
        self.btnQuit =  QtWidgets.QPushButton("Quit")
        button_layout.addWidget(self.btn_copy_from_src)
        button_layout.addWidget(self.btn_run_dst_param)
        button_layout.addWidget(self.btnSave)
        button_layout.addWidget(self.btnQuit)
        
                
        layout.addLayout(top_layout, 80)
        layout.addLayout(button_layout, 20)

        
        self.font = QtGui.QFont()
        self.font.setBold(False)
        self.font.setPointSize(12)
        self.font.setWeight(75)
        self.srcExtStim.setFont(self.font)
        self.srcConnexions.setFont(self.font)
        self.dstExtStim.setFont(self.font)
        self.dstConnexions.setFont(self.font)
        
        self.btn_copy_from_src.setFont(self.font)
        self.btn_run_dst_param.setFont(self.font)
        self.btnSave.setFont(self.font)
        self.btnQuit.setFont(self.font)
        
        self.btnSave.setEnabled(False)
        #self.btnNext.setEnabled(False)
        #self.btnMakeSeeds.setEnabled(False)
        #self.btnAddToSeeds.setEnabled(False)
        
        # ======================================================
        #          Actions
        # ======================================================
        self.dst_stimTable.cellChanged.connect(self.update_dst_stimTable)
        self.dst_synTable.cellChanged.connect(self.update_dst_synTable)   
        self.btn_copy_from_src.clicked.connect(self.transfer_matched)
        self.btn_run_dst_param.clicked.connect(self.run_dst_param)
        self.btnSave.clicked.connect(self.save)
        self.btnQuit.clicked.connect(self.closeIt)


        self.list_unfound_src_stimkeys = []
        self.list_unfound_dst_stimkeys = []
        
        
        self.nb_run = len(optSet.datastructure)
        if self.nb_run > 0:
            self.present_run = self.nb_run -1
            chartList = getChartListfromDatastructure(datastructure)
            chartName = chartList[-1]
            chart_path = chart_path = animatsimdir + "/Test/ChartFiles"
            self.actualize_graphs(chart_path, chartName)
            self.chart_name = chartName
            self.actualize_graph_comment(chart_path, chartName)
            #self.btnAddToSeeds.setEnabled(True)

        else:
            self.present_run = -1
            #Èself.btnNext.setEnabled(False)
            #self.btnPrevious.setEnabled(False)
            self.chart_name = "unsaved"
        
        
    def create_dict_table(self, source_dict, title, columnTit):
        table = QtWidgets.QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(['Clé', 'Valeur (nA)'])
        table.horizontalHeader().\
            setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        table.blockSignals(True)
        table.setRowCount(len(source_dict))
        for row, key in enumerate(source_dict):
            value = source_dict[key]
            table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(key)))
            table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(value)))        
        table.blockSignals(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.setWindowTitle(title)
        return table

    def update_dst_stimTable(self, row, column):
        key_item = self.dst_stimTable.item(row, 0)
        value_item = self.dst_stimTable.item(row, 1)
        
        if key_item and value_item:
            old_key = list(self.dst_dic_stim2.keys())[row]
            new_key = key_item.text()
            new_value = value_item.text()
            
            if new_key != old_key:
                self.dst_dic_stim2[new_key] = self.dst_dic_stim2.pop(old_key)
            self.dst_dic_stim2[new_key] = float(new_value)
    
    def update_dst_synTable(self, row, column):
        key_item = self.dst_synTable.item(row, 0)
        value_item = self.dst_synTable.item(row, 1)
        
        if key_item and value_item:
            old_key = list(self.dst_dic_syn2.keys())[row]
            new_key = key_item.text()
            new_value = value_item.text()
            
            if new_key != old_key:
                self.dst_dic_syn2[new_key] = self.dst_dic_syn2.pop(old_key)
            self.dst_dic_syn2[new_key] = float(new_value)
    
    def actualize_dst_stimTable(self, dst_dic_stim2):
        for row, key in enumerate(dst_dic_stim2):
            value = dst_dic_stim2[key]
            self.dst_stimTable.setItem(row, 1,
                                   QtWidgets.QTableWidgetItem(str(value)))  

    def actualize_dst_synTable(self, dst_dic_syn2):
        for row, key in enumerate(dst_dic_syn2):
            value = dst_dic_syn2[key]
            self.dst_synTable.setItem(row, 1,
                                  QtWidgets.QTableWidgetItem(str(value))) 
    
    def transfer_matched(self):
        res = transfer_values_srcTodest(self.src_dic_stim2, self.dst_dic_stim2)
        self.dst_dic_stim2 = res[0]
        self.list_unfound_src_stimkeys = res[1]
        self.list_unfound_dst_stimkeys = res[2]        
        self.actualize_dst_stimTable(self.dst_dic_stim2)
        for stim in self.list_unfound_src_stimkeys:
            row = get_row_by_name(self.src_stimTable, stim)
            print(stim, row)
            item = self.src_stimTable.item(row,1)
            item.setBackground(QtGui.QColor('yellow'))
            
        for stim in self.list_unfound_dst_stimkeys:  
            row2 = get_row_by_name(self.dst_stimTable, stim)
            item = self.dst_stimTable.item(row2,1)
            item.setBackground(QtGui.QColor('magenta'))

        res2 = transfer_values_srcTodest(self.src_dic_syn2, self.dst_dic_syn2)
        self.dst_dic_syn2 = res2[0]
        self.list_unfound_src_synkeys = res2[1]
        self.list_unfound_dst_synkeys = res2[2]
        self.actualize_dst_synTable(self.dst_dic_syn2)
        for syn in self.list_unfound_src_synkeys:
            row3 = get_row_by_name(self.src_synTable, syn)
            item = self.src_stimTable.item(row3,1)
            item.setBackground(QtGui.QColor('yellow'))
        for syn in self.list_unfound_dst_synkeys: 
            row4 = get_row_by_name(self.dst_synTable, syn)
            item = self.dst_synTable.item(row4,1)
            item.setBackground(QtGui.QColor('magenta'))


    def build_df_chart(self, chart_path, chartName):
        optSet=self.optSet
        df, dfsrtTime, dfendTime = df_from_chart(optSet, chart_path,
                                                 chartName, comment="")
        self.df = df
        self.dfsrtTime = dfsrtTime
        self.dfendTime = dfendTime
        # self.xmin = copy.deepcopy(self.dfsrtTime)
        # self.xmax = copy.deepcopy(self.dfendTime)
        self.xmin = 4.8
        self.xmax = 6.5

    def create_plot_widget(self, list_col, dic_color, xlabel, ylabel):
        """Initialise un graphique PyQtGraph"""
        plot = pg.PlotWidget()
        plot.setMaximumSize(300, 400)
        plot.setMinimumSize(300, 400)
        plot.setBackground('w')
        plot.setXRange(self.xmin, self.xmax)
        plot.addLegend(y=4, pen='y', offset=(0., .5))
        styles = {'color':'w', 'font-size':'14px'}
        plot.setLabel('bottom', xlabel, **styles)
        plot.setLabel('left', ylabel, **styles)
        Time = list(self.df.index)
        for name in list_col:
            tab =  self.df[name].tolist()        
            plot.plot(Time, tab,
                      pen=pg.mkPen(dic_color[name], width=2), name=name) 
        return plot    
    """
    def set_unmatched(self):
        transfer_remaining(self.list_unfound_src_stimkeys,
                           self.list_unfound_dst_stimkeys)
    """
    
    def actualize_graphs(self,  chart_path, chartName):
        for graph in self.list_graphs:
            graph.clear()
        self.build_df_chart(chart_path, chartName)
        
        for graph in self.list_graphs:
            list_col = self.dic_col[graph]
            graph.addLegend()
            Time = list(self.df.index)
            for name in list_col:
                tab =  self.df[name].tolist()
                color = self.dic_color[name]
                graph.plot(Time, tab, pen=pg.mkPen(color, width=2), name=name)

    def actualize_graph_comment(self, chart_path, chartName):
        tab = readTabloTxt(chart_path, chartName)
        behavElts = getbehavElts(optSet, tab, affich=0)
        [startangle, endangle, oscil1, oscil2, max_speed, endMvt2T, duration,
         varmse, coact, otherpenality, res1, res2] = behavElts
        text2 = self.chart_name + "     "
        text2 += "varmse:{:.4f}   coact:{:.4f}     ".format(varmse, coact)
        for key in otherpenality:
            text2 += key + ":{:.4f}    ".format(otherpenality[key])
        durMvt2 = self.behavElements[6]
        text2 += "mvt duration: {:.3f}".format(durMvt2)
        self.graph_comment.setText(text2)
                
    def actualizeStimTable(self, dic_stim2):
        for row, key in enumerate(dic_stim2):
            value = dic_stim2[key]
            self.stimTable.setItem(row, 1,
                                   QtWidgets.QTableWidgetItem(str(value)))  

    def actualizeSynTable(self, dic_syn2):
        for row, key in enumerate(dic_syn2):
            value = dic_syn2[key]
            self.synTable.setItem(row, 1,
                                  QtWidgets.QTableWidgetItem(str(value))) 
    
    def run_dst_param(self):
        optSet = self.optSet
        self.behavElements =\
            run_parameterSet(optSet, self.dst_dic_stim2, self.dst_dic_syn2)
        paramSet = real_to_norm(optSet, self.dst_dic_stim2, self.dst_dic_syn2)
        self.paramSet = paramSet
        resbehav = self.behavElements[:8]
        varmse = self.behavElements[7]
        coact = self.behavElements[8]
        mse_coact = [varmse, coact]
        self.behav = np.concatenate([mse_coact, resbehav])
        self.pair = np.concatenate([paramSet, mse_coact])
        
        optSet = self.optSet
        chart_path = folders.animatlab_result_dir
        chartName = findTxtFileName(model, optSet, "", 1)
        self.actualize_graphs(chart_path, chartName)
        self.chart_name = "unsaved"
        self.actualize_graph_comment(chart_path, chartName)
        self.btnSave.setEnabled(True)
        #self.btnAddToSeeds.setEnabled(False)
        
    def save(self):
        simulNb = self.simulNb
        add_pair(optSet, self.pair, self.behav)
        mse, coactP = self.behavElements[7], self.behavElements[8]
        paramSet = real_to_norm(optSet, self.dst_dic_stim2, self.dst_dic_syn2)
        chartName, complete_name = saves_chart_asim_aproj(optSet, simulNb, 
                                                          mse, coactP,
                                                          paramSet)
        self.chartName = chartName
        save_pairs(optSet, chartName)
        varmse = self.behavElements[7]
        if varmse<self.minerr:
            self.minerr = varmse
            model.saveXML(overwrite=True)
            aprojsourcedir = os.path.split(complete_name)[0]
            aprojName = os.path.split(complete_name)[-1]
            destdir = animatsimdir + "/Test/FinalModel"
            aprojdestName = os.path.split(model.aprojFile)[-1]
            ext = ".aproj"
            comment = ""
            copyRenameFilewithExt(aprojsourcedir, aprojName,
                                  destdir, aprojdestName,
                                  ".aproj", comment, replace=1)
            asimsourcedir = animatsimdir + "/FinalModel"
            asimName = os.path.split(model.asimFile)[-1]
            copyRenameFilewithExt(asimsourcedir, asimName,
                                  destdir, asimName,
                                  ".asim", comment, replace=1)
            copyFileDir_ext(asimsourcedir, destdir, [".aform"], copy_dir=0)

        chart_path = animatsimdir + "/Test/ChartFiles"
        templateFileName = animatsimdir + "/ResultFiles/template.txt"
        otherpenality = self.behavElements[9]
        text2 = ""
        for key in otherpenality:
            text2 += key + ":{:.2f}    ".format(otherpenality[key])
        durMvt2 = self.behavElements[6]
        text2 += "mvt duration: {:.2f}".format(durMvt2) 
        if not os.path.exists(animatsimdir + "/Test/ResultFiles"):
            sourcedir = animatsimdir + "/ResultFiles"
            destdir = animatsimdir + "/Test/ResultFiles"
            copyDirectory(sourcedir, destdir)
        graphfromchart(optSet, chart_path, chartName, templateFileName,
                       comment=text2)
        print("{} saved to {}".format(chartName, chart_path))
        self.nb_run += 1
        self.present_run += 1
        self.chart_name = chartName
        self.actualize_graph_comment(chart_path, chartName)
        #Vif self.present_run > 0:
            #self.btnPrevious.setEnabled(True)
    
    def closeIt(self):
        """
        doc string
        """
        self.close()
 
# =============================================================================
#                                   MAIN
# =============================================================================
if __name__ == '__main__':
    import sys
    
    root = tkinter.Tk()
    root.withdraw()
    
    previousanimatsimdir = readAnimatLabDir()
    dirname = filedialog.askdirectory(parent=root,
                                      initialdir=previousanimatsimdir,
                                      title='Select source base directory')
    animatsimdir = dirname
    if animatsimdir != "":
        saveAnimatLabSimDir(animatsimdir)
    animatsimdir = readAnimatLabDir()
    src_dic_dir = animatsimdir + "/Test"
    #src_dic_stim_name = choose_csvFile(src_dic_dir, "source dic_stim")
    src_dic_stim_name = src_dic_dir + "/dic_stim.csv"
    src_dic_stim = read_csvFile(src_dic_stim_name)
    #src_dic_syn_name = choose_csvFile(src_dic_dir, "source dic_syn")
    src_dic_syn_name = src_dic_dir + "/dic_syn.csv"
    src_dic_syn = read_csvFile(src_dic_syn_name)


    previousanimatsimdir = readAnimatLabDir()
    dirname = filedialog.askdirectory(parent=root,
                                      initialdir=previousanimatsimdir,
                                      title='Select dest base directory')
    animatsimdir = dirname
    if animatsimdir != "":
        saveAnimatLabSimDir(animatsimdir)
    animatsimdir = readAnimatLabDir()
    dst_dic_dir = animatsimdir + "/Test"
    #dst_dic_stim_name = choose_csvFile(dst_dic_dir, "destination dic_stim")
    dst_dic_stim_name = dst_dic_dir + "/dic_stim.csv"
    dst_dic_stim = read_csvFile(dst_dic_stim_name)
    #dst_dic_syn_name = choose_csvFile(dst_dic_dir, "destination dic_syn")
    dst_dic_syn_name = dst_dic_dir + "/dic_syn.csv"
    dst_dic_syn = read_csvFile(dst_dic_syn_name)
    
    root.destroy()
    
    
    pg.mkQApp()
    # ================  Initialises with infoComputer  ==================
    dialogue = "Choose the folder where animatLab V2 is stored (includes/bin)"
    animatLabV2ProgDir, nb_procs = getInfoComputer()
    if animatLabV2ProgDir == '':
        print("first instance to access to animatLab V2/bin")
        app = QtWidgets.QApplication(sys.argv)
        ComputInfoWin = SetComputerInfo(dialogue)
        ComputInfoWin.show()   # Show the form
        app.exec_()     # and execute the app
        print("animatLab V2/bin path and nb_procs have been saved", end=' ')
        print("in infos_computer.txt")
        animatLabV2ProgDir, nb_procs = getInfoComputer()
    # ===================================================================
    res = initAnimatLab(animatsimdir, animatLabV2ProgDir)
    OK = res[0]
    if OK:
        aprojFicName = res[4]
        optSet = res[5]
        model = optSet.model
        folders = optSet.folders
        projMan = optSet.projMan
        setMotorStimsOff(model, optSet.motorStimuli)
        asimName = os.path.split(model.asimFile)[-1]
    datastructure = optSet.datastructure
    if len(datastructure) > 0:
        errList = geterrListfromDatastructure(datastructure)
    else:
        errList = []
    optSet.errList = errList
    
    selected_stim = list(dst_dic_stim.keys())
    selected_syn = list(dst_dic_syn.keys())
    rep = selectparam(dst_dic_stim, dst_dic_syn, selected_stim, selected_syn)
    selected_stim_names = rep[0]
    selected_syn_names = rep[1]
    sorted_dic_stims = rep[2]
    sorted_dic_syn = rep[3]
    
    dic_stim2, dic_syn2 = changeparam(selected_stim_names, selected_syn_names,
                                      dst_dic_stim, dst_dic_syn)    
    behavElts = run_parameterSet(optSet, dst_dic_stim, dst_dic_syn)
    optSet.behavElts = behavElts
    
    app = QtWidgets.QApplication(sys.argv)
    TransWin = MainWindow(optSet, src_dic_stim, src_dic_syn,
                          dst_dic_stim, dst_dic_syn)
    TransWin.show()   
    sys.exit(app.exec_())
    
    #transfer_remaining(list_unfound_src_stimkeys, list_unfound_dst_stimkeys)
