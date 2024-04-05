# -*- coding: utf-8 -*-
"""
"optimization.py"
Created on Mon Jan 23 10:13:39 2017
Contain procedures used in several pythn files of the project
@author: cattaert
Translated in Python 3.8 Jan 2023 (D. Cattaert)

Modified January 24, 2023 (D.. Cattaert):
    In main Mode, builds graphs of movement, force and neuron activity against
    time (in addition to the previous minimum jerk fitting)
Modified February 2, 2023 (D. Cattaert):
    chartToDataFrame() procedure added
Modified February 3, 2023 (D. Cattaert):
    In testVarMsePlot() fonction, the coactivation0, and 1 are now read from
    coact1, coact2 = res1[0], res2[0] instead of res1[1], res2[1]
    Changes made in accordance with changes in makeGraphs.py
modified February 3, 2023 (D. Cattaert):
    Command added in control script file: span=from_file
    This command allows controlScriptGEP.py to read the listspanval and the
    span_dic from a file placed in the GEPdata folder (DicSpanVal.txt). It is
    processed in the set_span_par_name() procedure called from SetsRandParam():
        elif valPar == "from_file":
            dicSpanVal_file = win.animatsimdir + "/GEPdata/DicSpanVal.txt"
            dicSpanVal, listspanval = readSpan_from_DicSpanVal(dicSpanVal_file)
            if listspanval != []:
                win.listspanVal = listspanval
                lst_span_dic = [dicSpanVal]
                win.refresh_span(lst_span_dic)
            else:
                sys.exit()
    readSpan_from_DicSpanVal() is loaded from optmization.py
Modidied February 6, 2023 (D. Cattaert):
    Prodecures adapted for spanlist from file.
Modified February 14, 2023 (D. Cattaert):
    A new class "makeChartGraphs()" was created to allow calling graphfromchart
    that calls 'choose_elements_in_list()" that needs to be called from a
    QWidget graphic window. This was necessary when optimization is -used as
    a __main__ script to test movement from GEPcharts
    Errors in testVarMsePlot() are now handled with try... except...
Modified February 16, 2023 (D. Cattaert):
    Procedure checknonzeroSyn() modified t include ThreshV and SaturationV of
    synapses in the File "VoltageNeuronConnexions.txt" saved in GEPdata dir
Modified Febrary 20, 2023 (D. Cattaert):
    Bug fixed: pg.QtGui.QMessageBox() replaced by pg.QtWidgets.QMessageBox()
Modified February 24, 2023 (D. Cattaert):
    Bug fixed in improve_span_list procedure
Modified February 27, 2023 (D. Cattaert):
    readSpan() procedure improved to accept read from datactructre when no
    spanlist dictionary exists.
Modified April 23, 2023 (D. Cattaert):
    Three new procedures added to plot the relationship between mas_speed and
    ampliude, for given values of duration:
        def calculate_maxspeed_from_ampl_duration(rate, amplitude, duration):
        def curve_maxspeed_ampl_duration(duration):
        def plot_series_curves_maxspeed_ampl_duration(graph_path, mindur,
                                                      maxdur, stepdur):
    The last procedure is called in makegraphs.py
Modified May 11, 2023 (D. Cattaert):
    procedure readSpan(datastructure, dicSpanVal_file="") modified to read the
    name of the "DicSpanVal.txt" file instead of the list of span values.
    listspanVal is read from the file "DicSpanVal.txt"
Modified May 16, 2023 (D. Cattaert):
    In Get_good_span_list(), Span values are no more multiplied by 5 because it
    was too large.
Modified June 19, 2023 (D. Cattaert):
    chartToDataFrame() modified to suppress the "\n" at the end of colNames
Modified July 27, 2023 ( D. Cattaert):
    Procedure get_good_span_list() and associated functions (improve_span_list,
    calculate_newspan_list, run_listparamsets) have been modified to ru onky
    parameter sets that obtained a score >1.
    A new procedure  (getNbPacketVar()) was created to build nbEpochParam,
    nbRunParam, paramserieSlicesAllEpochs for the global parameter sets witt
    variable number of runs for each epoch.
Modified September 18, 2023 (D. Cattaeert):
    Procedure chartToDataFrame(completeName, colnames=None) modified for column
    names: if colnames is not None, columns names are taken from colnames, but
    if it is None, then columns names are taken from the chart file.
Modified February 01, 2024 (D. Cattaert):
    in checknonzeroSynFR()  range(4-(len(synapseName)+1)/8) replaced by
                            range(4-int((len(synapseName)+1)/8))
    in affichConnexionsFR() range(3-(len(synapseName[syn])+1)/8) replaced by
                            range(3-int((len(synapseName[syn])+1)/8))
"""

import class_animatLabModel as AnimatLabModel
# import class_animatLabSimulationRunner as AnimatLabSimRunner
import class_simulationSet as SimulationSet
# import class_projectManager as ProjectManager
import class_chartData as ChartData
# import xml.etree.ElementTree as elementTree
# import class_chartViz as ChartViz
import numpy as np
import pandas as pd
import pyqtgraph as pg
import copy
import glob
import shutil
import traceback
import pickle

import os
from os import listdir
from os.path import isfile, join
from pyqtgraph.Qt import QtCore
from pyqtgraph.Qt import QtGui
from pyqtgraph.Qt import QtWidgets

import matplotlib.pyplot as plt
# from copy import copy
# import class_chartData as chartData
from math import sqrt
from math import fmod
from cma import fmin

# from copy import deepcopy
import datetime

global verbose
verbose = 0  # level of details printed in the console


def readAnimatLabDir():
    filename = "animatlabSimDir.txt"
    try:
        f = open(filename, 'r')
        directory = f.readline()
        f.close()
    except Exception as e:
        if (verbose > 2):
            print(e)
        directory = ""
    return directory


def loadParams(paramFicName, optSet):
    """
    loads parameters for optimization procedures (VSCD and CMAes)
    from a file named "paramOpt.pkl" stored in ResultFiles directory of the
    chosen simulation. This file (and the 3ResultFiles" directory were created
    by the "GUI_AnimatLabOptizarion.py" graphic user interface)
    After reading the "paramOpt.pkl" file, parameters are stored in the
    optSet object (from the Class OptimizeSimSettings)
    If "paramOpt.pkl" exists return "True"
    If "paramOpt.pkl" does not exist, return "False"
    """
    try:
        print
        print("looking paramOpt file:", paramFicName)
        with open(paramFicName, 'rb') as input:
            optSet.paramVSCDName = pickle.load(input)
            optSet.paramVSCDValue = pickle.load(input)
            optSet.paramVSCDType = pickle.load(input)
            optSet.paramVSCDCoul = pickle.load(input)
            optSet.paramMarquezName = pickle.load(input)
            optSet.paramMarquezValue = pickle.load(input)
            optSet.paramMarquezType = pickle.load(input)
            optSet.paramMarquezCoul = pickle.load(input)
        print("nb loaded param :", len(optSet.paramVSCDName))
        # print("nb nb actual param param:", len(listparNameOpt))
        print("nb expected param:", 42)
        # There are 41 VSCD parameters in this version
        nbloadedpar = len(optSet.paramVSCDName)
        if nbloadedpar == 42:
            if optSet.paramVSCDName[16] == 'disabledSynNbs':
                # This is the last version that includes "seriesSynNSParam"
                print("paramOpt :")
                optSet.printParams(optSet.paramVSCDName, optSet.paramVSCDValue)
            elif optSet.paramVSCDName[16] == 'allsyn':
                # This is the last version that includes "seriesSynNSParam"
                print("this version does not indicate seriesSynNSParam")
                print("ACTUALIZING...")
                optSet.update_optSetParamVSCD()
                saveParams_pickle(optSet.paramFicName, optSet)
            print("paramMarquez :")
            optSet.printParams(optSet.paramMarquezName,
                               optSet.paramMarquezValue)
            print('===================  Param loaded  ====================')
            response = True
        elif nbloadedpar == 41:
            print("paramOpt with only 41 params:")
            pln = ['selectedChart'] + optSet.paramVSCDName
            optSet.paramVSCDName = pln
            plv = [0] + optSet.paramVSCDValue
            optSet.paramVSCDValue = plv
            plt = [int] + optSet.paramVSCDType
            optSet.paramVSCDType = plt
            plc = ["Magenta"] + optSet.paramVSCDCoul
            optSet.paramVSCDCoul = plc
            optSet.printParams(optSet.paramVSCDName,
                               optSet.paramVSCDValue)
            print("paramMarquez :")
            optSet.printParams(optSet.paramMarquezName,
                               optSet.paramMarquezValue)
            print('===================  Param loaded  ====================')
            response = True
        else:
            print("Mismatch between existing and actual parameter files")
            response = False
    except Exception as e:
        if (verbose > 2):
            print(e)
        # print("No parameter file with this name in the directory", end=' ')
        # print("NEEDs to create a new parameter file")
        response = False
    return response


def saveParams_pickle(paramFicName, optSet):
    """
    doc string
    """
    with open(paramFicName, 'wb') as output:
        pickle.dump(optSet.paramVSCDName, output)
        pickle.dump(optSet.paramVSCDValue, output)
        pickle.dump(optSet.paramVSCDType, output)
        pickle.dump(optSet.paramVSCDCoul, output)
        pickle.dump(optSet.paramMarquezName, output)
        pickle.dump(optSet.paramMarquezValue, output)
        pickle.dump(optSet.paramMarquezType, output)
        pickle.dump(optSet.paramMarquezCoul, output)
    print("&&&&&& File saved :", paramFicName, "  &&&&&&")


def checknonzeroSynFR(model, optSet):
    """
    checks if synaptic weight of enabled synapses between firing rate neurons
    is different from zero. All parameters are accessible in the optSet object.
    If synaptic weight is zero, the weight is changed to 1e-15
    This procedure is used to avoid a synaptic weight to be trapped in zero
    value in the optimization process.
    """
    folders = optSet.folders
    dirGEP = os.path.join(folders.animatlab_rootFolder, "GEPdata")
    fileparname = "FRNeuronConnexions.txt"
    completeparname = os.path.join(dirGEP, fileparname)
    fparname = open(completeparname, 'w')

    print()
    print("Checking 'Firing Rate Neuron' connexions...")
    firstSynapseFR = findFirstType(model, "SynapsesFR")
    for syn in range(len(optSet.SynapsesFR)):
        s = ""
        if syn not in optSet.disabledSynFRNbs:
            s += "[{}]\t".format(syn)
            tempName = optSet.model.lookup["Name"][firstSynapseFR+syn]
            tempName.split('*')
            neuronSource = tempName.split('*')[0]
            neuronTarget = tempName.split('*')[1]
            connexSourceName = neuronSource
            connexTargetName = neuronTarget
            synapseID = optSet.SynapsesFR[syn].find("ID").text
            synapseName = connexSourceName + "-" + connexTargetName
            # synapseType = optSet.SynapsesFR[syn].find("Type").text
            synapseWeight = optSet.model.getElementByID(synapseID).\
                find("Weight").text
            s += synapseName
            print(synapseName, end=' ')
            for sp in range(4-int((len(synapseName)+1)/8)):
                s += '\t'
                # print('\t', end=' ')
            s += "Weight : "
            # print("Weight : ", end=' ')
            s += str(synapseWeight)
            # print(synapseWeight, end=' ')
            if synapseWeight == '0':
                s += "\t\t\t-->"
                # print("\t\t\t-->", end=' ')
                model.getElementByID(synapseID).find("Weight").text = '1e-15'
                s += optSet.model.getElementByID(synapseID).find("Weight").text
                # print(optSet.model.getElementByID(synapseID).\
                #     find("Weight").text)
            print(s)
            s += "\n"
            fparname.write(s)
    fparname.close()


def checknonzeroSyn(model, optSet):
    """
    checks if synaptic weight  (G) of enabled synapses between voltage neurons
    is different from zero. All parameters are accessible in the optSet object.
    If synaptic weight is zero, the weight is changed to 1e-15
    This procedure is used to avoid a synaptic weight G to be trapped in zero
    value in the optimization process.
    """
    folders = optSet.folders
    dirGEP = os.path.join(folders.animatlab_rootFolder, "GEPdata")
    fileparname = "VoltageNeuronConnexions.txt"
    completeparname = os.path.join(dirGEP, fileparname)
    fparname = open(completeparname, 'w')

    print()
    print("Checking 'Voltage Neuron' connexions...")
    for syn in range(len(optSet.Connexions)):
        s = ""
        if syn not in optSet.disabledSynNbs:
            s += "[{}]\t".format(syn)
            sourceID = optSet.Connexions[syn].find("SourceID").text
            targetID = optSet.Connexions[syn].find("TargetID").text
            neuronSource = model.getElementByID(sourceID)
            neuronTarget = model.getElementByID(targetID)
            connexSourceName = neuronSource.find("Name").text
            connexTargetName = neuronTarget.find("Name").text
            synapseTempID = optSet.Connexions[syn].find("SynapseTypeID").text
            synapseTempName = model.getElementByID(synapseTempID).\
                find("Name").text
            if len(synapseTempName) < 24:
                s += synapseTempName + "\t\t"
            else:
                s += synapseTempName + "\t"
            synapseTempType = model.getElementByID(synapseTempID).\
                find("Type").text
            if syn in optSet.dontChangeSynNbs:
                s += "dontChange\t"
            else:
                s += "Optim     \t"
            s += connexSourceName
            for sp in range(2-int((len(connexSourceName)+0)/7)):
                s += '\t'
            s += '-> {}'.format(connexTargetName)
            for sp in range(3-int((len(connexTargetName)+3)/8)):
                s += '\t'
            if synapseTempType == 'NonSpikingChemical':
                # The value of SynAmp is in the SynapseType
                s += "SynAmp : "
                synAmpVal = model.getElementByID(synapseTempID).\
                    find("SynAmp").text
                s += str(synAmpVal)
                if synAmpVal == 'O':
                    s += "\t-->"
                    model.getElementByID(synapseTempID).\
                        find("SynAmp").text = '0.0001'
                    s += model.getElementByID(synapseTempID).\
                        find("SynAmp").text
                synThresh = model.getElementByID(synapseTempID).\
                    find("ThreshV").text
                s += '\t' + "ThreshV: " + str(synThresh) + '\t'
                
                synSat = model.getElementByID(synapseTempID).\
                    find("SaturateV").text
                s += '\t' + "SaturateV: " + str(synSat)
                
            elif synapseTempType == 'SpikingChemical':
                # The value of G is in the "Connexion"
                s += "G : "
                s += optSet.Connexions[syn].find("G").text
                if optSet.Connexions[syn].find("G").text == '0':
                    s += "\t-->"
                    optSet.Connexions[syn].find("G").text = '0.0001'
                    s += optSet.Connexions[syn].find("G").text
            print(s)
            s += "\n"
            fparname.write(s)
    fparname.close()


def checknonzeroExtStimuli(optSet):
    """
    checks if external stimuli is different from zero.
    All parameters are accessible in the optSet object. If it is the case, the
    value of external stimuli is set to 1e-11 (usig the optSet object)
    This procedure is used to avoid a synaptic weight G to be trapped in zero
    value in the optimization process.
    """
    folders = optSet.folders
    dirGEP = os.path.join(folders.animatlab_rootFolder, "GEPdata")
    fileparname = "ExtStimuli.txt"
    completeparname = os.path.join(dirGEP, fileparname)
    fparname = open(completeparname, 'w')

    print()
    print("Checking External Stimuli...")
    for stim in range(optSet.nbStims):
        s = ""
        if optSet.ExternalStimuli[stim].find("Enabled").text == 'True':
            s += "[{}]\t".format(stim)
            stimName = optSet.ExternalStimuli[stim].find("Name").text
            if stim in optSet.dontChangeStimNbs:
                s += "dontChange\t"
            else:
                s += "Optim     \t"
            s += stimName
            for sp in range(3-int((len(stimName)+1)/8)):
                s += '\t'
            s += "CurrentOn : "
            s += optSet.ExternalStimuli[stim].find("CurrentOn").text
            if optSet.ExternalStimuli[stim].find("CurrentOn").text == '0':
                s += "-->"
                optSet.ExternalStimuli[stim].find("CurrentOn").text = '1e-11'
                s += optSet.ExternalStimuli[stim].find("CurrentOn").text
            print(s)
            s += "\n"
            fparname.write(s)
    fparname.close()


def getInfoComputer():
    """
    Out : directory : the directory in which the animatlab exe is
        nb_processors : the amount of processors the machine have
    This function read the txt file infos_computer to seek animatlab's
    directory and the amount of processors
    """
    try:
        with open("infos_computer.txt", 'r') as fich:
            directory = fich.readline()
            directory = directory[: directory.find("\n")]
            txt = fich.readline()
            nb_processors = int(txt[txt.find("=")+1:])
            fich.close()
    except Exception as e:
        if (verbose > 1):
            print(e)
        directory = ""
        nb_processors = 1
    return directory, nb_processors


def readAnimatLabSimDir():
    """
    Out : directory : the directory in which we want to startseq the simulations
    This function read the content of the animatlabSimDir.txt file and return
    the path to the directory on which we're working
    """
    filename = "animatlabSimDir.txt"
    try:
        fic = open(filename, 'r')
        directory = fic.readline()
        fic.close()
    except Exception as e:
        if (verbose > 1):
            print(e)
        directory = ""
    # print("First instance: Root directory will be created from GUI")
    return directory


def saveAnimatLabSimDir(directory):
    """
    This procedure save the path of the directory in which we're working in
    animatlabSimDir.txt
    """
    filename = "animatlabSimDir.txt"
    fic = open(filename, 'w')
    fic.write(directory)
    fic.close()


def setAnimatLabSimDir(win):
    """
    In : win : Unused
    Out : dirname :
    This function
    """
    """
    if win is None:
        win = pg.GraphicsWindow()
        win.hide()
        # win.resize(10,10)
    """
    animatsimdir = readAnimatLabSimDir()
    if animatsimdir != "":
        subdir = os.path.split(animatsimdir)[-1]
        # rootname = os.path.dirname(animatsimdir)
    else:
        print("First instance - no previous animatlab folder selected")
        # rootname = ""
    res = (pg.QtWidgets.QFileDialog.
           getExistingDirectory(None, "Select Directory", animatsimdir))
    if type(res) == tuple:
        dirname, __tmp = res
    else:
        dirname = res
    print(dirname)

    dname = ""
    for ch in dirname:
        if ch == '\\':
            ch = '/'
        dname += ch
    print(dname)
    dirname = dname
    if dirname:       # if user didn't pick a directory don't continue
        print("You chose %s" % dirname)
        subdir = os.path.split(dirname)[-1]
        print(subdir)
        # rootname = os.path.dirname(dirname)
        saveAnimatLabSimDir(dirname)
    return dirname


# 2 functions here, one wihch create a dir, another which increments a number
def SaveIncrementNb(directory, name, ext):
    """
    In : directory : the directory in which we'd like to create a file
        name : the name of the file to create
        ext : the extension of the file
    Out : destfilename : the final name of the created file
    This function create a directiry if the specified directory doesn't exist
    then look a the amount of file with the same name and increment the number
    to put at the endseq of the file's name then finally save it
    """
    number = 0
    txtnumber = "00"
    if not os.path.exists(directory):
        os.makedirs(directory)
    destfilename = os.path.join(directory, name + "00" + ext)
    while os.path.exists(destfilename):
        number = number + 1
        if number < 10:
            txtnumber = "0" + str(number)
        else:
            txtnumber = str(number)
        destfilename = os.path.join(directory, name + txtnumber + ext)
    return destfilename


def saveListToDir(list_names, fileName, path):
    """
    Saves a list of words in a text file in path directory
    """
    completename = os.path.join(path, fileName)
    f = open(completename, 'w')
    s = ""
    for idx, name in enumerate(list_names[:-1]):
        s += "{}".format(name) + '\n'
        # s += "{:4.8f}".format(optSet.pairs[idx][idy+1]) + '\t'
    s += list_names[-1] + '\n'
    # print(s, end=" ")
    f.write(s)
    f.close()


def chartToDataFrame(completeName, colnames=None):
    """
    Reads a text file (chart data). The two first lines are title and param
    names. Uses paramnames to build a dataframe. Returns the nparray of data,
    the dataframe, the title and the list of parameter names.
    """
    tabFinal = []
    tabparams = []
    try:
        with open(completeName, 'r') as fich:
            titre = fich.readline()
            params = fich.readline()
            if params == "\n":
                params = fich.readline()
            # tabparams = getValuesFromText(params)
            tabparams = params.split('\t')
            tabparams[-1] = tabparams[-1][:-1] #  suppress the "\n" at end
            # if tabparams[1] != 'Time':
            #     tabparams = colnames
            if colnames is not None:  
                tabparams = colnames
            while 1:
                tab1 = []
                tab2 = []
                txt = fich.readline()
                if txt == '':
                    break
                else:
                    tab1 = getValuesFromText(txt)
                    # print tab1
                    try:
                        for k in range(len(tab1)):
                            tab2.append(float(tab1[k]))
                            # tab2.append(tab1[k])
                        tabFinal.append(tab2)
                    except Exception as e:
                        k = 0
                        if (verbose > 1):
                            print(e)
    except Exception as e:
        if (verbose > 2):
            print(e)
    tabFinal = np.array(tabFinal)
    dataframe = pd.DataFrame(tabFinal, columns=tabparams)
    return (tabFinal, dataframe, titre, tabparams)


# ============================================================================
#                          gestion of parameters
# ============================================================================

# Define callback function before the __main__ loop in order to ensure that
# it has global scope. Defining it within the __main__ loop will result in
# a runtime error!
#
# Callbacks must accept arguments: asimFile, results, obj_simRunner


def callback_compressData(asimFile, results, obj_simRunner):
    """
    In : asimFile :
        results :
        obj_simRunner :
    This procedure
    """
    # Instantiate chartData object with unique name
    chartData = ChartData.chartData('Example1')

    print(results)
    chartData.get_source(results, analogChans=['Essai'],
                         saveCSV=True, asDaemon=False)

    print("\nCompressing: %s" % asimFile)
    # Reduce the impact on memory by compressing spike data channels
    chartData.compress()

    print("\nSaving chart data: %s" % asimFile)
    # Save compressed data to a data file using default naming options
    try:
        # dataName = os.path.split(asimFile)[-1].split('.')[0]
        dataName = os.path.splitext(os.path.split(asimFile)[-1])[0]
        chartData.saveData(filename=os.path.join(obj_simRunner.resultFiles,
                                                 dataName+'.dat'))
    except Exception as e:
        if verbose > 2:
            print(traceback.format_exc())
            print(e)


def ecritpairs(pairs, startseq=0, all=0):
    """
    In : pairs :
        startseq :
        all :
    This procedure
    """
    print("parameters_msecoat pairs")
    for idx in range(startseq, len(pairs)):
        s = str(idx) + "\t"
        for idy in range(len(pairs[0])-2):
            tmpval = pairs[idx][idy]
            s += "{:1.5f}".format(tmpval) + ' '
        # the two last values are the behav (mse, coactpenality)
        if pairs[idx][idy+1] >= 10000:
            s += "{:4.1f}".format(pairs[idx][idy+1]) + '\t'
        else:
            s += "{:4.2f}".format(pairs[idx][idy+1]) + '\t'
        s += "{:4.2f}".format(pairs[idx][idy+2]) + '\n'
        if not all:
            if idx < 10:
                print(s, end=' ')
            elif idx == 10:
                print(". . .")
            if (len(pairs) - startseq) > 10:
                if idx > (len(pairs) - startseq - 10):
                    print(s, end=' ')
        else:
            print(s, end=' ')
    print()


def ecrit_tab(tab, startseq=0, all=0, comment="", col_width=12):
    """
    In : tab :
        startseq :
        all :
        comment :
        col_width :
    This procedure
    """
    print(comment)
    for idx in range(startseq, len(tab)):
        s = str(idx) + "\t"  # print the row number
        for idy in range(len(tab[0])-1):
            tmpval = tab[idx][idy]
            s += "{:4.4f}".format(tmpval)
            for i in range(col_width-len("{:4.4f}".format(tmpval))):
                s += ' '
        s += "{:4.5f}".format(tab[idx][idy+1]) + '\n'
        if not all:
            if idx < 10:
                print(s, end=' ')
            elif idx == 10:
                print(". . .")
            if (len(tab) - startseq) > 10:
                if idx > (len(tab) - startseq - 10):
                    print(s, end=' ')
        else:
            print(s, end=' ')
    print()


def ecrit_tab_int(tab, startseq=0, all=0, comment="", col_width=12):
    print(comment)
    for idx in range(startseq, len(tab)):
        s = str(idx) + "\t"  # print the row number
        for idy in range(len(tab[0])-1):
            tmpval = tab[idx][idy]
            s += "{:3d}".format(tmpval)
            for i in range(col_width-len("{:3d}".format(tmpval))):
                s += ' '
        s += "{:3d}".format(tab[idx][idy+1]) + '\n'
        if not all:
            if idx < 10:
                print(s, end=' ')
            elif idx == 10:
                print(". . .")
            if (len(tab) - startseq) > 10:
                if idx > (len(tab) - startseq - 10):
                    print(s, end=' ')
        else:
            print(s, end=' ')
    print()


def ecrit_tabStr(tab, startseq=0, all=0, comment="", col_width=9):
    print(comment)
    for idx in range(startseq, len(tab)):
        s = str(idx) + "\t"  # print the row number
        for idy in range(len(tab[0])-1):
            tmpval = float(tab[idx][idy])
            s += "{:4.2f}".format(tmpval)
            for i in range(col_width-len("{:4.2f}".format(tmpval))):
                s += ' '
        s += "{:4.2f}".format(float(tab[idx][idy+1])) + '\n'
        if not all:
            if idx < 10:
                print(s, end=' ')
            elif idx == 10:
                print(". . .")
            if (len(tab) - startseq) > 10:
                if idx > (len(tab) - startseq - 10):
                    print(s, end=' ')
        else:
            print(s, end=' ')
    print


def listNamesToComment(list_names, col_width=12):
    s = "\t"
    for idx_name, name in enumerate(list_names):
        name = name[:col_width]
        s += name
        for i in range(col_width-len(name)+1):
            s += ' '
    # print(s)
    return s


def affich_corrtable(corr):
    str_line = ''
    tabspace = ""
    for i in range(len(corr)):
        for j in range(len(corr[i])):
            tabspace = ""
            for k in range(2-((len(corr[i][j])+0)/8)):
                tabspace += "\t"
            str_line += '{}{}'.format(corr[i][j], tabspace)
        # str_line += '\t'
        print(str_line)
        str_line = ''
    print


def affich_table(tab, ntab):
    str_line = ''
    tabspace = ""
    for i in range(len(tab)):
        for j in range(len(tab[i])):
            tabspace = ""
            for k in range(ntab-((len(str(tab[i][j]))+0)/8)):
                tabspace += "\t"
            str_line += '{}{}'.format(tab[i][j], tabspace)
        # str_line += '\t'
        print(str_line)
        str_line = ''
    print


def affiche_liste(liste):
    txt = "["
    for idx, behavElt in enumerate(liste):
        if idx < len(liste) - 1:
            txt += "{:4.3f}    ".format(float(behavElt))
        else:
            txt += "{:4.3f}".format(float(behavElt))
    print(txt, "]\t", end=' ')


def affichChartColumn(ChartColumns, show):
    # To find elements by type:
    # Options are: Neurons, Adapters, ExternalStimuli
    # Neurons = model.getElementByType("Neurons")
    tabchartcolname = []
    i = 0
    chartcolName = []
    while i < len(ChartColumns):
        chartcolName.append(ChartColumns[i].find("ColumnName").text)
        i = i+1
    # ... and print them
    if show == 1:
        print('\n')
        print("list of chart column names")
    i = 0
    while i < len(ChartColumns):
        if show == 1:
            txt = '[%2d]  %s:'
            print(txt % (i, chartcolName[i]))
        tabchartcolname.append([chartcolName[i]])
        i = i+1
    return tabchartcolname


def findFirstType(model, Type):
    firstType = -10
    for i in range(len(model.lookup["Type"])):
        # print(i, model.lookup["Type"][i])
        if model.lookup["Type"][i] == Type:
            if firstType == -10:
                firstType = i
    # print("1st", Type, "is", firstType, "in model.lookup list")
    return firstType


def affichMotor(modl, motorStimuli, show):
    # find elements by type:   MotorPosition, MotorVelocity
    tabMotorVal = []
    i = 0
    motorName, motorType, start_motor, end_motor = [], [], [], []
    speed, enabled_motor = [], []
    jointID, jointName = [], []
    for i in list(range(len(motorStimuli))):
        motorEl = motorStimuli[i]
        for idx, elem in enumerate(motorEl):
            motorName.append(motorEl[idx].find("Name").text)
            motorType.append(motorEl[idx].find("Type").text)
            start_motor.append(float(motorEl[idx].find("StartTime").text))
            end_motor.append(float(motorEl[idx].find("EndTime").text))
            speed.append(float(motorEl[idx].find("Equation").text))
            enabled_motor.append(motorEl[idx].find("Enabled").text)
            jID = motorEl[idx].find("JointID").text
            jointID.append(jID)
            tmpjointName = modl.getElementByID(jID).find("Name").text
            jointName.append(tmpjointName)
    # ... and print them
    if show == 1:
        print("list of motor stimuli ")
    i = 0
    while i < len(motorName):
        if show == 1:
            txt0 = '[{:02d}] '.format(i)
            txt1 = str(motorName[i])
            for k in list(range(int(3-((len(txt1)+5)/8)))):
                txt1 += "\t"
            txt2 = "Type:{}; ".format(motorType[i])
            txt3 = '  {};  \tStartTime:{:6.2f};   EndTime:{:6.2f};'
            ftxt3 = txt3.format(jointName[i],
                                start_motor[i],
                                end_motor[i])
            if motorType[i] == "MotorPosition":
                label = "position"
            elif motorType[i] == "MotorVelocity":
                label = "velocity"
            txt4 = '   {}:{:5.2f};\tEnabled:{}'.format(label, speed[i],
                                                       enabled_motor[i])
            print(txt0 + txt1 + txt2 + ftxt3 + txt4)

        tabMotorVal.append([
                            motorName[i],
                            start_motor[i],
                            end_motor[i],
                            speed[i],
                            jointID[i],
                            enabled_motor[i]
                           ]
                           )
        i = i+1
    # print()
    return tabMotorVal


def affichExtStim(optSet, ExternalStimuli, show):
    # To find elements by type:
    # Options are: Neurons, Adapters, ExternalStimuli
    # Neurons = model.getElementByType("Neurons")
    tabStimVal = []
    st = 0
    stimName, start_stim, end_stim = [], [], []
    currON_stim, currOFF_stim, enabled_stim = [], [], []
    targetNodeId = []
    while st < len(ExternalStimuli):
        stimName.append(ExternalStimuli[st].find("Name").text)
        start_stim.append(float(ExternalStimuli[st].find("StartTime").text))
        end_stim.append(float(ExternalStimuli[st].find("EndTime").text))
        currON_stim.append(float(ExternalStimuli[st].find("CurrentOn").text))
        currOFF_stim.append(float(ExternalStimuli[st].find("CurrentOff").text))
        enabled_stim.append(ExternalStimuli[st].find("Enabled").text)
        targetNodeId.append(ExternalStimuli[st].find("TargetNodeID").text)
        st = st+1
    # ... and print them
    if show == 1:
        print()
        print("list of external stimuli")
    st = 0
    while st < len(ExternalStimuli):
        if show == 1:
            if optSet.ExternalStimuli[st].find("Enabled").text == 'True':
                txt = '[%2d]  %s:\tStartTime:%.4e;\tEndTime:%.4e;'\
                        + '\tCurrentOn %.4e;\tCurrentOff:%.4e;\tEnabled:%s'
                print(txt % (
                            st,
                            stimName[st],
                            start_stim[st],
                            end_stim[st],
                            currON_stim[st],
                            currOFF_stim[st],
                            enabled_stim[st]
                            ))
        tabStimVal.append([
                           stimName[st],
                           start_stim[st],
                           end_stim[st],
                           currON_stim[st],
                           currOFF_stim[st],
                           enabled_stim[st],
                           targetNodeId[st]
                           ]
                          )
        st = st+1
    # print()
    return tabStimVal


def affichNeurons(optSet, Neurons, show):
    # To find elements by type:
    # Options are: Neurons, Adapters, ExternalStimuli
    # Neurons = model.getElementByType("Neurons")
    tabNeurons = []
    i = 0
    neurName = []
    while i < len(Neurons):
        neurName.append(Neurons[i].find("Name").text)
        i = i+1
    # ... and print them
    if show == 1:
        print()
        print("list of 'Voltage' neurons (disabled neurons are not shown)")
    if len(Neurons) == 0:
        print("No 'Voltage' Neuron")
    i = 0
    while i < len(Neurons):
        if show == 1:
            if optSet.Neurons[i].find("Name").text != 'Disabled':
                txt = '[%2d]  %s:'
                print(txt % (
                            i,
                            neurName[i]
                            ))
        tabNeurons.append([
                           neurName[i]
                           ]
                          )
        i = i+1
    return tabNeurons


def affichNeuronsFR(optSet, NeuronsFR, show):
    # To find elements by type:
    # Options are: Neurons, Adapters, ExternalStimuli
    # Neurons = model.getElementByType("Neurons")
    tabNeuronsFR = []
    i = 0
    neurNameFR = []
    while i < len(NeuronsFR):
        neurNameFR.append(NeuronsFR[i].find("Name").text)
        i = i+1
    # ... and print them
    if show == 1:
        print()
        print("list of 'Firing Rate' neurons (disabled neurons are not shown)")
        if len(NeuronsFR) == 0:
            print("No  'Firing Rate' Neuron")

    i = 0
    while i < len(NeuronsFR):
        if show == 1:
            if optSet.NeuronsFR[i].find("Name").text != 'Disabled':
                txt = '[{:2d}]  {}:'
                print(txt.format(
                            i,
                            neurNameFR[i]
                            ))
        tabNeuronsFR.append([
                           neurNameFR[i]
                           ]
                          )
        i = i+1
    return tabNeuronsFR


def liste(Neurons):
    listNeurons = []
    i = 0
    while i < len(Neurons):
        listNeurons.append(Neurons[i].find("Name").text)
        i = i+1
    return listNeurons


def affichConnexions(model, optSet, Connexions, show):
    tabConnexions = []
    syn = 0
    sourceID, targetID, connexType, connexG = [], [], [], []
    connexSourceName, connexTargetName = [], []
    synapseID, synapseName, synapseType = [], [], []
    synapseEquil, synapseSynAmp, synapseThr = [], [], []
    # get connexions' source, target, and values...
    while syn < len(Connexions):
        sourceID.append(Connexions[syn].find("SourceID").text)
        targetID.append(Connexions[syn].find("TargetID").text)
        neuronSource = model.getElementByID(sourceID[syn])
        neuronTarget = model.getElementByID(targetID[syn])
        connexSourceName.append(neuronSource.find("Name").text)
        connexTargetName.append(neuronTarget.find("Name").text)
        connexType.append(Connexions[syn].find("Type").text)
        connexG.append(float(Connexions[syn].find("G").text))

        synapseTempID = Connexions[syn].find("SynapseTypeID").text
        synapseID.append(synapseTempID)
        synapseTempName = model.getElementByID(synapseTempID).find("Name").text
        synapseName.append(synapseTempName)
        synapseTempType = model.getElementByID(synapseTempID).find("Type").text
        synapseType.append(synapseTempType)
        TempEquil = model.getElementByID(synapseTempID).find("Equil").text
        synapseEquil.append(float(TempEquil))
        TempSynAmp = model.getElementByID(synapseTempID).find("SynAmp").text
        synapseSynAmp.append(float(TempSynAmp))
        if synapseTempType == "NonSpikingChemical":
            TempThreshV = model.getElementByID(synapseTempID).\
                find("ThreshV").text
            synapseThr.append(float(TempThreshV))
        elif synapseTempType == "SpikingChemical":
            TempThreshV = model.getElementByID(synapseTempID).\
                find("ThreshPSPot").text
            synapseThr.append(float(TempThreshV))
        syn = syn+1
    # ... and print them
    if show == 1:
        print()
        print("list of 'Voltage neurons' connexions")
    if len(Connexions) == 0:
        print("No  'Voltage neurons' Connexions")
    syn = 0
    nbConnexions = len(Connexions)
    for syn in range(nbConnexions):
        if show == 1:
            if syn not in optSet.disabledSynNbs:
                space = ""
                for k in range(4-int((len(synapseName[syn])+7)/8)):
                    space += "\t"
                txt = '[%2d]  %s;' + space + 'SynAmp:%4.2f;\tThr:%4.2f;'
                txt = txt + '\tGMax:%4.3f;\tEquil:%4.2f; \t%s;\t%s->%s'
                print(txt % (
                            syn,
                            synapseName[syn],
                            synapseSynAmp[syn],
                            synapseThr[syn],
                            connexG[syn],
                            synapseEquil[syn],
                            synapseType[syn],
                            connexSourceName[syn],
                            connexTargetName[syn]
                            ))
        tabConnexions.append([
                        synapseName[syn],
                        synapseSynAmp[syn],
                        synapseThr[syn],
                        connexG[syn],
                        synapseEquil[syn],
                        synapseType[syn],
                        connexSourceName[syn],
                        connexTargetName[syn]
                        ]
                        )
    return tabConnexions


def affichConnexionsFR(model, optSet, SynapsesFR, show):
    tabConnexionsFR = []
    syn = 0
    # sourceID, targetID = [], []
    connexSourceName, connexTargetName = [], []
    synapseID, synapseName, synapseType = [], [], []
    synapseWeight = []
    # get connexions' source, target, and values...
    firstSynapseFR = findFirstType(model, "SynapsesFR")

    for syn in range(len(SynapsesFR)):
        tempName = model.lookup["Name"][firstSynapseFR+syn]
        tempName.split('*')
        neuronSource = tempName.split('*')[0]
        neuronTarget = tempName.split('*')[1]
        connexSourceName.append(neuronSource)
        connexTargetName.append(neuronTarget)

        synapseTempID = SynapsesFR[syn].find("ID").text
        synapseID.append(synapseTempID)
        synapseTempName = connexSourceName[syn] + "-" + connexTargetName[syn]
        synapseName.append(synapseTempName)
        synapseTempType = SynapsesFR[syn].find("Type").text
        synapseType.append(synapseTempType)

        TempWeight = model.getElementByID(synapseTempID).find("Weight").text
        synapseWeight.append(float(TempWeight))

    # ... and print them
    if show == 1:
        print()
        print("list of 'Firing Rate' neuron connexions")
        if len(SynapsesFR) == 0:
            print("No  'Firing Rate' neuron Connexions")
    syn = 0
    for syn in range(len(SynapsesFR)):
        if show == 1:
            if syn not in optSet.disabledSynFRNbs:
                sp = ""
                for n in range(3-int((len(synapseName[syn])+1)/8)):
                    sp += '\t'
                txt = '[{:2d}]\t{};' + sp + '\tWeight:{:.2e};\t{};\t{}  ->\t{}'
                print(txt.format(
                            syn,
                            synapseName[syn],
                            synapseWeight[syn],
                            synapseType[syn],
                            connexSourceName[syn],
                            connexTargetName[syn]
                            ))
        tabConnexionsFR.append([
                        synapseName[syn],
                        synapseWeight[syn],
                        synapseType[syn],
                        connexSourceName[syn],
                        connexTargetName[syn]
                        ]
                        )
    return tabConnexionsFR


def getlistparam(optSet, seriesStimParam,
                 seriesSynParam, seriesSynNSParam, seriesSynFRParam,
                 asimtab_stims,
                 asimtab_connexions,
                 asimtab_connexionsFR):
    val = []
    stimName = []
    synName = []
    synFRName = []

    listSt = optSet.stimList + optSet.dontChangeStimNbs
    for partyp in range(len(seriesStimParam)):
        paramTyp = seriesStimParam[partyp]
        if paramTyp == "StartTime":
            for stim in range(len(listSt)):
                val.append(asimtab_stims[listSt[stim]][1])
                stimName.append(asimtab_stims[listSt[stim]][0] + "." +
                                paramTyp)
        if paramTyp == "EndTime":
            for stim in range(len(listSt)):
                val.append(asimtab_stims[listSt[stim]][2])
                stimName.append(asimtab_stims[listSt[stim]][0] + "." +
                                paramTyp)
        if paramTyp == "CurrentOn":
            for stim in range(len(listSt)):
                valstim = asimtab_stims[listSt[stim]][3]
                val.append(valstim)
                stimName.append(asimtab_stims[listSt[stim]][0] + "." +
                                paramTyp)

    synNbs = optSet.synList + optSet.dontChangeSynNbs
    for synparam in range(len(seriesSynParam)):
        synparamTyp = seriesSynParam[synparam]
        if synparamTyp == 'G':
            # this is a connexion -> name is in "model.lookup["Name"]"
            firstConnexion = findFirstType(optSet.model, "Connexions")
            for idx, syn in enumerate(synNbs):
                if asimtab_connexions[syn][5] == 'SpikingChemical':
                    # confirms that it is a spiking chemichal synapse
                    rang = syn + firstConnexion
                    name = optSet.model.lookup["Name"][rang] +\
                        "." + synparamTyp
                    synName.append(name)
                    synval = asimtab_connexions[syn][3]
                    val.append(synval)

    for synparam in range(len(seriesSynNSParam)):
        synparamTyp = seriesSynNSParam[synparam]
        if synparamTyp == 'SynAmp':
            for syn in synNbs:
                if asimtab_connexions[syn][5] == 'NonSpikingChemical':
                    synName.append(asimtab_connexions[syn][0] + "." +
                                   synparamTyp)
                    synval = asimtab_connexions[syn][1]
                    val.append(synval)
        if synparamTyp == 'ThreshV':
            for syn in synNbs:
                if asimtab_connexions[syn][5] == 'NonSpikingChemical':
                    synName.append(asimtab_connexions[syn][0] + "." +
                                   synparamTyp)
                    synval = asimtab_connexions[syn][2]
                    val.append(synval)

    for synparam in range(len(seriesSynFRParam)):
        synparamTyp = seriesSynFRParam[synparam]
        if synparamTyp == "Weight":
            firstConnexionFR = findFirstType(optSet.model, "SynapsesFR")
            for idx, synFR in enumerate(optSet.synListFR):
                rang = synFR + firstConnexionFR
                temp = optSet.model.lookup["Name"][rang] + "." + synparamTyp
                synFRName.append(temp)
                val.append(asimtab_connexionsFR[synFR][1])

    result = [listSt, val, stimName, synName, synFRName]
    return result


def getSimSetFromAsim(optSet,
                      seriesStimParam, seriesSynParam,
                      seriesSynNSParam, seriesSynFRParam,
                      asimFileName, affiche=0):
    asimModel = AnimatLabModel.AnimatLabSimFile(asimFileName)

    asim_motorP = asimModel.getElementByType("MotorPosition")
    asim_motorV = asimModel.getElementByType("MotorVelocity")
    asim_motorStimuli = [asim_motorP, asim_motorV]
    asimtab_motorst = affichMotor(asimModel, asim_motorStimuli,
                                  affiche)
    asimExternalStimuli = asimModel.getElementByType("ExternalStimuli")
    asimtab_stims = affichExtStim(optSet, asimExternalStimuli,
                                  affiche)
    asimConnexions = asimModel.getElementByType("Connexions")
    asimtab_connexions = affichConnexions(asimModel, optSet, asimConnexions,
                                          affiche)
    asimSynapsesFR = asimModel.getElementByType("SynapsesFR")
    asimtab_connexionsFR = affichConnexionsFR(asimModel, optSet,
                                              asimSynapsesFR,
                                              affiche)
    # initlistparam()
    res = getlistparam(optSet,
                       seriesStimParam,
                       seriesSynParam, seriesSynNSParam, seriesSynFRParam,
                       asimtab_stims,
                       asimtab_connexions,
                       asimtab_connexionsFR)
    [listSt, val, stimParName, synParName, synFRParName] = res
    simSet = SimulationSet.SimulationSet()
    for st in range(len(stimParName)):
        simSet.set_by_range({stimParName[st]: [val[st]]})
    nst = len(stimParName)
    for syn in range(len(synParName)):
        simSet.set_by_range({synParName[syn]: [val[nst+syn]]})
    nsyn = len(synParName)
    for syFR in range(len(synFRParName)):
        simSet.set_by_range({synFRParName[syFR]: [val[nst+nsyn+syFR]]})
    if affiche:
        print(simSet.samplePts)
    return [simSet, asimtab_stims, asimtab_motorst]


# TODO : datastructure
# ============================================================================
#                          gestion of datastructure
# ============================================================================
def mise_a_jour(optSet, datastructure, structNb, typ,
                startseq, endseq, packetsize, conditions):
    val = {structNb: [typ, startseq, endseq, packetsize, conditions]}
    datastructure.update(val)
    optSet.datastructure = datastructure


def save_datastructure(datastructure, completeparfilename):
    # datastructure = optSet.datastructure
    f = open(completeparfilename, 'w')
    for idx in range(len(datastructure)):
        s = str(idx) + '\t'
        for idy in range(len(datastructure[idx])-1):
            tmpval = datastructure[idx][idy]
            s += "{}".format(tmpval) + '\t'
        s += "{}".format(datastructure[idx][idy+1]) + '\n'
        f.write(s)
    print(s)
    print
    f.close()


def load_datastructure(completeparfilename):
    filename = os.path.split(completeparfilename)[-1]
    sourceDir = os.path.split(completeparfilename)[0:-1][0]
    tab = readTabloTxt(sourceDir, filename)
    st = tab[0]
    txt4 = st[4]
    txt4 = txt4[1:-1]       # suppress the crochets (or parentheses)
    sptxt4 = txt4.split()
    if sptxt4 == []:
        datastructure = load_datastructureWithPacketSize(completeparfilename)
    else:
        datastructure = load_datastructureNoPacketSize(completeparfilename)
    return datastructure


def load_datastructureNoPacketSize(completeparfilename):
    filename = os.path.split(completeparfilename)[-1]
    sourceDir = os.path.split(completeparfilename)[0:-1][0]
    tab = readTabloTxt(sourceDir, filename)
    datastructure = {}
    for idx, st in enumerate(tab):
        tmpCond = []
        tmpCond2 = []
        newCondition = []
        debList = []
        finList = []
        listOfLists = []
        nbList = 0
        try:
            txt4 = st[4]
            txt4 = txt4[1:-1]       # suppress the crochets (or parentheses)
            sptxt4 = txt4.split()   # -> split in an array
            for ind, txt in enumerate(sptxt4):
                if txt[-1] == ",":   # suppress the comas
                    txb = txt[:-1]
                else:
                    txb = txt
                tmpCond.append(txb)
            for index, tx in enumerate(tmpCond):
                if tx[0] == '[':
                    tx = tx[1:]
                    nbList += 1
                    debList.append(index)
                if tx[-1] == ']':
                    tx = tx[:-1]
                    finList.append(index)
                try:
                    tmpCond2.append(float(tx))
                except Exception as e:  # this is text variable->chartName
                    if (verbose > 2):
                        print(e)
                    # suppression of left and right " ' "
                    tx = tx[1:-1]
                    tmpCond2.append(tx)

            for k in range(len(debList)):
                tmpList = []
                for idy in range(debList[k], finList[k]+1):
                    tmpList.append(tmpCond2[idy])
                listOfLists.append(tmpList)

            k = 0
            j = 0
            while k < len(debList):
                for i in range(j, debList[k]):
                    newCondition.append(tmpCond2[i])
                newCondition.append(listOfLists[k])
                j = finList[k] + 1
                k += 1
            datastructure[idx] = [st[1], int(st[2]), int(st[3]), 0,
                                  newCondition]
        except Exception as e:
            if (verbose > 2):
                print(e)
            datastructure[idx] = [st[1], int(st[2]), int(st[3]), 0]
    if (verbose > 4):
        None
        # print(datastructure)
    return datastructure


def load_datastructureWithPacketSize(completeparfilename):
    filename = os.path.split(completeparfilename)[-1]
    sourceDir = os.path.split(completeparfilename)[0:-1][0]
    tab = readTabloTxt(sourceDir, filename)
    datastructure = {}
    for idx, st in enumerate(tab):
        tmpCond = []
        tmpCond2 = []
        newCondition = []
        debList = []
        finList = []
        listOfLists = []
        nbList = 0
        try:
            txt5 = st[5]
            txt5 = txt5[1:-1]       # suppress the crochets (or parentheses)
            sptxt5 = txt5.split()   # -> split in an array
            for ind, txt in enumerate(sptxt5):
                if txt[-1] == ",":   # suppress the comas
                    txb = txt[:-1]
                else:
                    txb = txt
                tmpCond.append(txb)
            for index, tx in enumerate(tmpCond):
                # print(index, tx, "\t---> ", end=' ')
                if tx[0] == '[':
                    tx = tx[1:]
                    nbList += 1
                    debList.append(index)
                if tx[-1] == ']':
                    tx = tx[:-1]
                    finList.append(index)
                try:
                    if tx.find(".") == -1:
                        tmpCond2.append(int(tx))
                    else:
                        tmpCond2.append(float(tx))
                except Exception as e:  # this is text variable->chartName
                    if (verbose > 2):
                        print(e)
                    # suppression of left and right " ' "
                    tx = tx[1:-1]
                    tmpCond2.append(tx)
                # print(tx)

            for k in range(len(debList)):
                tmpList = []
                for idy in range(debList[k], finList[k]+1):
                    tmpList.append(tmpCond2[idy])
                listOfLists.append(tmpList)

            k = 0
            j = 0
            while k < len(debList):
                for i in range(j, debList[k]):
                    newCondition.append(tmpCond2[i])
                newCondition.append(listOfLists[k])
                j = finList[k] + 1
                k += 1
            datastructure[idx] = [st[1], int(st[2]), int(st[3]),
                                  int(st[4]), newCondition]
        except Exception as e:
            if (verbose > 2):
                print(e)
            datastructure[idx] = [st[1], int(st[2]), int(st[3]), int(st[4])]
    if (verbose > 4):
        None
        # print(datastructure)
    return datastructure


def oldload_datastructureNoPacketSize(completeparfilename):
    filename = os.path.split(completeparfilename)[-1]
    sourceDir = os.path.split(completeparfilename)[0:-1][0]
    tab = readTabloTxt(sourceDir, filename)
    datastructure = {}
    for idx, st in enumerate(tab):
        tmpCond = []
        newCondition = []
        newErrList = []
        newChartList = []
        newParamSetNb = []
        debIdxErr = 0
        finIdxErr = 0
        try:
            txt4 = st[4]
            txt4 = txt4[1:-1]       # suppress the crochets (or parentheses)
            sptxt4 = txt4.split()   # -> split in an array
            for ind, txt in enumerate(sptxt4):
                if txt[-1] == ",":   # suppress the comas
                    txb = txt[:-1]
                else:
                    txb = txt
                tmpCond.append(txb)
            for index, tx in enumerate(tmpCond):
                print(index, tx)
                if tx[0] != '[' and tx[-1] != ']':
                    if verbose > 2:
                        print(tx)
                if tx[0] == '[':
                    tx = tx[1:]     # suppress left crochet
                    if verbose > 2:
                        print(tx)
                    if debIdxErr == 0:
                        debIdxErr = index
                if tx[-1] == ']':
                    tx = tx[:-1]     # suppress right crochet
                    if verbose > 2:
                        print(tx)
                    tmpCond[index] = tx
                    if finIdxErr == 0:  # this is the first right crochet
                        finIdxErr = index
                if len(tx) > 0:
                    try:
                        tmpCond[index] = float(tx)
                    except Exception as e:  # this is text variable->chartName
                        if (verbose > 2):
                            print(e)
                        # suppression of left and right " ' "
                        tmpCond[index] = tx[1:-1]
                else:
                    tmpCond[index] = []
            if finIdxErr != len(tmpCond)-1:    # test if errList exsit
                if tmpCond[finIdxErr] == []:
                    None
                else:
                    for ind in range(debIdxErr, finIdxErr+1):
                        if tmpCond[ind] != '':
                            newErrList.append(tmpCond[ind])
                    for ind in range(finIdxErr+1,
                                     finIdxErr+1+finIdxErr+1-debIdxErr):
                        if tmpCond[ind] != '':
                            newChartList.append(tmpCond[ind])
            else:
                for ind in range(debIdxErr, finIdxErr+1):
                    newChartList.append(tmpCond[ind])
            if finIdxErr+1+finIdxErr+1-debIdxErr < len(tmpCond):
                # this means that param sets of charts are present
                for ind in range(finIdxErr+1+finIdxErr+1-debIdxErr,
                                 len(tmpCond)):
                    if tmpCond[ind] != []:
                        newParamSetNb.append(int(tmpCond[ind]))
            for i in range(debIdxErr):
                newCondition.append(tmpCond[i])
            if newErrList != []:
                newCondition.append(newErrList)
            if newChartList != []:
                newCondition.append(newChartList)
            if newParamSetNb != []:
                newCondition.append(newParamSetNb)

            # A fouth parameter is added with a value = O to allow compatibiliy
            # with previous version without packetsize
            datastructure[idx] = [st[1], int(st[2]), int(st[3]), 0,
                                  newCondition]
        except Exception as e:
            if (verbose > 2):
                print(e)
            datastructure[idx] = [st[1], int(st[2]), int(st[3]), 0]
    if (verbose > 4):
        None
        # print(datastructure)
    return datastructure


def oldload_datastructureWithPacketSize(completeparfilename):
    filename = os.path.split(completeparfilename)[-1]
    sourceDir = os.path.split(completeparfilename)[0:-1][0]
    tab = readTabloTxt(sourceDir, filename)
    datastructure = {}
    for idx, st in enumerate(tab):
        tmpCond = []
        newCondition = []
        newErrList = []
        newChartList = []
        newParamSetNb = []
        newSupplInfo = []
        debIdxErr = 0
        finIdxErr = 0
        try:
            txt5 = st[5]
            txt5 = txt5[1:-1]       # suppress the crochets (or parentheses)
            sptxt5 = txt5.split()   # -> split in an array
            for ind, txt in enumerate(sptxt5):
                if txt[-1] == ",":   # suppress the comas
                    txb = txt[:-1]
                else:
                    txb = txt
                tmpCond.append(txb)
            for index, tx in enumerate(tmpCond):
                print(index, tx)
                if tx[0] != '[' and tx[-1] != ']':
                    if verbose > 2:
                        print(tx)
                if tx[0] == '[':
                    tx = tx[1:]     # suppress left crochet
                    if verbose > 2:
                        print(tx)
                    if debIdxErr == 0:
                        debIdxErr = index
                if tx[-1] == ']':
                    tx = tx[:-1]     # suppress right crochet
                    if verbose > 2:
                        print(tx)
                    tmpCond[index] = tx
                    if finIdxErr == 0:  # this is the first right crochet
                        finIdxErr = index
                if len(tx) > 0:
                    try:
                        tmpCond[index] = float(tx)
                    except Exception as e:  # this is text variable->chartName
                        if (verbose > 2):
                            print(e)
                        # suppression of left and right " ' "
                        tmpCond[index] = tx[1:-1]
                else:
                    tmpCond[index] = []

            # if errlist exists
            if debIdxErr != 0:
                if finIdxErr != len(tmpCond)-1:
                    if tmpCond[finIdxErr] != []:
                        # create newErrList
                        for ind in range(debIdxErr, finIdxErr+1):
                            if tmpCond[ind] != '':
                                newErrList.append(tmpCond[ind])
                        # create newChartList
                        for ind in range(finIdxErr+1,
                                         finIdxErr+1+finIdxErr+1-debIdxErr):
                            if tmpCond[ind] != '':
                                newChartList.append(tmpCond[ind])
                else:
                    # create newChartList
                    for ind in range(debIdxErr, finIdxErr+1):
                        newChartList.append(tmpCond[ind])
                if finIdxErr+1+finIdxErr+1-debIdxErr < len(tmpCond):
                    nbcharts = finIdxErr+1 - debIdxErr
                    # this means that param sets of charts are present
                    startparam = finIdxErr+1+finIdxErr+1-debIdxErr
                    for ind in range(startparam, startparam + nbcharts):
                        #            len(tmpCond)):
                        if tmpCond[ind] != []:
                            newParamSetNb.append(int(tmpCond[ind]))
                if startparam + nbcharts < len(tmpCond):
                    for ind in range(startparam + nbcharts, len(tmpCond)):
                        newSupplInfo.append(int(tmpCond[ind]))

                for i in range(debIdxErr):
                    newCondition.append(tmpCond[i])
            else:
                for i in range(len(tmpCond)):
                    newCondition.append(tmpCond[i])
            if newErrList != []:
                newCondition.append(newErrList)
            if newChartList != []:
                newCondition.append(newChartList)
            if newParamSetNb != []:
                newCondition.append(newParamSetNb)
            if newSupplInfo != []:
                newCondition.append(newSupplInfo)
            datastructure[idx] = [st[1], int(st[2]), int(st[3]),
                                  int(st[4]), newCondition]
        except Exception as e:
            if (verbose > 2):
                print(e)
            datastructure[idx] = [st[1], int(st[2]), int(st[3]), int(st[4])]
    if (verbose > 4):
        None
        # print(datastructure)
    return datastructure


def readSpan_from_DicSpanVal(dicSpanVal_file):
    dicSpanVal = {}
    listspanval = []
    if os.path.exists(dicSpanVal_file):
        with open(dicSpanVal_file, 'r') as f:
           for line in f:
               var, val = (item.strip() for item in line.split(':', 1))
               dicSpanVal[var] = float(val)
               listspanval.append(float(val))
               space = "\t"
               if len(var) < 28:
                   space += "\t"
                   if len(var) < 24:
                       space += "\t"
                       if len(var) < 20:
                           space += "\t"
                       # print("{}\t\t{}".format(var, val))
               print("{}{}{}".format(var, space, val))
        f.close()
    else:
        print("No file named dicSpanVal.txt in GEPdata")
        # print(dicSpanVal)
    return dicSpanVal, listspanval


def readSpan(datastructure, dicSpanVal_file=""):
    spanStim, spanSyn = 100, 100
    if len(datastructure) > 0:
        rg = len(datastructure) - 1
        # rg = 0
        conditions = datastructure[rg][4]
        if type(conditions[0]) is list:    # this is the new span list format
            if len(conditions[0]) == 1:
                if conditions[0][0] == 'DicSpanVal.txt':
                    print("listspanval <- 'DicSpanVal.txt'")
                rep = readSpan_from_DicSpanVal(dicSpanVal_file)
                response = rep[1]
            else:
                lenspanlist = len(conditions[0])
                listspanVal = [conditions[0][i] for i in range(lenspanlist)]
                response = listspanVal
        else:   # this is the old format with spanStim and spanSyn
            spanStim = conditions[0]
            spanSyn = conditions[1]
            print("spanstim={}; spansyn={}".format(spanStim, spanSyn))
            response = spanStim, spanSyn
    return response


def readCoacPenality(datastructure):
    coactpenality1, coactpenality2 = 100, 0
    if len(datastructure) > 0:
        rg = len(datastructure) - 1
        # rg = 0
        conditions = datastructure[rg][4]
        if type(conditions[0]) is list:    # this is the new span list format
            coact = conditions[1]
        else:   # this is the old format with spanStim and spanSyn
            coact = conditions[2]
        if type(coact) is list:
            coactpenality1 = coact[0]
            coactpenality2 = coact[1]
        else:
            coactpenality1 = coact
            coactpenality2 = coact
        print("coactpenality1={}; coactpenality2={}".format(coactpenality1,
                                                            coactpenality2))
    return coactpenality1, coactpenality2


def readGravity(datastructure):
    gravity = -9.81
    if len(datastructure) > 0:
        rg = len(datastructure) - 1
        # rg = 0
        conditions = datastructure[rg][4]
    typ = datastructure[rg][0]
    conditions = datastructure[rg][4]
    if type(conditions[0]) is list:    # this is the new span list format
        delta = -1
    else:   # this is the old format with spanStim and spanSyn
        delta = 0
    if typ == 'CMAES' or typ == 'CMAE':
        if len(conditions) > 7+delta:
            gravity = float(conditions[7+delta][0])
        else:
            gravity = -9.81
    else:
        if len(conditions) > 6+delta:
            gravity = float(conditions[6+delta][0])
        else:
            gravity = -9.81
    print("gravity = {}".format(gravity))
    return gravity


# TODO : files
# ============================================================================
#                          gestion of files (read, write)
# ============================================================================

def getValuesFromText(txt):
    t2 = txt
    xtab = []
    while t2.find('\t') != -1:
        t1 = t2[:t2.find('\t')]
        t2 = t2[t2.find('\t')+1:]
        xtab.append(t1)
    if t2.find('\n') != -1:
        t1 = t2[:t2.find('\n')]
    else:
        t1 = t2[:]
    xtab.append(t1)
    return xtab


def readTabloTxt(sourceDir, filename):
    tabfinal = []
    pathname = os.path.join(sourceDir, filename)
    if os.path.exists(pathname):
        f = open(pathname, 'r')
        i = 0
        while 1:
            # print(i)
            tab1 = []
            tab2 = []
            txt = f.readline()
            # print(txt)
            if txt == '':
                break
            else:
                tab1 = getValuesFromText(txt)
                # print(tab1)
                try:
                    for k in range(len(tab1)):
                        tab2.append(tab1[k])
                    tabfinal.append(tab2)
                except Exception as e:
                    k = 0
                    if (verbose > 1):
                        print(e)
                i = i+1
        f.close()
    return tabfinal


def readTablo(sourceDir, filename):
    tabfinal = []
    pathname = os.path.join(sourceDir, filename)
    if os.path.exists(pathname):
        f = open(pathname, 'r')
        i = 0
        while 1:
            # print(i)
            tab1 = []
            tab2 = []
            txt = f.readline()
            # print(txt)
            if txt == '':
                break
            else:
                tab1 = getValuesFromText(txt)
                # print(tab1)
                try:
                    for k in range(len(tab1)):
                        tab2.append(float(tab1[k]))
                    tabfinal.append(tab2)
                except Exception as e:
                    k = 0
                    if (verbose > 3):
                        print(e)
                i = i+1
        f.close()
    return tabfinal


# does the same thing that the one above ?
def tablo(directory, filename):
    """
    Function tablo:
        In : directory : the path to the file we want to read
            filename : the name of the file we want to read
        This function return an array which contains the values from a txt file
    """
    tabfinal = []
    pathname = os.path.join(directory, filename)
    if os.path.exists(pathname):
        f = open(pathname, 'r')
        i = 0
        while 1:
            tab1 = []
            tab2 = []
            txt = f.readline()
            if txt == '':
                break
            else:
                tab1 = getValuesFromText(txt)
                if type(tab1[0]) is str:
                    tab2 = tab1
                else:
                    for k in range(len(tab1)):
                        tab2.append(float(tab1[k]))
                tabfinal.append(tab2)
                i = i+1
        f.close()
    else:
        print(pathname, "does not exist!!!")
    return tabfinal


def savecurve(table, directory, filename):
    f = open(os.path.join(directory, filename), 'w')
    for i in range(len(table)):
        s = (str(table[i][0]) + '\t' +
             str(table[i][1]) + '\t' +
             str(table[i][2]) + '\n')
        f.write(s)
    f.close()


def erase_folder_content(folder):
    """
    This function erases the files of a directory.
    If sub-directories are to be erased too, then un-comment "elif"
    """
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            # elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)


def copyFile(filename, src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)
    sourcefile = os.path.join(src, filename)
    destfile = os.path.join(dst, filename)
    shutil.copy(sourcefile, destfile)


def moveFile(filename, src, dst):
    sourcefile = os.path.join(src, filename)
    destfile = os.path.join(dst, filename)
    os.rename(sourcefile, destfile)


def copyFileWithExt(sourceDir, destDir, ext):
    for basename in os.listdir(sourceDir):
        if basename.endswith(ext):
            print(basename)
            pathname = os.path.join(sourceDir, basename)
            if os.path.isfile(pathname):
                shutil.copy2(pathname, destDir)


def copyRenameFile(sourcedir, filesource,
                   destdir, filedest, comment, replace):
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    src = os.path.join(sourcedir, filesource)
    # rootName = filedest.split('.')[0]
    rootName = os.path.splitext(filedest)[0]

    if not replace:
        oldName = rootName + '*.asim'
        ix = len(glob.glob(os.path.join(destdir, oldName)))
        newName = rootName + '-{0:d}.asim'.format(ix)
    else:
        ix = 0
        newName = rootName + '.asim'
    tgt = os.path.join(destdir, newName)
    print("saving ", filesource, "to", os.path.join(destdir, newName))
    shutil.copyfile(src, tgt)
    return ix


def copyRenameFilewithExt(sourcedir, filesource,
                          destdir, filedest,
                          ext, comment, replace=1):
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    src = os.path.join(sourcedir, filesource)
    # rootName = filedest.split('.')[0]
    rootName = os.path.splitext(filedest)[0]

    if not replace:
        oldName = rootName + '*' + ext
        ix = len(glob.glob(os.path.join(destdir, oldName)))
        newName = rootName + '-{0:d}'.format(ix) + ext
    else:
        ix = 0
        newName = rootName + ext
    tgt = os.path.join(destdir, newName)
    # print("saving ", filesource, "to", os.path.join(destdir, newName))
    shutil.copyfile(src, tgt)
    return newName


def copyDirectory(sourcedir, destdir):
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    for f in os.listdir(sourcedir):
        src = os.path.join(sourcedir, f)
        tgt = os.path.join(destdir, f)
        if os.path.isdir(src):
            try:
                shutil.copytree(src, tgt)
            except Exception as e:
                if (verbose > 2):
                    print(e)
        else:
            shutil.copy(src, tgt)


def copyFileDir(sourcedir, destdir, copy_dir=0):
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    for f in os.listdir(sourcedir):
        src = os.path.join(sourcedir, f)
        tgt = os.path.join(destdir, f)
        if os.path.isdir(src):
            if copy_dir:
                shutil.copytree(src, tgt)
        else:
            shutil.copy(src, tgt)


def copyFileDir_ext(sourcedir, destdir, list_ext, copy_dir=0):
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    for f in os.listdir(sourcedir):
        src = os.path.join(sourcedir, f)
        tgt = os.path.join(destdir, f)
        if os.path.splitext(src)[1] in list_ext:
            if os.path.isdir(src):
                if copy_dir:
                    shutil.copytree(src, tgt)
            else:
                shutil.copy(src, tgt)


def savechartfile(name, directory, chart, comment):
    number = 0
    txtnumber = "00"
    if not os.path.exists(directory):
        os.makedirs(directory)
    destfilename = os.path.join(directory, name + "00.txt")
    while os.path.exists(destfilename):
        number = number + 1
        if number < 10:
            txtnumber = "0" + str(number)
        else:
            txtnumber = str(number)
        destfilename = os.path.join(directory, name + txtnumber + ".txt")
    chartname = ""
    # copy(folders.animatlab_result_dir + txtchartname)
    if chart != []:
        chartname = name + txtnumber + ".txt"
        text = chartname + "; " + comment
        print("saving charttxt  file... " + name + "{}.txt".format(txtnumber), end=' ')
        f = open(destfilename, 'w')
        f.write(str(text + '\n'))
        for i in range(len(chart)):
            for j in range(len(chart[i])-1):
                f.write(str(chart[i][j]) + '\t')
            f.write(str(chart[i][j+1]) + '\n')
        f.close()
    else:
        print("no chart")
    return chartname


def savefileincrem(name, directory, tab, comment):
    number = 0
    txtnumber = "00"
    if not os.path.exists(directory):
        os.makedirs(directory)
    destfilename = os.path.join(directory, name + "00.txt")
    while os.path.exists(destfilename):
        number = number + 1
        if number < 10:
            txtnumber = "0" + str(number)
        else:
            txtnumber = str(number)
        destfilename = os.path.join(directory, name + txtnumber + ".txt")
    filename = ""
    # copy(folders.animatlab_result_dir + txtchartname)
    if tab != []:
        filename = name + txtnumber + ".txt"
        text = filename + "; " + comment
        print("saving txt file... " + name + "{}.txt".format(txtnumber))
        f = open(destfilename, 'w')
        f.write(str(text + '\n'))
        for i in range(len(tab)):
            for j in range(len(tab[i])-1):
                f.write(str(tab[i][j]) + '\t')
            f.write(str(tab[i][j+1]) + '\n')
        f.close()
    else:
        print("no chart")
    return filename


def createSubDirIncrem(destDir, destSubDir):
    number = 0
    txtnumber = "00"
    if not os.path.exists(destDir):
        os.makedirs(destDir)
    destdirname = os.path.join(destDir, destSubDir + "-00")
    while os.path.exists(destdirname):
        number = number + 1
        if number < 10:
            txtnumber = "0" + str(number)
        else:
            txtnumber = str(number)
        destdirname = os.path.join(destDir, destSubDir + "-" + txtnumber)
    os.makedirs(destdirname)
    print(destdirname)
    return destdirname + "/"


def writeaddTab(folders, tab, filename, mode, comment, flag):
    s = ""
    pathname = os.path.join(folders.animatlab_result_dir, filename)
    if mode == 'w':
        f = open(pathname, 'w')
    else:
        f = open(pathname, 'a')
    for i in range(len(tab)-1):
        s = s + str(tab[i]) + '\t'
    s = s + str(tab[i+1]) + '\n'
    if flag == 1:
        print(comment)
    f.write(s)
    f.close()


def read_addTab(folders, tab, filename, comment="", flag=0):
    pathname = os.path.join(folders.animatlab_result_dir, filename)
    strTab = []
    tmp = []
    if os.path.exists(pathname):
        f = open(pathname, 'r')
        while 1:
            txt = f.readline()
            # print(txt)
            if txt == '':
                break
            else:
                strTab = getValuesFromText((txt))
                tmp.append(float(strTab))
    f.close()
    return tmp


def checkCreateSubdirs(folders, animatsimdir):
    """
    This function checks that a folder contains the requiered subdirectories.
    If not they are created
    """
    folders.affectDirectories()
    aprojSaveDir = os.path.join(folders.animatlab_rootFolder, "AprojFiles")
    if not os.path.exists(aprojSaveDir):
        os.makedirs(aprojSaveDir)
        copyFileDir(animatsimdir,
                    aprojSaveDir,
                    copy_dir=0)
    aprojCMAeDir = os.path.join(folders.animatlab_rootFolder,
                                "CMAeSeuilAprojFiles")
    if not os.path.exists(aprojCMAeDir):
        os.makedirs(aprojCMAeDir)
        copyFileDir(animatsimdir,
                    aprojCMAeDir,
                    copy_dir=0)
    dirGEPdata = os.path.join(folders.animatlab_rootFolder,
                              "GEPdata")
    if not os.path.exists(dirGEPdata):
        os.makedirs(dirGEPdata)


def get_filepaths(directory):
    """
    This function will generate the file names in a directory
    tree by walking the tree either top-down or bottom-up. For each
    directory in the tree rooted at directory top (including top itself),
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    return file_paths  # Self-explanatory.


def findList_asimFiles(directory):
    list_asim = []
    if not os.path.exists(directory):
        print(directory, "does not exist !!!!!!")
    else:
        onlyfiles = [f for f in os.listdir(directory)
                     if os.path.isfile(os.path.join(directory, f))]
        # print(onlyfiles)
        for f in onlyfiles:
            if f.endswith(".asim"):
                # print(f)
                # simN = f[:f.find('.')]
                # print(simN)
                list_asim.append(f)
    return list_asim


def findChartName(model, optSet):
    simN = os.path.splitext((os.path.split(model.asimFile)[-1]))[0]
    chartN = optSet.chartName[optSet.selectedChart]
    chartName = simN + "-1_" + chartN + ".txt"
    return [simN, chartN, chartName]


def findAsimName(model, optSet):
    simN = os.path.splitext((os.path.split(model.asimFile)[-1]))[0]
    simName = simN + "-1" + ".asim"
    return [simN, simName]


def findTxtFileName(model, optSet, pre, x):
    simFileName = findChartName(model, optSet)[0]
    chartFileName = findChartName(model, optSet)[1]
    if x < 10:
        txtFileName = simFileName + "-" + pre + str(x) + "_" +\
            chartFileName + '.txt'
    else:
        txtFileName = simFileName + "-" + str(x) + "_" +\
            chartFileName + '.txt'
    # print("reading {}".format(txtFileName))
    return txtFileName


# TODO : mse on movement
# ===========================================================================
#               Gestion of movement Template
# ===========================================================================
def formTemplate(rate, startMvt1, endMvt1, angle1,
                 startMvt2, endMvt2, angle2, endPos2):
    temp = []
    k = 0.0
    for i in range(int(startMvt1*rate)):
        temp.append([i, k/rate, 0])
        k = k + 1
    k = float(startMvt1*rate)
    n = 0.0
    for i in range(int(startMvt1*rate), int(endMvt1*rate)):
        angleIncrease = (n/rate)*(angle1 - 0)/(endMvt1 - startMvt1)
        temp.append([i, k/rate, 0 + angleIncrease])
        k = k + 1
        n = n + 1
    k = float(endMvt1*rate)
    for i in range(int(endMvt1*rate), int(startMvt2*rate)):
        temp.append([i, k/rate, angle1])
        k = k + 1
    k = float(startMvt2*rate)
    n = 0.0
    for i in range(int(startMvt2*rate), int(endMvt2*rate)):
        angleIncrease = (n/rate)*(angle2 - angle1)/(endMvt2 - startMvt2)
        temp.append([i, k/rate, angle1 + angleIncrease])
        k = k + 1
        n = n + 1
    k = float(endMvt2*rate)
    for i in range(int(endMvt2*rate), int(endPos2*rate)+1):
        temp.append([i, k/rate, angle2])
        k = k + 1
    return temp


def flash(i, startseq, dest, nbPts):
    """
    equatiion for minimum jerk movemen (from Flash & Hogan, 1985)
    """
    tau = 0.
    tau = float(i)/nbPts
    pos = startseq + float(startseq-dest)*(15 * tau**4 - 6 * tau**5 - 10 * tau**3)
    # print("i:{}\t tau:{:2.4f}\t pos:{}".format(i, tau, pos))
    return pos


def formTemplateSmooth(rate, startMvt1, endMvt1, angle1,
                       startMvt2, endMvt2, angle2, endPos2):
    nbPtsMvt1 = int(endMvt1*rate) - int(startMvt1*rate)
    nbPtsMvt2 = int(endMvt2*rate) - int(startMvt2*rate)
    temp = []
    k = 0.0
    for i in range(int(startMvt1*rate)):
        temp.append([i, k/rate, 0])
        k = k + 1
    k = float(startMvt1*rate)
    n = 0.0
    for i in range(int(startMvt1*rate), int(endMvt1*rate)):
        angleIncrease = flash(n, 0, angle1, nbPtsMvt1)
        temp.append([i, k/rate, angleIncrease])
        k = k + 1
        n = n + 1
    k = float(endMvt1*rate)
    for i in range(int(endMvt1*rate), int(startMvt2*rate)):
        temp.append([i, k/rate, angle1])
        k = k + 1
    k = float(startMvt2*rate)
    n = 0.0
    for i in range(int(startMvt2*rate), int(endMvt2*rate)):
        angleIncrease = flash(n, angle1, angle2, nbPtsMvt2)
        temp.append([i, k/rate, angleIncrease])
        k = k + 1
        n = n + 1
    k = float(endMvt2*rate)
    for i in range(int(endMvt2*rate), int(endPos2*rate)+1):
        temp.append([i, k/rate, angle2])
        k = k + 1
    return temp


def mjtg(current, setpoint, frequency, move_time):
    trajectory = []
    trajectory_derivative = []
    timefreq = int(move_time * frequency)

    for time in range(1, timefreq):
        trajectory.append(
            current + (setpoint - current) *
            (10.0 * (float(time)/timefreq)**3
             - 15.0 * (float(time)/timefreq)**4
             + 6.0 * (float(time)/timefreq)**5))

        trajectory_derivative.append(
            frequency * (1.0/timefreq) * (setpoint - current) *
            (30.0 * (float(time)/timefreq)**2.0
             - 60.0 * (float(time)/timefreq)**3.0
             + 30.0 * (float(time)/timefreq)**4.0))

    return trajectory, trajectory_derivative


def calculate_maxspeed_from_ampl_duration(rate, amplitude, duration):
    traj, traj_vel = mjtg(0, amplitude, rate, duration)
    maxspeed = max(traj_vel)
    return maxspeed


def curve_maxspeed_ampl_duration(duration):
    rate = 100
    curveX = []
    curveY = []
    for ampl in range(10, 130, 10):
        mspeed = calculate_maxspeed_from_ampl_duration(rate, ampl, duration)
        curveX.append(ampl)
        curveY.append(mspeed)
    return curveX, curveY


def plot_series_curves_maxspeed_ampl_duration(graph_path, graph_name,
                                              mindur, maxdur, stepdur):
    # xaxis = [ampl for ampl in range(10, 130, 10)]
    # graph_name = "abaques_duration"
    plt.figure(figsize=(10, 10))
    for dur in np.arange(mindur, maxdur, stepdur):
        curveX, curveY = curve_maxspeed_ampl_duration(dur)
        plt.plot(curveX, curveY)
    plt.xlabel("mvt amplitude (°)", fontsize=18)
    plt.ylabel("max speed (°/s)", fontsize=18)
    plt.axis([0, 120, 0, 500])
    lst_dur = [int(dur * 1000) for dur in np.arange(mindur, maxdur, stepdur)]
    plt.legend(lst_dur)
    # plt.figure(figsize=(10, 10))
    plt.savefig(graph_path + '/' + graph_name + '.pdf')
    plt.savefig(graph_path + '/' + graph_name + '.eps')
    plt.show()


def calculate_minjerk_duration(amplitude, max_speed, rate, makeGraph=0):
    # Set up and calculate trajectory.
    average_velocity = max_speed/1.87
    current = 0.0
    setpoint = amplitude
    frequency = rate
    duration = float(setpoint - current) / average_velocity
    # print("duration = ", duration)
    traj, traj_vel = mjtg(current, setpoint, frequency, duration)
    if makeGraph:
        # Create plot.
        xaxis = [float(i) / frequency 
                 for i in range(1, int(duration * frequency))]
        plt.plot(xaxis, traj)
        plt.plot(xaxis, traj_vel)
        plt.title("Minimum jerk trajectory")
        plt.xlabel("Time [s]")
        plt.ylabel("Angle [deg] and angular velocity [deg/s]")
        plt.legend(['pos', 'vel'])
        plt.show()
    return duration, traj, traj_vel


def calculateMvtdurFromMax_Speed(optSet, max_speed, amplitude):
    rate = optSet.rate
    startMvt1, endMvt1 = optSet.startMvt1, optSet.endMvt1
    angle1 = optSet.angle1
    startMvt2, endMvt2 = optSet.startMvt2, optSet.endMvt2
    angle2, endPos2 = amplitude, optSet.endPos2
    print(rate, startMvt1, endMvt1, angle1)
    print(startMvt2, endMvt2, angle2, endPos2)

    durMvt2 = 4
    maxSpeed = 0
    temp = []
    while maxSpeed < max_speed:
        durMvt2 -= 1/float(rate)
        endMvt2 = startMvt2 + durMvt2
        nbPtsMvt2 = int(durMvt2 * rate)
        k = float(startMvt2*rate)
        n = 0.0
        prevmaxSpeed = maxSpeed
        # prevtemp = temp
        temp = []
        for i in range(int(startMvt2*rate), int(endMvt2*rate)):
            angleIncrease = flash(n, angle1, angle2, nbPtsMvt2)
            temp.append([k/rate, angleIncrease])
            k = k + 1
            n = n + 1
        mvt = [x[1] for x in temp]
        mvt2 = mvt
        mvt2prim = []
        dic_mvt2prim = {}
        for ang_idx in range(len(mvt2)-1):
            derivate = (mvt2[ang_idx+1]-mvt2[ang_idx])*rate
            mvt2prim.append(derivate)
            dic_mvt2prim[ang_idx] = derivate
        maxSpeed = max(mvt2prim[1:])
        prevdurMvt2 = durMvt2
    print("aimed max_speed:{}   max_speed:{}   durMvt2:{}".format(max_speed,
                                                                  prevmaxSpeed,
                                                                  prevdurMvt2))
    return prevdurMvt2


def extract(table, col, lineStart, lineEnd):
    res = []
    for i in range(lineStart, lineEnd):
        res.append(table[i][col])
    return res


def extractCol(table, col):
    """
    Function extractCol
        In : table : The table from which we'd like to read
            col : The number of the column we'd like to read
        Out : res : a table which contains all the values from the column col
        This function read a column from the table
    """
    res = []
    for i in range(len(table)):
        try:
            res.append(float(table[i][col]))
        except Exception as e:
            if (verbose > 1):
                print(e)
    return res


def derive(table):
    dtable = []
    for i in range(len(table) - 1):
        dtable.append(table[i+1] - table[i])
    return dtable


def mean(x):
    mean = sum(x)/len(x)
    return mean


def variance(data):
    if len(data) == 0:
        return 0
    K = data[0]
    n = 0
    Sum = 0
    Sum_sqr = 0
    for x in data:
        n = n + 1
        Sum += x - K
        Sum_sqr += (x - K) * (x - K)
    variance = (Sum_sqr - (Sum * Sum)/n)/(n - 1)
    # use n instead of (n-1) if want to compute the exact
    # variance of the given data
    # use (n-1) if data are samples of a larger population
    return variance


def correl(table, column1, column2, lineStart, lineEnd):
    res1 = extract(table, column1, lineStart, lineEnd)
    res2 = extract(table, column2, lineStart, lineEnd)
    dres1 = derive(res1)
    dres2 = derive(res2)
    covariance = 0
    moy1 = mean(dres1)
    moy2 = mean(dres2)
    for i in range(len(dres1)):
        covariance += (dres1[i]-moy1) * (dres2[i]-moy2)
    covariance = covariance / len(dres1)
    if (variance(dres1) == 0 or variance(dres2) == 0):
        return 0
    else:
        cov = covariance / sqrt(variance(dres1) * variance(dres2))
    return cov


def MeanSquarreError(data, val):
    if len(data) == 0:
        return 0
    n = 0
    Sum_sqr = 0
    for x in data:
        n = n + 1
        Sum_sqr += (x - val) * (x - val)
    mse = Sum_sqr/n
    # use n instead of (n-1) if want to compute the exact
    # variance of the given data
    # use (n-1) if data are samples of a larger population
    return mse


def MeanSquarreErrorTemplate(data, template, mvtfirstline,
                             lineStart, lineEnd, lag):
    """
    calculate the MSE between mvtdata (that starts at line mvtfirstline)
    and template that starts at 0
    """
    if len(data) == 0:
        return 0
    n = 0
    Sum_sqr = 0
    for x in range(lineStart, lineEnd):
        n = n + 1
        Sum_sqr += (data[x] - template[x+lag+mvtfirstline][2])**2
    mse = Sum_sqr/n
    # use n instead of (n-1) if want to compute the exact
    # variance of the given data
    # use (n-1) if data are samples of a larger population
    return mse


def chargeBestFeatures(folders, filename, defaultval, nbpar):
    strTab = []
    tmp = []
    pathname = os.path.join(folders.animatlab_result_dir, filename)
    if os.path.exists(pathname):
        f = open(pathname, 'r')
        while 1:
            txt = f.readline()
            # print(txt)
            if txt == '':
                break
            else:
                strTab = getValuesFromText((txt))
                for k in range(len(strTab)):
                    tmp.append(float(strTab[k]))
    else:
        for p in range(nbpar):
            tmp.append(defaultval)
    return tmp


def chargeParamValues(folders, filename, allPhases,
                      seriesParam, Param):
    strTab = []
    tmp = []
    pathname = os.path.join(folders.animatlab_result_dir, filename)
    if os.path.exists(pathname):
        f = open(pathname, 'r')
        while 1:
            txt = f.readline()
            # print(txt)
            if txt == '':
                break
            else:
                strTab = getValuesFromText((txt))
                for k in range(len(strTab)):
                    tmp.append(float(strTab[k]))
    else:
        for ph in range(len(allPhases)):
            [parList, sh, lineStart, lineEnd, template] = allPhases[ph]
            for p in range(len(parList)):    # partyp = stim or syn
                rank = parList[p]
                for parTyp in range(len(seriesParam)):
                    tmp.append(float(Param[rank].
                                     find(seriesParam[parTyp]).text))
    return tmp


def chargeBestParams(folders, filename, defaultval, allPhases, seriesParam):
    strTab = []
    tmp = []
    pathname = os.path.join(folders.animatlab_result_dir, filename)
    if os.path.exists(pathname):
        f = open(pathname, 'r')
        while 1:
            txt = f.readline()
            # print(txt)
            if txt == '':
                break
            else:
                strTab = getValuesFromText((txt))
                for k in range(len(strTab)):
                    tmp.append(float(strTab[k]))
    else:
        for phase in range(len(allPhases)):
            [parList, sh, lineStart, lineEnd, template] = allPhases[phase]
            for p in range(len(parList)):
                for parTyp in range(len(seriesParam)):
                    tmp.append(defaultval)
    return tmp


def chargeBestSynValues(folders, model, filename, Connex,
                        PhasesSyn, sersynparam):
    # filename = "synbestvalues.txt"
    strTab = []
    tmp = []
    pathname = os.path.join(folders.animatlab_result_dir, filename)
    if os.path.exists(pathname):
        f = open(pathname, 'r')
        while 1:
            txt = f.readline()
            print(txt)
            if txt == '':
                break
            else:
                strTab = getValuesFromText((txt))
                for k in range(len(strTab)):
                    tmp.append(float(strTab[k]))
    else:
        for ph in range(len(PhasesSyn)):
            [syns, sh, lineStart, lineEnd, template] = PhasesSyn[ph]
            for st in range(len(syns)):
                synRank = syns[st]
                for par in range(len(sersynparam)):
                    # 'Connexion' Type is "0" are from a spiking neurone
                    # 'Connexion' Type is "1" are from a non-spiking neurone
                    # 'Synapse' Type is "regular" are from a rate nerone
                    if Connex[synRank].find("Type").text in ("0", "1"):
                        synapseTempID = Connex[synRank].\
                            find("SynapseTypeID").text
                        synapseTempType = model.getElementByID(synapseTempID).\
                            find("Type").text
                        if synapseTempType == "NonSpikingChemical":
                            amp = model.getElementByID(synapseTempID).\
                                find("SynAmp").text
                            thr = model.getElementByID(synapseTempID).\
                                find("ThreshV").text
                        elif synapseTempType == "SpikingChemical":
                            amp = model.getElementByID(synapseTempID).\
                                find("SynAmp").text
                            thr = model.getElementByID(synapseTempID).\
                                find("ThreshPSPot").text
                        G = Connex[synRank].find("G").text
                        if (sersynparam[par] == 'ThreshV'):
                            tmp.append(float(thr))
                        elif (sersynparam[par] == "SynAmp"):
                            tmp.append(float(amp))
                        elif (sersynparam[par] == "G"):
                            tmp.append(float(G))
                    elif Connex[synRank].find("Type").text == "Regular":
                        # if Connexions Type is "Regular" -> "SynapseFR"
                        weight = Connex[synRank].find("Weight").text
                        if (sersynparam[par] == 'Weight'):
                            tmp.append(float(weight))
    return tmp


def writeTabVals(folders, tab, filename, comment, flag):
    s = ""
    pathname = os.path.join(folders.animatlab_result_dir, filename)
    f = open(pathname, 'w')
    for i in range(len(tab)-1):
        try:
            s = s + "{0:1.8e}".format(tab[i]) + '\t'
        except Exception as e:
            if (verbose > 2):
                print(e)
            s = s + str(tab[i]) + '\t'
    try:
        # s = s + "{:%.4E}".format(tab[i+1]) + '\n'
        s = s + "{0:1.8e}".format(tab[i+1])
    except Exception as e:
        if (verbose > 2):
            print(e)
        # s = s + str(tab[i+1]) + '\n'
        s = s + str(tab[i+1])
    if flag == 1:
        print(comment, s)
    f.write(s)
    f.close()


def writeBestValuesTab(folders, filename, tab_var, params, trial,
                       chartfilename, bestfit):
    pathname = os.path.join(folders.animatlab_result_dir, filename)
    f = open(pathname, 'a')

    now = datetime.datetime.now()
    s = now.strftime("%Y-%m-%d %H:%M:%S")
    s = s + '  ' + '\n'
    f.write(s)

    s = 'trial:' + str(trial) + '\t' + 'chartfile name:' + '\t' \
        + chartfilename + '\t' + '    bestfit:' + '\t' + str(bestfit) + '\n'
    f.write(s)
    s = "param" + '\t'
    for k in range(len(tab_var)-1):
        s = s + tab_var[k][0] + '\t'
    s = s + tab_var[k+1][0] + '\n'
    f.write(s)
    for i in range(len(params)):
        s = params[i] + '\t'
        for k in range(len(tab_var)-1):
            s = s + str(tab_var[k][i+1]) + '\t'
        s = s + str(tab_var[k+1][i+1]) + '\n'
        f.write(s)
    f.write('\n')
    f.close()


def writeBestResSuite(folders, filename, bestresults, title):
    """
    Function writeBestResSuite
        In : folders : the path to the folders in which we want to write
            filename : the name of the file we want to write in
            bestresults : the results to write in the file
            title :
    """
    nblines = 0
    write = False
    pathname = os.path.join(folders.animatlab_result_dir, filename)
    if not os.path.exists(pathname):
        write = True
    if os.path.exists(pathname) and title == 0:
        write = True
    if os.path.exists(pathname) and title == 1:
        f = open(pathname, 'r')
        while True:
            txt = f.readline()
            # print(txt)
            if txt == '':
                break
            else:
                nblines = nblines + 1
        f.close()
        if nblines == 1:
            write = True
    if write:
        s = ""
        f = open(pathname, 'a')
        for i in range(len(bestresults)-1):
            s = s + str(bestresults[i]) + '\t'
        s = s + str(bestresults[len(bestresults)-1]) + '\n'
        # if titre == 0:
        #    print("{}: {}".format(ficname, s))
        f.write(s)
        f.close()


def writeTitres(folders, pre, allPhases, tab_targets, seriesParam):
    titres1 = []
    titres2 = []
    if len(allPhases[0][0]) > 0:
        for phase in range(len(allPhases)):
            [targetlist, tmp, lineStart, lineEnd, template] = allPhases[phase]
            for targ in range(len(targetlist)):
                target = targetlist[targ]
                targetName = tab_targets[target][0]
                for parTyp in range(len(seriesParam)):
                    titres1.append(targetName)
                    titres2.append(seriesParam[parTyp])
        writeBestResSuite(folders, pre + "bestvaluesSuite.txt", titres1, 1)
        writeBestResSuite(folders, pre + "bestvaluesSuite.txt", titres2, 1)
        writeBestResSuite(folders, pre + 'bestfitsSuite.txt', titres1, 1)
        writeBestResSuite(folders, pre + 'bestfitsSuite.txt', titres2, 1)
        writeBestResSuite(folders, pre + 'coefficientsSuite.txt', titres1, 1)
        writeBestResSuite(folders, pre + 'coefficientsSuite.txt', titres2, 1)
        writeBestResSuite(folders, pre + 'bestfitsCoactSuite.txt', titres1, 1)
        writeBestResSuite(folders, pre + 'bestfitsCoactSuite.txt', titres2, 1)


# TODO : Optimization procedures
###########################################################################
#                           OPTIMIZATION PROCEDURES
###########################################################################
def coactivityFR(tabMN0, tabMN1, lineStart, lineEnd, coactivityFactor):
    coact = 0.
    if lineStart == lineEnd:
        coact = tabMN0[lineStart] * tabMN1[lineStart]
    else:
        for x in range(lineStart, lineEnd):
            coact += tabMN0[x] * tabMN1[x]
        coact = coact/(lineEnd-lineStart)   # coact in range [0, 1]
    coactpenality = coact * coactivityFactor
    return [coactpenality, coact]


def coactivityVN(tabMN0, tabMN1, lineStart, lineEnd,
                 activThr, coactivityFactor):
    coact = 0.
    if lineStart == lineEnd:
        MN0 = tabMN0[lineStart]
        if MN0 <= activThr:
            MN0 = 0
        else:
            MN0 = MN0 - activThr
        MN1 = tabMN1[lineStart]
        if MN1 <= activThr:
            MN1 = 0
        else:
            MN1 = MN1 - activThr
        normMN0 = MN0/(0.030)  # /0.03  => normalize in range [0, 1]
        normMN1 = MN1/(0.030)  # /0.03  => normalize in range [0, 1]
        coact = normMN0 * normMN1
    else:
        for x in range(lineStart, lineEnd):
            MN0 = tabMN0[x]
            if MN0 <= activThr:
                MN0 = 0
            else:
                MN0 = MN0 - activThr
            MN1 = tabMN1[x]
            if MN1 <= activThr:
                MN1 = 0
            else:
                MN1 = MN1 - activThr
            normMN0 = MN0/(0.030)  # /0.03  => normalize in range [0, 1]
            normMN1 = MN1/(0.030)  # /0.03  => normalize in range [0, 1]
            coact += normMN0 * normMN1
        coact = coact/(lineEnd-lineStart)  # mean coactivation
    coactpenality = coact * coactivityFactor
    return [coactpenality, coact]


def testquality(optSet, tab, template, msetyp, affich=1):
    """
    Function testquality
        In : optSet :The object
            tab : The table which contains the values from the simulation
            template : The template to which compare the retrieved movement
            affich : Wether we display some infos or not
        Out : mse : The computed MSE
            coactpenality : The penality induced by the coactivity of
                the muscles correctly weighted
            coact : The coactivity of the muscles
    Calculates the Mean Square Error (mse) between a mouvement column vector
    (mvt) in an array (tab) and a reference vector (template).
    It calculates also the coactivity between two columns (tabMN0 and tabMN1)
    at two time intervals: [lineStart1, lineEnd1] and [lineStart2, lineEnd2]
    stored in optSet object.
    """
    max_lag = 100
    # mvt = tab[:][optSet.mvtcolumn]
    mvt = extractCol(tab, optSet.mvtcolumn)
    # timestart = tab[0][1]
    timestart = extractCol(tab, 1)[0]
    mvtfirstline = int(timestart/float(optSet.collectInterval))
    tabMN0 = extractCol(tab, optSet.mnColChartNbs[0])
    tabMN1 = extractCol(tab, optSet.mnColChartNbs[1])
    coactpenality = 0.
    coact = 0.
    # quality = variance(mvt)
    lag = -max_lag
    dmse = 0
    msetab = []
    mse = MeanSquarreErrorTemplate(mvt, template, mvtfirstline,
                                   optSet.lineStart+max_lag,
                                   optSet.lineEnd-max_lag, lag)
    # print(mse, end=' ')
    msetab.append(mse)
    prevmse = mse
    slide = ""
    # In order to compute the varmse we compare the produced movement to
    # different frame defined by lag.
    # while (dmse <= 0) and (lag < 20):
    while (dmse <= 0) and lag < max_lag:
        lag += 1
        # We compute the mse with the new lag
        mse = MeanSquarreErrorTemplate(mvt, template, mvtfirstline,
                                       optSet.lineStart+max_lag,
                                       optSet.lineEnd-max_lag, lag)
        # print(mse, end=' ')
        # if lag == -30:
        #     print(comment, mse, end=' ')
        msetab.append(mse)
        # Here we look if the new mse is better or worse than the previous
        dmse = mse - prevmse
        # The newly found mse become the new one
        prevmse = mse
        # One "/" we'll be printed for each step in this loop
        # print(dmse)
        if lag % 2 == 0:
            slide += "/"
    mse = min(msetab)
    if affich:
        if msetyp != "":
            print(msetyp, end=' ')
        else:
            print("mse", end=' ')
        affiche_liste(msetab[-3:])
        print(slide, end=' ')
        print("lag:", lag * float(optSet.collectInterval), " s", end=' ')
        optSet.templateLag = lag * float(optSet.collectInterval)
        # print(" --> min mse = ", mse, coactpenality, coact, end=' ')
        # print(" --> min mse = ", mse, end=' ')
    # cost function: coactivation of MN
    if min(tabMN0) < 0:
        res1 = coactivityVN(tabMN0, tabMN1, optSet.lineStart, optSet.lineEnd1,
                            optSet.activThr,
                            optSet.coactivityFactor*optSet.xCoactPenality1)
        res2 = coactivityVN(tabMN0, tabMN1, optSet.lineStart2, optSet.lineEnd,
                            optSet.activThr,
                            optSet.coactivityFactor*optSet.xCoactPenality2)
    else:
        res1 = coactivityFR(tabMN0, tabMN1, optSet.lineStart, optSet.lineEnd1,
                            optSet.coactivityFactor*optSet.xCoactPenality1)
        res2 = coactivityFR(tabMN0, tabMN1, optSet.lineStart2, optSet.lineEnd,
                            optSet.coactivityFactor*optSet.xCoactPenality2)

    if affich:
        print("coactpenality1:", res1[0], end=' ')
        print("coactpenality2:", res2[0])
    coactpenality = res1[0] + res2[0]
    coact = res1[1] + res2[1]
    """
    if proc_name == "VSCD":
        mse = MeanSquarreErrorTemplate(mvt, template, mvtfirstline,
                                       optSet.lineStart+20,
                                       optSet.lineEnd-20, 0)
    """
    return [mse, coactpenality, coact, res1, res2]


def getmaxspeed(mvt, line_startMvt2, rate):
    """
    """
    upward = False
    mvt2 = mvt[line_startMvt2:]
    mvt2prim = []
    dic_mvt2prim = {}
    endmvtfound = False
    x_end_mvt2 = len(mvt) - 1 - line_startMvt2
    for ang_idx in range(len(mvt2)-1):
        derivate = (mvt2[ang_idx+1]-mvt2[ang_idx])*rate
        mvt2prim.append(derivate)
        dic_mvt2prim[ang_idx] = derivate
    max_speed = max(mvt2prim[1:])
    min_speed = min(mvt2prim[1:])
    for ang_idx in range(len(mvt2)-1):
        # print(ang_idx, dic_mvt2prim[ang_idx])
        if dic_mvt2prim[ang_idx] == max_speed:
            x_max_speed = ang_idx
        if dic_mvt2prim[ang_idx] == min_speed:
            x_min_speed = ang_idx
            # print(x_max_speed, dic_mvt2prim[ang_idx])
    rg_max_speed = x_max_speed + line_startMvt2
    rg_min_speed = x_min_speed + line_startMvt2

    if rg_max_speed < rg_min_speed:     # if this is an upward mvt...
        rg_max_sp = rg_max_speed
        x_max_sp = x_max_speed
        upward = True
    else:                               # if this is a downward mvt...
        rg_max_sp = rg_min_speed
        x_max_sp = x_min_speed

    for ang_idx in range(x_max_sp, len(mvt2)-1):
        if upward:
            if dic_mvt2prim[ang_idx] < 0.01:
                if not endmvtfound:
                    x_end_mvt2 = ang_idx
                    endmvtfound = True
        else:
            if abs(dic_mvt2prim[ang_idx]) < 0.01:
                if not endmvtfound:
                    x_end_mvt2 = ang_idx
                    endmvtfound = True

    rg_end_mvt2 = x_end_mvt2 + line_startMvt2
    # txt = "rg_max_speed: {} \tmax_speed: {} \trg_end_mvt2: {}"
    # print(txt.format(rg_max_speed, mvt[rg_max_speed], rg_end_mvt2))
    return max_speed, rg_max_sp, rg_end_mvt2


def get_dur_mvt_old(max_speed, nbPtsMvt2, angle2, rate):
    OK = False
    nbPts = nbPtsMvt2
    mid_ang_minus = flash(nbPts / 2 - 1, 0, angle2, nbPts)
    mid_ang = flash(nbPts / 2, 0, angle2, nbPts)
    vmax_Tmplate = (mid_ang - mid_ang_minus) * rate
    # print(vmax_Tmplate, max_speed)
    if abs(max_speed) > 1:
        if vmax_Tmplate > max_speed:
            while not OK:
                if vmax_Tmplate > max_speed:
                    prev_vmax_Tmplate = vmax_Tmplate
                    nbPts += 1
                    mid_ang_minus = flash(nbPts / 2 - 1, 0, angle2, nbPts)
                    mid_ang = flash(nbPts / 2, 0, angle2, nbPts)
                    vmax_Tmplate = (mid_ang - mid_ang_minus) * rate
                else:
                    OK = True
                    nbPts -= 1
                # print(prev_vmax_Tmplate, max_speed)
        else:
            while not OK:
                if vmax_Tmplate < max_speed:
                    prev_vmax_Tmplate = vmax_Tmplate
                    nbPts -= 1
                    if nbPts == 0:
                        OK = True
                    else:
                        mid_ang_minus = flash(nbPts / 2 - 1, 0, angle2, nbPts)
                        mid_ang = flash(nbPts / 2, 0, angle2, nbPts)
                        vmax_Tmplate = (mid_ang - mid_ang_minus) * rate
                else:
                    OK = True
                    nbPts += 1
                # print(prev_vmax_Tmplate, max_speed)
    else:
        nbPts = optSet.endMvt2
    print("template maxspeed:", prev_vmax_Tmplate, "  run maxspeed:", max_speed)
    return nbPts


def get_dur_mvt_old2(mvt, line_startMvt2, max_speed, nbPtsMvt2_T,
                     startangle, endangle, rate):
    """
    This new version of get_dur_mvt() starts from an estimation of nbPtsMvt2_T,
    the number of points in the adapted template, based on the hypothesis that
    max_speed should be observed at half-time of movement duration.
    In this functiion, template angle is calculated at three points:
        1/3 of nbPtsMvt2_T
        1/2 of nbPtsMvt2_T
        2/3 of nbPtsMvt2_T
    and compared to run angle for these three points.
    The number of points is increased/decreased to reduce/increase template
    speed. Once the minimum is reached, the template movement duration is
    returned

    Does not work because lag is not taken into acount...
    """
    OK1 = False
    OK2 = False
    nbPts = nbPtsMvt2_T
    ampl = endangle - startangle
    # abs_speed = abs(max_speed)

    while not OK1:
        first_ang_T = flash(int(float(nbPts) / 3), 0, ampl, nbPts)
        # middle_ang_T = flash(int(float(nbPts) / 2), 0, ampl, nbPts)
        third_ang_T = flash(int(float(nbPts) * 2 / 3), 0, ampl, nbPts)
        angT_1st_abs = abs(first_ang_T)
        # angT_mid_abs = abs(middle_ang_T)
        angT_3rd_abs = abs(third_ang_T)
        # speed_T = (angT_3rd_abs - angT_1st_abs) / (float(nbPts/3) / rate)

        first_ang_run = mvt[line_startMvt2 + int(nbPts / 3)]
        # middle_ang_run = mvt[line_startMvt2 + int(nbPts / 2)]
        third_ang_run = mvt[line_startMvt2 + int(nbPts * 2 / 3)]
        ang_1st_abs = abs(first_ang_run - startangle)
        # ang_mid_abs = abs(middle_ang_run - startangle)
        ang_3rd_abs = abs(third_ang_run - startangle)
        print("angT_1st_abs - ang_1st_abs :", angT_1st_abs - ang_1st_abs, end=' ')
        print("   angT_3rd_abs - ang_3rd_abs :", angT_3rd_abs - ang_3rd_abs)
        # if (first_ang_T - first_ang_run) + (third_ang_run - third_ang_T) > 0:
        if (angT_1st_abs > ang_1st_abs) and (angT_3rd_abs < ang_3rd_abs):
            nbPts -= 1
        else:
            OK1 = True
        # if speed_T > max_speed * 4/3:
        #     OK1 = True
        # if ang_mid_abs - angT_mid_abs < -10:
        #     OK1 = True
    # print()
    while not OK2:
        first_ang_T = flash(int(float(nbPts) / 3), 0, ampl, nbPts)
        # middle_ang_T = flash(int(float(nbPts) / 2), 0, ampl, nbPts)
        third_ang_T = flash(int(float(nbPts) * 2 / 3), 0, ampl, nbPts)
        angT_1st_abs = abs(first_ang_T)
        # angT_mid_abs = abs(middle_ang_T)
        angT_3rd_abs = abs(third_ang_T)
        # speed_T = (angT_3rd_abs - angT_1st_abs) / (float(nbPts/3) / rate)

        first_ang_run = mvt[line_startMvt2 + int(nbPts / 3)]
        # middle_ang_run = mvt[line_startMvt2 + int(nbPts / 2)]
        third_ang_run = mvt[line_startMvt2 + int(nbPts * 2 / 3)]
        ang_1st_abs = abs(first_ang_run - startangle)
        # ang_mid_abs = abs(middle_ang_run - startangle)
        ang_3rd_abs = abs(third_ang_run - startangle)
        print("angT_1st_abs > ang_1st_abs :", angT_1st_abs - ang_1st_abs, end=' ')
        print("   angT_3rd_abs < ang_3rd_abs :", angT_3rd_abs - ang_3rd_abs)
        # if (first_ang_T - first_ang_run) + (third_ang_run - third_ang_T) < 0:
        if (angT_1st_abs < ang_1st_abs) and (angT_3rd_abs > ang_3rd_abs):
            nbPts += 1
        else:
            OK2 = True
        # if speed_T < max_speed * 3/4:
        #     OK2 = True
        # if ang_mid_abs - angT_mid_abs > 10:
        #     OK2 = True
    return nbPts


def get_dur_mvt_old3(optSet, mvt, line_startMvt2, max_speed, nbPtsMvt2_T,
                     startangle, endangle, rate, interval=1./6):
    """
    Mean_Speed is calculated between 3/8 and 5/8 of nbPts in the run mvt.
    This speed is considered to be also the max speed of the template.
    The number of points in the desired template is then calculated so that
    the maxspeed of the template = Mean_speed.
    """
    OK1 = False
    OK2 = False
    nbPts = nbPtsMvt2_T
    ampl = endangle - startangle
    strtPtSpeed = int(nbPts * (0.5 - interval))
    endPtSpeed = int(nbPts * (0.5 + interval))
    first_ang_run = mvt[line_startMvt2 + strtPtSpeed]
    third_ang_run = mvt[line_startMvt2 + endPtSpeed]
    ang_1st = first_ang_run - startangle
    ang_3rd = third_ang_run - startangle
    speed_r = (ang_3rd - ang_1st) / ((float(nbPts)*2*interval) / rate)

    if abs(endangle-startangle) < 1:
        OK1 = True
        OK2 = True
        nbPts = int((optSet.endMvt2 - optSet.startMvt2) * rate)
        speed_T = 0

    speed_r = max_speed
    while not OK1:
        strtPtSpeed = int(nbPts * (0.5 - interval))
        endPtSpeed = int(nbPts * (0.5 + interval))

        first_ang_T = flash(strtPtSpeed, 0, ampl, nbPts)
        third_ang_T = flash(endPtSpeed, 0, ampl, nbPts)
        angT_1st = first_ang_T
        angT_3rd = third_ang_T
        speed_T = (angT_3rd - angT_1st)/((float(nbPts)*2*interval) / rate)
        if abs(speed_T) > abs(speed_r):
            nbPts += 1
        else:
            OK1 = True
        # print(OK1)
        # print("template speed:", speed_T, "  run speed:", speed_r)
    # print
    while not OK2:
        strtPtSpeed = int(nbPts * (0.5 - interval))
        endPtSpeed = int(nbPts * (0.5 + interval))
        first_ang_T = flash(strtPtSpeed, 0, ampl, nbPts)
        third_ang_T = flash(endPtSpeed, 0, ampl, nbPts)
        angT_1st = first_ang_T
        angT_3rd = third_ang_T
        speed_T = (angT_3rd - angT_1st)/((float(nbPts)*2*interval) / rate)
        if abs(speed_T) < abs(speed_r):
            nbPts -= 1
        else:
            nbPts -= 1
            OK2 = True
        # print("template speed:", speed_T, "  run speed:", speed_r)
    print(" T/r speed: {:4.2f}/{:4.2f}\t".format(speed_T, speed_r), end=' ')
    return nbPts


def get_dur_mvt(optSet, mvt, line_startMvt2, max_speed, nbPtsMvt2_T,
                startangle, endangle, rate, interval=1./6):
    """
    Mean_Speed is calculated between 3/8 and 5/8 of nbPts in the run mvt.
    This speed is considered to be also the max speed of the template.
    The number of points in the desired template is then calculated so that
    the maxspeed of the template = Mean_speed.
    """
    OK1 = False
    OK2 = False
    nbPts = nbPtsMvt2_T
    ampl = endangle - startangle
    strtPtSpeed = int(nbPts * (0.5 - interval))
    endPtSpeed = int(nbPts * (0.5 + interval))
    first_ang_run = mvt[line_startMvt2 + strtPtSpeed]
    third_ang_run = mvt[line_startMvt2 + endPtSpeed]
    ang_1st = first_ang_run - startangle
    ang_3rd = third_ang_run - startangle
    speed_r = (ang_3rd - ang_1st) / ((float(nbPts)*2*interval) / rate)

    if abs(endangle-startangle) < 1:
        OK1 = True
        OK2 = True
        nbPts = int((optSet.endMvt2 - optSet.startMvt2) * rate)
        speed_T = 0

    speed_r = max_speed
    spd_T = []
    spd_r = []
    spd_delta = []
    nbpoints = []
    while not OK1:
        strtPtSpeed = int(nbPts * (0.5 - interval))
        endPtSpeed = int(nbPts * (0.5 + interval))

        first_ang_T = flash(strtPtSpeed, 0, ampl, nbPts)
        third_ang_T = flash(endPtSpeed, 0, ampl, nbPts)
        angT_1st = first_ang_T
        angT_3rd = third_ang_T
        speed_T = (angT_3rd - angT_1st)/((float(nbPts)*2*interval) / rate)
        spd_T.append(speed_T)
        spd_r.append(speed_r)
        spd_delta.append(abs(speed_T - speed_r))
        nbpoints.append(nbPts)

        if abs(speed_T) > abs(speed_r):
            nbPts += 1
        else:
            nbPts += 1
            OK1 = True
        # print(OK1)
        # print("template speed:", speed_T, "  run speed:", speed_r, " ", end=' ')
        # print(nbPts-1)
    # print()
    while not OK2:
        strtPtSpeed = int(nbPts * (0.5 - interval))
        endPtSpeed = int(nbPts * (0.5 + interval))
        first_ang_T = flash(strtPtSpeed, 0, ampl, nbPts)
        third_ang_T = flash(endPtSpeed, 0, ampl, nbPts)
        angT_1st = first_ang_T
        angT_3rd = third_ang_T
        speed_T = (angT_3rd - angT_1st)/((float(nbPts)*2*interval) / rate)
        spd_T.append(speed_T)
        spd_r.append(speed_r)
        spd_delta.append(abs(speed_T - speed_r))
        nbpoints.append(nbPts)

        if abs(speed_T) < abs(speed_r):
            nbPts -= 1
        else:
            nbPts -= 1
            OK2 = True
        if nbPts < 5:
            OK2 = True
        # print("template speed:", speed_T, "  run speed:", speed_r, " ", end=' ')
        # print(nbPts+1)

    if speed_T != 0:
        min_delta = min(spd_delta)
        idx = spd_delta.index(min_delta)
        nbPts = nbpoints[idx]
        print(" T/r speed: {:4.2f}/{:4.2f}\t".format(spd_T[idx], spd_r[idx]), end=' ')
    else:
        print(" T/r speed: {:4.2f}/{:4.2f}\t".format(speed_T, speed_r), end=' ')
    return nbPts


def searchStartMvt2(mvt, time, line_startMvt2, rate):
    startmvt2_idx, maxspeedmvt2_idx, endmvt2_idx = 0, 0, 0
    mvt2 = mvt[line_startMvt2:]
    mvt2prim = []
    dic_mvt2prim = {}
    for ang_idx in range(len(mvt2)-1):
        derivate = (mvt2[ang_idx+1]-mvt2[ang_idx])*rate
        mvt2prim.append(derivate)
        dic_mvt2prim[ang_idx] = derivate
    maxSpeed = max(mvt2prim[1:])
    mspd_idx = [idx for idx in range(len(mvt2prim))
                if mvt2prim[idx] == maxSpeed]
    if abs(maxSpeed) > 0.01:
        idx = 0
        while abs(mvt2prim[idx]) < 0.01:
            idx += 1
        start_mvt2_idx = idx
        # print(idx, mvt2prim[idx])
        idx = mspd_idx[0]
        while (abs(mvt2prim[idx]) > 0.01) and (idx < len(mvt2prim)-1):
            idx += 1
        end_mvt2_idx = idx
        # print(idx, mvt2prim[idx])
        startmvt2_idx = line_startMvt2 + start_mvt2_idx
        endmvt2_idx = line_startMvt2 + end_mvt2_idx
        maxspeedmvt2_idx = line_startMvt2 + mspd_idx[0]
        startseq = time[startmvt2_idx]
        endseq = time[endmvt2_idx]
        maxspeed_t = time[maxspeedmvt2_idx]
        if verbose > 1:
            msg = "startseq mvt2: {}  max speed: {}   endseq mvt2:{}"
            print(msg.format(startseq, maxspeed_t, endseq))
        if end_mvt2_idx < len(mvt2prim)-1:
            OK = True
        else:
            OK = False

        if maxspeedmvt2_idx < endmvt2_idx:
            OK = True
        else:
            OK = False
    else:
        OK = False
    return [OK, startmvt2_idx, maxspeedmvt2_idx, endmvt2_idx]


# TODO : to be continued
def getbehavElts(optSet, tab, affich=0, interval=1./6):
    """
    Function getbehavElts
        In : optSet : The object
            tab : The tab which contains the result from the asim file
            affich : Wether or not we display data
        Out :
    calculates some movement elements (startseq angle, endseq angle, oscillation
    phase 1, oscillation phase2, movement speed). This function is called by
    "runSimMvt" procedure required to run CMAes.
    It is also called by runTrials in GEP_GUI.
    """
    ok = True
    # lineStart1 and lineEnd1 are the row limits of the "stable" position
    # after mvt1
    lineStart1 = optSet.lineStart1
    lineEnd1 = optSet.lineEnd1
    # lineStart2 and lineEnd2 are the row limits of the "stable" position
    # after mvt2

    lineStart2 = optSet.lineStart2
    lineEnd2 = optSet.lineEnd2
    mvt = extractCol(tab, optSet.mvtcolumn)[:lineEnd2+1]
    time = extractCol(tab, 1)[:lineEnd2+1]

    startangle = mvt[optSet.lineEnd1]
    # endangle = mvt[optSet.lineEnd2]
    oscil1 = max(mvt[lineStart1:lineEnd1]) \
        - min(mvt[lineStart1:lineEnd1])
    lineStart2 = optSet.lineStart2
    oscil2 = max(mvt[lineStart2:lineEnd2]) - min(mvt[lineStart2:lineEnd2])
    startMvt2, rate = optSet.startMvt2, optSet.rate
    # aim_mvtDuration = optSet.endMvt2 - optSet.startMvt2
    # line_startMvt2 = int((optSet.startMvt2 - optSet.chartStart
    #                      + aim_mvtDuration / 4) * optSet.rate)
    line_startMvt2 = int((optSet.startMvt2 - optSet.chartStart) * optSet.rate)
    res0 = searchStartMvt2(mvt, time, line_startMvt2, optSet.rate)
    [OK0, startmvt2_idx, maxspeedmvt2_idx, endmvt2_idx] = res0
    if OK0:
        line_startMvt2 = startmvt2_idx
        startMvt2 = time[startmvt2_idx]
        # modifies optSet.lineStart2 to the new endMvt2
        # ===============================================================
        res = getmaxspeed(mvt, line_startMvt2, optSet.rate)
        # ===============================================================
        max_speed, rg_max_speed, rg_end_mvt2 = res
        endangle = mvt[rg_end_mvt2]
        # print("max_speed:", max_speed, "   rg_end_mvt2:", rg_end_mvt2)
        # prevLineStart2 = optSet.lineStart2
    else:
        rg_end_mvt2 = endmvt2_idx
        max_speed = 0
        endangle = mvt[rg_end_mvt2]
        # prevLineStart2 = optSet.lineStart2

    # if endseq of mvt out of record endseq...
    if (rg_end_mvt2 > len(mvt) - 1) or not OK0:
        ok = False
        nbPtsMvt2 = int(startMvt2*rate) - lineStart2
    else:
        # time_maxspeed = time[rg_max_speed]
        time_endMvt2 = time[rg_end_mvt2]
        # nbPtsMvt2 = int(time_endMvt2*rate) - int(startMvt2*rate)
        nbPtsMvt2 = endmvt2_idx - startmvt2_idx
        # angle2 = endangle - startangle
        lineStart2 = rg_end_mvt2
        lineEnd2 = optSet.lineEnd2
        if lineStart2 >= lineEnd2:  # in case no movement was produced...
            lineStart2 = int(optSet.endMvt2 * optSet.rate)
        oscil2 = max(mvt[lineStart2:lineEnd2]) - min(mvt[lineStart2:lineEnd2])

        nbPtsMvt2_T = int((time_endMvt2 - startMvt2) * rate)
        if nbPtsMvt2_T < 10:
            ok = False
            nbPtsMvt2 = int(startMvt2*rate) - lineStart2

    if abs(max_speed) > 1 and abs(max_speed) < 500 and ok:
        """
        # modification September 7, 2021 movement duration is now calculated
        # from max_speed using a new function : nbPts_mvt2T()
        """
        # ===============================================================
        # nbPts_mvt2T = get_dur_mvt(max_speed, nbPtsMvt2, angle2, rate)
        # endMvt2T = startMvt2 + float(nbPts_mvt2T)/rate
        # ===============================================================
        """
        # modification September 9, 2021 movement duration is now calculated
        # from rg_max_speed
        """

        # ===============================================================
        nbPts_mvt2T = get_dur_mvt(optSet, mvt, line_startMvt2, max_speed,
                                  nbPtsMvt2_T, startangle, endangle, rate,
                                  interval=interval)
        endMvt2T = startMvt2 + float(nbPts_mvt2T)/rate
        # ===============================================================

        # nbPts_mvt2T = nbPtsMvt2
        # endMvt2T = startMvt2 + float(nbPtsMvt2_T)/rate
        # time_midMvt2T = startMvt2 + (float(nbPtsMvt2_T)/rate)/2
        time_midMvt2T = startMvt2 + (float(nbPts_mvt2T)/rate)/2
        # end_mvt2 = float(rg_end_mvt2)/optSet.rate
        optSet.varmse_lineStart2 = rg_end_mvt2
    else:
        endMvt2T = optSet.endMvt2
        time_endMvt2 = optSet.endMvt2
        time_midMvt2T = (startMvt2 + time_endMvt2) / 2
        nbPts_mvt2T = nbPtsMvt2
    # timestart = extractCol(tab, 1)[0]
    tmplate = formTemplateSmooth(optSet.rate, optSet.startMvt1,
                                 optSet.endMvt1, startangle,
                                 startMvt2, endMvt2T,
                                 endangle, optSet.endPos2)
    quality = testquality(optSet, tab, tmplate, "varmse", affich=affich)
    optSet.varmse_tmplate = tmplate
    optSet.time_midMvt2T = time_midMvt2T
    optSet.nbPts_mvt2T = nbPts_mvt2T
    optSet.varmse_time_endMvt2 = time_endMvt2
    # optSet.lineStart2 = prevLineStart2
    optSet.varmse_startMvt2 = startMvt2
    optSet.varmse_lineStart2 = lineStart2
    duration = endMvt2T - startMvt2
    # ===============================================================
    """
    # mse = quality[0]  # Modified 2021 june, 17.
    When running GEP, coact must be calculated on
    the new adapted template, not on the original template
    Now we read mse, coactpenality and coact from the new template
    and these values are returned to getbehavElts
    """
    # mse = quality[0]
    # coactpenality = quality[1]
    # coact = quality[2]
    [mse, coactpenality, coact, res1, res2] = quality
    """
    # Modified 2021 August, 16. replacement of speedMvt2 by max_speed
    return [startangle, endangle, oscil1, oscil2, speedMvt2,
            end_mvt2 + timestart, end_mvt2 + timestart - optSet.startMvt2,
            mse, coactpenality, coact]
    """
    return [startangle, endangle, oscil1, oscil2, max_speed,
            endMvt2T, duration, mse, coactpenality, coact, res1, res2]


###########################################################################
#                           VSCD procedures
###########################################################################
def cleanChartsFromResultDir(optSet, firstChart, lastChart, pre,
                             directory="ResultFiles"):
    folder = os.path.join(optSet.folders.animatlab_rootFolder, directory)
    simFileName = findChartName(optSet.model, optSet)[0]
    nbchar = len(simFileName)
    for the_file in os.listdir(folder):
        ext = os.path.splitext(the_file)[1]
        if ext == ".txt":
            name = os.path.splitext(the_file)[0]
            # print(name[0:nbchar])
            if name[0:nbchar] == simFileName:
                # print(name)
                # print("file to be deleted: ", the_file)
                file_path = os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    # elif os.path.isdir(file_path): shutil.rmtree(file_path)
                except Exception as e:
                    print(e)


def cleanAsimsFromResultDir(optSet, firstAsim, lastAsim, pre,
                            directory="ResultFiles"):
    folder = os.path.join(optSet.folders.animatlab_rootFolder, directory)
    simFileName = findAsimName(optSet.model, optSet)[0]
    nbchar = len(simFileName)
    for the_file in os.listdir(folder):
        ext = os.path.splitext(the_file)[1]
        if ext == ".asim":
            name = os.path.splitext(the_file)[0]
            # print(name[0:nbchar])
            if name[0:nbchar] == simFileName:
                # print(name)
                # print("file to be deleted: ", the_file)
                file_path = os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    # elif os.path.isdir(file_path): shutil.rmtree(file_path)
                except Exception as e:
                    print(e)


# TODO : Simulation controls
# ===========================================================================
#               Gestion Simulation controls
# ===========================================================================
def enableStims(ExternalStimuli, stims):
    nbStims = len(ExternalStimuli)
    for stim in range(nbStims):
        ExternalStimuli[stim].find("Enabled").text = 'False'
    for stim in range(len(stims)):
        stimRank = stims[stim]
        ExternalStimuli[stimRank].find("Enabled").text = 'True'


def setMotorStimsON(model, motorStimuli):
    """
    sets motors stimulis to "disabled"
    """
    for i in range(len(motorStimuli)):
        motorEl = motorStimuli[i]
        for idx, elem in enumerate(motorEl):
            # nomMoteur = elem.find("Name").text
            # print(nomMoteur, end=' ')
            # space = ""
            # for sp in range(3-len(nomMoteur)/8):
            #     space += "\t"
            # print(space + "set from  ", end=' ')
            # print(elem.find("Enabled").text, end=' ')
            elem.find("Enabled").text = "True"
            # print("   to   ", elem.find("Enabled").text)
    affichMotor(model, motorStimuli, 0)
    print("motorstimuli have been enabled")


def setMotorStimsOff(model, motorStimuli):
    """
    sets motors stimulis to "disabled"
    """
    for i in range(len(motorStimuli)):
        motorEl = motorStimuli[i]
        for idx, elem in enumerate(motorEl):
            # nomMoteur = elem.find("Name").text
            # print(nomMoteur, end=' ')
            # space = ""
            # for sp in range(3-len(nomMoteur)/8):
            #     space += "\t"
            # print(space + "set from  ", end=' ')
            # print(elem.find("Enabled").text, end=' ')
            elem.find("Enabled").text = "False"
            # print("   to   ", elem.find("Enabled").text)
    affichMotor(model, motorStimuli, 0)
    print("motorstimuli have been disabled")


def setPlaybackControlMode(model, mode):
    """
    sets speed to 0 for Fastest and to 1 for matching Physics Steps
    """
    asimroot = model.tree.getroot()
    oldmode = asimroot.find("PlaybackControlMode").text
    if oldmode == '0':
        oldmodestr = "fastest"
    elif oldmode == '1':
        oldmodestr = "match Physics"
    else:
        oldmodestr = "perso"
    asimroot.find("PlaybackControlMode").text = str(mode)
    # After changing a property, save the updated model
    # model.saveXML(overwrite=True)   # in the FinalModel dir
    if mode == 0:
        modestr = "fastest"
    elif mode == 1:
        modestr = "match Physics"
    else:
        modestr = "perso"
    print("PlaybackControlMode has been changed from", oldmodestr, end=' ')
    print("to", modestr)


def setGravity(model, gravity):
    asimroot = model.tree.getroot()
    pathE = "Environment"
    oldGravity = asimroot.find(pathE).find("Gravity").text
    asimroot.find(pathE).find("Gravity").text = str(gravity)
    # enableStims(ExternalStimuli, twitStMusclesSt)
    # After changing a property, save the updated model
    model.saveXML(overwrite=True)   # in the FinalModel dir
    print("Gravity has been changed from", oldGravity, "to", gravity)

    aprojroot = model.aprojtree.getroot()
    pathE = "Environment"

    path = "Simulation/Environment/Gravity"
    grav = aprojroot.find(path)
    oldgravity = grav.get("Value")
    newgravity = gravity
    grav.set("Scale", "None")
    grav.set("Value", str(newgravity))
    grav.set("Actual", str(newgravity))
    model.saveXMLaproj(overwrite=True)
    text = "gravity changed from {} to {} in finalModel/ .aproj"
    print(text.format(oldgravity, newgravity))


def readGravityfromAsim(model):
    asimroot = model.tree.getroot()
    pathE = "Environment"
    gravity = asimroot.find(pathE).find("Gravity").text
    text = "gravity = {} from .asim file in finalModel"
    print(text.format(gravity))
    return gravity


# TODO : CMAES
###########################################################################
#                           CMAe procedures
###########################################################################
def actualiseSaveAprojFromAsimFile(optSet, asimFileName, aprojFileName,
                                   simSet=SimulationSet.SimulationSet(),
                                   overwrite=0, createSimSet=1, affiche=1):
    """
    Actualizes the parameter values in the .aproj object defined in the model
    object from class AnimatLabModel. It calls a function getSimSetFromAsim()
    that creates a simSet object (asimSimSet) from class SimulationSet, by
    extracting all parameter values from the .asim file, and assembling them
    in a simSet object that it returns with the table of external stimuli.
    Once the .aproj object (that is in memory) is actualized, it saves an
    .aproj file with the name and path contained in aprojFileName.
    Returns the path+Name of the saved aproj file (names endseq with an
    incremented number).
    """
    model = optSet.model

    seriesStimParam = ['CurrentOn', 'StartTime', 'EndTime']
    seriesSynParam = optSet.seriesSynParam
    # seriesSynNSParam = optSet.seriesSynNSParam
    seriesSynNSParam = ['SynAmp', 'ThreshV']
    seriesSynFRParam = optSet.seriesSynFRParam

    if createSimSet:
        res = getSimSetFromAsim(optSet, seriesStimParam, seriesSynParam,
                                seriesSynNSParam, seriesSynFRParam,
                                asimFileName, affiche=affiche)
        asimSimSet = res[0]
        asimtab_stims = res[1]
        asimtab_motorst = res[2]
    else:
        asimSimSet = simSet
        asimtab_stims = optSet.tab_stims
        asimtab_motorst = optSet.tab_motors
    model.actualizeAproj(asimSimSet)
    model.actualizeAprojStimState(asimtab_stims, affiche=affiche)
    model.actualizeAprojMotorState(asimtab_motorst, affiche=affiche)
    complete_name = model.saveXMLaproj(aprojFileName, overwrite=overwrite)
    return complete_name


def actualiseSaveAprojFromAsimFileDir(optSet, model, asimsourcedir,
                                      aprojdestdir, suffix):
    aprojFicName = os.path.split(model.aprojFile)[-1]
    listAsim = findList_asimFiles(asimsourcedir)
    name = os.path.splitext(aprojFicName)[0]
    ext = os.path.splitext(aprojFicName)[1]
    ficName = name + suffix + ext
    for filesource in listAsim:
        asimFileName = os.path.join(asimsourcedir, filesource)
        # print(asimFileName)
        nam = os.path.splitext(filesource)[0]
        numero = nam.split("-")[-1]
        ficName = name + suffix + str(numero) + ext
        aprojFileName = os.path.join(aprojdestdir, ficName)
        actualiseSaveAprojFromAsimFile(optSet,
                                       asimFileName,
                                       aprojFileName,
                                       overwrite=1,
                                       createSimSet=1,
                                       affiche=0)


def saveparams(folders, optSet, filename, lastname):
    """
    Writes the names and values of all parameters in a human readable text file
    The name is composed by the simulation name + VSCD  or CMAe,
    and the extension ".par"
    """
    listparnam = ["selectedChart",
                  "mvtcolumn",
                  "startMvt1",
                  "endMvt1",
                  "endPos1",
                  "angle1",
                  "startMvt2",
                  "endMvt2",
                  "endPos2",
                  "angle2",
                  "startEQM",
                  "endEQM",
                  "allstim",
                  "disabledStimNbs",
                  "dontChangeStimNbs",
                  "seriesStimParam",
                  "allsyn",
                  "dontChangeSynNbs",
                  "dontChangeSynFRNbs",
                  "seriesSynParam",
                  "seriesSynFRParam",
                  "nbepoch",
                  "nbstimtrials",
                  "nbsyntrials",
                  "nbsteps",
                  "deltaStimCoeff",
                  "maxDeltaStim",
                  "multSynCoeff",
                  "maxMultSyn",
                  "coactivityFactor",
                  "nsActivThr",
                  "limQuality",
                  "maxStim",
                  "maxSynAmp",
                  "maxG",
                  "maxWeight",
                  "defaultval",
                  "cmaes_sigma",
                  "spanStim",
                  "spanSyn"
                  ]
    listparval = [optSet.selectedChart,
                  optSet.mvtcolumn,
                  optSet.startMvt1,
                  optSet.endMvt1,
                  optSet.endPos1,
                  optSet.angle1,
                  optSet.startMvt2,
                  optSet.endMvt2,
                  optSet.endPos2,
                  optSet.angle2,
                  optSet.startEQM,
                  optSet.endEQM,
                  optSet.allstim,
                  optSet.disabledStimNbs,
                  optSet.dontChangeStimNbs,
                  optSet.seriesStimParam,
                  optSet.allsyn,
                  optSet.dontChangeSynNbs,
                  optSet.dontChangeSynFRNbs,
                  optSet.seriesSynParam,
                  optSet.seriesSynFRParam,
                  optSet.nbepoch,
                  optSet.nbstimtrials,
                  optSet.nbsyntrials,
                  optSet.nbsteps,
                  optSet.deltaStimCoeff,
                  optSet.maxDeltaStim,
                  optSet.multSynCoeff,
                  optSet.maxMultSyn,
                  optSet.coactivityFactor,
                  optSet.activThr,
                  optSet.limQuality,
                  optSet.maxStim,
                  optSet.maxSynAmp,
                  optSet.maxG,
                  optSet.maxWeight,
                  optSet.defaultval,
                  optSet.cmaes_sigma,
                  optSet.spanStim,
                  optSet.spanSyn
                  ]
    comment = "Optimization Parameters Values Saved for " + lastname

    listparval.append(lastname)
    pathname = os.path.join(folders.animatlab_result_dir, filename)
    if not os.path.exists(pathname):
        writeaddTab(folders, listparnam, filename, 'w', "", 0)
    writeaddTab(folders, listparval, filename, 'a', comment, 1)


def affichParamLimits(sParName, vallower, valupper, valx0, deb):
    for st, sName in enumerate(sParName):
        txt1 = ""
        for sp in range(4-int((len(sName)+0)/8)):
            txt1 += "\t"
        low = str(vallower[st + deb])
        upp = str(valupper[st + deb])
        # mid = 0.5 * (vallower[st + deb] + valupper[st + deb])
        lowsp = ""
        for sp in range(3-int((len(low)+1)/8)):
            lowsp += "\t"
        uppsp = ""
        for sp in range(3-int((len(upp)+5)/8)):
            uppsp += "\t"
        valrange = str("[" + low + lowsp + ",    " + upp + uppsp + "]")
        # limst = sName + txt1 + valrange + "\t"
        # txt2 = "\t"
        # for sp in range(3-((len(str(mid))+0)/8)):
        #     txt2 += "\t"
        print(sName + txt1 + valrange + "\t" + str(valx0[st + deb]))
        # + txt2 + str(mid))


def normToRealVal(x, optSet, simSet, stimParName,
                  synParName, synNSParName, synFRParName):
    simSet.samplePts = []
    vals = []
    for st in range(len(stimParName)):
        # calculation of real values... for external stimuli
        val = x[st]*(optSet.realxMax[st] - optSet.realxMin[st]) +\
                     optSet.realxMin[st]
        vals.append(val)
        # print(stimParName[st], val)
        simSet.set_by_range({stimParName[st]: [val]})
        # print(simSet.samplePts)
        # calculation of real values... for synapses

    rg1stsy = len(stimParName)
    for sy in range(len(synParName)):
        val = (x[rg1stsy+sy]*(optSet.realxMax[rg1stsy+sy] -
                              optSet.realxMin[rg1stsy+sy]) +
               optSet.realxMin[rg1stsy+sy])
        vals.append(val)
        # print(synParName[sy], val)
        simSet.set_by_range({synParName[sy]: [val]})
        # print(simSet.samplePts)

    rg1stsyNS = len(stimParName) + len(synParName)
    for syNS in range(len(synNSParName)):
        val = (x[rg1stsyNS+syNS]*(optSet.realxMax[rg1stsyNS+syNS] -
                                  optSet.realxMin[rg1stsyNS+syNS]) +
               optSet.realxMin[rg1stsyNS+syNS])
        vals.append(val)
        simSet.set_by_range({synNSParName[syNS]: [val]})

    rg1stsyFR = len(stimParName) + len(synParName) + len(synNSParName)
    for syFR in range(len(synFRParName)):
        val = (x[rg1stsyFR+syFR]*(optSet.realxMax[rg1stsyFR+syFR] -
                                  optSet.realxMin[rg1stsyFR+syFR]) +
               optSet.realxMin[rg1stsyFR+syFR])
        vals.append(val)
        # print(synFRParName[syFR], val)
        simSet.set_by_range({synFRParName[syFR]: [val]})
        # print(simSet.samplePts)
    return [simSet, vals]


def saveAsimAprojFilesformSimFilesDir(folders, optSet, model,
                                      nameSuffix,
                                      destAsimDir,
                                      destAprojDir,
                                      simSet=SimulationSet.SimulationSet(),
                                      createSimSet=1, affiche=0):
    # --------------------------------------------------------------------
    # Copies .asim file from "SimFiles" directory
    simFileName = os.path.splitext(os.path.split(model.asimFile)[-1])[0]
    destdir = os.path.join(folders.animatlab_rootFolder, destAsimDir)
    sourcedir = folders.animatlab_simFiles_dir
    filesource = simFileName + "-1.asim"
    filedest = simFileName + ".asim"
    # Add the .asim file with increment number
    numero = copyRenameFile(sourcedir, filesource,
                            destdir, filedest, "",
                            replace=0)

    # --------------------------------------------------------------------
    # saves the bestfit .aproj file in AprojFiles folder
    aprojFicName = os.path.split(model.aprojFile)[-1]
    name = os.path.splitext(aprojFicName)[0]
    ext = os.path.splitext(aprojFicName)[1]
    ficName = name + nameSuffix + ext
    aprojSaveDir = os.path.join(folders.animatlab_rootFolder, destAprojDir)
    asimFileName = os.path.join(sourcedir, filesource)
    aprojFileName = os.path.join(aprojSaveDir, ficName)
    complete_name = actualiseSaveAprojFromAsimFile(optSet,
                                                   asimFileName,
                                                   aprojFileName,
                                                   simSet=simSet,
                                                   createSimSet=createSimSet,
                                                   affiche=affiche)
    return [numero, simFileName, complete_name]


def runSimMvt(folders, model, optSet, projMan,
              x, simNb, chartRootName, fitValFileName, affiche):
    simSet = SimulationSet.SimulationSet()
    stimParName = optSet.stimParName
    synParName = optSet.synParName
    synNSParName = optSet.synNSParName
    synFRParName = optSet.synFRParName

    [simSet, vals] = normToRealVal(x, optSet, simSet, stimParName,
                                   synParName, synNSParName, synFRParName)
    if affiche == 1:
        print(simSet.samplePts)
    projMan.make_asims(simSet)
    projMan.run(cores=-1)
    tab = readTabloTxt(folders.animatlab_result_dir,
                       findTxtFileName(model, optSet, "", 1))
    quality = testquality(optSet, tab, optSet.template, "")
    behavElts = getbehavElts(optSet, tab)[:-2]
    mse, coactpenality, coact = quality[0], quality[1], quality[2]
    # destdir = folders.animatlab_rootFolder + "ChartResultFiles/"
    err = mse+coactpenality
    txt = "err:{:4.4f}; mse:{:4.4f}; coactpenality:{}"
    comment = txt.format(err, mse, coactpenality)
    # print(comment, end=' ')
    # chartname = savechartfile(chartRootName, destdir, tab, comment)
    # print("... chart file {} saved; {}".format(chartname, comment))
    # trial = chartname[0:chartname.find(".")]
    trial = str(simNb)
    if err < optSet.seuilMSEsave:
        print()
        print("-----------------------------------")
        # Saves the chart in CMAeSeuilChartFiles folder
        destdir = os.path.join(folders.animatlab_rootFolder,
                               "CMAeSeuilChartFiles")
        txtchart = tab
        comment = "bestfit:" + str(err)
        chartname = savechartfile('CMAeSeuilChart', destdir, txtchart, comment)
        # print("... chart file {} saved; {}".format(chartname, comment))
        # Saves the .asim file with increment in CMAeSeuilAsimFiles folder
        res = saveAsimAprojFilesformSimFilesDir(folders, optSet, model,
                                                "CMAeSeuil",
                                                "CMAeSeuilAsimFiles",
                                                "CMAeSeuilAprojFiles",
                                                simSet=simSet, createSimSet=0,
                                                affiche=affiche)
        [numero, simFileName, complete_name] = res

# TODO :
        """
        destdir = os.path.join(folders.animatlab_rootFolder,
                               "CMAeSeuilAsimFiles")
        sourcedir = folders.animatlab_simFiles_dir
        filesource = simFileName + "-1.asim"
        filedest = simFileName + ".asim"
        numero = copyRenameFile(sourcedir, filesource,
                                destdir, filedest, comment, replace=0)
        # Saves the corresponding .aproj file in CMAeSeuilAprojFiles folder
        aprojFileName = os.path.split(model.aprojFile)[-1]
        model.actualizeAproj(simSet)
        name = os.path.splitext(aprojFileName)[0]
        ext = os.path.splitext(aprojFileName)[1]
        ficname = name + "CMAeSeuil" + ext
        aprojCMAeDir = os.path.join(folders.animatlab_rootFolder,
                                    "CMAeSeuilAprojFiles")
        model.actualizeAprojStimState(optSet.tab_stims, affiche=0)
        model.actualizeAprojMotorState(optSet.tab_motors, affiche=0)
        model.saveXMLaproj(os.path.join(aprojCMAeDir, ficname))
        """
        print("-----------------------------------")
        comment = simFileName + '-{0:d}.asim'.format(numero)
        comment = comment + " " + chartname
        result = [trial, mse+coactpenality, mse, coactpenality, coact, comment]
        if optSet.seuilMSETyp == "Var":
            optSet.seuilMSEsave = err
            print("new threshold: ", optSet.seuilMSEsave)
    else:
        result = [trial, mse+coactpenality, mse, coactpenality, coact]
    writeBestResSuite(folders, fitValFileName, result, 0)
    return [result, vals, tab, behavElts]


def prepareTxtOutputFiles(optSet):
    folders = optSet.folders
    comment = ["trial", "eval", "mse", "coactpenality", "coact"]
    writeBestResSuite(folders, "CMAeFitCourse.txt", comment, 1)
    deb = 0
    affichParamLimits(optSet.stimParName, optSet.reallower,
                      optSet.realupper, optSet.realx0, deb)
    deb = len(optSet.stimParName)
    affichParamLimits(optSet.synParName, optSet.reallower,
                      optSet.realupper, optSet.realx0, deb)
    deb = len(optSet.stimParName) + len(optSet.synParName)
    affichParamLimits(optSet.synNSParName, optSet.reallower,
                      optSet.realupper, optSet.realx0, deb)
    deb = len(optSet.stimParName) + len(optSet.synParName) +\
        len(optSet.synNSParName)
    affichParamLimits(optSet.synFRParName, optSet.reallower,
                      optSet.realupper, optSet.realx0, deb)
    print
    deb = 0
    affichParamLimits(optSet.stimParName, optSet.lower,
                      optSet.upper, optSet.x0, deb)
    deb = len(optSet.stimParName)
    affichParamLimits(optSet.synParName, optSet.lower,
                      optSet.upper, optSet.x0, deb)
    deb = len(optSet.stimParName) + len(optSet.synParName)
    affichParamLimits(optSet.synNSParName, optSet.lower,
                      optSet.upper, optSet.x0, deb)
    deb = len(optSet.stimParName) + len(optSet.synParName) +\
        len(optSet.synNSParName)
    affichParamLimits(optSet.synFRParName, optSet.lower,
                      optSet.upper, optSet.x0, deb)

    titres1 = ["simN°"]
    titres2 = ["simN°"]
    for st in optSet.allPhasesStim[0][0]:
        for parName in optSet.seriesStimParam:
            titres1.append(optSet.stimName[st])
            titres2.append(parName)
    for sy in optSet.allPhasesSynFR[0][0]:
        for parName in optSet.seriesSynFRParam:
            titres1.append(optSet.connexFRName[sy])
            titres2.append(parName)

    writeBestResSuite(folders, "CMAeXValues.txt", titres1, 0)
    writeBestResSuite(folders, "CMAeXValues.txt", titres2, 0)
    writeBestResSuite(folders, "CMAeRealValues.txt", titres1, 0)
    writeBestResSuite(folders, "CMAeRealValues.txt", titres2, 0)


def saveCMAEResults(optSet, simSet):
    folders = optSet.folders
    projMan = optSet.projMan
    projMan.make_asims(simSet)  # saves the asim in "SimFiles" directory
    # this is the best asim file (even if MSE > seuilMSEsave)

    # --------------------------------------------------------------------
    # Copies asim file from "SimFiles" folder into "CMAeBestSimFiles"
    # actualizes aproj file from asim file and saves it to "AprojFiles" folder
    res = saveAsimAprojFilesformSimFilesDir(folders, optSet, optSet.model,
                                            "CMAeBest",
                                            "CMAeBestSimFiles",
                                            "AprojFiles")
    [numero, simFileName, complete_name] = res

    """
    # --------------------------------------------------------------------
    # Copies asim file from "SimFiles" to "CMAeFinalSimFiles" folder
    model = optSet.model
    simFileName = os.path.splitext(os.path.split(model.asimFile)[-1])[0]
    destdir = os.path.join(folders.animatlab_rootFolder, "CMAeBestSimFiles")
    sourcedir = folders.animatlab_simFiles_dir
    filesource = simFileName + "-1.asim"
    filedest = simFileName + ".asim"
    # Add the .asim file with increment number
    numero = copyRenameFile(sourcedir, filesource,
                            destdir, filedest, "",
                            replace=0)
    # --------------------------------------------------------------------
    # saves the bestfit .aproj file in AprojFiles folder
    aprojFicName = os.path.split(model.aprojFile)[-1]
    name = os.path.splitext(aprojFicName)[0]
    ext = os.path.splitext(aprojFicName)[1]
    ficName = name + "CMAeBest" + ext
    aprojSaveDir = os.path.join(folders.animatlab_rootFolder, "AprojFiles")
    asimFileName = os.path.join(sourcedir, filesource)
    aprojFileName = os.path.join(aprojSaveDir, ficName)
    complete_name = actualiseSaveAprojFromAsimFile(optSet,
                                                   asimFileName,
                                                   aprojFileName)
    """

    lastname = os.path.split(complete_name)[-1]
    saveparams(folders, optSet, folders.subdir + "CMAe.par", lastname)

    cwd = folders.animatlab_rootFolder
    CMAeDataSourceDir = os.path.join(cwd, "SimFiles")
    CMAeDataDestDir = os.path.join(folders.animatlab_rootFolder, "CMAeData")
    CMAeDataSubDir = "CMAeData"
    destDir = createSubDirIncrem(CMAeDataDestDir, CMAeDataSubDir)
    dirname = os.path.basename(os.path.split(destDir)[0])
    copyFileWithExt(CMAeDataSourceDir, destDir, ".dat")
    # --------------------------------------------------------------------
    # add two last lines in "CMAeFitCourse.txt" file
    comment = simFileName + '-{0:d}.asim'.format(numero)
    comment = comment + "; " + dirname
    titles = ["trial", "eval", "mse", "coactpenality", "coact", comment]
    writeBestResSuite(folders, "CMAeFitCourse.txt", titles, 0)


# TODO : Marquez
###########################################################################
#                           Marquez procedures
###########################################################################
def writeWeightMarquezTab(folders, weightMarquez, twitchAmpSet, nbruns,
                          chartColNames, mnCol, sensCol):
    filename = folders.animatlab_result_dir + "weightMarquez.txt"
    f = open(filename, 'a')
    now = datetime.datetime.now()
    s = now.strftime("%Y-%m-%d %H:%M:%S")
    s = s + '  ' + '\n'
    f.write(s)

    for amp in range(len(twitchAmpSet)):
        s = ''
        for i in range(len(mnCol)):
            s = s + chartColNames[mnCol[i]] +\
                '\t' + str(twitchAmpSet[amp]) + '\t'
            for j in range(len(sensCol)-2):
                s = s + '   ' + '\t'
        s = s + '  ' + '\n'
        f.write(s)
        s = ''
        for i in range(len(mnCol)):
            for j in range(len(sensCol)):
                s = s + chartColNames[sensCol[j]] + '\t'
        s = s + '\n'
        f.write(s)
        s = ''
        for t in range(nbruns):
            for i in range(len(mnCol)):
                for j in range(len(sensCol)):
                    s = s + str(weightMarquez[amp][i][j][t]) + '\t'
            s = s + '\n'
            f.write(s)
            s = ''
        s = '\n'
        f.write(s)

    f.write('\n')
    f.close()


def calcDeltaWeight(eta, mi, siprim, weighti):
    dweight = (- eta) * mi * (siprim + mi * weighti)
    return dweight


def runMarquez(folders, model, optSet, projMan):
    """
    This procedure is inspire from (Marquez et al, PLOS ComputBiol 2014)
    It controls ExternalStimulis to keep only stimuli on MNs
    It produces brief stimuli (100 ms) in those MNs (Uo to 4 intensities are
    used: 50nA, 20nA, 10nA and 5 nA)
    The produced movements activate sensory neurons
    The procedure calculate the otpimal gain between sensory neurons and each
    MN using a anti-Oja rule (Marquez et al, Biol Cybern, 2013)

    Practically the original asim file present in "FinalModel" is copied in a
    temp directory (to allow restoration after the Marquez procedure).
    Then each stimuli amplitude is applied to each MN sequentially
    (indeed in separate trials). The results of these stimuli are stored in
    chart files (whose content was defined in Animatlab) in the
    "ChartTwitchFiles" directory, and tables containing     the MN and sensory
    activities are stored in a table in memory (tableTmp). This table is used
    for applying the anti-Oja rule in a recursive way, using a fixed number of
    steps (nbruns).
    The result is a table of the evolution of synaptic weights between sensory
    neurons (sj) and motor neurons (mi). This table is saved in the
    "ResultFiles" directory under the name "weightMarquez.txt". If new runs
    of Marquez procedure are made, the results are added in this file.

    """
    global weightMarquez
    lineStartTwitch = int((optSet.startTwitch - optSet.chartStart) *
                          optSet.rate) + 1
    lineEndTwitch = int((optSet.startTwitch + optSet.timeMes + optSet.delay -
                         optSet.chartStart)*optSet.rate) + 2

    corr_sensName = ['', '']  # starts with two empty columns
    corr = []
    twitchAmpSet = [5.0000e-08, 2.0000e-08, 1.0000e-08, 5.0000e-09]
    # twitchAmpSet = [5.0000e-09]
    weightMarquez = [[[[0]]]]
    for amp in range(len(twitchAmpSet)-1):
        weightMarquez.append([[[0]]])
    for amp in range(len(twitchAmpSet)):
        for i in range(len(optSet.twitStMusclesStNbs)-1):
            weightMarquez[amp].append([[0]])
    for amp in range(len(twitchAmpSet)):
        for i in range(len(optSet.twitStMusclesStNbs)):
            for j in range(len(optSet.sensColChartNbs)-1):
                weightMarquez[amp][i].append([0])

    mi = []
    tmp = []
    for amp in range(len(twitchAmpSet)):
        for i in range(len(optSet.twitStMusclesStNbs)):
            tmp.append(0)
        mi.append(tmp)
        tmp = []
    # Preparation of the first line of the corr table with sensory neuron names
    for i in range(len(optSet.sensColChartNbs)):
        corr_sensName.append(optSet.chartColNames[optSet.sensColChartNbs[i]])
    # print(corr_sensName)
    corr.append(corr_sensName)

    print("\ncopying asim File to Temp Directory")
    # simFileName = findChartName(folders.animatlab_commonFiles_dir)[0]+'.asim'
    simFileName = os.path.split(model.asimFile)[-1]
    sourceDir = folders.animatlab_commonFiles_dir
    destDir = os.path.join(folders.animatlab_rootFolder, "temp")
    if not os.path.exists(destDir):
        os.makedirs(destDir)
    copyFile(simFileName, sourceDir, destDir)
    # seriesStimParam = ["CurrentOn", "StartTime", "EndTime"]

    # Ensures that asim environment is OK
    # setGravity(model, 0)
    setPlaybackControlMode(model, 0)  # 0: fastestPossible; 1: match physics
    # enableStims(ExternalStimuli, twitStMusclesSt)

    print("PREPARING asim File for twitches")
    # initSimulation()
    simSet = SimulationSet.SimulationSet()  # Instantiate simulationSet object

    for i in range(len(optSet.tab_stims)):  # set all external stimuli to zero
        # optSet.ExternalStimuli[i].find("CurrentOn").text = '0'
        optSet.ExternalStimuli[i].find("Enabled").text = 'False'
    stimName = [optSet.tab_stims[optSet.twitStMusclesStNbs[0]][0],
                optSet.tab_stims[optSet.twitStMusclesStNbs[1]][0]]

    tableTmp = []
    k = 0
    for ii in range(len(optSet.twitStMusclesStNbs)):
        print("")
        print('twit=', ii)
        corr_mn = []
        stimRank = optSet.twitStMusclesStNbs[ii]
        # print(stimRank)
        optSet.ExternalStimuli[stimRank].find("Enabled").text = 'True'
        optSet.ExternalStimuli[stimRank].\
            find("StartTime").text = str(optSet.startTwitch)
        optSet.ExternalStimuli[stimRank].\
            find("EndTime").text = str(optSet.endTwitch)
        optSet.tab_stims = affichExtStim(optSet, optSet.ExternalStimuli, 1)
        model.saveXML(overwrite=True)
        simSet.samplePts = []
        simSet.set_by_range({stimName[ii] + ".CurrentOn": twitchAmpSet})
        print(simSet.samplePts)
        projMan.make_asims(simSet)
        projMan.run(cores=-1)
        optSet.ExternalStimuli[stimRank].find("Enabled").text = 'False'
        for amp in range(len(twitchAmpSet)):
            twitchdir = os.path.join(folders.animatlab_rootFolder,
                                     "ChartTwitchFiles")
            tableTmp.append(readTabloTxt(folders.animatlab_result_dir,
                                         findTxtFileName(model, optSet,
                                                         "", amp+1)))
            stimtxt = '%2.2f' % (twitchAmpSet[amp] * 1e09)
            comment = '\t' + stimName[ii] + ' ' + stimtxt + 'nA' + ' ' + str(k)
            savechartfile("twitchchart", twitchdir, tableTmp[k], comment)
            k += 1

        print("\nsaving twitch asim File to FinalTwitchModel Directory")
        sourceDir = folders.animatlab_simFiles_dir
        destDir = os.path.join(folders.animatlab_rootFolder,
                               "FinalTwitchModel")
        if not os.path.exists(destDir):
            os.makedirs(destDir)
        simTwitchFileNames = findList_asimFiles(sourceDir)
        for asimFileName in simTwitchFileNames:
            copyFile(asimFileName, sourceDir, destDir+stimName[ii])

# TODO:
    for amp in range(len(twitchAmpSet)):
        # print()
        # print('twitchAmp: ', twitchAmpSet[amp])
        for t in range(optSet.nbruns):
            for ii in range(len(optSet.twitStMusclesStNbs)):
                if t == 0:
                    corr_mn.append([twitchAmpSet[amp]])
                    corr_mn.append(optSet.
                                   chartColNames[optSet.mnColChartNbs[ii]])
                for j in range(len(optSet.sensColChartNbs)):
                    # miprec = mi[ii]
                    mitempTab = extract(tableTmp[amp + ii*len(twitchAmpSet)],
                                        optSet.mnColChartNbs[ii],
                                        lineStartTwitch,
                                        lineEndTwitch)
                    mi[amp][ii] = mitempTab[int(optSet.timeMes *
                                                optSet.rate)] - mitempTab[0]
                    sitempTab = extract(tableTmp[amp + ii*len(twitchAmpSet)],
                                        optSet.sensColChartNbs[j],
                                        lineStartTwitch,
                                        lineEndTwitch)
                    sitempPrimTab = derive(sitempTab)
                    siprim = sitempPrimTab[int((optSet.timeMes +
                                                optSet.delay)*optSet.rate)-2] \
                        - sitempPrimTab[0]
                    deltaweight = calcDeltaWeight(optSet.eta, mi[amp][ii],
                                                  siprim,
                                                  weightMarquez[amp][ii][j][t])
                    # if deltaweight == 0:
                    #   print("ii= {}; j= {}; siprim ={}".format(ii, j, siprim))
                    nextweight = weightMarquez[amp][ii][j][t] + deltaweight
                    weightMarquez[amp][ii][j].append(nextweight)
                    txt = "t: %2d; mi[%2d] = %.4e; \tdeltaweight = %.4e"
                    txt = txt + "\tweightMarquez[%2d]=%.5e;"
                    txt = txt + "\t   weightMarquez[%2d]=%2.4e"
                    # if j == 0:
                    #   print(txt % (t, ii, mi[amp][ii], deltaweight,
                    #                t, weightMarquez[amp][ii][j][t],
                    #                t+1, weightMarquez[amp][ii][j][t+1]))
                    # print(weightMarquez)
                    corrcoeff = correl(tableTmp[amp + ii*len(twitchAmpSet)],
                                       optSet.mnColChartNbs[ii],
                                       optSet.sensColChartNbs[j],
                                       lineStartTwitch, lineEndTwitch)
                    if t == 0:
                        corr_mn.append('{:02.6f}'.format(corrcoeff))
                        # print("corr coeff =", corrcoeff)
                if t == 0:
                    corr.append(corr_mn)
                    corr_mn = []

    # print('')
    affich_corrtable(corr)
    writeWeightMarquezTab(folders, weightMarquez, twitchAmpSet, optSet.nbruns,
                          optSet.chartColNames, optSet.mnColChartNbs,
                          optSet.sensColChartNbs)

    print("\ncopying original asim File back to FinalModel Directory")
    sourceDir = os.path.join(folders.animatlab_rootFolder, "temp")
    destDir = folders.animatlab_commonFiles_dir
    copyFile(simFileName, sourceDir, destDir)


# TODO : rGEP
# ############################################################################
#                       rGEP procedures
# ############################################################################
def nonBlockingMsg(title="dialog", info="info", details="details"):
    widget = QtWidgets.QMessageBox()
    widget.setText(title)
    widget.setInformativeText(info)
    widget.setDetailedText(details)
    widget.setWindowModality(QtCore.Qt.NonModal)
    widget.show()


def showdialog(title="dialog", info="info", details="details"):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText(title)
    msg.setInformativeText(info)
    msg.setWindowTitle("MessageBox")
    msg.setDetailedText(details)
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
    msg.buttonClicked.connect(msgbtn)

    retval = msg.exec_()
    print("value of pressed message box button:", retval)
    return retval


def msgbtn(i):
    print("Button pressed is:", i.text())


def get_brushes_from_gist(sequence):
    my_palette = []
    cmap = plt.get_cmap('gist_rainbow')
    nb_levels = len(sequence)
    for i in range(nb_levels):
        # print(cmap(float(i)/nb_levels, float(10)/10))
        my_palette.append(cmap(float(i)/nb_levels, float(10)/10))
    lut = []
    for i, pal in enumerate(my_palette):
        red = pal[0]
        green = pal[1]
        blue = pal[2]
        lut.append([red, green, blue])
    a = min(sequence)
    b = max(sequence)
    positions = np.linspace(a, b, nb_levels, endpoint=True)
    q_colormap = pg.ColorMap(pos=positions, color=lut)
    color_for_points = q_colormap.map(sequence)
    brushes = [QtGui.QBrush(QtGui.QColor(*color_for_points[i, :].
                                         tolist())) for i in
               range(color_for_points.shape[0])]
    return brushes


def set_limits(x, rand, span, inf, sup, optSet, stim_liminf=False,
               stim_limsup=False,
               syn_liminf=True, syn_limsup=False):
    """
    Function set_limits
        In : x :²
    """
    stpar_nb = int(len(optSet.stimParName))
    xstim = x[:, :stpar_nb]
    xsyn = x[:, stpar_nb:]

    spanstim = span[:np.shape(x)[0], :stpar_nb]
    spansyn = span[:np.shape(x)[0], stpar_nb:]
    # else:
    #    spanstim = span[:stpar_nb]
    #    spansyn = span[stpar_nb:]

    randstim = rand[:, :stpar_nb]
    randsyn = rand[:, stpar_nb:]

    @np.vectorize
    def limitinf(xsubarr, randsubarr, span):
        return xsubarr if xsubarr >= inf else (randsubarr*span/1000)

    @np.vectorize
    def limitsup(xsubarr, randsubarr, span):
        return xsubarr if xsubarr <= sup else (1-randsubarr*span/1000)

    # first ensure that the first value is not out of the range(inf, sup)
    if x[0][0] > sup:
        x[0][0] = sup
    elif x[0][0] < inf:
        x[0][0] = inf
    """
    if stim_lim:
        stimarray = limitinf(limitsup(xstim, randstim), randstim)
    else:
        stimarray = xstim

    if syn_lim:
        synarray = limitinf(limitsup(xsyn, randsyn), randsyn)
    else:
        synarray = xsyn
    """
    stimarray = xstim
    if stim_liminf:
        stimarray = limitinf(stimarray, randstim, spanstim)
    if stim_limsup:
        stimarray = limitsup(stimarray, randstim, spanstim)

    synarray = xsyn
    if syn_liminf:
        synarray = limitinf(synarray, randsyn, spansyn)
    if syn_limsup:
        synarray = limitsup(synarray, randsyn, spansyn)
    return np.concatenate((stimarray, synarray), axis=1)


def string(setval):
    st = "["
    for idx, val in enumerate(setval):
        st += "{:2.2f}".format(val)
        if idx < len(setval) - 1:
            st += "  "
        else:
            st += "]"
    return st


def getGEPdataFileName(optSet):
    pre = ""
    folders = optSet.folders
    list_par = []
    mydir = os.path.join(folders.animatlab_rootFolder, "GEPdata")
    if not os.path.exists(mydir):
        os.makedirs(mydir)
    onlyfiles = [f for f in listdir(mydir)
                 if isfile(join(mydir, f))]
    # print(onlyfiles)
    if len(onlyfiles) > 0:
        for f in onlyfiles:
            if f.endswith(".par"):
                # print(f)
                # simN = f[:f.find('.')]
                # print(simN)
                list_par.append(f)
        if (len(list_par) < 10):
            pre = "0"
        else:
            pre = ""
    else:
        pre = "0"
    GEP_rootname = "GEPdata" + pre + str(len(list_par))
    return GEP_rootname


def findNewParamSerie(behav_obj, nbNeighbours, pairs_rg, order_series,
                      sigma_span, nbpar, affich, optSet):
    """
    NB sigma_span is deprecated. Not used anymore. It is set to 0 in the call
    """
    paramserie = np.zeros(shape=(1, nbpar))
    newParamSet = np.zeros(nbpar)

    closestParamSet = optSet.pairs[pairs_rg]
    if affich:
        print(" closest ParamSet:", formatparamset(closestParamSet))

    if len(closestParamSet) > 0:
        # calculate new param set as mean of nbNeighbours closest paramsets
        for idex in range(0, nbNeighbours):
            newParamSet += optSet.pairs[order_series.index[idex]][0:nbpar]
            print("=>", formatparamset(newParamSet))
        newParamSet = newParamSet/nbNeighbours
        noiseset = np.random.random_sample((1, nbpar))
        noiseset = (noiseset * 2) - 1           # noiseset in  [-1, 1]
        paramserie += noiseset * sigma_span + newParamSet
        if affich:
            # print("noiseset:", noiseset, end=' ')
            print(" newParamSet:", formatparamset(newParamSet))
            print("noiseset*sigma:", formatparamset((noiseset*sigma_span)[0]))
            print(" paramserie:\t", formatparamset(paramserie[0]))
        """
        for idex in range(nbpar):
            if paramserie[0][idex] > 1:
                paramserie[0][idex] = 1
            if paramserie[0][idex] < 0:
                paramserie[0][idex] = 0
        """
        # print(newParamSet, "->", paramserie)
    else:
        print("NO parameters in memory... RUN randParam")
    return paramserie


def formatparamset(parset):
    partxt = ""
    nbpar = len(parset)
    for par in range(nbpar-1):
        partxt += "{:1.4f} ".format(parset[par])
    partxt += "{:1.4f}".format(parset[nbpar-1])
    return "[{}]".format(partxt)


def findClosestParam(mse_coact_obj, nbpar, optSet, affich=0):
    objarr = np.array(mse_coact_obj)
    order_series = []
    closestParamSet = np.array([])
    if len(optSet.pairs) > 0:
        params = optSet.pairs[:, 0:nbpar]           # array of parameters
        mse_coact = optSet.pairs[:, nbpar:nbpar+2]  # array of mse_coact output
        dist = abs(mse_coact - objarr)
        sumdist_2 = dist[:, 0]**2 + dist[:, 1]**2
        sumdist = sumdist_2**0.5
        nbRunParam = len(sumdist)
        dtype = [('dist', float), ('order', int)]
        values = []
        for idx, val in enumerate(sumdist):
            values.append((val, idx))
        sumdist_index = np.array(values, dtype=dtype)   # -> structured array
        sumdist_order = np.sort(sumdist_index, order='dist')
        for idx in range(nbRunParam):
            order_series.append(sumdist_order[idx][1])
        rang = {}   # dictionary containing the rank of each trial / best
        for idx, val in enumerate(order_series):
            rang[val] = idx
        closestParamSet = optSet.pairs[order_series[0]][0:nbpar]
        if affich:
            text = "[behav0    behav1] \tdistance \torder \t\t\tparameters"
            print(text)
            for idx, mse_set in enumerate(mse_coact):
                paramset = params[idx]
                print("[{:5.2f}    {:5.2f}]".format(mse_set[0], mse_set[1]),\
                    "\t{:5.1f}".format(sumdist[idx]),\
                    "\t", rang[idx], "\t",\
                    formatparamset(paramset), end=' ')
                if rang[idx] == 0:
                    print(" <- best param")
                    print()
                else:
                    print()
    else:
        closestParamSet = optSet.x0
    # ecritpairs(optSet.pairs)
    return (closestParamSet, order_series)


def findClosestPair_behav(win, behav_aim, df_bhv_selected,
                          startseq, behav_col, mseThr, optSet, affich=0):
    objarr = np.array(behav_aim)
    order_series = []
    closest_behav = np.array([])
    if behav_aim is None:       # if we do not look for a given behavior ...
        return None
        None
    else:                   # if a given bevaviour is searched ...
        if len(optSet.pairs) > 0:
            norm_objarr = objarr/[100, 1]
            behavs_cues = df_bhv_selected[df_bhv_selected.columns[behav_col]]
            rel_behavs_cues = behavs_cues/[100, 1]
            dist = abs(rel_behavs_cues - norm_objarr)
            sumdist_2 = dist[dist.columns[0]]**2 +\
                dist[dist.columns[1]]**2
            sumdist = sumdist_2**0.5
            closestDist = sumdist.min()
            behavs_rg = sumdist.idxmin()
            closest_behav = behavs_cues.loc[[behavs_rg]].values.tolist()[0]
            order_series = sumdist.sort_values(ascending=True)
            # list_rg_seeds = list(order_series.index)
            list_rg_seeds = order_series.index
            rang = {}
            for idx, val in enumerate(list_rg_seeds):
                rang[val] = idx

        else:
            closestDist = -1
            behavs_rg = -1

        if affich:
            text = "[behav0    behav1] \tdist \torder \t\t\tparameters"
            print(text)
            for idx in range(1, len(behavs_cues)):
                behavset = df_bhv_selected.iloc[[idx]].values.tolist()
                bhvcues = list(behavs_cues.iloc[idx])
                dist = list(sumdist[idx:idx+1])
                print("[{:5.2f}    {:5.2f}]".format(bhvcues[0], bhvcues[1]),\
                    "\t{:5.1f}".format(dist[0]),\
                    "\t", rang[behavs_cues.index[idx]], "\t",\
                    formatparamset(behavset[0]), end=' ')
                if rang[behavs_cues.index[idx]] == 0:
                    print(" <- best param")
                    print()
                else:
                    print()

        return (closest_behav, closestDist, behavs_rg, order_series)


def findClosestPair_mse(mse_coact, startseq, optSet):
    objarr = np.array(mse_coact)
    order_series = []
    nbpar = len(optSet.x0)
    closestMSECoact = np.array([])
    if len(optSet.pairs) > 0:
        mse_coacts = optSet.pairs[startseq:, nbpar:nbpar+2]  # array of mse_coact
        dist = abs(mse_coacts - objarr)
        sumdist_2 = dist[:, 0]**2 + dist[:, 1]**2
        sumdist = sumdist_2**0.5
        nbRun = len(sumdist)
        dtype = [('dist', float), ('order', int)]
        values = []
        for idx, val in enumerate(sumdist):
            values.append((val, idx))
        sumdist_index = np.array(values, dtype=dtype)   # -> structured array
        sumdist_order = np.sort(sumdist_index, order='dist')
        for idx in range(nbRun):
            order_series.append(sumdist_order[idx][1])
        rang = {}   # dictionary containing the rank of each trial / best
        for idx, val in enumerate(order_series):
            rang[val] = idx
        closestMSECoact = optSet.pairs[startseq + order_series[0]][nbpar:nbpar+2]
        closestDist = sumdist_order[0][0]
        pairs_rg = order_series[0] + startseq
    else:
        closestDist = -1
        pairs_rg = -1
    return (closestMSECoact, closestDist, pairs_rg)


def findClosestPair_varmse(startseq, optSet):
    objarr = np.array([0, 0, 0])
    order_series = []
    nbpar = len(optSet.x0)
    closestMSECoact = np.array([])
    if len(optSet.pairs) > 0:
        varmse_array = optSet.behavs[startseq:, -1]  # array of mse_coact
        coact_array = optSet.behavs[startseq:, 1]
        filterStAngle = abs(optSet.behavs[startseq:, 2]) < 1
        filterMinAmplitude = optSet.behavs[startseq:, 3] > 10
        filterMvtOK = filterStAngle * filterMinAmplitude
        # varmse_coacts = list(zip(varmse_array, coact_array))
        varmse_coacts = np.column_stack((varmse_array, coact_array))
        temp = np.zeros((len(varmse_coacts), 3))
        temp[:, :-1] = varmse_coacts
        temp[:, 2] = np.arange(len(varmse_coacts))
        temp = temp[filterMvtOK]
        if temp.size == 0:
            return (closestMSECoact, -1, -1, -1)
        dist = abs(temp - objarr)
        sumdist_2 = dist[:, 0]**2 + dist[:, 1]**2
        sumdist = sumdist_2**0.5
        nbRun = len(sumdist)
        dtype = [('dist', float), ('order', int)]
        values = []
        for idx, val in enumerate(sumdist):
            values.append((val, temp[idx][2]))
        sumdist_index = np.array(values, dtype=dtype)   # -> structured array
        sumdist_order = np.sort(sumdist_index, order='dist')
        for idx in range(nbRun):
            order_series.append(sumdist_order[idx][1])
        rang = {}   # dictionary containing the rank of each trial / best
        for idx, val in enumerate(order_series):
            rang[val] = temp[idx, 2]
        closestMSECoact = optSet.pairs[startseq + order_series[0]][nbpar:nbpar+2]
        closestDist = sumdist_order[0][0]
        pairs_rg = order_series[0] + startseq
        bestvarmse = optSet.behavs[pairs_rg, -1]
    else:
        closestDist = -1
        pairs_rg = -1
        bestvarmse = -1
    return (closestMSECoact, closestDist, pairs_rg, bestvarmse)


def findRandObjective(closestDist, closest_behav, span):
    randserie = np.random.random_sample((1, 2))             # range 0, 1
    randserie = (randserie - 0.5) * 2 * span / 100        # range -0.1, 0.1
    behavserie = randserie
    if len(closest_behav) > 0:
        objective = closest_behav + behavserie    # range 0, dist_to_closest
    else:
        objective = behavserie
    return objective


def saveBestFit_to_AsimAproj(paramset, sourceAsimFile, optSet, folders,
                             model, procName="", typ=""):
    # bestParamSet = optSet.pairs[pairs_rg, 0:win.nbpar]
    simSet = SimulationSet.SimulationSet()
    simSet.samplePts = []
    stimParName = optSet.stimParName
    synParName = optSet.synParName
    synNSParName = optSet.synNSParName
    synFRParName = optSet.synFRParName
    [simSet, vals] = normToRealVal(paramset, optSet, simSet, stimParName,
                                   synParName, synNSParName, synFRParName)
    savedir = procName + "AsimFiles"
    destAsimdir = os.path.join(folders.animatlab_rootFolder, savedir)
    sourceAsimdir = os.path.join(folders.animatlab_result_dir, "tmpBestChart")
    # sourceAsimFile = srcasim
    destName = os.path.splitext(os.path.split(model.asimFile)[-1])[0]
    copyRenameFilewithExt(sourceAsimdir, sourceAsimFile, destAsimdir, destName,
                          ".asim", "", replace=0)

    aprojSaveDir = os.path.join(folders.animatlab_rootFolder, "AprojFiles")
    asimFileName = os.path.join(sourceAsimdir, sourceAsimFile)
    aprojFicName = os.path.split(model.aprojFile)[-1]
    name = os.path.splitext(aprojFicName)[0]
    ext = os.path.splitext(aprojFicName)[1]
    projficName = name + "_best" + procName + typ + ext
    aprojFileName = os.path.join(aprojSaveDir, projficName)
    complete_name = actualiseSaveAprojFromAsimFile(optSet,
                                                   asimFileName,
                                                   aprojFileName,
                                                   simSet=simSet,
                                                   overwrite=0,
                                                   createSimSet=0,
                                                   affiche=0)
    return complete_name


def saveBestpairtoAproj(win, optSet, typ, folders, model, projMan):
    (closestMseCoact,
     closestDist, pairs_rg) = findClosestPair_mse([0, 0], win.startEval,
                                                  optSet)
    bestParamSet = optSet.pairs[pairs_rg, 0:win.nbpar]
    simSet = SimulationSet.SimulationSet()
    simSet.samplePts = []
    stimParName = optSet.stimParName
    synParName = optSet.synParName
    synNSParName = optSet.synNSParName
    synFRParName = optSet.synFRParName
    [simSet, vals] = normToRealVal(bestParamSet, optSet, simSet,
                                   stimParName,
                                   synParName, synNSParName, synFRParName)
    # projMan = optSet.projMan
    projMan.make_asims(simSet)
    # After changing a property, save the updated model
    # ################################
    model.saveXML(overwrite=True)   # in the FinalModel dir
    # ################################

    simficName = os.path.split(model.asimFile)[-1]
    sourcedir = folders.animatlab_commonFiles_dir   # FinalModel dir
    destAprojDir = "AprojFiles"
    aprojFicName = os.path.split(model.aprojFile)[-1]
    name = os.path.splitext(aprojFicName)[0]
    ext = os.path.splitext(aprojFicName)[1]
    projficName = name + "bestGEP" + typ + ext
    aprojSaveDir = os.path.join(folders.animatlab_rootFolder, destAprojDir)
    asimFileName = os.path.join(sourcedir, simficName)
    aprojFileName = os.path.join(aprojSaveDir, projficName)
    complete_name = actualiseSaveAprojFromAsimFile(optSet,
                                                   asimFileName,
                                                   aprojFileName,
                                                   simSet=simSet,
                                                   overwrite=0,
                                                   createSimSet=0,
                                                   affiche=0)
    return complete_name


def saveBestChart(bestSimulNb, runType, srcdir, comment, optSet, folders,
                  model):
    chartname = findTxtFileName(model, optSet, "", bestSimulNb + 1)
    bestchart = readTabloTxt(srcdir, chartname)
    savedir = runType + "ChartFiles"
    destRootName = runType + "_chart"
    destdir = os.path.join(folders.animatlab_rootFolder, savedir)
    txtchart = bestchart
    bestchartName = savechartfile(destRootName, destdir, txtchart, comment)
    return bestchart, bestchartName


def saveBestAsim(sourcedir, sourcefile, destdir, destfile, folders):
    destdir = os.path.join(folders.animatlab_rootFolder, destdir)
    # Add the .asim file with increment number
    numero = copyRenameFile(sourcedir, sourcefile, destdir, destfile, "",
                            replace=0)
    return numero


def erase_file(path, filename):
    file_path = os.path.join(path, filename)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(e)


def SetupFoldersForRun(optSet):
    folders = optSet.folders
    erase_folder_content(os.path.join(folders.animatlab_rootFolder,
                                      "SimFiles"))
    dstdir = os.path.join(folders.animatlab_result_dir, "tmpBestChart")
    if not os.path.exists(dstdir):
        os.makedirs(dstdir)
    return dstdir


def savesChartAndAsimToTmpBestChart(data_behav, deb, preTot, pre, dstdir,
                                    folders, model, optSet):
    for behav in data_behav:
        # For each behavior found
        [err, mse, CoactP, simSubNb, simulNb] = behav
        if simulNb >= deb:
            # We check if the beahvior is in the current run
            chartFileName = findTxtFileName(model, optSet, pre, simSubNb + 1)
            # We retrieve the chart file with the number of
            simN = os.path.splitext((os.path.split(model.asimFile)[-1]))[0]
            # We retrieve the name of the asim file
            chartN = optSet.chartName[optSet.selectedChart]
            # We retrieve the name of the chart we get the parameters from
            if (simulNb + 1) < 10:
                dstfile = simN + "-" + preTot + str(simulNb+1)
            else:
                dstfile = simN + "-" + str(simulNb+1)
            dstfile += "_" + chartN
            srcdir = folders.animatlab_result_dir
            srcfile = chartFileName
            comment1 = ""
            copyRenameFilewithExt(srcdir, srcfile, dstdir, dstfile, ".txt",
                                  comment1, replace=1)
            if (simSubNb + 1) < 10:
                srcasim = simN + "-" + pre + str(simSubNb+1) + ".asim"
            else:
                srcasim = simN + "-" + str(simSubNb + 1) + ".asim"

            if (simulNb + 1) < 10:
                dstasim = simN + "-" + preTot + str(simulNb+1)
            else:
                dstasim = simN + "-" + str(simulNb + 1)
            srcasimdir = folders.animatlab_simFiles_dir
            copyRenameFilewithExt(srcasimdir, srcasim, dstdir, dstasim,
                                  ".asim", "", replace=1)


def getBestResults(newinfound, minErr, err, mse, coactpenality, idx, deb,
                   minMse, minCoactP, minsimSubNb, minsimulNb):
    """
    Function getBestResults
        In : newinfound : wether or not we found a new best solution
            minErr : the minimal explored error
            err : the error of the current sim
            mse : the mean squared error
            coactpenality : the penality for using both muscle at the same
                time
            idx : the indices of the current run
            deb : the beginning of the current batch
            minMse : the minimal mean squared error
            minCoactP : the minimum coactpenality
            minsimSubNb
    """
    # if we find a better solution we change our parameters
    if err < minErr:   # We keep only one chart!!!!  (the best)
        if abs(coactpenality) <= minCoactP:
            return [True, err, mse, coactpenality, idx, (idx+deb)]
    # if there's no parameters, then the first solution is the best
    elif minsimSubNb < 0:
        return [False, minErr, minMse, minCoactP, idx, (idx+deb)]
    # else we return the paramaters as they are
    return [newinfound, minErr, minMse, minCoactP, minsimSubNb, minsimulNb]


def runTrials(win, paramserie, paramserieSlices,
              savechart=0, procName="GEP",
              runType="rdparam", randParEvol=""):
    """
    Function that runs a series of AnimatLab simulations defined in paramserie
    and organized in paramseriSlices (number of parallel runs, and number o
    rounds). It is used in exec_rand_param(): the script used by various
    simulations:
        the mehtod do_GEP_rand() of the class MaFenetre, that calls:
            the method exec_gep_rand()  that calls:
                the method exec_rand_param()  that calls:
        the function find_aim_behav() of the class MaFenetre, that calls:
            aim_behav_extend()
            aim_behav_fill()    These thre functions are in gep_tl_bix.py
        the method do_rand_param()    that also calls
            the method exec_rand_param()
        and in the method saves_seeds() to re-run the selected behav parameters
    It returns:
        mse_coact, simSetGlob, lst_err, tabBehavElts, lst_tab, lst_simNb:
            the list of coactivation cost
            the the list of simSet files
            the list of errors
            the list of behaviour elements
            the list of charts
            the list of simulation numbers
    """
    # the two next lines are for debug
    optSet = win.optSet
    win.optSet.paramserie = paramserie
    win.optSet.paramserieSlices = paramserieSlices

    def saves_chart_asim_aproj(behav):
        """
        Function saves_chart_asim_aproj
            In : behav : a variable containing a summary of the values returned
                byt the searchAlgorihtm
            This function
        """
        # Here we retrieve the error, the mse, the coactPenality, the number of
        # the simulation in the current batch and the number of the current of
        # the simulation in the current run
        [err, mse, CoactP, simSubNb, simulNb] = behav
        print(simulNb, "-> rang dans le databhv:", end=' ')
        print(simulNb + len(optSet.pairs))
        # Here we read the values contained in the last simulation we've done
        txtchart = readTabloTxt(dstdir, findTxtFileName(model, optSet,
                                                        preTot, simulNb + 1))
        win.lst_bestchart.append(txtchart)
        # txtchart = win.lst_bestchart[idx]
        comment = "randParam bestfit:" + str(err)
        comment += "; mse bestfit:" + str(mse)
        comment += "; coactBestFit:" + str(CoactP)
        chart_glob_name = procName + "_chart"
        chartName = savechartfile(chart_glob_name,
                                  chartdir, txtchart, comment)
        win.lst_chartName.append(chartName)
        text = "... chart files {} saved; {}"
        print(text.format(chartName, comment))
        saveBestFit_to_AsimAproj(paramserie[simulNb], sourceAsimFile,
                                 optSet, folders, model, procName=procName,
                                 typ="")
        lst_simNb.append(simulNb)
        lst_err.append(err)
        win.lst_bestParNb.append(len(optSet.pairs) + simulNb)

    if procName == "GEP":
        print_adapt_tmplate_proc_MSE = 0
        print_adapt_tmplate_proc_varmse = 1
    else:
        print_adapt_tmplate_proc_MSE = 1
        print_adapt_tmplate_proc_varmse = 0

    folders = optSet.folders
    print("paramserieSlices:", paramserieSlices, end=' ')
    erase_folder_content(os.path.join(folders.animatlab_rootFolder,
                                      "SimFiles"))
    mse_coact = np.array(None)
    win.lst_bestchart = []
    win.lst_chartName = []
    win.lst_bestParNb = []
    gooddata_behav = []
    baddata_behav = []
    data_behav = []
    tab_mse = []
    lst_simNb = []
    lst_err = []
    tabBehavElts = []
    win.bestchartName = ""
    win.bestParamNb = 0
    simSet = SimulationSet.SimulationSet()
    simSetGlob = SimulationSet.SimulationSet()
    stimParName = optSet.stimParName
    synParName = optSet.synParName
    synNSParName = optSet.synNSParName
    synFRParName = optSet.synFRParName
    minMse = 100000
    minCoactP = 100000
    minErr = 100000
    minErrGEP = 100000
    bestGEPmse = 100000
    bestGEPerr = 100000
    bestCoactP = 100000
    minerrgoodGEP = 100000
    simulNb = 0
    saveBad = True
    newminfound = False
    minsimSubNb = -1
    minsimulNb = -1
    sourceAsimFile = optSet.model.asimFile
    if len(paramserie) > 9:
        preTot = "0"
    else:
        preTot = ""
    deb = 0
    fin = 0
    lst_tab = []
    dstdir = os.path.join(folders.animatlab_result_dir, "tmpBestChart")
    if not os.path.exists(dstdir):
        os.makedirs(dstdir)

    goodChartFound = False
    for run in range(len(paramserieSlices)):
        saveBad = True
        goodChartInRun = False
        erase_folder_content(os.path.join(folders.animatlab_rootFolder,
                                          "SimFiles"))
        deb = fin
        # deb = run*win.nb_activeprocs
        fin = deb + paramserieSlices[run]
        # fin = (run+1)*win.nb_activeprocs
        print("deb:", deb, "fin:", fin, end=' ')
        subparamserie = paramserie[deb:fin]
        if verbose > 2:
            print()
            print(subparamserie)
        simSet.samplePts = []
        simSetGlob.samplePts = []
        for idx, x in enumerate(subparamserie):
            if verbose > 2:
                print(idx, x)
            [simSet, vals] = normToRealVal(x, optSet, simSet,
                                           stimParName, synParName,
                                           synNSParName, synFRParName)
            simSetGlob.set_by_pts(simSet.samplePts)
        if verbose > 2:
            print(simSetGlob.samplePts)

        folders = optSet.folders
        model = optSet.model
        projMan = optSet.projMan
        projMan.make_asims(simSetGlob)
        # projMan.run(cores=-1)
        projMan.run(cores=paramserieSlices[run])

        for idx, x in enumerate(subparamserie):
            # reading the .asim files in SimFile directory
            if len(subparamserie) > 9:
                pre = "0"
            else:
                pre = ""
            tab = readTablo(folders.animatlab_result_dir,
                            findTxtFileName(model, optSet, pre, idx+1))
            lst_tab.append(tab)
            quality = testquality(optSet, tab, optSet.template, "",
                                  affich=print_adapt_tmplate_proc_MSE)
            mse, coactpenality, coact = quality[0], quality[1], quality[2]
            resbehav = getbehavElts(optSet, tab,
                                    print_adapt_tmplate_proc_varmse)
            startangle = resbehav[0]
            endangle = resbehav[1]
            # end_mvt2 = resbehav[5]
            # dur_mvt2 = resbehav[6]
            varmse = resbehav[7]
            comment0 = ""
            if procName != "GEP":
                err = mse+coactpenality
                txt = "\terr:{:4.4f}; mse:{:4.4f}; coactpenality:{};"
                txt = txt + " coact:{:4.8f}"
                comment0 = txt.format(err, mse, coactpenality, coact)
            else:
                varcoactpenality = resbehav[8]
                varcoact = resbehav[9]
                err = varmse+varcoactpenality
                txt = "\terr:{:4.4f}; varmse:{:4.4f}; coactpenality:{};"
                txt = txt + " coact:{:4.8f}"
                comment0 = txt.format(err, varmse, varcoactpenality, varcoact)
                coactpenality = varcoactpenality
                coact = varcoact
            resbehav = resbehav[:8]  # remove coactpenality and coact

            if verbose > 3:
                print(comment0)

            if procName != "GEP":  # If we don't want to get variable templates
                [newminfound,
                 minErr,
                 minMse,
                 minCoactP,
                 minsimSubNb,
                 minsimulNb] = getBestResults(newminfound, minErr, err, mse,
                                              coactpenality, idx, deb, minMse,
                                              minCoactP, minsimSubNb,
                                              minsimulNb)
            elif procName == "GEP":  # the aim is to save all acceptable behavs
                # (if savechart == 2)  or only the best (savechart == 1)
                if (err < 1) and (abs(startangle) < 1) and (endangle > 10):
                    saveBad = False
                    goodChartInRun = True
                    goodChartFound = True
                    minCoactP = coactpenality
                    simSubNb = idx
                    simulNb = idx + deb
                    gooddata_behav.append([err, varmse, minCoactP,
                                           simSubNb, simulNb])
                    if err < minerrgoodGEP:
                        minerrgoodGEP = err
                        best_gooddata = [err, varmse, minCoactP,
                                         simSubNb, simulNb]
                    data_behav.append([err, varmse, minCoactP,
                                       simSubNb, simulNb])
                    print(simulNb, err, "\t")
                elif abs(startangle) < 1 and endangle > 10 and err < minErrGEP:
                    saveBad = False
                    # In case no corret varmse would be found
                    # saves the best one
                    minErrGEP = err
                    bestGEPmse = varmse
                    bestGEPerr = err
                    bestCoactP = coactpenality
                    bestGEPSubNb = idx
                    bestGEPsimulNb = idx + deb
                else:
                    badGEPSubNb = idx
                    badGEPsimulNb = idx + deb

            mse_coact = [mse, coactpenality]
            behavElts = np.concatenate([mse_coact, resbehav])
            tabBehavElts.append(behavElts)
            tab_mse.append([mse, coactpenality])

        if procName == "GEP":
            if not goodChartInRun:   # will save only the best err
                if saveBad:
                    baddata_behav.append([minErrGEP, bestGEPmse, bestCoactP,
                                          badGEPSubNb, badGEPsimulNb])
                    data_behav.append([minErrGEP, bestGEPmse, bestCoactP,
                                       badGEPSubNb, badGEPsimulNb])
                else:
                    baddata_behav.append([minErrGEP, bestGEPmse, bestCoactP,
                                          bestGEPSubNb, bestGEPsimulNb])
                    data_behav.append([minErrGEP, bestGEPmse, bestCoactP,
                                       bestGEPSubNb, bestGEPsimulNb])
                print("goodChartInRun = ", goodChartInRun, "->", baddata_behav)
            elif goodChartInRun:
                print("goodChartInRun = ", goodChartInRun, "->", gooddata_behav)
            print

        if procName != "GEP":  # to present the single behav data in a tab
            # gooddata_behav.append([minErr, minMse, minCoactP,
            #                        simSubNb, simulNb])
            if newminfound:
                data_behav.append([minErr, minMse, minCoactP,
                                   minsimSubNb, minsimulNb])

        # ================   saves charts & asim to tmpBestChart   ============
        savesChartAndAsimToTmpBestChart(data_behav, deb, preTot, pre, dstdir,
                                        folders, model, optSet)
        # else this behav has already been saved to "tmpBestChart" folder
        data_behav = []

    if savechart > 0:
        # Saves the chart in GEPChartFile folder (or VSCDChartFile)
        savedir = procName + "ChartFiles"
        chartdir = os.path.join(folders.animatlab_rootFolder, savedir)
        if procName == "GEP":
            print("-----------------------------------")
            if goodChartFound:  # procName = GEP and some charts were found
                if savechart == 1 and win.saveAllMvtsVarmse == 0:
                    # Saves only the best of the series
                    saves_chart_asim_aproj(best_gooddata)
                elif savechart == 2 or win.saveAllMvtsVarmse == 1:
                    # saves all accepted behavs
                    for idx, behav in enumerate(gooddata_behav):
                        saves_chart_asim_aproj(behav)
            elif saveBad:
                # no good chart ... takes the best varmse
                print("No Good varmse Found -> save the best found")
                behav = [bestGEPerr, bestGEPmse, bestCoactP,
                         badGEPSubNb, badGEPsimulNb]
                saves_chart_asim_aproj(behav)
            else:
                # no good chart ... takes the best varmse
                print("No Good varmse Found -> save the best found")
                behav = [bestGEPerr, bestGEPmse, bestCoactP,
                         bestGEPSubNb, bestGEPsimulNb]
                saves_chart_asim_aproj(behav)
            print("-----------------------------------")
            if saveBad:
                lst_simNb.append(badGEPsimulNb)
            elif not goodChartFound:
                lst_simNb.append(bestGEPsimulNb)

        elif procName != "GEP":
            # we save only the chart with the best mse
            print()
            ("-----------------------------------")
            behav = [minErr, minMse, minCoactP, minsimSubNb, minsimulNb]
            saves_chart_asim_aproj(behav)
            print("-----------------------------------")
        lst_err.append(bestGEPerr)
    if procName == "VSCD":
        # savechart is set to 0, we need only the minsimulNb and minErr
        lst_simNb = minsimulNb
        lst_err = [minErr]
    mse_coact = np.array(tab_mse)
    return [mse_coact, simSetGlob, lst_err, tabBehavElts, lst_tab, lst_simNb]


# TODO : Span list improvement
# ==========================================================================
#                            Span  improvment
# ==========================================================================
def get_good_span_list(win, lst_paramserie):
    """
    procedure to be called by win.saves_seeds()
    From the selected seeds, the list of span values is optimized
    and saved in datastructure (in win.saves_seesds)
    """
    optSet = win.optSet
    win.lst_tab_rg_param_torun = []
    win.listparamSets_badspans = []
    win.listparamsets_remain_rg = []
    win.listparamSets_slices = []
    # win.listspanVal = [float(win.listDicSpanVal[0][nam])
    #                    for nam in win.xparName]
    win.listspanVal = [100 for name in win.xparName]
    span = win.listspanVal
    # open a seed drectory
    # df_parremain = win.df_parremain
    # df_bhvremain = win.df_bhvremain
    # list_rg_seeds = win.seeds_selected
    list_rg_seeds = win.selectedSeedsOK
    list_rg_seeds = list_rg_seeds[:4]
    # list_rg_seeds = win.lst_rg
    # ====================   Eliminate duplicates   ====================
    new_list_rg_seeds = []
    for idx, x in enumerate(list_rg_seeds):
        if x not in new_list_rg_seeds:
            new_list_rg_seeds.append(x)
            print(new_list_rg_seeds)
    list_rg_seeds = new_list_rg_seeds       
    lst_rg_bhv_to_search = new_list_rg_seeds
    #  ================== construct tab_rg_param_torun  =====================
    tab_rg_param_torun = []
    for idx in list_rg_seeds:
        list_param_rg = np.arange(win.nbpar)
        tab_rg_param_torun.append(np.array(list_param_rg))
    # ==================================================================
    listparamSets = [lst_paramserie[i] for i in list_rg_seeds]
    optSet.newtabBehavElts = np.array(win.newtabBehavElts)
    # listbehavs = optSet.newtabBehavElts[list_rg_seeds]
    listbehavs = [optSet.newtabBehavElts[i] for i in list_rg_seeds]
    finished_bhv = []
    OK = False
    listbhvOK = []  # list of paramset N° for which spans are OK
    while not OK:
        prev_tab_rg_param_torun = tab_rg_param_torun
        oldspan = copy.deepcopy(span)
        result = improve_span_list(win, span, listparamSets,
                                   listbehavs, listbhvOK,
                                   tab_rg_param_torun)
        span, listbhvOK, lst_new_valid = result
        new_tab_rg_param_torun = []
        
        for idx, newvalid in enumerate(lst_new_valid):
            #print(newvalid)
            rg_param = [tab_rg_param_torun[idx][i] 
                        for i in np.arange(len(tab_rg_param_torun[idx]))
                        if i not in newvalid]
            print(rg_param)
            """
            if len(rg_param) > 0:
                new_tab_rg_param_torun.append(np.array(rg_param))
            else:
                finished_bhv.append(idx)
            """
            new_tab_rg_param_torun.append(np.array(rg_param))
            if len(rg_param) == 0:
                finished_bhv.append(idx)
        new_lst_rg_bhv_to_search = [i for i in lst_rg_bhv_to_search
                                  if i not in finished_bhv]    
        
        lst_rg_bhv_to_search = new_lst_rg_bhv_to_search
        print("prev tab_rg_param_torun:")
        for idx in np.arange(len(tab_rg_param_torun)):
            print(prev_tab_rg_param_torun[idx])
        print()
        print("new tab_rg_param_torun:")
        for idx in np.arange(len(tab_rg_param_torun)):
            print(new_tab_rg_param_torun[idx])
        tab_rg_param_torun = new_tab_rg_param_torun
        print("listbhvOK:",listbhvOK)
        if (span == oldspan):
            print("Stabilized span list found")
            OK = True
        else:
            if min(span) > 0.01:
                print("Not yet")
                OK = False
            else:
                print("span list not stabilized : STOP for some span < 0.01")
                """
                spanStim = win.optSet.spanStim
                span = [spanStim for i in range(len(win.listspanVal))]
                """
                OK = True
        if tab_rg_param_torun == []:
            OK = False
            print("no more param to improve")
    roundspan = [sp*2 if sp<50 else 100 for sp in span]
    # roundspan = [sp for sp in span]
    rndspan=[round(sp, 4) for sp in roundspan]
    print(rndspan)
    lst_dic_span = [{}]
    for i, nam in enumerate(win.xparName):
        # lst_dic_span[0][nam] = win.listDicSpanVal[0][win.xparName[0]]
        lst_dic_span[0][nam] = rndspan[i]
    win.refresh_span(lst_dic_span)
    win.listspanVal = rndspan
    return OK, rndspan


def improve_span_list(win, span, listparamSets, listbehavs, listbhvOK,
                      tab_rg_param_torun):
    # optSet = win.optSet
    # folders = optSet.folders
    # model = optSet.model
    # sims = sim
    # projMan = optSet.projMan
    # aprojFicName = os.path.split(model.aprojFile)[-1]
    startseq = 0
    endseq = len(listbehavs)
    nbsrcbehavs = endseq-startseq

    df_behav_srceOK = pd.DataFrame(listbehavs[startseq:endseq],
                        columns=win.bhv_names,
                        index=np.arange(len(listbehavs[startseq:endseq])))
    print(df_behav_srceOK.to_string())
    list_varmse, list_st_angle, list_ampl = extract_err(listbehavs)
    list_parSets_rg_remain = []
    for idx, rg_lst in enumerate(tab_rg_param_torun):
        saut_rg = idx * win.nbpar
        print(rg_lst)
        for rg in rg_lst:
            rg += saut_rg
            list_parSets_rg_remain.append(rg)
    saut = 0
    prev_rg_lst = []
    for idx, rg_lst in enumerate(tab_rg_param_torun):
        for idy, rg in enumerate(rg_lst):
            print(list_parSets_rg_remain[idy+saut], end=" ")
        prev_rg_lst = rg_lst
        saut += len(prev_rg_lst)
        print()

    globalParamSets = []
    for idx, paramSet in enumerate(listparamSets):
        for k in range(len(paramSet)):
            tempParamSet = copy.deepcopy(paramSet)
            tempParamSet[k] += span[k]/200
            globalParamSets.append(tempParamSet)
    listparSets_badspans = [globalParamSets[idx]
                                 for idx in list_parSets_rg_remain] 
    win.listparamSets_badspans.append(listparSets_badspans)
    win.listparamsets_remain_rg.append(list_parSets_rg_remain)
    # print(listparSets_badspans)         
    if listparSets_badspans != []:
        """
        lists = calculate_newspan_list(win, span, globalParamSets,
                                       nbsrcbehavs, listbhvOK,
                                       tab_rg_param_torun)
        """
        lists = calculate_newspan_list(win, span, listparSets_badspans,
                                       nbsrcbehavs, listbhvOK,
                                       tab_rg_param_torun)
        newspan_list, listbhvOK, lst_new_valid = lists
        span = newspan_list
    trunc_span = [int(x * 100)/100 if x > 0.01 else 0.01 for x in span ]
    return trunc_span, listbhvOK, lst_new_valid


def calculate_newspan_list(win, span, listparSets_badspans, nbsrcbehavs,
                           listbhvOK, tab_rg_param_torun):
    """
    From the listparSets_badspans, calls run_listparamsets() to estimate
    the rate of failures in behaviors, and adapts the list of span values
    (span), accordingly
    Returns a list of new span (newspan_list)
    """
    # listremainbhv = [i for i in range(nbsrcbehavs) if i not in listbhvOK]
    par_span_fail_rate = []
    nb_procs = win.nb_procs
    org = getNbPacketVar(tab_rg_param_torun, nb_procs)
    nbEpochParam, nbRunParam, paramserieSlicesAllEpochs = org
    win.listparamSets_slices.append(paramserieSlicesAllEpochs)
    resp = run_listparamsets(win, listparSets_badspans, nbEpochParam,
                             nbRunParam, paramserieSlicesAllEpochs)
    lst_new_df_bhv, lst_new_df_par, lst_new_valid = resp
    lst_new_valid_rg = [[tab_rg_param_torun[j][i] for i in  lst_new_valid[j]]
                         for j in np.arange(len(lst_new_valid))]
    list_span_to_change = np.zeros(win.nbpar)
    sublistrunOK = []
    # calculates the number of times new behaviors was rejected for each par
    for idx, new_valid_rg in enumerate(lst_new_valid_rg):
        print(new_valid_rg, end=' ')
        if len(new_valid_rg) == len(tab_rg_param_torun[idx]):
            # all param with span OK
            print("---> ", "All spanValues OK in bhv", idx)
            sublistrunOK.append(idx)
        else:
            print()
        # print(newdf_bhv.to_string())
        for idy, param in enumerate(win.xparName):
            if idy in tab_rg_param_torun[idx]:
                # print(idy, param, new_valid_rg)
                if idy not in new_valid_rg:
                    list_span_to_change[idy] += 1
    newspan_list = copy.deepcopy(span)
    for i, sp in enumerate(span):
        print(i, win.xparName[i], "\t", sp, "--->", end=' ')
        par_span_fail_rate.append(list_span_to_change[i]/nbsrcbehavs)
        newspan_list[i] = newspan_list[i] / (1 + par_span_fail_rate[i])
        print(newspan_list[i])
    listbhvOK = sublistrunOK
    return newspan_list, listbhvOK, lst_new_valid


def run_listparamsets(win, listparSets_badspans, nbEpochParam, nbRunParam,
                      paramserieSlicesAllEpochs):
    """
    Runs a series of simulations from listparSets_badspans and returns:
        dataframe of new behaviors
        dataframe of new parameters
        list of valid ranks
    """
    stangl = 0
    st_err = 1
    minampl = 10
    max_coactpenalty = 0.01
    mseThr = win.mseThr

    lst_new_df_bhv = []
    lst_new_df_par = []
    lst_new_valid = []
    st_run = 0
    for epoch in range(nbEpochParam):
        listpairs = []
        behavs = []
        list_valid = []
        paramserieSlices = paramserieSlicesAllEpochs[epoch]
        if paramserieSlices != [0]:  # if there are paramsets to run
            paramserie = listparSets_badspans[st_run:st_run+nbRunParam[epoch]]
            # =================================================================
            result = runTrials(win, paramserie, paramserieSlices,
                               savechart=0, procName="GEP",
                               runType="GEPrand", randParEvol="")
            # =================================================================
            mse_coact = result[0]
            tabBehavElts = result[3]
            res = extract_err(tabBehavElts)
            newlist_varmse, newlist_st_angle, newlist_ampl = res
            for idx in range(nbRunParam[epoch]):
                pair_ParMseCoact = np.concatenate([listparSets_badspans[idx+st_run],
                                                   mse_coact[idx]])
                behav = tabBehavElts[idx]
                # win.add_pair(pair_ParMseCoact, behav)
                listpairs.append(pair_ParMseCoact)
                behavs.append(behav)
            st_run += nbRunParam[epoch]
            pairs = listpairs
            startseq = 0
            endseq = len(pairs)
            if len(behavs) > 1:
                new_index = np.arange(len(behavs[startseq:endseq]))
                df_newbehav = pd.DataFrame(behavs[startseq:endseq],
                                           columns=win.bhv_names,
                                           index=new_index)
            elif len(behavs) == 1:
                df_newbehav = pd.DataFrame(behavs[:], columns=win.bhv_names,
                                           index=np.arange(len(behavs[:])))
            # else:
            #     return (None, None)
            list_names = copy.deepcopy(win.xparName)
            list_names.append("mse")
            list_names.append("coactPen")
            df_newparam = pd.DataFrame(pairs[startseq:endseq],
                                       columns=list_names,
                                       index=np.arange(len(pairs[startseq:endseq])))
            res2 = win.selctValidBehav(behavs, pairs, startseq, endseq,
                                       stangl=stangl, st_err=st_err,
                                       minampl=minampl,
                                       maxCoactP=max_coactpenalty)
            (df_behav, df_param) = res2
            df_newvalidbhv = copy.deepcopy(df_behav)
            df_newvalidpar = copy.deepcopy(df_param)
            varmse_OK = df_newvalidbhv['varmse'] <= mseThr
            df_newvalidbhv = df_newvalidbhv[varmse_OK]
            df_newvalidpar = df_newvalidpar[varmse_OK]
            list_valid = list(df_newvalidbhv["rgserie"])
            lst_new_df_bhv.append(df_newbehav)
            lst_new_df_par.append(df_newparam)
        lst_new_valid.append(np.array(list_valid))
    return lst_new_df_bhv, lst_new_df_par, lst_new_valid


def extract_err(listbehavs):
    """
    From a list of behavior set values (listbehavs), extracts lists of:
        varmse, startseq angle and amplitude
    """
    list_varmse = []
    list_st_angle = []
    list_ampl = []
    for idx in range(len(listbehavs)):
        behav = listbehavs[idx]
        list_varmse.append(behav[-1])
        list_st_angle.append(behav[2])
        ampl = behav[3]-behav[2]
        list_ampl.append(ampl)
    return list_varmse, list_st_angle, list_ampl


def getNbPacketVar(tab_rg_param_torun, nb_procs):
    """

    """
    def makeSliceParams(packetSize, nb_procs):
        paramserieSlices = []
        if packetSize > nb_procs:
            nbrunsByPckt = int(packetSize/nb_procs)
            # self.nb_activeprocs = self.nb_procs
            for idxrun in range(nbrunsByPckt):
                paramserieSlices.append(nb_procs)
            remainRunsInPckt = packetSize - (nbrunsByPckt * nb_procs)
            if remainRunsInPckt != 0:
                paramserieSlices.append(remainRunsInPckt)
        elif packetSize < nb_procs:
            paramserieSlices.append(packetSize)
        else:   # if packetSize == self.nb_procs
            paramserieSlices.append(nb_procs)
        return paramserieSlices

    nbRunParam = []
    paramserieSlicesAllEpochs = []
    nbEpochParam = len(tab_rg_param_torun)
    nbRunParam = [len(paramsets) for paramsets in tab_rg_param_torun] 
    for idx, paramset in  enumerate(tab_rg_param_torun):
        print(len(paramset), "trials for behav", idx)
        packetSize = len(paramset)
        paramserieSlices = makeSliceParams(packetSize, nb_procs)
        paramserieSlicesAllEpochs.append(paramserieSlices)
    return nbEpochParam, nbRunParam, paramserieSlicesAllEpochs


class makeChartGraphs(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(makeChartGraphs, self).__init__(parent)
        
    def graphfromchart(self, optSet, chart_path, chartName, templateFileName):
        graphfromchart(optSet, chart_path, chartName, templateFileName)

    """
    def select_variables(self):
        choice = choose_elements_in_list(self.list_elem,
                                         self.typ, self.selected, self.text)
        return choice
    """


def save_listDicSpanVal(destDir, ficname, listDicSpanVal):
    ficname = "DicSpanVal.txt"
    completeparname = os.path.join(destDir, ficname)
    fparname = open(completeparname, 'w')
    for parname in list(listDicSpanVal[0].keys()):
        s = "{}:\t {}".format(parname, listDicSpanVal[0][parname]) 
        print(s)
        fparname.write(s+"\n")
    fparname.close()
    print("DicSpanVal saved in " + destDir)

def testVarMsePlot(optSet, chartFullName, interval=1./6):
    chartDir = os.path.split(chartFullName)[0]
    chartName = os.path.split(chartFullName)[-1]
    tab = readTablo(chartDir, chartName)
    # ================================================================
    behavElts = getbehavElts(optSet, tab, affich=1, interval=interval)
    # ================================================================
    startangle, endangle, oscil1, oscil2, max_speed = behavElts[:5]
    endMvt2, duration = behavElts[5:7]
    mse, coactpenality, coact = behavElts[7:10]
    res1, res2 = behavElts[-2:]
    coact1, coact2 = res1[0], res2[0]
    # chartName = chartFullName[chartFullName.find("GEP_chart"):]
    chartName = os.path.split(chartFullName)[-1]
    tmplate = optSet.varmse_tmplate
    lag = optSet.templateLag
    line_lag = -int(lag*optSet.rate) + 1

    time_endMvt2 = optSet.varmse_time_endMvt2 - lag
    time_midMvt2T = optSet.time_midMvt2T - lag
    # time_startMvt2 = optSet.startMvt2
    time_startMvt2 = optSet.varmse_startMvt2
    nbPts_mvt2T = optSet.nbPts_mvt2T
    rate = optSet.rate

    end_time = time_endMvt2 + 0.2
    time_first_ang_T = time_startMvt2 + (float(nbPts_mvt2T) * 3 / 8)/rate - lag
    time_third_ang_T = time_startMvt2 + (float(nbPts_mvt2T) * 5 / 8)/rate - lag
    lag = optSet.templateLag
    line_lag = -int(lag*optSet.rate) + 1

    Tdf = pd.DataFrame(tmplate)
    Tdf[2] = Tdf[2].shift(line_lag)
    Tdf.index = Tdf[1]

    (L, df, titre, tabparams) = chartToDataFrame(chartFullName,
                                                 colnames=optSet.chartColNames)
    dfsrtTime = df.Time[0]
    if line_lag < 0:
        dfendTime = min(df.index[len(df)-1], Tdf.index[len(Tdf)-1+line_lag])
    else:
        dfendTime = min(df.index[len(df)-1], Tdf.index[len(Tdf)-1])
    df.index = df.Time
    df[:0.6]

    # add two columns to df : TemplateTime and Template
    # df.loc[:, 'TemplateTime'] = Tdf[dfsrtTime:dfendTime][1]
    # df.loc[:, 'Template'] = Tdf[dfsrtTime:dfendTime][2]
    df2 = copy.deepcopy(df[dfsrtTime: dfendTime])
    colSup1 = list(Tdf[dfsrtTime:dfendTime][1])
    colSup2 = list(Tdf[dfsrtTime:dfendTime][2])
    if len(colSup1) < len(df2):
        colSup1.append(0)
        colSup2.append(0)
    df2.loc[:, 'TemplateTime'] = colSup1
    df2.loc[:, 'Template'] = colSup2

    shift = 0
    amplitude = endangle - startangle
    if amplitude > 10:
        durMvt2, traj, traj_vel = calculate_minjerk_duration(amplitude,
                                                             max_speed, rate)
        nPtsbeforemvt2strt = int(round(optSet.startMvt2 * rate)
                                 - round(dfsrtTime * rate) + 1)
        nPtsaftermvt2end = int(round(dfendTime * rate)
                               - round((durMvt2 + time_startMvt2) * rate) + 1)
        colSup3 = [0 for i in range(nPtsbeforemvt2strt+1)] + traj \
            + [amplitude for i in range(nPtsaftermvt2end+1)]
        shift = len(df2) - len(colSup3)
        if len(colSup3) < len(df2):
            while len(colSup3) < len(df2):
                colSup3.append(amplitude)
        if len(colSup3) > len(df2):
            colSup3 = colSup3[:-1]
        df2.loc[:, 'Template_lag'] = colSup3
        print("duration_template = ", durMvt2)
        text = "{}   varmse: {}   coact1: {}   coact2: {}\n  mvt duration: {}"
        title = text.format(chartName, behavElts[7], coact1, coact2, durMvt2)
    else:
        text = "{}   varmse: {}   coact1: {}   coact2: {}"
        title = text.format(chartName, behavElts[7], coact1, coact2)
    plt.rc('xtick', labelsize=18)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=18)    # fontsize of the tick labels
    plt.figure(figsize=(20, 15), dpi=50)
    # plt.subplot(211)
    df2[4.8:end_time]["Elbow"].plot(color="c")
    df2[4.8:end_time]["Template"].plot(color="grey")
    if amplitude > 10:
        df2[4.8:end_time]["Template_lag"].plot(color="red")
    plt.vlines(time_midMvt2T, ymin=startangle, ymax=endangle,
               colors='purple', linestyles='solid')
    plt.vlines(time_first_ang_T, ymin=startangle, ymax=endangle,
               colors='purple', linestyles='dashed')
    plt.vlines(time_third_ang_T, ymin=startangle, ymax=endangle,
               colors='purple', linestyles='dashed')

    plt.grid()
    unitx = "Time (s)"
    unity = "Elbow Mvt (degres)"
    plt.xlabel(unitx, fontsize=18)
    plt.ylabel(unity, fontsize=18)
    plt.legend(fontsize=14)
    basename = os.path.splitext(chartName)[0] + "_fitMinimumJerk"
    plt.suptitle(title, fontsize=20)
    plt.savefig(os.path.join(chartDir, basename + '.pdf'))
    plt.savefig(os.path.join(chartDir, basename + '.eps'))
    plt.show()
    return shift


# ==========================================================================
#                                   MAIN
# ==========================================================================
if __name__ == '__main__':
    # from tkinter import filedialog
    # import tkFileDialog as filedialog
    import tkinter.filedialog as filedialog
    from GEP_GUI import initAnimatLab
    # from makeGraphs import chartToDataFrame
    from makeGraphs import graphfromchart

    import sys
    app = QtWidgets.QApplication(sys.argv)
    chartFullName = filedialog.askopenfilename(title="Select chart file",
                                               filetypes=(("chart", "*.txt"),
                                                          ("all files",
                                                           "*.*")))
    chartDir = os.path.split(chartFullName)[0]
    chartName = os.path.split(chartFullName)[-1]
    animatsimdir = os.path.split(chartDir)[0]

    animatLabV2ProgDir, nb_procs = getInfoComputer()
    res = initAnimatLab(animatsimdir, animatLabV2ProgDir)
    aprojFicName = res[4]
    optSet = res[5]

    GEPdata_path = animatsimdir + "/GEPdata"
    parfilename = "GEPdata00.par"
    completeparfilename = os.path.join(GEPdata_path, parfilename)
    optSet.datastructure = load_datastructure(completeparfilename)
    datastructure = optSet.datastructure
    xCoactPenality = readCoacPenality(datastructure)
    xCoactPenality1, xCoactPenality2 = xCoactPenality
    optSet.xCoactPenality1 = xCoactPenality1
    optSet.xCoactPenality2 = xCoactPenality2
    folders = optSet.folders
    # listCharts = os.listdir(chartDir)
    # ======================================================================
    # truc is needed because choose_one_element_in_list() can be called only
    # from a graphic window (QWidget)
    truc = makeChartGraphs()
    truc.show()   # Show the form
    truc.close()
    # truc is created and closed, but its method graphfromchart can be called
    # ======================================================================
    # truc.select_variables()
    Go_ON = True
    while Go_ON:
        chartFullName = filedialog.askopenfilename(initialdir=chartDir,
                                                   title="Select chart file",
                                                   filetypes=(("chart",
                                                               "*.txt"),
                                                              ("all files",
                                                               "*.*")))
        chart_path = os.path.split(chartFullName)[0]
        chartName = os.path.split(chartFullName)[-1]
        print(chartName)
        if chartFullName != "":
            try:
                shift = testVarMsePlot(optSet, chartFullName, interval=1./8)
                print("shift=", shift)
            except Exception as e:
                print(e)
                shift = 1000
            if shift < 10:
                templateFileName = os.path.join(folders.animatlab_result_dir,
                                                "template.txt")
                truc.graphfromchart(optSet, chart_path, chartName,
                                    templateFileName)
        else:
            Go_ON = False
    app.exec_()

