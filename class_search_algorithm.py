# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 13:36:34 2020

@author: nrault
Translated in Python 3.8 Jan 2023 (D. Cattaert)
"""
import os
import numpy as np
from optimization import readTablo
from optimization import findTxtFileName
from optimization import savechartfile
from optimization import saveBestFit_to_AsimAproj
from optimization import erase_folder_content
from optimization import normToRealVal
from optimization import testquality
from optimization import getbehavElts
from optimization import getBestResults
from optimization import savesChartAndAsimToTmpBestChart

verbose = 1


class search_algo(object):

    def __init__(self, folders, model, optSet, projMan, win):
        self.folders = folders
        self.model = model
        self.optSet = optSet
        self.projMan = projMan
        self.win = win

    def runTrials(win, paramserie, paramserieSlices, optSet, folders, model,
                  projMan, savechart=0, procName="GEP", runType="rdparam",
                  randParEvol=""):
        """
        comment...
        """
        def saves_chart_asim_aproj(behav):
            """
            Function saves_chart_asim_aproj
                In : behav : a variable containing a summary of the values
                    returned by the searchAlgorihtm
                This function
            """
            # Here we retrieve the error, the mse, the coactPenality, the number of
            # the simulation in the current batch and the number of the current of
            # the simulation in the current run
            [err, mse, CoactP, simSubNb, simulNb] = behav
            print(simulNb, "-> rang dans le databhv:", end=' ')
            print(simulNb + len(optSet.pairs))
            # Here we read the values contained in the last simulation we've done
            txtchart = readTablo(dstdir, findTxtFileName(model, optSet,
                                                         preTot, simulNb + 1))
            win.lst_bestchart.append(txtchart)
            # txtchart = self.lst_bestchart[idx]
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
                # deb = run*self.nb_activeprocs
                fin = deb + paramserieSlices[run]
                # fin = (run+1)*self.nb_activeprocs
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
                # projMan = optSet.projMan
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
                    [mse, coactpenality, coact] = quality
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
                        err = varmse+coactpenality
                        txt = "\terr:{:4.4f}; varmse:{:4.4f}; coactpenality:{};"
                        txt = txt + " coact:{:4.8f}"
                        comment0 = txt.format(err, varmse, coactpenality, coact)
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
                    print()
        
                if procName != "GEP":  # to present the single behav data in a tab
                    # gooddata_behav.append([minErr, minMse, minCoactP,
                    #                        simSubNb, simulNb])
                    if newminfound:
                        data_behav.append([minErr, minMse, minCoactP,
                                           minsimSubNb, minsimulNb])

                # ================   saves charts & asim to tmpBestChart   ============
                savesChartAndAsimToTmpBestChart(data_behav, deb, preTot, pre,
                                                dstdir, folders, model, optSet)
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
                    else:
                        lst_simNb.append(bestGEPsimulNb)
        
                elif procName != "GEP":
                    # we save only the chart with the best mse
                    print("-----------------------------------")
                    behav = [minErr, minMse, minCoactP, minsimSubNb, minsimulNb]
                    saves_chart_asim_aproj(behav)
                    print("-----------------------------------")
                lst_err.append(bestGEPerr)
            if procName == "VSCD":
                # savechart is set to 0, we need only the minsimulNb and minErr
                lst_simNb = minsimulNb
                lst_err = [minErr]
            mse_coact = np.array(tab_mse)
            return [mse_coact, simSetGlob, lst_err, tabBehavElts,
                    lst_tab, lst_simNb]
