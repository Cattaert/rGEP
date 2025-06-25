# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 10:19:24 2025
Python scritp to handle Stimuli and Synapses, to run an AnilmatLab model, and
do save the good parameter sets, aproj and asim in specific sub-directories
@author: cattaert

Modified March 18, 2025 (D. Cattaert):
    optSet.errList added (get from datastructure)
Modified june 26, 2025 (D. Cattaert):
    The previous list of selected variables is now proposed in the selection
    windows
    Two new buttons added 
     - to add the current (saved) run in a list of seeds
     - to save this list and create a seed directory that can be used in 
         buildCOntrolScript.py. Note that the seed directory is a sub directory
         of the Test directory in which seekValidParam.py is working.
         the content of this Seed_directory  (Test_Seeds0x) is then copued to
         a conventional seed directory (0_IDYYYY_seedsOZ). For this procedure
         work correctly IT IS IMPORTANT TO CHOOSE a base_directory when runing
         seekValidParam.py
"""

import os
import tkinter
import tkinter.filedialog as filedialog
import csv
import copy

import pickle
import json

import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
from pyqtgraph.Qt import QtCore
from pyqtgraph.Qt import QtGui
from PyQt5.QtWidgets import QInputDialog, QLineEdit

import numpy as np
import pandas as pd

import seaborn as sns

from optimization import showdialog
from optimization import readAnimatLabDir
from optimization import copyDirectory
from optimization import getInfoComputer
from optimization import readGravity
from optimization import readGravityfromAsim
from optimization import readCoacPenality
from optimization import readSpan_from_DicSpanVal
from optimization import normToRealVal
from optimization import readTablo
from optimization import readTabloTxt
from optimization import findTxtFileName
from optimization import testquality
from optimization import getbehavElts
from optimization import getSimSetFromAsim
from optimization import setMotorStimsOff
from optimization import savechartfile
from optimization import findList_asimFiles
from optimization import copyFileDir_ext
from optimization import copyRenameFilewithExt
from optimization import actualiseSaveAprojFromAsimFile
from optimization import chartToDataFrame
from optimization import load_datastructure
from optimization import save_datastructure
from optimization import mise_a_jour
from optimization import testVarMsePlot
from optimization import copyFileDir
from optimization import copyFile
from optimization import copyFileWithExt
from optimization import copyRenameFilewithExt

from makeGraphs import select_chartcol
from makeGraphs import graphfromchart

from SaveInfoComputer import SetComputerInfo
from GUI_AnimatPar import saveAnimatLabSimDir
from GEP_GUI import MaFenetre, initAnimatLab
from GEP_GUI import copyTo_0_idXXX_Seeds0x

from DialogChoose_in_List import choose_one_element_in_list
from DialogChoose_in_List import choose_elements_in_list
from DialogChoose_in_List import set_values_in_list
from DialogChoose_in_List import MyMessageBox
from DialogChoose_in_List import DialogBoxValues

from FoldersArm import FolderOrg
from animatlabOptimSetting import OptimizeSimSettings
import class_animatLabModel as AnimatLabModel
import class_animatLabSimulationRunner as AnimatLabSimRunner
import class_simulationSet as SimulationSet
import class_projectManager as ProjectManager


verbose = 3

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context,
                                            text,
                                            disambig,
                                            _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)



def chooseAsimFile(optSet, animatsimdir):
    root = tkinter.Tk()
    root.withdraw()
    asimName = filedialog.askopenfilename(initialdir=animatsimdir,
                                          title="Select asim file",
                                          filetypes=(("asim", "*.asim"),
                                                     ("all files", "*.*")))
    asimFileName = asimName
    root.destroy()
    optSet.actualizeparamCMAes()

    return optSet, asimFileName


def getparamsFromAsim(optSet, asimFileName):
    seriesStimParam = ['CurrentOn', 'StartTime', 'EndTime']
    seriesSynParam = optSet.seriesSynParam
    # seriesSynNSParam = optSet.seriesSynNSParam
    seriesSynNSParam = ['SynAmp', 'ThreshV']
    seriesSynFRParam = optSet.seriesSynFRParam

    res = getSimSetFromAsim(optSet, seriesStimParam, seriesSynParam,
                            seriesSynNSParam, seriesSynFRParam,
                            asimFileName, affiche=1)
    asimSimSet = res[0]
    asimtab_stims = res[1]
    asimtab_motors = res[2]
    asimtab_connexions = res[3]
    asimtab_connexionsFR = res[4]
    
    # asimSimSet.samplePts
                      
    projMan.make_asims(asimSimSet)
    projMan.run(cores=-1)
    tab = readTabloTxt(folders.animatlab_result_dir,
                       findTxtFileName(model, optSet, "", 1))
    # quality = testquality(optSet, tab, optSet.template, "")
    behavElts = getbehavElts(optSet, tab, affich=1)
    [startangle, endangle, oscil1, oscil2, max_speed, endMvt2T, duration,
     varmmse, coactpenality, otherpenality, res1, res2] = behavElts

    dic_stim = {}
    for idx, stim in enumerate(asimtab_stims):
        if idx in optSet.stimList:
            # print(stim[0])
            stimName = stim[0]
            stimVal = stim[3]
            dic_stim[stimName] = int(stimVal * 1e9 *100000)/100000

    dic_syn = {}
    for idx, syn in enumerate(asimtab_connexions):
        if idx in optSet.synList:
            # print(syn[0])
            if syn[5] == "SpikingChemical":
                syn_name = syn[0]
                syn_val = syn[1]
                dic_syn[syn_name] = syn_val
            if syn[5] == "NonSpikingChemical":
                synNS_name = syn[0]
                synNS_val = syn[1]
                dic_syn[synNS_name] = synNS_val
    for idx, synName in enumerate(optSet.synFRParName):
        rg = optSet.synListFR[idx]
        synFR_name = synName[:synName.find(".")]
        syn = asimtab_connexionsFR[rg]
        synFR_val = syn[1]
        dic_syn[synFR_name] = synFR_val
    return dic_stim, dic_syn


def selectparam(dic_stim, dic_syn, selected_stim="all", selected_syn="all"):
    # sorted_dic_stim = optSet.sorted_dic_stim
    selected_stim_names = selectStimToChange(dic_stim, selected_stim)
    # sorted_dic_syn = optSet.sorted_dic_syn
    selected_syn_names = selectSynToChange(dic_syn, selected_syn)
    return selected_stim_names, selected_syn_names


def changeparam(selected_stim_names, selected_syn_names,
                dic_stim, dic_syn):
    dic_stim2 = change_stim_val(selected_stim_names, dic_stim)
    dic_syn2 = change_syn_val(selected_syn_names, dic_syn)
    return dic_stim2, dic_syn2, 



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
    return selected_stim_names



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
    return selected_syn_names


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


def geterrListfromDatastructure(datastructure):
    errList = []
    for sim in datastructure:
        # print(datastructure[sim])
        listerr = datastructure[sim][4][3]
        for err in listerr:
            errList.append(err)
    return errList

def getChartListfromDatastructure(datastructure):
    chartList = []
    for sim in datastructure:
        # print(datastructure[sim])
        listchart = datastructure[sim][4][4]
        for chart in listchart:
            chartList.append(chart)
    return chartList

def getRunListfromDatastructure(datastructure):
    runList = []
    for sim in datastructure:
        # print(datastructure[sim])
        listrun = datastructure[sim][4][5]
        for run in listrun:
            runList.append(run)
    return runList

def run_parameterSet(optSet, dic_stim2, dic_syn2):
    folders = optSet.folders
    model = optSet.model
    projMan = optSet.projMan
    simSet = SimulationSet.SimulationSet()

    stimParName = optSet.stimParName
    synParName = optSet.synParName
    synNSParName = optSet.synNSParName
    synFRParName = optSet.synFRParName
    
    sourceAsimFile = optSet.model.asimFile

    vals = []
    simSet.samplePts = []
    for st in stimParName:
        short_st = st[ :st.find(".")]
        if short_st in dic_stim2.keys():
            val = dic_stim2[short_st] * 1e-9
            vals.append(val)
            simSet.set_by_range({st: [val]})

    for sy in synParName:
        short_sy = sy[ :sy.find(".")]
        if short_sy in dic_syn2.keys():
            val = dic_syn2[short_sy]
            vals.append(val)
            simSet.set_by_range({sy: [val]})
    
    for syNS in synNSParName:
        short_syNS = syNS[ :syNS.find(".")]
        if short_syNS in dic_syn2.keys():
            val = dic_syn2[short_syNS]
            vals.append(val)
            simSet.set_by_range({syNS: [val]})
    
    for syFR in synFRParName:
        short_syFR = syFR[ :syFR.find(".")]
        if short_syFR in dic_syn2.keys():
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

    
def real_to_norm(optSet, dic_stim, dic_syn, dic_stim2, dic_syn2):
    paramSet = []
    for stim in dic_stim.keys():
        stim_name = stim + ".CurrentOn"
        if stim in dic_stim2.keys():
            stim_val = dic_stim2[stim]
        else:
            stim_val = dic_stim[stim]
        parName = stim_name
        rval = stim_val * 1e-9
        norm = int(optSet.normFromReal(parName, rval) * 100000) / 100000
        paramSet.append(norm)
    for idx, syn in enumerate(dic_syn.keys()):
        if syn + ".G" in optSet.synParName:
            syn_name = syn + ".G"
            if syn in dic_syn2.keys():
                syn_val = dic_syn2[syn]
            else:
                syn_val = dic_syn[syn]
            parName = syn_name
            rval = syn_val
            norm = int(optSet.normFromReal(parName, rval) * 100000) / 100000
            paramSet.append(norm)
        elif syn + ".SynAmp" in optSet.synNSParName:
            synNS_name = syn + ".SynAmp"
            if syn in dic_syn2.keys():
                synNS_val = dic_syn2[syn]
            else:
                synNS_val = dic_syn[syn]
            parName = synNS_name
            rval = synNS_val
            norm = int(optSet.normFromReal(parName, rval) * 100000) / 100000
            paramSet.append(norm)
        elif syn + ".Weight" in optSet.synFRParName:
            synFR_name = syn + ".Weight"
            if syn in dic_syn2.keys():
                synFR_val = dic_syn2[syn]
            else:
                synFR_val = dic_syn[syn]
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


def set_Xrange(dfsrtTime, dfendTime):
    dicValues = {}
    keys = ["xmin", "xmax"]
    values = [dfsrtTime, dfendTime]
    for idx, key in enumerate(keys):
        dicValues[key] = values[idx]
    # selected = list(dicValues.keys())
    selected = keys
    typ = "setXrange"
    text = "set graph Xrange"
    dic_Xrange = set_values_in_list(dicValues, selected, typ, text)
    xmin = dic_Xrange["xmin"]
    xmax = dic_Xrange["xmax"]
    return xmin, xmax


def create_dict_table(source_dict, title, columnTit):
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


def create_seeds_dir():
    typ = "_seeds"
    rootdir = os.path.dirname(animatsimdir)
    subdir = os.path.split(animatsimdir)[-1]
    
    rootSeedDir = "Test" + typ
    listDirGEPfromTyp = [name for name in os.listdir(animatsimdir)
                           if (os.path.isdir(os.path.join(animatsimdir, name))
                               and name[0:len(rootSeedDir)] == rootSeedDir)]
    if len(listDirGEPfromTyp) < 10:
        newGEPDir_fromTyp = rootSeedDir+'0'+str(len(listDirGEPfromTyp))
    else:
        newGEPDir_fromTyp = rootSeedDir + str(len(listDirGEPfromTyp))
    newSeedDir = testDir + "/" + newGEPDir_fromTyp
    os.makedirs(newSeedDir)
    
    list_ext = [".aproj", ".asim", ".aform"]
    copyFileDir_ext(animatsimdir, newSeedDir, list_ext, copy_dir=0)
    

    # =============== save resultFiles  ======================    
    srcResult = testDir + "/ResultFiles"
    dstResult = newSeedDir + "/ResultFiles"
    # copyFile("paramOpt.pkl", src, dst)
    copyFile("template.txt", srcResult, dstResult)
    copyFileWithExt(srcResult, dstResult, ".pkl")   # copy all pickle files
    copyFileWithExt(srcResult, dstResult, ".csv")   # copy all csv files
    copyFileWithExt(srcResult, dstResult, ".json")   # copy all json files

    # ============== copy Test directories  ======================  
    srcChartDir = testDir + "/ChartFiles"
    dstChartDir = newSeedDir + "/ChartFiles"
    if not os.path.exists(dstChartDir):
        os.makedirs(dstChartDir)    
    srcAprojDir = testDir + "/AprojFiles"
    dstAprojDir = newSeedDir + "/AprojFiles"
    if not os.path.exists(dstAprojDir):
        os.makedirs(dstAprojDir)  
    srcAsimDir = testDir + "/AsimFiles"
    dstAsimDir = newSeedDir + "/AsimFiles"
    if not os.path.exists(dstAsimDir):
        os.makedirs(dstAsimDir) 
    srcFinalDir = testDir + "/FinalModel"
    dstFinalDir = newSeedDir + "/FinalModel"
    if not os.path.exists(dstFinalDir):
        os.makedirs(dstFinalDir)
    copyFileDir_ext(srcFinalDir, dstFinalDir, list_ext, copy_dir=0)
    
    list_ranks_GEPdata = []
    for chart in TestWin.seed_list:
        tmp = chart[chart.find("chart")+5:]
        tmp2 = tmp[:tmp.find(".txt")]
        idx = int(tmp2)
        print(idx)
        list_ranks_GEPdata.append(idx)        
    list_ranks_GEPdata.sort()
    unique_list = []
    for element in list_ranks_GEPdata:
        if element not in unique_list:
            unique_list.append(element)
    aproj_name = os.path.splitext(aprojFicName)[0]
    aproj_ext = os.path.splitext(aprojFicName)[1]
    asim_name = os.path.splitext(asimName)[0]
    asim_ext = os.path.splitext(asimName)[1]
    list_dstchartNames = []
    for idx, number in enumerate(unique_list):
        if idx < 10:
            numDst = "0" + str(idx)
        else:
            numDst = str(idx)

        if number < 10:
            numSrc = "0" + str(number)
        else:
            numSrc = str(number)    
        srcChartName = "Test_chart" + numSrc + ".txt"
        dstChartName = "Test_chart" + numDst + ".txt"
        list_dstchartNames.append(dstChartName)
        print(srcChartName, "->", dstChartName)  
        copyRenameFilewithExt(srcChartDir, srcChartName,
                              dstChartDir, dstChartName, ".txt", "")
        
        srcAprojName = aproj_name + "-" + str(number) + aproj_ext
        dstAprojName = aproj_name + "-" + str(idx) + aproj_ext
        print(srcAprojName, "->", dstAprojName)  
        copyRenameFilewithExt(srcAprojDir, srcAprojName,
                              dstAprojDir, dstAprojName, aproj_ext, "")
        
        srcAsimName = asim_name + "-" + str(number) + asim_ext
        dstAsimName = asim_name + "-" + str(idx) + asim_ext
        print(srcChartName, "->", dstChartName)  
        copyRenameFilewithExt(srcAsimDir, srcAsimName,
                              dstAsimDir, dstAsimName, asim_ext, "")
    chartdir = dstChartDir
    templateFileName = dstResult + "/template.txt"
    for chartName in list_dstchartNames:
        graphfromchart(optSet, chartdir, chartName, templateFileName)    

    # =============== Save new_datastructure =================
    dic_structure = optSet.datastructure
    new_datastructure = {}
    for idx,rank in enumerate(unique_list):
        line = dic_structure[rank]
        print(idx,line)
        if idx < 10:
            number = "0"+str(idx)
        else:
            number = str(idx)
        newline = line
        newline[1] = idx+1
        newline[2] = idx+1
        if newline[4][3][0] > 1:
            newline[4][3][0] = 0
        newline[4][4] = ["Test_chart"+number+".txt"]
        newline[4][5] = [idx]
        new_datastructure[idx] = newline 
    print()
    for idx in new_datastructure.keys():
        print(idx, new_datastructure[idx])
    print()
    dstGEPdataDir = newSeedDir + "/GEPdata"
    if not os.path.exists(dstGEPdataDir):
        os.makedirs(dstGEPdataDir)
    complete_GEPdata_filename = dstGEPdataDir + "/GEPdata00.par"  
    # assert os.path.isfile(complete_GEPdata_filename)    
    save_datastructure(new_datastructure, complete_GEPdata_filename)
    
    # ================= Save GEPdata files ===================
    parfilename = "GEPdata00.txt"
    bhvfilename = "GEPdata00bhv.txt"
    completeparname = dstGEPdataDir + "/" + parfilename
    completebhvname =  dstGEPdataDir + "/" + bhvfilename
    fpar = open(completeparname, 'a')
    fbhv = open(completebhvname, 'a')
    endSerie = 0
    for idx,rank in enumerate(unique_list):
        # ==================== saves GEPdata00.txt ===========
        pair = optSet.pairs[rank]
        print(pair[-2])
        if pair[-2] > 1:
            pair[-2] = 0
        s = ""
        for idy, tmpval in enumerate(pair):
            s += "{:4.8f}".format(tmpval) + '\t'
        s += str(endSerie) + '\n'
        # print(s, end=" ")
        fpar.write(s)
        # ================== saves GEPdata00bhv.txt ==========
        behav = optSet.behavs[rank]
        if behav[-1] > 1:
            behav[-1] = 0
        s = ""
        for idy, tmpval in enumerate(behav):
            s += "{:4.8f}".format(tmpval) + '\t'
        s += str(endSerie) + '\n'
        # print(s, end=" ")
        fbhv.write(s)
        endSerie += 1
    fpar.close()
    fbhv.close()
    
    # ==============  Create 0_IDname_seeds0x directory  =================
    copyTo_0_idXXX_Seeds0x(newSeedDir, animatsimdir)    
        

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, optSet, dic_stim, selected_stim_names,
                               dic_syn, selected_syn_names,
                               parent=None):
        super(MainWindow, self).__init__(parent)
        self.simulNb = 0
        testDir = optSet.testDir
        load_pairs(testDir)
        if optSet.errList == []:
            self.minerr = 100000
        else:
            self.minerr = min(optSet.errList)
        self.behavElements = behavElts
        self.optSet = optSet
        self.dic_stim = dic_stim
        self.dic_syn = dic_syn
        self.selected_stim_names = selected_stim_names
        self.selected_syn_names = selected_syn_names
        self.dic_stim2 = {}
        self.dic_syn2 = {}
        for name in self.selected_stim_names:
            self.dic_stim2[name] = dic_stim[name]
        for name in self.selected_syn_names:
            self.dic_syn2[name] = dic_syn[name]
        self.seed_list = []
        self.init_ui()   
        
    def init_ui(self):
        self.setWindowTitle("Dictionnaires & Graphiques")
        
        # Configuration du layout principal
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        layout = QtWidgets.QVBoxLayout(main_widget)
        
        # Section supérieure (tableaux + graphiques)
        top_layout = QtWidgets.QHBoxLayout()
        
        # Partie gauche : deux tableaux de dictionnaires
        self.ExtStim = QtWidgets.QLabel("External Stimuli")
        self.ExtStim.setMinimumSize(QtCore.QSize(0, 27))
        self.Connexions = QtWidgets.QLabel("Connexions")
        self.Connexions.setMinimumSize(QtCore.QSize(0, 27))

        tables_widget = QtWidgets.QWidget()
        tables_layout = QtWidgets.QHBoxLayout(tables_widget)
        tabStim_vertical_with_title = QtWidgets.QVBoxLayout(tables_widget)
        tabSyn_vertical_with_title = QtWidgets.QVBoxLayout(tables_widget)
        self.stimTable = self.create_dict_table(self.dic_stim2,"Extl Stimuli",
                                                ['Clé', 'Valeur (nA)'])
        self.synTable = self.create_dict_table(dic_syn2,"Connexions",
                                               ['Clé', 'Valeur (nS)'])
        tabStim_vertical_with_title.addWidget(self.ExtStim)
        tabStim_vertical_with_title.addWidget(self.stimTable)
        tabSyn_vertical_with_title.addWidget(self.Connexions)
        tabSyn_vertical_with_title.addWidget(self.synTable)
        tables_layout.addLayout(tabStim_vertical_with_title)
        tables_layout.addLayout(tabSyn_vertical_with_title)
        
        # Partie droite : graphiques avec comment
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
        
        # graph_container = QtWidgets.QWidget()
        # graph_container = QtWidgets.QVBoxLayout(graphs_widget)
        
        optSet = self.optSet
        folders = optSet.folders
        chart_path = folders.animatlab_result_dir
        chartName = findTxtFileName(optSet.model, optSet, "", 1)    
        self.build_df_chart(chart_path, chartName)
        self.dic_col = {}
        self.dic_color = {'1FlxIa': 'magenta', '1ExtIa': 'cyan',
                          '1FlxIb': 'pink', '1ExtIb': 'lightblue',
                          '1FlxAlpha': 'red', '1ExtAlpha': 'blue',
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
        graph_vertival_with_comment.addWidget(graph_container, 60)
        
        top_layout.addWidget(tables_widget, 40)
        # top_layout.addWidget(graph_vertival_with_comment)
        top_layout.addWidget(graph_widget, 60)
        
        # Boutons en bas
        button_layout =  QtWidgets.QHBoxLayout()
        self.btnRun =  QtWidgets.QPushButton("Run simulation")
        self.btnChgXrange = QtWidgets.QPushButton("Change XRange")
        self.btnSave = QtWidgets.QPushButton("Save asim, aproj, chart")
        self.btnMakeSeeds = QtWidgets.QPushButton("Make seeds Dir")
        self.btnAddToSeeds = QtWidgets.QPushButton("Add to seeds")
        self.btnPrevious = QtWidgets.QPushButton("Previous Test")
        self.btnNext = QtWidgets.QPushButton("Next Test")
        self.btnQuit =  QtWidgets.QPushButton("Quit")
        button_layout.addWidget(self.btnRun)
        button_layout.addWidget(self.btnMakeSeeds)
        button_layout.addWidget(self.btnAddToSeeds)
        button_layout.addWidget(self.btnSave)
        button_layout.addWidget(self.btnChgXrange)
        button_layout.addWidget(self.btnPrevious)
        button_layout.addWidget(self.btnNext)
        button_layout.addWidget(self.btnQuit)
        
        layout.addLayout(top_layout, 80)
        layout.addLayout(button_layout, 20)
        
        self.btnMakeSeeds.setStyleSheet('QPushButton\
                                       {background-color: #A3C1DA;\
                                                   color: blue;}')
        
        self.btnQuit.setStyleSheet('QPushButton\
                                        {background-color: #A3C1DA;\
                                                    color: red;}')
        
        
        self.font = QtGui.QFont()
        self.font.setBold(False)
        self.font.setPointSize(12)
        self.font.setWeight(75)
        self.ExtStim.setFont(self.font)
        self.Connexions.setFont(self.font)

        self.font = QtGui.QFont()
        self.font.setBold(False)
        self.font.setPointSize(10)
        self.font.setWeight(75)
        self.graph_comment.setFont(self.font)


        self.fontax = QtGui.QFont()
        self.fontax.setBold(False)
        self.fontax.setPointSize(12)
        self.fontax.setWeight(75)

        self.btnRun.setFont(self.font)
        self.btnChgXrange.setFont(self.font)
        self.btnRun.setFont(self.font)
        self.btnSave.setFont(self.font)
        self.btnPrevious.setFont(self.font)
        self.btnNext.setFont(self.font)
        self.btnQuit.setFont(self.font)
        self.btnSave.setEnabled(False)
        self.btnNext.setEnabled(False)
        self.btnMakeSeeds.setEnabled(False)
        self.btnAddToSeeds.setEnabled(False)
        
        # actions
        self.stimTable.cellChanged.connect(self.update_stimTable)
        self.synTable.cellChanged.connect(self.update_synTable)
        self.btnRun.clicked.connect(self.run)
        self.btnChgXrange.clicked.connect(self.changeXrange)
        self.btnSave.clicked.connect(self.save)
        self.btnAddToSeeds.clicked.connect(self.add_to_seeds)
        self.btnMakeSeeds.clicked.connect(self.make_seeds)
        self.btnPrevious.clicked.connect(self.show_previous_run)
        self.btnNext.clicked.connect(self.show_next_run)
        self.btnQuit.clicked.connect(self.closeIt)

        self.nb_run = len(optSet.datastructure)
        if self.nb_run > 0:
            self.present_run = self.nb_run -1
            chartList = getChartListfromDatastructure(datastructure)
            chartName = chartList[-1]
            chart_path = chart_path = animatsimdir + "/Test/ChartFiles"
            self.actualize_graphs(chart_path, chartName)
            self.chart_name = chartName
            self.actualize_graph_comment(chart_path, chartName)
            self.btnAddToSeeds.setEnabled(True)

        else:
            self.present_run = -1
            self.btnNext.setEnabled(False)
            self.btnPrevious.setEnabled(False)
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

    def update_stimTable(self, row, column):
        key_item = self.stimTable.item(row, 0)
        value_item = self.stimTable.item(row, 1)
        
        if key_item and value_item:
            old_key = list(self.dic_stim2.keys())[row]
            new_key = key_item.text()
            new_value = value_item.text()
            
            if new_key != old_key:
                self.dic_stim2[new_key] = self.dic_stim2.pop(old_key)
            self.dic_stim2[new_key] = float(new_value)

    def update_synTable(self, row, column):
        key_item = self.synTable.item(row, 0)
        value_item = self.synTable.item(row, 1)
        
        if key_item and value_item:
            old_key = list(self.dic_syn2.keys())[row]
            new_key = key_item.text()
            new_value = value_item.text()
            
            if new_key != old_key:
                self.dic_syn2[new_key] = self.dic_syn2.pop(old_key)
            self.dic_syn2[new_key] = float(new_value)

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

    def changeXrange(self):
        self.xmin, self.xmax = set_Xrange(self.dfsrtTime, self.dfendTime)
        for graph in self.list_graphs:
            graph.setXRange(self.xmin, self.xmax)


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


    def run(self):
        optSet = self.optSet
        self.behavElements =\
            run_parameterSet(optSet, self.dic_stim2, self.dic_syn2)
        paramSet = real_to_norm(optSet, dic_stim, dic_syn,
                                self.dic_stim2, self.dic_syn2)
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
        self.btnAddToSeeds.setEnabled(False)
        
    def save(self):
        simulNb = self.simulNb
        add_pair(optSet, self.pair, self.behav)
        mse, coactP = self.behavElements[7], self.behavElements[8]
        paramSet = real_to_norm(optSet, dic_stim, dic_syn, 
                                self.dic_stim2, self.dic_syn2)
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
        if self.present_run > 0:
            self.btnPrevious.setEnabled(True)
        self.btnAddToSeeds.setEnabled(True)

    def savedic_pdf_param(self):     
         chartList = getChartListfromDatastructure(datastructure)
         runList = getRunListfromDatastructure(datastructure)
         chart_path = animatsimdir + "/Test/ChartFiles"
         dic_pdf_param = {}
         for idx, chart in enumerate(chartList):
             chartName = chart[:chart.find(".")]
             pdfName = chartName + '_bhvMvt.pdf'
             dic_pdf_param[pdfName] = runList[idx]
         jsondicfile_name = animatsimdir + "/Test/ResultFiles/dic_PdfPar.json"
         with open(jsondicfile_name, 'w+') as f:
             # this would place the entire output on one line
             json.dump(dic_pdf_param, f, indent=4)
         self.jsondicfile_name = jsondicfile_name


    def add_to_seeds(self):
        print("Add current run to seed list (the ist is saved by clicking on 'Make seeds'")
        self.seed_list.append(self.chart_name)
        self.btnMakeSeeds.setEnabled(True)
        
    def make_seeds(self):
        print("saves the list of seeds in a seed directory")
        create_seeds_dir()

    def show_previous_run(self):
        if self.nb_run == 0:  # There is no run
            print("no datastructure yet")
        else:
            optSet = self.optSet
            datastructure = optSet.datastructure
            chartList = getChartListfromDatastructure(datastructure)
            runList = getRunListfromDatastructure(datastructure)
            if self.present_run > 0:
                self.present_run -= 1
            
            pair = optSet.pairs[runList[self.present_run]]
            paramset = pair[:-2]
            dic_stim, dic_syn = norm_to_real(optSet, paramset,
                                             self.dic_stim, self.dic_syn)
            for st in selected_stim_names:
                dic_stim2[st] = dic_stim[st]            
            for sy in selected_syn_names:
                dic_syn2[sy] = dic_syn[sy] 
            self.actualizeStimTable(dic_stim2)
            self.actualizeSynTable(dic_syn2)
            chartName = chartList[self.present_run]
            chart_path = testDir + "/ChartFiles"
            self.actualize_graphs(chart_path, chartName)
            self.chart_name = chartName
            self.actualize_graph_comment(chart_path, chartName)

            self.btnNext.setEnabled(True)
            if self.present_run == 0:
                self.btnPrevious.setEnabled(False)

    def show_next_run(self):
        if self.nb_run == 0:  # There is no run
            print("no datastructure yet")
        else:
            optSet = self.optSet
            datastructure = optSet.datastructure
            chartList = getChartListfromDatastructure(datastructure)
            runList = getRunListfromDatastructure(datastructure)
            if self.present_run < self.nb_run - 1:
                self.present_run += 1
            pair = optSet.pairs[runList[self.present_run]]
            paramset = pair[:-2]
            dic_stim, dic_syn = norm_to_real(optSet, paramset,
                                             self.dic_stim, self.dic_syn)
            for st in selected_stim_names:
                dic_stim2[st] = dic_stim[st]            
            for sy in selected_syn_names:
                dic_syn2[sy] = dic_syn[sy] 
            self.actualizeStimTable(dic_stim2)
            self.actualizeSynTable(dic_syn2)
            chartName = chartList[self.present_run]
            chart_path = testDir + "/ChartFiles"
            self.actualize_graphs(chart_path, chartName)
            self.chart_name = chartName
            self.actualize_graph_comment(chart_path, chartName)
            
            self.btnPrevious.setEnabled(True)
            if self.present_run == self.nb_run - 1:
                self.btnNext.setEnabled(False)

    def closeIt(self):
        """
        doc string
        """
        self.close()


def main():
    None


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
                                      title='Please select a base directory')
    root.destroy()
    if len(dirname ) > 0:
        print("You chose %s" % dirname)

    # import tkFileDialog as filedialog
    # animatsimdir = filedialog.askdirectory()
    animatsimdir = dirname
    if animatsimdir != "":
        saveAnimatLabSimDir(animatsimdir)
    animatsimdir = readAnimatLabDir()
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

    testDir = animatsimdir + "/Test"
    optSet.testDir = testDir
    if os.path.exists(testDir):
        GEPdataDir = testDir + "/GEPdata"
        parfilename = "GEPdata00.par"
        completeparfilename = os.path.join(GEPdataDir, parfilename)
        optSet.datastructure = load_datastructure(completeparfilename)
    
    datastructure = optSet.datastructure
    if len(datastructure) > 0:
        errList = geterrListfromDatastructure(datastructure)
    else:
        errList = []
    optSet.errList = errList

    simulNb = 0
    optSet,asimFileName = chooseAsimFile(optSet, animatsimdir)
    dic_stim, dic_syn = getparamsFromAsim(optSet, asimFileName)
    
    
    selectStimFileName = "selectStimlist.json"
    selectSynFileName = "selectSynlist.json"
    completeStimFileName = testDir + "/" + selectStimFileName
    completeSynFileName = testDir + "/" + selectSynFileName
    
    selected_stim = list(dic_stim.keys())
    selected_syn = list(dic_syn.keys())
    if (os.path.exists(completeStimFileName) 
        and os.path.exists(completeSynFileName)):
        print("previous selection of stim and syn found")
        
        with open(completeStimFileName, "r") as f:
            selected_stim = json.load(f)
        with open(completeSynFileName, "r") as f:
            selected_syn = json.load(f)    

    selected_stim_names, selected_syn_names = selectparam(dic_stim,
                                                          dic_syn,
                                                          selected_stim,
                                                          selected_syn)
    with open(completeStimFileName, "w") as f:
        json.dump(selected_stim_names, f)
    with open(completeSynFileName, "w") as f:
        json.dump(selected_syn_names, f)

    
 
    dic_stim2, dic_syn2 = changeparam(selected_stim_names, selected_syn_names,
                                      dic_stim, dic_syn)
    # paramSet = real_to_norm(optSet, dic_stim, dic_syn, dic_stim2, dic_syn2)
    behavElts = run_parameterSet(optSet, dic_stim2, dic_syn2)

    
    app = QtWidgets.QApplication(sys.argv)

    TestWin = MainWindow(optSet, dic_stim, selected_stim_names,
                                 dic_syn, selected_syn_names)
    TestWin.show()   
    sys.exit(app.exec_())
    