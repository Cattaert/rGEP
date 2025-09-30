# -*- coding: utf-8 -*-
"""
Created on Fri Mar 06 13:20:45 2020
Contains the procedures used in VSCD process in GEP_GUI
Translated in Python 3.8 Jan 2023 (D. Cattaert)
Modified February 22, 2023 (D. Cattaert):
    all pg.Qt.QtGui replaced by pg.Qt.QtWidgets

modified September 04, 2025 (D. Cattaert):
    errThr and coactThr values is now red from win.errThr and win.coactThr
    All methods and functions have been modified accordingly in optimization.py
    The value of win.errThr (that was 1.0 in previous version) is now given in
    a method from GUI ("setErrThr()").
    The value of win.coactThr (that was 0.01 in previous version) is now given in
    a method from GUI ("setErrThr()"). Using this method plus two new buttons,
    win.errThr and win.coactThr can be changed in the GUI.
    These two values are incorporated in datastructure (conditons' last list')
    and saved in GEPdata00.par.
"""
from random import shuffle

import os
import copy
from pyqtgraph.Qt import QtWidgets
import numpy as np

from optimization import erase_file
from optimization import writeBestResSuite
from optimization import chargeBestFeatures
from optimization import writeTabVals
from optimization import saveBestChart
from optimization import saveBestAsim
from optimization import findClosestParam
from optimization import mise_a_jour
from optimization import cleanChartsFromResultDir
from optimization import cleanAsimsFromResultDir
from optimization import erase_folder_content
from optimization import findClosestPair_mse
from optimization import normToRealVal
from optimization import SetupFoldersForRun
from optimization import readTabloTxt
from optimization import findTxtFileName
from optimization import testquality
from optimization import getbehavElts
from optimization import getBestResults
from optimization import savesChartAndAsimToTmpBestChart
from optimization import copyRenameFile
from optimization import saveparams
from optimization import actualiseSaveAprojFromAsimFile

from makeGraphs import graphfromFitCourse


import class_simulationSet as SimulationSet


def exec_VSCD_from_gui(win, optSet, proj_man, folders, model):
    """
    Before executing VSCD optimization procedure, the best param of
    preceeding paramseries run is searched to actualize optSet.x0.
    Then launches execVSCD() to execute VSCD optimization procedures.
    """
    sim_set = SimulationSet.SimulationSet()
    erase_folder_content(os.path.join(folders.animatlab_rootFolder,
                                      "SimFiles"))

    # affich act as a boolean to know if we want to display the results or
    # not
    # find the parameters of the point the closest to the goal we seek to
    # achieve
    (optSet.x0, _) = findClosestParam([0, 0], win.nbpar, optSet,
                                       affich=0)
    #
    (closest_mse_coact, closest_dist,
     pairs_rg) = findClosestPair_mse([0, 0], win.startEval, optSet)

    if closest_dist > 0:
        point_mse_coact = np.array(closest_mse_coact)
        point_mse_coact = point_mse_coact.reshape(1, 2)
        win.mseplt_itm.plot(point_mse_coact[:, 0],
                            point_mse_coact[:, 1], pen=None,
                            symbol='o',
                            symbolBrush=win.mvtcolor)
        paramset = optSet.pairs[:, 0:win.nbpar]
        paramset = paramset[pairs_rg]
        point_param = np.array(paramset)
        point_param = point_param.reshape(1, win.nbpar)
        win.parplt_itm.plot(point_param[:, optSet.parx],
                            point_param[:, optSet.pary], pen=None,
                            symbol='o',
                            symbolBrush=win.mvtcolor)
    else:
        paramset = optSet.x0
    # paramset is the best set of params
    # a simset is built from paramset
    [sim_set, _] = normToRealVal(paramset, optSet, sim_set,
                                 optSet.stimParName,
                                 optSet.synParName,
                                 optSet.synNSParName,
                                 optSet.synFRParName)
    proj_man.make_asims(sim_set)  # make a new asim from simset
    # saves the updated model in the FinalModel dir
    model.saveXML(overwrite=True)
    exec_VSCD(win, optSet, model, proj_man)


def exec_VSCD(win, optSet, model, proj_man):
    """
    Executes VSCD optimization procedures. When optimization is finished,
    It copies the bestfit .asim file in VSCDBestSimFiles folder and saves
    the bestfit .aproj file in AprojFiles folder
    """
    # The type of the algorithm to use
    runType = "VSCD"
    # Get the root of the animatLab project
    rt_asim_fic_name = os.path.splitext(os.path.split(model.asimFile)[-1])[0]
    best_param_list = []
    best_chart_list = []
    best_err_list = []
    min_err = 10000
    min_mse = 10000
    prev_min_coact = 10000
    min_coact_p = 10000
    min_simul_nb = -1
    win.err = []
    win.tabBehavElts = []
    win.orderedpar = []
    # Set the variability allowed to our parameters
    span = np.zeros((3, len(win.xparName)))
    for idx in range(2):
        for idx2 in range(len(win.xparName)):
            span[idx, idx2] = win.listDicSpanVal[0][win.xparName[0]]
    # Set the amount of epoch we'd like to perform
    # Set the amount of steps per epoch to perform
    if not optSet.datastructure:
        struct_nb = 0
        lastrun = 0
    else:
        struct_nb = len(optSet.datastructure)
        lastinfo = optSet.datastructure[struct_nb-1]
        lastrun = lastinfo[2]
    nbsim = 0
    # Create a list which contains the order of the parameters
    win.orderedpar = np.arange(win.nbpar)
    win.shuffledpar = copy.deepcopy(win.orderedpar)
    # shuffle(self.shuffledpar)
    param_value = copy.deepcopy(optSet.x0)

    # ------- if new start ->  Remove bestfits.txt and coeff.txt ----------
    if not optSet.pairs.any():
        erase_file(optSet.folders.animatlab_result_dir, "bestfits.txt")
        erase_file(optSet.folders.animatlab_result_dir, "coeff.txt")
    # ---------------------------------------------------------------------

    comment = ["trial", "eval", "mse", "coactpenality", "coact"]
    # Write the best results in a file called VSCDFitCourse.txt
    writeBestResSuite(optSet.folders, "VSCDFitCourse.txt", comment, 1)
    # For each epoch
    for epoch in range(optSet.nbepoch):
        # We shuffle the order of the parameters to change
        shuffle(win.shuffledpar)
        # We get the list of the delta coefficient (the size of the steps
        # to take on our gradient descent) for every parameters
        lst_delta_co = chargeBestFeatures(optSet.folders, "coeff.txt",
                                          optSet.deltacoeff,
                                          win.nbpar)
        #  If file exists, loads ...
        #  but if no such file, then creates deltaStimCo values
        # We get the best features written in bestfits.txt
        lst_best_fits = chargeBestFeatures(optSet.folders, "bestfits.txt",
                                           optSet.defaultval,
                                           win.nbpar)

        # For each parameters
        for rgpar in win.orderedpar:
            print()
            # We get the name of the parameters on the rank we're
            # looking at
            parname = optSet.xparName[win.shuffledpar[rgpar]]
            # We get the type of the parameter to change, either st for
            # stimulation, or syNS for synapse
            typ_par = optSet.struct_param[win.shuffledpar[rgpar]]
            # We get the previous best values for those parameters
            if lst_best_fits:
                previous_bestfit = min(lst_best_fits)
            else:
                previous_bestfit = 100000
            # For each steps
            for step in range(optSet.nbsteps):
                # We get the closest parameters to the goal we aim for
                (param_value, _) = findClosestParam([0, 0],
                                                    win.nbpar,
                                                    optSet,
                                                    affich=0)
                # We get the delta_coeff for the parameter we're changing
                delta = lst_delta_co[win.shuffledpar[rgpar]]
                listpairs = []
                print("epoch =", epoch, "/ last =", optSet.nbepoch - 1, end=' ')
                print("\t", rgpar, win.shuffledpar[rgpar], parname, end=' ')
                print("\t->", param_value[win.shuffledpar[rgpar]], end=' ')
                print("\tstep =", step)

                # We get the parameters to test, and their different values
                (paramserie, listvals) = win.get_paramserie(param_value,
                                                            rgpar,
                                                            step,
                                                            lst_delta_co,
                                                            span)
                # We get the amount of sets to test
                nb_sets = len(paramserie)
                # We update the plot
                win.parplt_itm.plot(paramserie[:, win.parx],
                                    paramserie[:, win.pary],
                                    pen=3, symbol='o',
                                    symbolBrush='c')

                win.plotOtherParam(paramserie, pen=3,
                                   symbol='o', symbolBrush=2)
                # -----------------------------------
                QtWidgets.QApplication.processEvents()
                # -----------------------------------
                # We set the minus value of the parameter retrieved by
                # get_paramserie
                # We set the plus value of the parameter retrieved by
                # get_paramserie
                print("val_minus:", listvals[0], end=' ')
                print("val_plus:", listvals[1], end=' ')
                # If we're on the first step we've got the base value of
                # the parameters
                if step == 0:
                    paramserie_slices = [3]
                    print("val_base:", listvals[2], end=' ')
                else:
                    paramserie_slices = [2]
                # print
                # ##################################################
                result = run_VSCD(paramserie, paramserie_slices, optSet,
                                  proj_man, min_err, min_mse, min_coact_p,
                                  min_simul_nb)
                # ##################################################
                win.result=result
                mse_coact = result[0]
                err = result[1]
                min_err = err
                tab_behav_elts = result[2]
                bestSimulNb = result[3]
                min_mse = mse_coact[bestSimulNb, 0]
                min_coact_p = mse_coact[bestSimulNb, 1]
                min_simul_nb = bestSimulNb
                win.bestParamNb = bestSimulNb + len(optSet.pairs)
                bestfit = err
                win.mseplt_itm.plot(mse_coact[:, 0], mse_coact[:, 1],
                                    pen=None, symbol='o', symbolBrush='c')
                # -----------------------------------
                QtWidgets.QApplication.processEvents()
                # -----------------------------------
                for idx in range(nb_sets):
                    pair_param_mse_coact = np.concatenate([paramserie[idx],
                                                           mse_coact[idx]])
                    behav = tab_behav_elts[idx]
                    # print idx, behav
                    win.add_pair(pair_param_mse_coact, behav)
                    listpairs.append(pair_param_mse_coact)

                df_bhvremain = win.update_df_bhvremain(errThr=win.errThr)
                win.test_for_save_map_bhv(df_bhvremain, affich=0)
                nptab_behav_elts = np.array(tab_behav_elts)
                np_pairs = np.array(listpairs)
                win.plotBhvSet(nptab_behav_elts, np_pairs, 0, nb_sets)
                # -----------------------------------
                QtWidgets.QApplication.processEvents()
                # -----------------------------------
                win.err.append(err)
                win.tabBehavElts.append(tab_behav_elts)

                if previous_bestfit <= bestfit:
                    # calculates the new increments
                    delta = delta / 2
                    lst_delta_co[win.shuffledpar[rgpar]] = delta
                    print("No improvement, bestfit =", previous_bestfit)
                else:
                    delta = delta * 2.5
                    if typ_par == "st":
                        if delta > optSet.maxDeltaStim:
                            delta = optSet.maxDeltaStim
                    else:
                        if delta > optSet.maxMultSyn:
                            delta = optSet.maxMultSyn
                    print("BestFit improved :", bestfit)
                    lst_delta_co[win.shuffledpar[rgpar]] = delta
                    lst_best_fits[win.shuffledpar[rgpar]] = bestfit

                    writeTabVals(optSet.folders, lst_delta_co,
                                 "coeff.txt",
                                 "deltaCoeff:", 1)
                    writeTabVals(optSet.folders, lst_best_fits,
                                 "bestfits.txt",
                                 "bestFits:", 1)
                    rang = win.shuffledpar[rgpar]
                    bestvalue = paramserie[bestSimulNb, rang]
                    param_value[win.shuffledpar[rgpar]] = bestvalue

                    # chartfile is saved if there were an improvement
                    coact_p = mse_coact[bestSimulNb, 1]
                    mse = mse_coact[bestSimulNb, 0]
                    comment = "randParam bestfit:" + str(err)
                    comment += "; mse bestfit:" + str(mse)
                    comment += "; coactBestFit:" + str(coact_p)
                    srcdir = os.path.join(optSet.folders.animatlab_result_dir,
                                          "tmpBestChart")
                    print("-----------------------------------------------")
                    print("best =", bestSimulNb)
                    name_tab = saveBestChart(bestSimulNb, runType, srcdir,
                                             comment, optSet, optSet.folders,
                                             model)
                    win.bestchart, win.bestchartName = name_tab
                    if win.bestchartName == "": 
                        saveChart = False
                        print("No chart to save...")
                        win.bestSimulNb = bestSimulNb
                        win.halt()
                        
                    else:
                        saveChart = True
                        txttmp = "... chart file {} saved, paramNb: {}"
                        print(txttmp.format(win.bestchartName,
                                            win.bestParamNb))
                    print("-----------------------------------------------")
                    if saveChart:
                        win.plotmvt(win.bestchart)
                        # -----------------------------------
                        QtWidgets.QApplication.processEvents()
                        # -----------------------------------
                        best_chart_list.append(win.bestchartName)
                        best_err_list.append(bestfit)
                        best_param_list.append(win.bestParamNb)
    
                        # asimfile is saved if there were an improvement
                        asim_nb = bestSimulNb + 1
                        sourcedir = optSet.folders.animatlab_simFiles_dir
                        sourcefile = rt_asim_fic_name + "-" + str(asim_nb)
                        sourcefile += ".asim"
                        destdir = "VSCDBestAsimFiles"
                        destfile = rt_asim_fic_name + ".asim"
                        nb_best_asim = saveBestAsim(sourcedir, sourcefile,
                                                    destdir, destfile,
                                                    optSet.folders)

                for index, mse_co in enumerate(mse_coact):
                    if index != 0:
                        mse = mse_co[0]
                        coact_p = mse_co[1]
                        nbsim += 1
                        if bestfit < previous_bestfit and index == bestSimulNb:
                            if coact_p < prev_min_coact:
                                prev_min_coact = coact_p
                            comment = rt_asim_fic_name +\
                                '-{0:d}.asim'.format(nb_best_asim)
                            comment = comment + " " + win.bestchartName
                            res = [nbsim, mse+coact_p, mse, coact_p, coact_p,
                                   comment]
                            previous_bestfit = bestfit

                        else:
                            res = [nbsim, previous_bestfit, mse,
                                   prev_min_coact, prev_min_coact]
                        writeBestResSuite(optSet.folders, "VSCDFitCourse.txt",
                                          res, 0)
    packetsize = 3
    mise_a_jour(optSet, optSet.datastructure, struct_nb, runType,
                lastrun+1, lastrun + nbsim, packetsize,
                [optSet.spanStim, optSet.spanSyn,
                 [optSet.xCoactPenality1, optSet.xCoactPenality2],
                 best_err_list, best_chart_list, best_param_list,
                 [optSet.gravity]])
    graphfromFitCourse(optSet.folders.animatlab_result_dir,
                       "VSCDFitCourse.txt")
    if len(paramserie) > 9:
        pre = "0"
    else:
        pre = ""

    win.startSerie = lastrun
    print("win.startSerie: ", win.startSerie)
    win.save_pairs(runType)

    clean_result_dir(optSet, 1, len(paramserie), pre)


def clean_result_dir(optSet, first_file, last_file, pre):
    """
    Function clean_result_dir
        In :
        Out :
        This function clean the ResultFiles dir after the execution of a VSCD
        algorithm
    """
    cleanChartsFromResultDir(optSet, first_file, last_file, pre)
    subdir = os.path.join("ResultFiles", "tmpBestChart")
    cleanChartsFromResultDir(optSet, first_file, last_file, pre,
                             directory=subdir)
    cleanAsimsFromResultDir(optSet, first_file, last_file, pre,
                            directory=subdir)


def run_VSCD(paramserie, paramserie_slices, optSet, proj_man, min_err,
             min_mse, min_coact_p, min_simul_nb):
    """
    comment...
    """
    print("paramserie_slices:", paramserie_slices, end=' ')
    data_behav = []
    tab_mse = []
    lst_err = []
    tab_behav_elts = []
    sim_set = SimulationSet.SimulationSet()
    sim_set_glob = SimulationSet.SimulationSet()
    stim_par_name = optSet.stimParName
    syn_par_name = optSet.synParName
    syn_ns_par_name = optSet.synNSParName
    syn_fr_par_name = optSet.synFRParName
    # min_mse = 100000
    # min_coact_p = 100000
    # min_err = 100000
    # min_simul_nb = -1
    min_sim_sub_nb = -1
    if len(paramserie) > 9:
        pre_tot = "0"
    else:
        pre_tot = ""
    deb = 0
    fin = 0

    dstdir = SetupFoldersForRun(optSet)
    for serie_slice in paramserie_slices:
        newm_in_found = False
        folders = optSet.folders
        model = optSet.model
        erase_folder_content(os.path.join(folders.animatlab_rootFolder,
                                          "SimFiles"))
        deb = fin
        fin = deb + serie_slice
        print("deb:", deb, "fin:", fin, end=' ')
        subparamserie = paramserie[deb:fin]
        sim_set.samplePts = []
        sim_set_glob.samplePts = []
        for idx, param_value in enumerate(subparamserie):
            [sim_set, _] = normToRealVal(param_value, optSet, sim_set,
                                         stim_par_name, syn_par_name,
                                         syn_ns_par_name, syn_fr_par_name)
            sim_set_glob.set_by_pts(sim_set.samplePts)

        proj_man = optSet.projMan
        proj_man.make_asims(sim_set_glob)
        # projMan.run(cores=-1)
        proj_man.run(cores=serie_slice)

        for idx, param_value in enumerate(subparamserie):
            # reading the .asim files in SimFile directory
            if len(subparamserie) > 9:
                pre = "0"
            else:
                pre = ""
            tab = readTabloTxt(folders.animatlab_result_dir,
                               findTxtFileName(model, optSet, pre, idx+1))
            # quality = testquality(optSet, tab, optSet.template, "",
            #                       "VSCD", 1)
            quality = testquality(optSet, tab, optSet.template, "", 1)
            # [mse, coactpenality, _] = quality
            mse = quality[0]
            coactpenality = quality[1]
            resbehav = getbehavElts(optSet, tab, 0)
            resbehav = resbehav[:8]  # remove coactpenality and coact
            # end_mvt2 = resbehav[5]
            # dur_mvt2 = resbehav[6]
            err = mse+coactpenality

            [newm_in_found,
             min_err,
             min_mse,
             min_coact_p,
             min_sim_sub_nb,
             min_simul_nb] = getBestResults(newm_in_found, min_err, err, mse,
                                            coactpenality, idx, deb, min_mse,
                                            min_coact_p, min_sim_sub_nb,
                                            min_simul_nb)

            mse_coact = [mse, coactpenality]
            behav_elts = np.concatenate([mse_coact, resbehav])
            tab_behav_elts.append(behav_elts)
            tab_mse.append([mse, coactpenality])

        if newm_in_found:
            data_behav.append([min_err, min_mse, min_coact_p,
                               min_sim_sub_nb, min_simul_nb])

        # ================   saves charts & asim to tmpBestChart   ============
        savesChartAndAsimToTmpBestChart(data_behav, deb, pre_tot, pre, dstdir,
                                        folders, model, optSet)
        data_behav = []
        lst_sim_nb = min_simul_nb
        lst_err = min_err
    mse_coact = np.array(tab_mse)
    return [mse_coact, lst_err, tab_behav_elts, lst_sim_nb]


def initialize_exec_VSCD(win, optSet, proj_man, model):
    """
    Initialize VSCD procedures before starting a new series.
    Sets essai to 0.
    Erases the 5 files that contain the state of the last VSCD process
    Executes a new VSCD optimization process.
    """
    folders = optSet.folders
    initialize_VSCD(folders)
    exec_VSCD_from_gui(win, optSet, proj_man, folders, model)


def saveresults_VSCD(optSet, aproj_fic_name):
    """
    Copies the bestfit .asim file in VSCDLastSimFiles folder
    saves the bestfit .aproj file in AprojFiles folder
    """
    folders = optSet.folders
    model = optSet.model
    # ---------------------------------------------------------
    # Copies the bestfit .asim file in VSCDLastSimFiles folder
    destdir = os.path.join(folders.animatlab_rootFolder,
                           "VSCDLastSimFiles")
    sourcedir = folders.animatlab_commonFiles_dir
    sim_file_name = os.path.splitext(os.path.split(model.asimFile)[-1])[0]
    filesource = sim_file_name + ".asim"
    filedest = sim_file_name + ".asim"
    comment = ""
    numero = copyRenameFile(sourcedir, filesource,
                            destdir, filedest, comment,
                            replace=0)
    comment = sim_file_name + '-{0:d}.asim'.format(numero)
    titles = ["trial", "eval", "mse", "coactpenality", "coact", comment]
    writeBestResSuite(folders, "VSCDFitCourse.txt", titles, 0)

    # ---------------------------------------------------------
    # saves the bestfit .aproj file in AprojFiles folder
    name = os.path.splitext(aproj_fic_name)[0]
    ext = os.path.splitext(aproj_fic_name)[1]
    ficname = name + "VSCD" + ext
    asim_file_name = model.asimFile
    aproj_save_dir = os.path.join(folders.animatlab_rootFolder,
                                  "AprojFiles")
    aproj_file_name = os.path.join(aproj_save_dir, ficname)
    complete_name = actualiseSaveAprojFromAsimFile(optSet,
                                                   asim_file_name,
                                                   aproj_file_name)
    lastname = os.path.split(complete_name)[-1]
    saveparams(folders, optSet, folders.subdir + "VSCD.par", lastname)


def initialize_VSCD(folders):
    """
    Initialize VSCD procedures before starting a new series
    Sets essai to 0
    erases the 5 files that contain the state of the previous VSCD process
    """
    # global essai
    # essai = 0
    dir_name = os.path.join(folders.animatlab_rootFolder,
                            "ResultFiles")
    # if os.path.exists(destDir):
    if os.path.exists(os.path.join(dir_name, "stimbestfits.txt")):
        os.remove(os.path.join(dir_name, "stimbestfits.txt"))
    if os.path.exists(os.path.join(dir_name, "stimbestfitsCoact.txt")):
        os.remove(os.path.join(dir_name, "stimbestfitsCoact.txt"))
    if os.path.exists(os.path.join(dir_name, "stimcoeff.txt")):
        os.remove(os.path.join(dir_name, "stimcoeff.txt"))
    if os.path.exists(os.path.join(dir_name, "synbestfits.txt")):
        os.remove(os.path.join(dir_name, "synbestfits.txt"))
    if os.path.exists(os.path.join(dir_name, "synbestfitsCoact.txt")):
        os.remove(os.path.join(dir_name, "synbestfitsCoact.txt"))
    if os.path.exists(os.path.join(dir_name, "syncoeff.txt")):
        os.remove(os.path.join(dir_name, "syncoeff.txt"))
    erase_folder_content(os.path.join(folders.animatlab_rootFolder,
                                      "SimFiles"))
