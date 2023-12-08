# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 15:06:01 2020
Contains the procedures used in CMAes process in GEP_GUI.py
Translated in Python 3.8 Jan 2023 (D. Cattaert)
Modified February 22, 2023 (D. Cattaert):
    all pg.Qt.QtGui replaced by pg.Qt.QtWidgets
Modified April 03, 2023 (D. Cattaert):
    In exec_CMAeFromGUI() procedure, security added before launching 
    graphfromchart() (try: ... except), in case graphs cannot be drawn.
"""

import os

import numpy as np
# import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
import class_simulationSet as SimulationSet

from math import fmod
from cma import fmin

from optimization import affiche_liste

from optimization import writeBestResSuite
from optimization import runSimMvt
from optimization import prepareTxtOutputFiles
from optimization import saveCMAEResults
from optimization import findClosestParam
from optimization import erase_folder_content
from optimization import readTablo
from optimization import normToRealVal
from optimization import cleanChartsFromResultDir
from optimization import mise_a_jour
from optimization import savechartfile

from makeGraphs import graphfromchart
from makeGraphs import graphfromFitCourse

verbose = 1


def runPacketCMAe(win, optSet, projMan):
    if win.modelchanged != 1:
        exec_packet_CMAe(win, optSet, projMan)
    else:
        print()
        print()
        print("*****************************************************")
        print("This is a different model: run animatLabOptimSettings")
        print("*****************************************************")


def exec_packet_CMAe(win, optSet, projMan):
    None


def exec_CMAeFromGUI(win, optSet, projMan):
    # Retrieve the folders in which we're working
    folders = optSet.folders
    # Retrieves the model
    model = optSet.model
    # projMan = optSet.projMan
    # Create a set of simulation
    simSet = SimulationSet.SimulationSet()
    # Clean the content of the folder
    erase_folder_content(os.path.join(folders.animatlab_rootFolder,
                                      "SimFiles"))
    # Set the source directory
    sourcedir = os.path.join(folders.animatlab_rootFolder,
                             "CMAeSeuilChartFiles")
    # Set the minimum error at a high value to start
    win.minErr = 1000000.0
    # Set the minMSE to a high value to start
    win.minMse = 1000000.0
    # Set the minCoactP to a high value to start
    win.minCoactP = 100000000.0
    # Create an empty array which will contains the chart
    win.minchart = []
    # Set the minimum chart error to a high value to start
    win.minchartErr = 1000000.0
    # Set the simNb to 0 to start
    win.simNb = 0
    # Set the error array
    win.err = []
    optSet.nbevals = int(win.valueLine3.text())
    span = float(win.listDicSpanVal[0][win.xparName[0]])
    optSet.cmaes_sigma = float(win.valueLine5.text())
    optSet.xCoactPenality1 = float(win.valueCoactPen1.text())
    optSet.xCoactPenality2 = float(win.valueCoactPen2.text())

    # procedure = "runCMAe"

    def f(x):
        xcomplet = conformToConstant(x)
        # affiche_liste(xcomplet)
        # =======================================================
        resultat = runSimMvt(folders, model, optSet, projMan,
                             xcomplet, win.simNb,
                             'CMAeChart', "CMAefitCourse.txt", 0)
        # =======================================================
        result, vals, tab = resultat[0], resultat[1], resultat[2]
        normVals = [win.simNb]
        realVals = [win.simNb]
        for i in range(len(xcomplet)):
            normVals.append(xcomplet[i])
            realVals.append(vals[i])
        writeBestResSuite(folders, "CMAeXValues.txt", normVals, 0)
        writeBestResSuite(folders, "CMAeRealValues.txt", realVals, 0)
        behav = [result[2], result[3]]
        paramserie = np.array(xcomplet)
        paramserie.shape = (1, nbpar)
        mse_coact = np.array(behav)
        mse_coact.shape = (1, 2)
        win.parplt_itm.plot(paramserie[:, parx], paramserie[:, pary],
                            pen=3, symbol='o', symbolBrush='b')
        win.plotOtherParam(paramserie,
                           pen=3, symbol='o', symbolBrush='b')
        win.mseplt_itm.plot(mse_coact[:, 0], mse_coact[:, 1],
                            pen=3, symbol='o', symbolBrush='b')
        # -----------------------------------
        QtWidgets.QApplication.processEvents()
        # -----------------------------------
        pair_param_mseCoact = np.concatenate([paramserie[0], mse_coact[0]])
        resbehav = resultat[3]
        # startangle = resbehav[0]
        # endangle = resbehav[1]
        # end_mvt2 = resbehav[5]
        # dur_mvt2 = resbehav[6]
        varmse = resbehav[7]
        varcoactpenality = resbehav[8]
        # varcoact = resbehav[9]
        err = varmse+varcoactpenality
        # coactpenality = varcoactpenality  # values calculated from adapted
        # coact = varcoact                  # template used to get varmse
        resbehav = resbehav[:8]  # remove coactpenality and coact
        behavElts = np.concatenate([mse_coact[0], resbehav])

# TODO : continuer
        nptabBehavElts = np.array([behavElts])
        nppair_param_mseCoact = np.array([pair_param_mseCoact])
        # ========================================================
        win.plotBhvSet(nptabBehavElts, nppair_param_mseCoact, 0, 1)
        # ========================================================

        affiche_liste(behavElts)
        print()     # print is necessary because affiche_liste ends with ","
        win.add_pair(pair_param_mseCoact, behavElts)
        if len(result) > 5:     # if a chart was saved...
            win.bestchartName = result[-1].split(" ")[-1]
            bestchartList.append(win.bestchartName)
            print(win.bestchartName)
            err = result[1]
            besterrList.append(err)
            bestparamList.append(lastrun + win.simNb)
            win.bestchart = readTablo(sourcedir, win.bestchartName)
            win.plotmvt(win.bestchart)
            # -----------------------------------
            QtWidgets.QApplication.processEvents()
            # -----------------------------------

        err = result[1]
        if err < win.minchartErr:
            win.minchartErr = err
            win.minchart = tab
        if err < win.minErr:
            win.minErr = err
            win.minSimNb = win.simNb
            win.minMse = result[2]
            win.minCoactP = result[3]
        win.simNb += 1
        # if fmod(self.simNb, 10) == 0.0:
        #     print
        return err

    def improve(x0, nbevals, adj_cmaes_sigma, simSet):
        # =================================================================
        res = fmin(f, x0, adj_cmaes_sigma,
                   options={'bounds': [optSet.lower, optSet.upper],
                            'verb_log': 3,
                            'verb_disp': True,
                            'maxfevals': nbevals,
                            'seed': 0})
        # =================================================================
        x = res[0]
        xcomplet = conformToConstant(x)
        # once all nbevals tests are done...
        # ... save the best asim file in simFiles directory
        [simSet, vals] = normToRealVal(xcomplet, optSet, simSet,
                                       stimParName, synParName,
                                       synNSParName, synFRParName)
        # print simSet.samplePts
        return [res, simSet]

    def conformToConstant(x):
        if len(win.dicConstParam) > 0:  # if constant parameters...
            tmptab = []
            for idx, name in enumerate(win.xparName):
                if name not in win.listConstantNames:
                    tmptab.append(x[idx])
                else:
                    tmptab.append(win.dicConstParam[name])
            xcomplet = np.array(tmptab)
        else:
            xcomplet = x
        return xcomplet

    #  ============================= runCMAE ============================
    print("===============================")
    print("    Start CMAES for", optSet.nbevals, "runs")
    print("===============================")
    parx = win.parx
    pary = win.pary
    optSet.spanSyn = span
    optSet.spanStim = span
    bestchartList = []
    besterrList = []
    bestparamList = []
    nbpar = win.nbpar
    affich = 0
    (optSet.x0, order_series) = findClosestParam([0, 0], nbpar, optSet,
                                                 affich)
    optSet.x0 = conformToConstant(optSet.x0)
    try:
        optSet.seuilMSEsave = float(win.valueLine4b.text())
        optSet.seuilMSETyp = "Fix"
    except Exception as e:
        if (verbose > 1):
            print(e)
        optSet.seuilMSETyp = "Var"
        win.valueLine4b.setText(str("Var"))
        if order_series != []:
            optSet.seuilMSEsave = optSet.pairs[order_series[0]][nbpar]
        else:
            optSet.seuilMSEsave = 5000

    stimParName = optSet.stimParName
    synParName = optSet.synParName
    synNSParName = optSet.synNSParName
    synFRParName = optSet.synFRParName
    [simSet, realx0] = normToRealVal(optSet.x0, optSet, simSet,
                                     stimParName, synParName,
                                     synNSParName, synFRParName)
    projMan.make_asims(simSet)
    model.saveXML(overwrite=True)   # saves the new asim in FinalModel dir

    datastructure = optSet.datastructure  # dictionary for data structure
    if len(datastructure) > 0:
        structNb = len(datastructure)
        lastinfo = datastructure[structNb-1]
        lastrun = lastinfo[2]
    else:
        structNb = 0
        lastrun = 0

    # optSet.actualizeparamLoeb()
    optSet.actualizeparamCMAes(realx0=realx0)
    adj_cmaes_sigma = min(optSet.upper)*optSet.cmaes_sigma
    prepareTxtOutputFiles(optSet)
    x0 = conformToConstant(optSet.x0)
    ####################################################################
    [res, simSet] = improve(x0, optSet.nbevals, adj_cmaes_sigma, simSet)
    ####################################################################
    win.err.append(res[1])

    print(res[0])
    print("#############################")
    print("final score:", res[1], win.minMse, win.minCoactP, "simN°:", end=' ')
    print(win.minSimNb)
    print("#############################")
    cleanChartsFromResultDir(optSet, 1, 1, "")
    #  ============================= runCMAE ============================
    saveCMAEResults(optSet, simSet)  # Creates and Saves the new asim file
    print("===================================================")
    print("    End of", win.simNb, "CMAES runs")
    print("===================================================")
    besterrList.append(win.minchartErr)
    destdir = os.path.join(folders.animatlab_rootFolder,
                           "CMAeMinChartFiles")
    txtchart = win.minchart
    comment = "bestfit:" + str(win.minchartErr)
    chartname = savechartfile('CMAeMinChart', destdir, txtchart, comment)
    bestchartList.append(chartname)
    bestparamList.append(lastrun + win.minSimNb)
    packetsize = 0
    mise_a_jour(optSet, datastructure, structNb, 'CMAES',
                lastrun + 1, lastrun + win.simNb, packetsize,
                [optSet.spanStim, optSet.spanSyn,
                 [optSet.xCoactPenality1, optSet.xCoactPenality2],
                 optSet.cmaes_sigma,
                 besterrList, bestchartList, bestparamList, [optSet.gravity]])
    # ----------------------------------------------------------------
    # actualize optSet.x0 to the best result of CMAES
    (optSet.x0, order_series) = findClosestParam([0, 0], nbpar, optSet,
                                                 affich=0)
    [simSet, realx0] = normToRealVal(optSet.x0, optSet, simSet,
                                     stimParName, synParName,
                                     synNSParName, synFRParName)
    optSet.actualizeparamCMAes(realx0=realx0)
    print("##########################################")
    print("optSet.x0 and realx0  have been updated")
    print("##########################################")
    if win.bestchart != []:
        win.plotmvt(win.bestchart)
    else:
        win.plotmvt(win.minchart)
    win.startSerie = lastrun
    win.save_pairs("CMAES")
    templateFileName = os.path.join(folders.animatlab_result_dir,
                                    "template.txt")
    # colnames = win.optSet.chartColNames
    try:
        graphfromchart(optSet, destdir, chartname, templateFileName)
    except Exception as e:
        print(e)
    graphfromFitCourse(folders.animatlab_result_dir,
                       "CMAeFitCourse.txt")
