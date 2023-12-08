# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 12:35:22 2020 (N Rault) from d.cattaert script.
defines the procedures used in rGEP process in GEP_GUI
Translated in Python 3.8 Jan 2023 (D. Cattaert)
Modified February 22, 2023 (D. Cattaert):
    all pg.Qt.QtGui replaced by pg.Qt.QtWidgets
"""

import os
import numpy as np
from scipy.signal import argrelmin

from pyqtgraph.Qt import QtWidgets

import class_search_algorithm

from optimization import findClosestPair_behav
from optimization import ecrit_tab_int
from optimization import findNewParamSerie
from optimization import findClosestPair_mse
from optimization import findClosestPair_varmse
from optimization import set_limits
from optimization import mise_a_jour
from optimization import cleanChartsFromResultDir
from optimization import cleanAsimsFromResultDir
# from optimization import runTrials

# TODO : continuer l'implementation du GEP


class gep(class_search_algorithm.search_algo):
    def __init__(win, opt_set):
        None


def aim_behav_extend(win, df_bhv_selected, opt_set):
    """
    Searches to extend the borders of the density map of df_bhv_selected
    """
    behavs_cues = df_bhv_selected[df_bhv_selected.columns[win.behav_col]]
    rel_behavs_cues = behavs_cues/[win.scale_x, win.scale_y]
    step = 0.06
    density_map, listx, listy = win.makeDensityMap(rel_behavs_cues,
                                                   step=step)
    # self.plot_map_behav(df_bhv_selected)
    ecrit_tab_int(density_map, startseq=0, all=1, col_width=4)

    border_inf_x = -np.ones(len(listy))
    border_sup_x = -np.ones(len(listy))
    for y_idx in range(len(listy)):
        print(y_idx, "\t", end=' ')
        for x_idx in range(len(listx)):
            if x_idx < len(listx) - 1:
                valx = density_map[y_idx][x_idx]
                val_nextx = density_map[y_idx][x_idx+1]
                if valx == 0 and val_nextx != 0:
                    #  if border_inf_X[x_idx] == -1:
                    border_inf_x[y_idx] = int(x_idx)
                    print("O", end=' ')
                elif valx != 0 and val_nextx == 0:
                    border_sup_x[y_idx] = int(x_idx)
                    print("X", end=' ')
                else:
                    print("-", end=' ')
        print()
    border_inf_y = -np.ones(len(listx))
    border_sup_y = -np.ones(len(listx))
    for x_idx in range(len(listx)):
        print(x_idx, "\t", end=' ')
        for y_idx in range(len(listy)-1):
            valy = density_map[y_idx][x_idx]
            val_nexty = density_map[y_idx+1][x_idx]
            if valy == 0 and val_nexty != 0:
                # if border_inf_Y[y_idx] == -1:
                border_inf_y[x_idx] = int(y_idx)
                print("O", end=' ')
            elif valy != 0 and val_nexty == 0:
                border_sup_y[x_idx] = int(y_idx+1)
                print("X", end=' ')
            else:
                print("-", end=' ')
        print()

    for y_rg, x_rg in enumerate(border_sup_y):
        if x_rg > 0:
            x = int(x_rg)
            y = int(y_rg)
            print(y_rg, border_sup_y[y_rg], x, y, end=' ')
            print(density_map[x][y])

    aim_list = []
    for y_rg, x_rg in enumerate(border_inf_x):
        if x_rg > -1:
            aim_x = win.scale_x*(listx[int(x_rg)])
            aim_y = win.scale_y*listy[int(y_rg)]+step/2
            aim_list.append([aim_x, aim_y])
    for y_rg, x_rg in enumerate(border_sup_x):
        if x_rg > -1:
            aim_x = win.scale_x*(listx[int(x_rg)]+step*2)
            aim_y = win.scale_y*listy[int(y_rg)]
            aim_list.append([aim_x, aim_y])
    for x_rg, y_rg in enumerate(border_inf_y):
        if y_rg > -1:
            aim_x = win.scale_x*(listx[int(x_rg)]+step/2)
            aim_y = win.scale_y*listy[int(y_rg)]
            aim_list.append([aim_x, aim_y])
    for x_rg, y_rg in enumerate(border_sup_y):
        if y_rg > -1:
            aim_x = win.scale_x*(listx[int(x_rg)]+step/2)
            aim_y = win.scale_y*listy[int(y_rg)]+step
            aim_list.append([aim_x, aim_y])
    win.plot_2D_density_map(df_bhv_selected, step=step, aimbhv=aim_list)
    win.plot_map_behav(df_bhv_selected, aimbhv=aim_list)

    if aim_list:
        win.lst_GEPextend_aims.append(aim_list)
        # ###############################################################
        win.exec_gep_rand(opt_set, aim_list=aim_list, typ_gep="extend",
                          df_bhv_selected=df_bhv_selected)
        # ###############################################################
        df_bhvremain = win.update_df_bhvremain(mseThr=1.0)
        if not df_bhvremain.empty:
            win.plot_3D_density_map(df_bhvremain, step=0.02,
                                    incline=60, rot=-80)


def aim_behav_fill(win, df_bhv_selected, opt_set):
    """
    Searches to fill empty areas in the density map of df_bhv_selected
    """
    behavs_cues = df_bhv_selected[df_bhv_selected.columns[win.behav_col]]
    rel_behavs_cues = behavs_cues/[win.scale_x, win.scale_y]
    step = 0.04
    density_map, listx, listy = win.makeDensityMap(rel_behavs_cues,
                                                   step=step)
    # self.plot_map_behav(df_bhv_selected)
    ecrit_tab_int(density_map, startseq=0, all=1, col_width=4)
    min_list = []
    print("\t", end=' ')
    for i in range(len(density_map[0])):
        print("{:3d}".format(i), end=' ')
    print("\t  positions \tvalues    \tranks \t          accepted")
    print
    for y_idx in range(len(density_map)-1):
        a = np.array(density_map[y_idx])
        print(y_idx, "\t", end=' ')
        for val in a:
            print("{:3d}".format(val), end=' ')
        print("\t-->", end=' ')
        list_tmp = argrelmin(a)[0]
        print(list_tmp, "\t", end=' ')
        if not list_tmp.any():
            print("\t", end=' ')
        min_values = a[list_tmp]
        print(min_values, "\t", end=' ')
        if len(min_values) < 3:
            print("\t", end=' ')
        ranks = np.argsort(min_values)  # list of ranks
        # ranks = ranks * min_values
        print(ranks, "\t", end=' ')
        if len(ranks) < 3:
            print("\t", end=' ')
        pos_min = [i for i in range(len(ranks)) if min_values[i] < 3]
        x_rank = list_tmp[pos_min]
        print(x_rank, "\t", end=' ')
        for x_idx in x_rank:
            print(x_idx, end=' ')
            min_list.append([win.scale_x*(listx[int(x_idx)]+step/2),
                             win.scale_y*listy[int(y_idx)]+step/2])
        print()
    min_list
    win.plot_2D_density_map(df_bhv_selected, step=step, aimbhv=min_list)
    win.plot_map_behav(df_bhv_selected, aimbhv=min_list)

    if min_list:
        win.lst_GEPfill_mins.append(min_list)
        # ###############################################################
        win.exec_gep_rand(opt_set, aim_list=min_list, typ_gep="fill",
                          df_bhv_selected=df_bhv_selected)
        # ###############################################################
        df_bhvremain = win.update_df_bhvremain(mseThr=1.0)
        if not df_bhvremain.empty:
            win.plot_3D_density_map(df_bhvremain, step=step,
                                    incline=60, rot=-60)


def find_aim_behav(win, opt_set):

    """
    Procedure find_aim_behav:
        In :
    """
    print("looking for aimBehav, ", end=' ')
    df_bhvremain = win.update_df_bhvremain(mseThr=1.0)
    print(len(df_bhvremain), "behavs in df_bhvremain")
    if not df_bhvremain.empty:
        for extend_nb in range(win.nbGEPextend):
            print("extend N°", extend_nb, "/ last = ", win.nbGEPextend-1)
            win.extend_nb = extend_nb
            aim_behav_extend(win, df_bhvremain, opt_set)
            df_bhvremain = win.update_df_bhvremain(mseThr=1.0)
            win.test_for_save_map_bhv(df_bhvremain, affich=1)
            print("Fin extend N°", extend_nb)
            print

    else:
        df_bhv_selected = win.find_df_bvh_2ndChoice()
        if df_bhv_selected.empty:
            for extend_nb in range(win.nbGEPextend):
                win.extend_nb = extend_nb
                aim_behav_extend(win, df_bhv_selected, opt_set)
                df_bhvremain = win.update_df_bhvremain(mseThr=1.0)
                win.test_for_save_map_bhv(df_bhvremain, affich=1)
                if not df_bhvremain.empty:
                    df_bhv_selected = df_bhvremain
                else:
                    df_bhv_selected = win.find_df_bvh_2ndChoice()

    df_bhvremain = win.update_df_bhvremain(mseThr=1.0)
    if not df_bhvremain.empty:
        for fill_nb in range(win.nbGEPfill):
            win.fill_nb = fill_nb
            aim_behav_fill(win, df_bhvremain, opt_set)
            df_bhvremain = win.update_df_bhvremain(mseThr=1.0)
            win.test_for_save_map_bhv(df_bhvremain, affich=1)
    else:
        df_bhv_selected = win.find_df_bvh_2ndChoice()
        if not df_bhv_selected.empty:
            for fill_nb in range(win.nbGEPfill):
                win.fill_nb = fill_nb
                aim_behav_fill(win, df_bhv_selected, opt_set)
                df_bhvremain = win.update_df_bhvremain(mseThr=1.0)
                win.test_for_save_map_bhv(df_bhvremain, affich=1)
                if not df_bhvremain.empty:
                    df_bhv_selected = df_bhvremain
                else:
                    df_bhv_selected = win.find_df_bvh_2ndChoice()


def exec_gep_rand(win, opt_set, aim_list=[], typ_gep="", df_bhv_selected=None):
    """
    Runs n behav trials and add the data(param, behaviour) to optSet.pairs
    Each behav trial looks for the closest behav in the list and
    proposes a new behav in its vicinity
    For each run, the chart is saved in a temporary directory.
    When the n runs are done, the best result chart is saved in "GEP_Chart"
    under an incremented name.
    """
    win.err = []
    win.tabBehavElts = []
#       span = float(self.valueLine4.text())
#       optSet.spanStim, optSet.spanSyn = span, span
    opt_set.xCoactPenality1 = float(win.valueCoactPen.text())
    nb_neighbours = int(win.valueLine2a.text())
    # sigma = float(self.valueLine2b.text())
    # sigma_span = sigma * span / 200
    # print("sigma=", sigma, "sigma_span", sigma_span)
    startseq_bhv_x = float(win.aimBhvValueX.text())  # reads X startseq behav
    startseq_bhv_y = float(win.aimBhvValueY.text())  # reads Y startseq behav
    startseq = 0   # line to startseq from in the GEPdataxxbhv.txt list
    run_type = "GEPrand"

    if aim_list:
        lst_closest_bhv = []
        lst_closest_par = []
        for aim_bhv in aim_list:
            (closest_behav, closest_dist, pairs_rg,
             order_series) = findClosestPair_behav(win, aim_bhv,
                                                   df_bhv_selected,
                                                   startseq, win.behav_col,
                                                   win.mseThr, opt_set)
            closest_param_set = opt_set.pairs[pairs_rg][0:len(opt_set.x0)]
            paramserie = closest_param_set
            lst_closest_bhv.append(closest_behav)
            lst_closest_par.append(paramserie)

        bhv_aim = np.array(aim_list)
        win.bhvPlot.plot_item.plot(bhv_aim[:, 0], bhv_aim[:, 1],
                                   pen=None, symbol='+',
                                   markersize=25, symbolBrush='b')
        behav_obj = np.array(lst_closest_bhv)
        win.bhvPlot.plot_item.plot(behav_obj[:, 0], behav_obj[:, 1],
                                   pen=None,
                                   symbol='+', markersize=40,
                                   symbolBrush='g')
        # =============================================================
        QtWidgets.QApplication.processEvents()
        # =============================================================
        lst_closest_par = np.array(lst_closest_par)
        win.valueLine1a.setText(str(len(lst_closest_par)))
        win.valueLine1b.setText(str(len(lst_closest_par)))
# ############################################################################
        exec_rand_param(win, run_type, opt_set, lst_parset=lst_closest_par,
                        typGEP=typ_gep)
# ############################################################################

    elif win.GEPauto == 0:
        win.behav_col = [3, 8]  # 3 is "endangle"; 8 is "dur_mvt2"
        win.behav_aim[0] = startseq_bhv_x
        win.behav_aim[1] = startseq_bhv_y
        bhv_aim = np.array(win.behav_aim).reshape(1, 2)
        win.bhvPlot.plot_item.plot(bhv_aim[:, 0], bhv_aim[:, 1],
                                   pen=None, symbol='+',
                                   markersize=25, symbolBrush='b')
        # for idx in range(nbRunBehav):
        df_bhv_selected = win.update_df_bhvremain(mseThr=1.0)
        if not df_bhv_selected.empty:
            (closest_behav, closest_dist, pairs_rg,
             order_series) = findClosestPair_behav(win, win.behav_aim,
                                                   df_bhv_selected,
                                                   startseq,
                                                   win.behav_col,
                                                   win.mseThr, opt_set)
            if closest_behav is not None:
                # behav_obj = findRandObjective(closestDist,
                #                               closest_behav, span)
                behav_obj = np.array(closest_behav).reshape(1, 2)
                print('rg=', pairs_rg, win.behav_aim, '->', behav_obj)
                win.bhvPlot.plot_item.plot(behav_obj[:, 0],
                                           behav_obj[:, 1],
                                           pen=None,
                                           symbol='+', markersize=40,
                                           symbolBrush='b')
                # =====================================================
                QtWidgets.QApplication.processEvents()
                # =====================================================
                affich = 0
                # sigma_span = 0 to eliminate noise on paramserie
                paramserie = findNewParamSerie(behav_obj, nb_neighbours,
                                               pairs_rg, order_series,
                                               0, len(opt_set.x0), affich,
                                               opt_set)
                parx = win.parx
                pary = win.pary
                win.parplt_itm.plot(paramserie[:, parx],
                                    paramserie[:, pary],
                                    pen=3, symbol='o', symbolBrush=5)
                pairs_rg = order_series.index[0]
                closest_param_set = opt_set.pairs[pairs_rg]
                paramserie = closest_param_set
                print(paramserie)
                win.startseqSet = paramserie[0:win.nbpar]
                # self.prefix = ""
# #############################################################################
                exec_rand_param(win, run_type, opt_set)
# #############################################################################
                df_bhvremain = win.update_df_bhvremain(mseThr=1.0)
                if not df_bhvremain.empty:
                    win.test_for_save_map_bhv(df_bhvremain, affich=1)
                win.startseqSet = []
                win.startseqEval = 0
                # self.prefix = ""
        else:
            print()
            print("######################################################")
            print(" No behavior data in memory !! --> look for best vmse")
            print("######################################################")


"""
def exec_rand_param(win, runType, optSet, lst_parset=[], typGEP=""):

    Runs nbRunParam random params generated around optSet.x0
    with a width of span/100 and add the data(param, behaviour)
    to optSet.pairs


    procName = ""
    parx = win.parx
    pary = win.pary
    bestparamList = []
    bestchartList = []
    besterrList = []
    win.err = []
    win.tabBehavElts = []
    # span = float(self.valueLine4.text())
    # optSet.spanStim, optSet.spanSyn = span, span
    optSet.xCoactPenality1 = float(win.valueLine4c.text())
    datastructure = optSet.datastructure  # dictionary for data structure
    if len(datastructure) > 0:
        structNb = len(datastructure)
        lastinfo = datastructure[structNb-1]
        lastrun = lastinfo[2]
    else:
        structNb = 0
        lastrun = 0

    win.packetRand = int(win.valueLine1a.text())
    if win.packetRand <= 0:
        win.packetRand = 1
    nbRandTrial = int(win.valueLine1b.text())
    win.nbRandTrial = nbRandTrial

    org = win.getNbPacket(win.packetRand, nbRandTrial)
    nbEpochParam, nbRunParam, paramserieSlicesAllEpochs = org
    for epoch in range(nbEpochParam):
        lst_span = np.zeros((nbRunParam[epoch], len(optSet.x0)))
        win.previousstartseqEval = len(optSet.pairs)
        listpairs = []
        randpar = np.random.random_sample((nbRunParam[epoch],
                                           len(optSet.x0)))
        randpar = (randpar - 0.5) * 2     # paramserie in range (-1, 1)
        # recalculate paramserie centered on x0, width = span
        if len(win.listDicSpanVal) > 0:
            for i in range(len(randpar)):
                for idx, span in enumerate(win.xparName):
                    print randpar[i][idx], '\t',
                    print(win.listDicSpanVal[0][span], '\t', end=" ")
                    randpar[i][idx] = randpar[i][idx] *\
                        float(win.listDicSpanVal[0][span])/200
                    lst_span[i][idx] = float(win.listDicSpanVal[0][span])
                    print(randpar[i][idx])
        else:
            randpar = randpar * span / 200
        if runType == "rdparam":
            if win.randParEvol == "MSE":
                procName = "MSE"
                res = findClosestPair_mse([0, 0], win.startseqEval, optSet)
                closestMseCoact = res[0]
                closestDist = res[1]
                pairs_rg = res[2]

            elif win.randParEvol == "varmse":
                procName = "GEP"
                res = findClosestPair_varmse(win.startseqEval, optSet)
                closestMseCoact = res[0]
                closestDist = res[1]
                pairs_rg = res[2]
                bestvarmse = res[3]

            else:
                procName = "GEP"
                closestDist = -1

            win.procName = procName
            if closestDist > 0:
                pointMSECoact = np.array(closestMseCoact)
                plotMSECoact = pointMSECoact.reshape(1, 2)
                win.mseplt_itm.plot(plotMSECoact[:, 0],
                                    plotMSECoact[:, 1], pen=None,
                                    symbol='o',
                                    symbolBrush=win.mvtcolor)
                if win.randParEvol == "varmse":
                    print("best varmse: {} at rg={}\
                          [MSE,Coact]: {}".format(bestvarmse, pairs_rg,
                                                  plotMSECoact))
                elif win.randParEvol == "MSE":
                    print("best MSE: {} at rg={}\
                          [MSE,Coact]: {}".format(closestMseCoact[0],
                                                  pairs_rg,
                                                  plotMSECoact))

                params = optSet.pairs[:, 0:win.nbpar]
                paramset = params[pairs_rg]
                pointParam = np.array(paramset)
                plotParam = pointParam.reshape(1, win.nbpar)
                win.parplt_itm.plot(plotParam[:, parx],
                                    plotParam[:, pary], pen=None,
                                    symbol='o',
                                    symbolBrush=win.mvtcolor)
                text = "best param: {:2.4f}   {:2.4f}"
                print(text.format(plotParam[0][parx], plotParam[0][pary]))

            else:   # If not GEP script_mode then random set of parameters
                paramset = optSet.x0

        elif runType == "GEPrand":
            procName = "GEP"
            if len(lst_parset) > 0:
                paramset = lst_parset  # the sets of aims around behavs
            else:
                paramset = win.startseqSet

        elif runType == "systRand":
            paramset = win.startseqSet
        # nb= paramset is the set of parametesr we sart from to get random
        # parameters (with noise in the range "span"/2 around paramset)

        # ------------------------------------------------
        #             if some constant parameters...
        # ------------------------------------------------
        if len(win.dicConstParam) > 0:
            list_par = []
            tmptab = []
            if runType == "GEPrand":
                if len(lst_parset) > 0:
                    for parset in lst_parset:
                        tmptab = []
                        for idx, name in enumerate(win.xparName):
                            if name not in win.listConstantNames:
                                tmptab.append(parset[idx])
                            else:
                                tmptab.append(win.dicConstParam[name])
                        list_par.append(tmptab)
                    paramset = np.array(list_par)
            else:
                for idx, name in enumerate(win.xparName):
                    if name not in win.listConstantNames:
                        tmptab.append(paramset[idx])
                    else:
                        tmptab.append(win.dicConstParam[name])
                paramset = np.array(tmptab)
                # in randpar array, ranks of constants are set to 0
        for idx, name in enumerate(win.listConstantNames):
            constparnb = win.xparNameDict[name]
            if len(lst_parset) > 0:
                paramset[:, constparnb] = win.dicConstParam[name]
            else:
                paramset[constparnb] = win.dicConstParam[name]
            randpar[:, constparnb] = 0
        # ------------------------------------------------

        paramserie = randpar + paramset
        # randset is used to modify parameters that are out of limits
        randset = np.random.random_sample((nbRunParam[epoch],
                                          len(optSet.x0)))
        paramserie = set_limits(paramserie, randset, lst_span, 0, 1,
                                optSet, stim_liminf=False,
                                stim_limsup=False, syn_liminf=True,
                                syn_limsup=False)

        if typGEP == "extend":
            print(typGEP, win.extend_nb, "/ last = ", win.nbGEPextend-1)
        elif typGEP == "fill":
            print(typGEP, win.fill_nb, "/ last = ", win.nbGEPfill - 1)
        if runType == "rdparam":
            print("epoch =", epoch, "/ last =", nbEpochParam - 1)
        win.parplt_itm.plot(paramserie[:, parx], paramserie[:, pary],
                            pen=3, symbol='o', symbolBrush=2)
        # in MainWindow, we plot only the two first parameters
        win.plotOtherParam(paramserie, pen=3, symbol='o', symbolBrush=2)
        # -----------------------------------
        QtWidgets.QApplication.processEvents()
        # -----------------------------------
        paramserieSlices = paramserieSlicesAllEpochs[epoch]
        # ###############################################################
        # if procName == "GEP":
        #    result = runGEP(self, paramserie, paramserieSlices)
        # else:
        result = runTrials(win, paramserie, paramserieSlices, savechart=1,
                           procName=procName, runType=runType,
                           randParEvol=win.randParEvol)
        # ###############################################################
        mse_coact = result[0]
        lst_err = result[2]
        tabBehavElts = result[3]  # list of behaviour variables sets

        win.mseplt_itm.plot(mse_coact[:, 0], mse_coact[:, 1], pen=None,
                            symbol='o', symbolBrush=2)
        # -----------------------------------
        QtWidgets.QApplication.processEvents()
        # -----------------------------------

        for idx in range(nbRunParam[epoch]):
            pair_param_mseCoact = np.concatenate([paramserie[idx],
                                                  mse_coact[idx]])
            behav = tabBehavElts[idx]
            # print idx, behav
            win.add_pair(pair_param_mseCoact, behav)
            listpairs.append(pair_param_mseCoact)
        df_bhvremain = win.update_df_bhvremain(mseThr=1.0)
        win.test_for_save_map_bhv(df_bhvremain, affich=1)

# ====    creates a dataframe from tabBehavElts   ======
"""
# ["mse", "coactpen", "startseqangle", "endangle", "oscil1",
#  "oscil2", "speed_mvt2", "end_mvt2", "duree", "varmse"]
"""
        nptabBehavElts = np.array(tabBehavElts)
        np_pairs = np.array(listpairs)
        win.plotBhvSet(nptabBehavElts, np_pairs, 0, nbRunParam[epoch])
        for err in lst_err:
            win.err.append(err)
        win.tabBehavElts.append(tabBehavElts)

        for bestchart in win.lst_bestchart:
            win.plotmvt(bestchart)
        # -----------------------------------
        QtWidgets.QApplication.processEvents()
        # -----------------------------------
        for idx, chartName in enumerate(win.lst_chartName):
            bestchartList.append(chartName)
            besterrList.append(win.err[idx])
            bestparamList.append(win.lst_bestParNb[idx])
        win.startseqEval = win.previousstartseqEval
        # saveBestpairtoAproj(self, optSet, "")

    print("===================================================")
    print("    End of", nbRandTrial, runType, "parameter runs")
    print("===================================================")
    packetsize = win.packetRand
    mise_a_jour(optSet, datastructure, structNb,
                runType + "_" + win.randParEvol,
                lastrun+1, lastrun + nbRandTrial, packetsize,
                [optSet.spanStim, optSet.spanSyn,
                 optSet.xCoactPenality1,
                 besterrList, bestchartList, bestparamList])
    if len(paramserie) > 9:
        pre = "0"
    else:
        pre = ""

    cleanChartsFromResultDir(optSet, 1, len(paramserie), pre)
    subdir = os.path.join("ResultFiles", "tmpBestChart")
    cleanChartsFromResultDir(optSet, 1, len(paramserie), pre,
                             directory=subdir)
    cleanAsimsFromResultDir(optSet, 1, len(paramserie), pre,
                            directory=subdir)
    win.startseqSerie = lastrun
    print("self.startseqSerie: ", win.startseqSerie)
    win.save_pairs(runType)
    """

