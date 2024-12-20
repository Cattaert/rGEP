# -*- coding: utf-8 -*-
"""
GEP_GUI is a scrtipt that opens a GUI for GEP optimization on AnimatLab
parameters. It works with previous animatLab optimization CMAES procedures
Created on Tue Feb 27 11:05:28 2018 (D. Cattaert)
translated in Python 3.8 Jan 2023
@author: cattaert
Modified January 16, 2023 (D.Cattaert):
    choose_seeds() method modfied to allow selection of seeds with various
    varmse. Instead of retaining only the first mse condition, all of them are
    concatened:
        {'mse_threshold1': 1.0, 'mse_threshold2': 1.5, 'mse_threshold3': 2.0}
        list_mse = ['mse_threshold1', 'mse_threshold2', 'mse_threshold3']
        df_bhvremain = pd.concat(listdf_bhv)
    and sorted in right order:
        df_bhvremain.sort_values(by=['rgserie'], inplace=True)
    search_list_spanValues() method is not launched (because woudl not work
        with varmse>1)
    in saves_seeds() method, GEPdata00bhv.txt is modified so that
        varmse --> 0.000 to allow their selection in randGEP process
Modified January 23, 2023 (D. Cattaert):
    get_seeds method improved:
        in saves_seeds(), the newSeed_folder is copied into the root directory
        as 0_IDXXX_seedsXX directory name, by calling a new procedure:
            copyTo_0_idXXX_Seeds0x. The seeds_origin.txt file is automatcally
            created.
Modified February 3, 2023 (D. Cattaert):
    Modifications in accordance to modifications in MakeGraphs.py, in order to
    select/build dataframes from several folders, and select a range of
    amplitude and maxspeed from bhv window to run the corresponding parameters
    sets. In partucular saves_seeds() method was modified: it is called with
    a parameter (seedDirCreate=True when called from get_seeds(); and
                 seedDirCreate=False when called from makeGraphs.py with the
                 method run_selected_bhv())
Modidied February 6, 2023 (D. Cattaert):
    Prodecures adapted for spanlist from file.
Modifier February 17, 2023 (D. Cattaert):
    Call to GUI_AnimatLabOptmization.py) replace by "GUI_AnimatLabPar.py"
    New method "save_neuron_properties()" called at the end of the main
Modified February 20, 2023 (D. Cattaert):
    Color of command buttons are now blue (inactive) or red (actve)
    Modifications made also in class_UiMainWindow, accordingly
Modified February 22, 2023 (D. Cattaert):
    all pg.Qt.QtGui replaced by pg.Qt.QtWidgets
Modified February 24, 2023 (D. Cattaert):
    Before launching GEP_GUI, the collectInterval of charts is checked in
    initAnimatLab(). If not '0.01' then a warning is given to the user and
    changes to be made are indicated.
Modified April 03, 2023 (D. Cattaert):
    Method choose_seeds() improved in case no valid behav exists
Modified April 20, 2023 (D.Cattaert):
    If exists, self.listDicSpanVal is red from DicSpanVal.txt in GEPdata folder
    when we unactivate Use global span (%) in the GUI.
Modified May 11, 2023 (D. Cttaert):
    saves_seeds() method don't place spanList in the datastructure. Instead, it
    writes ["DicSpanVal.txt"]. Optimization's procedures have been changed
    accordingly.
Modified May 12, 2023 (D. Cattaert):
    set_span() method: bug found and fixed:
        optSet.x0 was filed with span values. This was an error, now fixed.
Modified Mai 16, 2023 (D. Cattaert):
    Modification of bhvplot window setYRange -> 0-500 (for MaxSpeed)
Modified June 22, 2023 (D. Cattaert):
    in search_list_spanValues() method, new lines added to ask the user if 
    searh is needed or not:
        titre = "Search list_spanValues"
        info = "Do you want to launch search?"
        rep = dialogWindow(titre, info, details="")
Modified June 22, 2023 (D. Cattaert):
    checkChartComment() method modified to avoid an empty line to added after
    the title when the old Chart number length is larger than the new one
    for example when Chart03.txt replaces chart123.txt
Modified September 15, 2023 (D. Cattaert):
    Method search_list_spanValues() modified so that if no valid behav in seeds
    get_good_span_list() is not launched (an even no querry about it).
modified October 02, 2023 (D. Cattaert):
    In method search_list_spanValues() bug fixed when no valid behavior exists
modified October 13, 2023 (D. Cattaert):
    A new Possibility added to create charts regularly distributed over the
    valid behaviors. The new method (build_charts()) uses the same methods as
    get_seeds() method:
        run_selected_param()
        saves_newGEPdata()
    The names of these methods have been changed to be more general.
        search_list_spanValues() hase alos been modified for compatibility with
        the new methods for charts:
            build_charts() that give info on the process and launches it if OK
            launch_CreateNewCharts() that run the process.
    Dialog procedures have been grouped in DialogChoose_in_List.py script
        Accordingly buildControlScript.py, makeGraphs.py and class_UiMainWindow
        have also been modified.
"""

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets

import os
import pickle
import numpy as np
import pandas as pd
import copy
import matplotlib.pyplot as plt
import matplotlib as mpl
# mpl.use('TkAgg')
# import seaborn as sns

import class_animatLabModel as AnimatLabModel
import class_animatLabSimulationRunner as AnimatLabSimRunner
import class_simulationSet as SimulationSet
import class_projectManager as ProjectManager

from FoldersArm import FolderOrg
from animatlabOptimSetting import OptimizeSimSettings
# from GUI_AnimatLabOptimization import GetList

from optimization import setPlaybackControlMode
from optimization import setGravity
from optimization import readGravityfromAsim
from optimization import affichMotor
from optimization import affichNeurons, affichNeuronsFR
from optimization import affichExtStim
from optimization import normToRealVal
from optimization import affichConnexions, affichConnexionsFR
from optimization import writeTitres
from optimization import findTxtFileName
from optimization import testquality
from optimization import setMotorStimsOff
from optimization import copyFile
from optimization import copyFileWithExt
from optimization import copyFileDir
from optimization import copyFileDir_ext
from optimization import copyDirectory
from optimization import erase_folder_content
from optimization import cleanChartsFromResultDir
from optimization import cleanAsimsFromResultDir
from optimization import readTablo
from optimization import readTabloTxt
from optimization import savechartfile
from optimization import getbehavElts
# from optimization import ecritpairs
from optimization import ecrit_tab
# from optimization import ecrit_tabStr
from optimization import listNamesToComment
# from optimization import extractCol
from optimization import copyRenameFilewithExt
from optimization import mise_a_jour
from optimization import save_datastructure
from optimization import load_datastructure
from optimization import get_brushes_from_gist
from optimization import set_limits
from optimization import string
from optimization import getGEPdataFileName
from optimization import findClosestPair_mse
from optimization import findClosestPair_varmse
from optimization import saveBestFit_to_AsimAproj
from optimization import savesChartAndAsimToTmpBestChart
from optimization import getBestResults
from optimization import findClosestPair_behav
from optimization import findNewParamSerie
from optimization import getValuesFromText
from optimization import readCoacPenality
from optimization import readGravity
from optimization import readSpan
from optimization import readSpan_from_DicSpanVal
from optimization import extract_err
from optimization import save_listDicSpanVal

from VSCD_tool_box import exec_VSCD_from_gui

# from gep_tool_box import exec_gep_rand
from gep_tool_box import find_aim_behav

from cmaes_tool_box import exec_CMAeFromGUI

from optimization import checknonzeroExtStimuli
from optimization import checknonzeroSyn
from optimization import checknonzeroSynFR
from optimization import loadParams
from optimization import readAnimatLabDir
from optimization import get_good_span_list
# from optimization import chartToDataFrame

from GUI_AnimatPar import saveAnimatLabSimDir

from optimization import getInfoComputer
from SaveInfoComputer import SetComputerInfo

from optimization import runTrials

from makeGraphs import graphfromchart

# from makeGraphs import GUI_Graph

from DialogChoose_in_List import ChooseInList
from DialogChoose_in_List import choose_one_element_in_list
from DialogChoose_in_List import MyMessageBox
from DialogChoose_in_List import showdialog
from DialogChoose_in_List import dialogWindow
from DialogChoose_in_List import InfoWindow
from DialogChoose_in_List import Enter_Values
from DialogChoose_in_List import DialogBoxValues

import mvt_GUI
import bhv_GUI
import param_GUI
import class_UiMainWindow
global verbose
verbose = 1

pg.setConfigOption('background', 'w')


class MaFenetre(class_UiMainWindow.Ui_MainWindow):
    def __init__(self, aprojFName, opSet):
        super(MaFenetre, self).__init__()
        self.setupUi()  # le 2eme self est pour l'argument MainWindow
        #                     qui est la fenetre elle-meme -> donc self
        global folders, model, projMan, aprojFicName, optSet
        optSet = opSet
        self.optSet = optSet
        folders = optSet.folders
        model = optSet.model
        # sims = sim
        projMan = optSet.projMan
        aprojFicName = aprojFName

        self.to_init()
        self.show()

    def location_on_the_screen(self, xshift=0, yshift=0):
        ag = QtWidgets.QDesktopWidget().availableGeometry()
        # sg = QtWidgets.QDesktopWidget().screenGeometry()

        widget = self.geometry()
        x = ag.width() - widget.width() - xshift
        # y = 2 * ag.height() - sg.height() - widget.height()
        y = ag.height() - widget.height() - yshift
        self.move(x, y)

    def to_init(self):
        # self.behav_col = [3, 8]  # 3 is "endangle"; 8 is "dur_mvt2"
        self.behav_col = [3, 6]  # 3 is "endangle"; 6 is "max_speed"

        self.bg.buttonClicked[QtWidgets.QAbstractButton].connect(self.btngroup)
        self.btn_systParam.clicked.connect(self.do_syst_param)

        self.b_bhv.buttonClicked.connect(self.bhv_choix)

        self.chk_MSE.stateChanged.connect(self.btnstate_MSE)
        self.chk_varmse.stateChanged.connect(self.btnstate_varmse)
        # self.bg2.buttonClicked[QtWidgets.QAbstractButton].connect(self.btngroup2)

        self.btn_randParam.clicked.connect(self.do_rand_param)
        self.btn_GEPrand.clicked.connect(self.do_GEP_rand)
        self.chkBx_autoGEP.stateChanged.connect(self.auto_aim_GEP)
        self.btn_getfile.clicked.connect(self.load_pairs)
        self.btn_getseeds.clicked.connect(self.get_seeds)
        self.btn_addcharts.clicked.connect(self.build_charts)
        """
        self.btn_mkpdf.clicked.connect(self.make_save_eps)
        """
        # self.btn_set_span.clicked.connect(self.set_span)
        self.btn_CMAes.clicked.connect(self.runCMAeFromGUI)
        self.btn_VSCD.clicked.connect(self.runVSCDFromGUI)
        self.chkBx_saveAllMvts.stateChanged.connect(self.btnstate_saveAllMvts)
        self.chkBx_glob_span.stateChanged.connect(self.span_setup)

        self.chkBox_const.stateChanged.connect(self.checkButtonConstants)
        # self.btn_fixParam.clicked.connect(self.setConstantParams)
        self.btn_clear_pw_param.clicked.connect(self.clearParam)
        self.btn_scaleTot_pw_param.clicked.connect(self.totalRange)
        self.btn_choose_pw_param.clicked.connect(self.chooseParam)
        self.btn_clear_pw_behav.clicked.connect(self.clearMseCoact)
        self.btn_getinfo_chart.clicked.connect(calculate_coact_from_chart)

        self.btn_Reset.clicked.connect(self.reset)
        self.btn_show_allgraphs.clicked.connect(self.showAllParGraphs)
        # self.btn_addROI.clicked.connect(lambda: self.addROI(pargr=-1))
        self.btn_quit.clicked.connect(self.closeWindows)

        self.initialiseParam()
        self.parplt_itm.setLabel('left', self.xparName[self.pary], units='',
                                 color='black', size='12pt')
        self.parplt_itm.setLabel('bottom', self.xparName[self.parx], units='',
                                 color='black', size='12pt')
        for par in range(int(self.nbpar/2)):
            self.pargraph.append((par * 2, par * 2 + 1))
        if int(self.nbpar % 2) != 0:
            par += 1
            self.pargraph.append((par*2, 0))

        # ===================== movement plot windows ========================
        self.mvtPlot = mvt_GUI.MvtWin()
        self.mvtPlot.pw_mvt.setXRange(0, optSet.endEQM)
        self.mvtPlot.pw_mvt.setYRange(0, 180)
        self.mvtTemplate = np.array(optSet.mvtTemplate)
        self.mvtPlot.pw_mvt.plot(self.mvtTemplate[:, 1],
                                 self.mvtTemplate[:, 2],
                                 pen='k')
        # self.mvtPlot.btn_erase.clicked.connect(self.clearResetMvts)
        self.mvtPlot.btn_showAll.clicked.connect(self.showAllMvts)
        self.mvtPlot.btn_showNext.clicked.connect(self.showNextMvtSet)
        self.mvtPlot.check_keepSet.stateChanged.connect(self.keepMvtSet)
        self.mvtPlot.check_bestMvt.stateChanged.connect(self.onlyBest)
        self.mvtPlot.check_perPacket.stateChanged.connect(self.perPackt)
        self.mvtPlot.btn_showPrev.clicked.connect(self.showPrevMvtSet)
        self.mvtPlot.btn_showFirst.clicked.connect(self.showFirstMvtSet)
        self.mvtPltOn = 1
        self.mvtcolor = 1
        # ====================================================================

        # ===================== behavior plot windows ========================
        self.bhvPlot = bhv_GUI.BhvWin(self)
        self.behav_label_X = self.bhv_names[self.behav_col[0]]
        self.behav_label_Y = self.bhv_names[self.behav_col[1]]
        self.bhvPlot.plot_item.setLabel('left', self.behav_label_Y,
                                        units='s',
                                        color='black', size='12pt')
        self.bhvPlot.plot_item.setLabel('bottom', self.behav_label_X,
                                        units='degrees',
                                        color='black', size='12pt')
        self.bhvPlot.plot_item.setXRange(0, 120)
        self.bhvPlot.plot_item.setYRange(0, 5.0)
        self.bhvPlot.btn_erase.clicked.connect(self.clearBhv)
        self.bhvPlot.btn_mse_filter.clicked.connect(self.bhv_filterWithMse)
        self.bhvPlot.btn_coactP_filt.clicked.connect(self.bhv_filterWithCoactP)
        self.bhvPlot.btn_cst_filter.clicked.connect(self.bhv_filterWithCst)
        self.bhvPlot.check_select_curs.stateChanged.connect(self.cursorsONOFF)
        self.bhvPlot.btn_selctRegion.clicked.connect(self.show_param_Curs)
        self.bhvPlot.btn_unselect.clicked.connect(self.unselect_clicked)
        self.bhvPlot.btn_showAll.clicked.connect(self.showAllBhvs)
        self.bhvPltOn = 1
        # ====================================================================

    def initialiseParam(self):
        self.bestchart = []
        self.DEFAULT_span_VALUE = 100.0
        self.glob_span = 100.0
        optSet.xCoactPenality1 = float(self.valueCoactPen1.text())
        optSet.xCoactPenality2 = float(self.valueCoactPen2.text())
        optSet.gravity = float(self.editValueGravity.text())
        self.animatsimdir = ""
        self.modelchanged = 0
        self.GEP_rootname = ""
        self.mydir = ""
        self.filename = ""
        self.nbpar = len(optSet.x0)
        self.main_mode = True
        self.nbpargraphs = int(self.nbpar/2) + int(self.nbpar % 2)
        self.nbactivepargraphs = 0
        self.pargraph = []          # list of couples of parameters in graphs
        self.present_graph = 0
        self.screen = []
        self.xparName = []           # name of parameters
        self.xparNameDict = {}
        for stim, name in enumerate(optSet.stimParName):
            self.xparName.append(name)
        for syn, name in enumerate(optSet.synParName):
            self.xparName.append(name)
        for syn, name in enumerate(optSet.synNSParName):
            self.xparName.append(name)
        for syn, name in enumerate(optSet.synFRParName):
            self.xparName.append(name)
        for par in range(self.nbpar):
            self.xparNameDict[self.xparName[par]] = par
        
        self.param_to_graph = []
        self.parx = 0   # default parameter to plot as x
        self.pary = 1   # default parameter to plot as y
        self.selectedParams = []  # parameters selected with ROI in main window
        self.indexROIcolor = 0
        self.listbestparamset = []
        self.bestParamNb = 0
        self.lst_bestchart = []
        self.lst_chartName = []
        self.lst_bestParNb = []
        self.bestchartName = ""
        self.startSet = []  # used in systematic exploration
        self.startEval = 0
        self.previousStartEval = 0
        self.startSerie = 0
        # self.prefix = ""
        self.simNb = 0
        self.minSimNb = 0
        self.minErr = 1000000.0
        self.minMse = 1000000.0
        self.minCoactP = 100000000.0
        self.minchart = []
        self.minchartErr = 1000000.0
        self.procName = ""
        self.formatpairs = 1    # new format pairs includes pair number
        self.mvt_ord_duration = 0
        self.mvt_ord_maxSpeed = 1
        self.systWithRand = 1
        self.systWithCMAE = 0
        self.packetCMA_Size = 1
        self.packetCMA_Nb = 1
        self.packetCMA_Set = []
        self.err = []
        self.deltacoeff = 0.01
        # =================    behav procedures parameters    ================
        self.randParEvol = "MSE"
        self.scrip_mode = "GEP"
        self.bhv_names = ["mse", "coactpen", "startangle", "endangle",
                          "oscil1", "oscil2", "max_speed", "end_mvt2",
                          "dur_mvt2", "varmse"]
        self.tabBehavElts = []
        self.GEPauto = 1
        self.nbGEPextend = 1
        self.nbGEPfill = 1
        self.behav_aim = [80, 0.900]
        if self.behav_col[1] == 8:
            self.scale_x, self.scale_y = 100, 1
        elif self.behav_col[1] == 6:
            self.scale_x, self.scale_y = 100, 100
        self.extend_nb = 0
        self.fill_nb = 0
        self.lst_GEPextend_aims = []
        self.lst_GEPfill_mins = []
        self.listDicItBhvMse = [{'mse_threshold': []}]
        self.list_mse_thr_names = ["mse_threshold1", "mse_threshold2",
                                   "mse_threshold3", "mse_threshold4"]
        self.list_mse_thr_val = [1, 10, 20, 50]
        self.listdicmsethr = [{}]
        for idx, name in enumerate(self.list_mse_thr_names):
            self.listdicmsethr[0][name] = self.list_mse_thr_val[idx]
        self.firstSelectedMseThr = []
        self.dicSelectedMseThr = {}
        self.mseThr = 1.
        self.df_parremain = None
        self.df_bhvremain = None
        self.source_df_parremain = None
        self.source_df_bhvremain = None
        self.plot500 = 0
        self.list_save_steps = [100, 500, 1000, 2000]
        self.cursor_active = 0
        self.lastClicked = []
        self.selected_bhv = []
        self.selectedROI = []

        # ====================================================================
        self.mvtSet = 0    # mvt set to be plotted with "show next Set" button
        self.rgpackt = -1
        self.keepSet = 1
        self.onlyBestInSet = 0
        self.perPacket = 1
        self.nb_procs = 1
        self.nbrunsByPckt = 1
        self.saveAllMvtsVarmse = 0

        # self.lstDicBhvCst_itm = [{'param1': []}]
        self.listParNamesFilter = []
        # self.listDicParamFilter = [{}]
        self.listDicParamFilter = [{"paramFilter": []}]

        self.lstDicBhvCst_itm = [{}]
        self.list_const_items = ['value1', 'value2', 'value3',
                                 'value4', 'value5']
        self.listCstValFilt = [0.010, 0.015, 0.020, 0.025, 0.030]
        self.listdiccstFlt = [{}]
        for idx, name in enumerate(self.list_const_items):
            self.listdiccstFlt[0][name] = self.listCstValFilt[idx]
        self.firstSelectedConstFilt = []
        self.dicSelectedCstFilt = {}

        self.listDicItConst = [{'constant': []}]
        self.listDicParVal = [{}]
        for idx, name in enumerate(self.xparName):
            self.listDicParVal[0][name] = optSet.x0[idx]
        self.listConstantNames = []
        self.dicConstParam = {}
        # resultFilePath = os.path.join(animatsimdir, "ResultFiles")
        resultFilePath = folders.animatlab_result_dir
        listDicGraphsPath = os.path.join(resultFilePath, 'listDicGraphs.pkl')
        if not os.path.exists(listDicGraphsPath):
            None
            self.listDicGraphs = [{"abscissa": [self.xparName[0]],
                                   "ordinate": [self.xparName[1]]}]
            # self.save_listDicGraphs(listDicGraphsPath)
        else:
            self.read_listDicGraphs(listDicGraphsPath)
            self.affect_param_to_graph(self.listDicGraphs)

        self.listDicItspan = [{'span': []}]
        self.listDicSpanVal = [{}]
        for name in self.xparName:
            self.listDicSpanVal[0][name] = 100
        self.listspanNames = []
        self.dicspanParam = {}
        self.listspanVal = [float(self.listDicSpanVal[0][name])
                            for name in [self.xparName][0]]
        self.spanlistfound = False
        self.lst_paramserie = []
        self.listDicSeeds = [{'seed_rank': []}]
        self.rg_bhv_selected = []
        self.varmse_selected = []

        self.mvtTemplate = np.array(optSet.mvtTemplate)
        self.select_paramSer = []
        self.optSet = optSet

    def save_paramNames_bhvNames(self):
        fileparname = "xparnames.txt"
        completeparname = os.path.join(self.mydir, fileparname)
        fparname = open(completeparname, 'w')
        s = ""
        for idx, parname in enumerate(self.xparName[:-1]):
            s += "{}".format(parname) + '\t'
            # s += "{:4.8f}".format(optSet.pairs[idx][idy+1]) + '\t'
        s += self.xparName[-1] + '\n'
        # print s,
        fparname.write(s)
        fparname.close()
    
        filebhvname = "xbhvnames.txt"
        completebhvname = os.path.join(self.mydir, filebhvname)
        fbhvname = open(completebhvname, 'w')
        s = ""
        for idx, bhvname in enumerate(self.bhv_names[:-1]):
            s += "{}".format(bhvname) + '\t'
            # s += "{:4.8f}".format(optSet.pairs[idx][idy+1]) + '\t'
        s += self.bhv_names[-1] + '\n'
        # print s,
        fbhvname.write(s)
        fbhvname.close()

    def save_neuron_properties(self):
        filename = "neuronProperties.txt"
        completefname = os.path.join(self.mydir, filename)
        Neurons = model.getElementByType("Neurons")
        lst_neuron = [neur for neur in Neurons
                      if neur.find("Name").text != 'Disabled']
        lst_neurName = [neur.find("Name").text for neur in lst_neuron]

        # list(lst_neuron[0])

        lst_restPot, lst_size, lst_timeConst = [], [], []
        for neur in lst_neuron:
            lst_restPot.append(neur.find('RestingPot').text)
            lst_size.append(neur.find('Size').text)
            lst_timeConst.append(neur.find('TimeConst').text)
        #  = [int(rest) for rest in lst_restPot]
        
        f = open(completefname, 'w')
        s = "Neuron" +"\t" + "RestingPot" + "\t" + "size" + "\t"\
            + "timeConst" + "\n"
        f.write(s)
        for idx in np.arange(len(lst_neuron)):
            s = ""
            s += "{}\t{}\t{}\t{}".format(lst_neurName[idx],
                                         lst_restPot[idx],
                                         lst_size[idx],
                                         lst_timeConst[idx])
            s += "\n"
            f.write(s)
        f.close()

    # =========================================================================
    """
                           Main window  controls
    """
    # =========================================================================
    def bhv_choix(self, btn):
        print(btn.text() + " is selected")
        if btn.text() == "bhv_ordinate_duration":
            print(btn.text() + " Mvt ordinate defined by duration")
            self.mvt_ord_duration = 1
            self.mvt_ord_maxSpeed = 0
        else:
            print(btn.text() + " Mvt ordinate defined by maxSpeed")
            self.mvt_ord_duration = 0
            self.mvt_ord_maxSpeed = 1
        self.configureforbhvcriteria()

    def configureforbhvcriteria(self):
        if self.mvt_ord_duration == 1:
            self.mvt_ord_maxSpeed = 0
            self.behav_col = [3, 8]  # 3 is "endangle"; 8 is "dur_mvt2"
            self.scale_x, self.scale_y = 100, 1
        else:
            self.mvt_ord_duration = 0
            self.mvt_ord_maxSpeed = 1
            self.behav_col = [3, 6]  # 3 is "endangle"; 6 is "max_speed"
            self.scale_x, self.scale_y = 100, 100
        self.behav_label_X = self.bhv_names[self.behav_col[0]]
        self.behav_label_Y = self.bhv_names[self.behav_col[1]]
        self.bhvPlot.plot_item.setLabel('left', self.behav_label_Y,
                                        units='s',
                                        color='black', size='12pt')
        self.bhvPlot.plot_item.setYRange(0, 500 * self.scale_y / 100)

        self.bhvPlot.plot_item.setLabel('bottom', self.behav_label_X,
                                        units='degrees',
                                        color='black', size='12pt')
        self.bhvPlot.plot_item.setXRange(0, 120)

    def auto_aim_GEP(self, btn):
        print(self.chkBx_autoGEP.checkState(), end=' ')
        if self.chkBx_autoGEP.checkState() > 0:
            print("button checked")
            self.GEPauto = 1
            self.aimBhvValueX.setStyleSheet("color: lightgray;")
            self.aimBhvValueY.setStyleSheet("color: lightgray;")
        else:
            self.GEPauto = 0
            print("button unchecked")
            self.aimBhvValueX.setStyleSheet("color: black;")
            self.aimBhvValueY.setStyleSheet("color: black;")

    def btngroup(self, btn):
        print(btn.text() + " is selected")
        if btn.text() == "Checkbox1":
            print(btn.text() + " Syst will run with RandParam")
            self.systWithRand = 1
            self.systWithCMAE = 0
        else:
            print(btn.text() + " Syst will run with CMAES")
            self.systWithRand = 0
            self.systWithCMAE = 1

    def btnstate_MSE(self):
        if self.chk_MSE.checkState() > 0:
            print("RandParam will evolve with MSE")
            self.chk_varmse.setChecked(False)
            self.randParEvol = "MSE"
        elif self.chk_varmse.checkState() <= 0:
            print(" RandParam will not evolve with MSE nor varmse")
            self.randParEvol = "noEvol"

    def btnstate_varmse(self):
        if self.chk_varmse.checkState() > 0:
            print("RandParam will evolve with varmse")
            self.chk_MSE.setChecked(False)
            self.randParEvol = "varmse"
        elif self.chk_MSE.checkState() <= 0:
            print(" RandParam will not evolve with varmse nor MSE")
            self.randParEvol = "noEvol"

    def btnstate_saveAllMvts(self):
        print(self.chkBx_saveAllMvts.checkState(), end=' ')
        if self.chkBx_saveAllMvts.checkState() > 0:
            print("button checked; All good varmse will be saved")
            self.saveAllMvtsVarmse = 1
        else:
            print("button unchecked; only one best varmse will be saved/run")
            self.saveAllMvtsVarmse = 0

    def checkButtonConstants(self):
        print(self.chkBox_const.checkState(), end=' ')
        if self.chkBox_const.checkState() > 0:
            print("button checked")
            self.setConstantParams()
            if len(self.listConstantNames) > 0:
                # self.chkBox_const.setCheckState(True)
                print(self.chkBox_const.checkState(), "Const button checked")
            else:
                self.chkBox_const.setCheckState(False)
                print(self.chkBox_const.checkState(), "const Button Unchecked")
        else:
            print("button unchecked")
            self.listConstantNames = []
            self.dicConstParam = {}
            self.listDicItConst = [{'constant': []}]

    def setConstantParams(self):
        listChoix = list(self.listDicItConst[0].keys())
        titleText = "select constant params and set their values"
        if __name__ == '__main__':
            rep = ChooseInList.listTransmit(parent=None,
                                            graphNo=0,
                                            listChoix=listChoix,
                                            items=self.xparName,
                                            listDicItems=self.listDicItConst,
                                            onePerCol=[0],
                                            colNames=["constant", "Value"],
                                            dicValues=self.listDicParVal[0],
                                            typ="val",
                                            titleText=titleText)
        # self.listDicItems = rep[0]
            self.listDicItConst = rep[0]
            if len(rep[1]) == 0:    # No values entered,  ESC button was used
                return
            self.listConstantNames = []
            self.dicConstParam = {}
            for i in range(len(self.listDicItConst[0][listChoix[0]])):
                itemName = self.listDicItConst[0][listChoix[0]][i]
                self.listConstantNames.append(itemName)
                self.listDicParVal[0][itemName] = float(rep[1][itemName])
                self.dicConstParam[itemName] = float(rep[1][itemName])
                print(itemName, rep[1][itemName])
                constparnb = self.xparNameDict[itemName]
                optSet.x0[constparnb] = float(self.dicConstParam[itemName])

        # Preparing lstDicBhvCst_itm for DialogChoose_in_list
        for grNb, constNam in enumerate(self.listConstantNames):
            if grNb+1 > len(self.lstDicBhvCst_itm):
                self.lstDicBhvCst_itm.append({})
                self.listdiccstFlt.append({})
                for idx, name in enumerate(self.list_const_items):
                    self.listdiccstFlt[grNb][name] = self.listCstValFilt[idx]
            self.lstDicBhvCst_itm[grNb][constNam] = []

    def lookforconstpar(self, tab_par):
        constexist = False
        listconst = []
        self.dicConstParam = {}
        for col in range(len(tab_par[0])):
            mincol = min(tab_par[:, col])
            maxcol = max(tab_par[:, col])
            if maxcol-mincol == 0:
                itemName = self.xparName[col]
                print("const:", col, itemName, "\t-->", mincol)
                self.dicConstParam[itemName] = float(mincol)
                optSet.x0[col] = float(mincol)
                listconst.append(itemName)
                self.listDicParVal[0][itemName] = mincol
                constexist = True
        if constexist:
            self.listDicItConst = [{'constant': listconst}]
            # self.listDicItems = [{'constant': listconst}]
            self.chkBox_const.setChecked(True)

    def reset(self):
        # clears all param plots
        self.parplt_itm.clearPlots()
        for pargr in range(self.nbactivepargraphs):
            self.screen[pargr].plot_item.clearPlots()
        # clears behav plot
        self.mseplt_itm.clear()
        # clears mvt plot ...
        if self.mvtPltOn:
            try:
                self.clearmvt()  # ... and plots the template
            except Exception as e:
                print(e)
        self.lst_bestchart = []
        if self.bhvPltOn:
            try:
                self.clearBhv()
            except Exception as e:
                print(e)

        # reset the optSet.x0 to params frm asim file
        optSet.actualizeparamCMAes(realx0=[])
        # clears all pairs in optSet.pairs
        optSet.pairs = np.array([])
        optSet.behavs = np.array([])
        # clears optSet.datastructure
        optSet.datastructure = {}
        self.GEP_rootname = ""
        self.mvtcolor = 1
        self.optSet = optSet

    def closeWindows(self):
        if len(self.screen) > 0:
            for pargr, parwin in enumerate(self.screen):
                parwin.close()
            self.screen = []
            # for pargr in range(self.nbactivepargraphs):
            #     self.screen[pargr].PlotWindow.close()
        if self.mvtPltOn:
            try:
                self.mvtPlot.close()
            except Exception as e:
                print(e)
        if self.bhvPltOn:
            try:
                self.bhvPlot.close()
            except Exception as e:
                print(e)
        self.close()

    # =========================================================================
    """
                           Mouvement graph controls
    """
    # =========================================================================

    def plotmvt(self, chart):
        if len(chart) > 0:
            mvt = []
            for i in range(len(chart)-1):
                try:
                    mvt.append([float(chart[i + 1][1]),
                                float(chart[i + 1][optSet.mvtcolumn])])
                except Exception as e:
                    if (verbose > 1):
                        print(e)
            mouvement = np.array(mvt)

            self.mvtPlot.pw_mvt.plot(mouvement[:, 0],
                                     mouvement[:, 1],
                                     pen=self.mvtcolor)
            self.mvtcolor += 1

    def clearResetMvts(self):
        self.clearmvt()
        self.mvtSet = 0
        self.mvtcolor = 1

    def clearmvt(self):
        self.mvtPlot.pw_mvt.clearPlots()
        # print("removing mvt graph")
        self.mvtPlot.pw_mvt.plot(self.mvtTemplate[:, 1],
                                 self.mvtTemplate[:, 2],
                                 pen='k')
        self.clearParam()
        self.clearMseCoact()
        self.mvtPlot.serie_label.setText("no plot")
        self.clearBhv()

    def showFirstMvtSet(self):
        datastructure = optSet.datastructure
        nbMvtSet = len(datastructure)
        if nbMvtSet > 0:
            self.clearmvt()
            self.listbestparamset = []
            self.mvtSet = 0
            self.rgpackt = 0
            typ = datastructure[self.mvtSet][0]
            if self.perPacket == 0:
                startseq = datastructure[self.mvtSet][1] - 1
                endseq = datastructure[self.mvtSet][2] - 1
                rgpackt = -1    # -> plot all packets mvt chart in each run
                print(self.mvtSet, rgpackt, "start=", startseq, "end=", endseq)
            else:
                if typ == 'CMAES' or typ == 'CMAE':
                    nb_mvts = len(datastructure[self.mvtSet][4][4])
                else:
                    nb_mvts = len(datastructure[self.mvtSet][4][3])
                startseq = datastructure[self.mvtSet][1] - 1
                endseq = datastructure[self.mvtSet][2] - 1
                packetsize = datastructure[self.mvtSet][3]

                if packetsize > 0:
                    runperpackt = packetsize
                else:
                    runperpackt = (endseq-startseq + 1) / nb_mvts
                startseq = startseq + (self.rgpackt*runperpackt)
                endseq = startseq + runperpackt - 1
                # endseq = startseq
                rgpackt = self.rgpackt

                print(self.mvtSet, rgpackt, "start=", startseq, "end=", endseq, end=' ')
            self.mvtcolor = 1
            typ = datastructure[self.mvtSet][0]
            conditions = datastructure[self.mvtSet][4]
            if type(conditions[-1][0]) is float:
                mvts_rgs = conditions[-2]
            else:
                mvts_rgs = conditions[-1]
            print(mvts_rgs, end=' ')
            for idx, rg_mvt in enumerate(mvts_rgs):
                if rg_mvt in range(startseq, endseq+1, 1):
                    print(idx, rg_mvt, end=' ')
                    self.plotMvtSet(conditions, typ, idx,
                                    best=self.onlyBestInSet)
            print()
            paramserie = optSet.pairs[:, 0:self.nbpar]
            mse_coact = optSet.pairs[:, self.nbpar:]
            self.plotSetParam_mseCoact(paramserie, startseq, endseq, mse_coact,
                                       typ, best=self.onlyBestInSet)
            # print(conditions)
            comment = "Serie {}/{}".format(self.mvtSet+1, nbMvtSet)
            self.mvtPlot.serie_label.setText(comment)
            self.plotBhvSet(optSet.behavs, optSet.pairs, startseq, endseq)
        else:
            print("no data to plot")

    def showNextMvtSet(self):
        datastructure = optSet.datastructure
        nbMvtSet = len(datastructure)
        if self.keepSet == 0:
            self.clearmvt()
            self.bhvPlot.plot_item.clearPlots()
        if nbMvtSet > 0:
            startseq = datastructure[self.mvtSet][1] - 1
            endseq = datastructure[self.mvtSet][2] - 1
            packetsize = datastructure[self.mvtSet][3]
            typ = datastructure[self.mvtSet][0]
            if self.perPacket == 0:
                self.mvtSet += 1
                if self.mvtSet >= nbMvtSet:
                    self.mvtSet = 0
                startseq = datastructure[self.mvtSet][1] - 1
                endseq = datastructure[self.mvtSet][2] - 1
                rgpackt = -1    # -> plot all packets mvt chart in each run
                print(self.mvtSet, rgpackt, "start=", startseq, "end=", endseq)
            else:
                if typ == 'CMAES' or typ == 'CMAE':
                    nb_mvts = len(datastructure[self.mvtSet][4][4])
                else:
                    nb_mvts = len(datastructure[self.mvtSet][4][3])
                if packetsize > 0:
                    nb_packets = ((endseq - startseq) + 1) / packetsize
                elif packetsize == 0:
                    nb_packets = nb_mvts
                self.rgpackt += 1
                if self.rgpackt >= nb_packets:
                    self.rgpackt = 0
                    self.mvtSet += 1
                    if self.mvtSet > nbMvtSet-1:
                        self.mvtSet = 0
                    startseq = datastructure[self.mvtSet][1] - 1
                    endseq = datastructure[self.mvtSet][2] - 1
                    packetsize = datastructure[self.mvtSet][3]
                    if typ == 'CMAES' or typ == 'CMAE':
                        nb_mvts = len(datastructure[self.mvtSet][4][4])
                    else:
                        nb_mvts = len(datastructure[self.mvtSet][4][3])
                    if packetsize > 0:
                        nb_packets = ((endseq - startseq) + 1) / packetsize
                    elif packetsize == 0:
                        nb_packets = nb_mvts

                if packetsize > 0:
                    runperpackt = packetsize
                else:
                    runperpackt = (endseq-startseq + 1) / nb_mvts
                startseq = startseq + (self.rgpackt*runperpackt)
                endseq = startseq + runperpackt - 1
                # endseq = startseq
                rgpackt = self.rgpackt
                print(self.mvtSet, rgpackt, "start=", startseq, "end=", endseq, end=' ')

            self.mvtcolor = self.mvtSet + 1
            typ = datastructure[self.mvtSet][0]
            conditions = datastructure[self.mvtSet][4]
            mvts_rgs = conditions[-1]
            print(mvts_rgs, end=' ')
            for idx, rg_mvt in enumerate(mvts_rgs):
                if rg_mvt in range(startseq, endseq+1, 1):
                    print(idx, rg_mvt, end=' ')
                    self.plotMvtSet(conditions, typ, idx,
                                    best=self.onlyBestInSet)
            paramserie = optSet.pairs[:, 0:self.nbpar]
            mse_coact = optSet.pairs[:, self.nbpar:]
            self.plotSetParam_mseCoact(paramserie, startseq, endseq, mse_coact,
                                       typ, best=self.onlyBestInSet)
            # print conditions
            comment = "Serie {}/{}".format(self.mvtSet+1, nbMvtSet)
            self.mvtPlot.serie_label.setText(comment)
            self.plotBhvSet(optSet.behavs, optSet.pairs, startseq, endseq)
        print()

    def showPrevMvtSet(self):
        datastructure = optSet.datastructure
        nbMvtSet = len(datastructure)
        if self.keepSet == 0:
            self.clearmvt()
            self.bhvPlot.plot_item.clearPlots()
        if nbMvtSet > 0:
            startseq = datastructure[self.mvtSet][1] - 1
            endseq = datastructure[self.mvtSet][2] - 1
            packetsize = datastructure[self.mvtSet][3]
            typ = datastructure[self.mvtSet][0]
            if self.perPacket == 0:
                self.mvtSet -= 1
                if self.mvtSet < 0:
                    self.mvtSet = nbMvtSet-1
                startseq = datastructure[self.mvtSet][1] - 1
                endseq = datastructure[self.mvtSet][2] - 1
                rgpackt = -1    # -> plot all packets mvt chart in each run
                print(self.mvtSet, rgpackt, "start=", startseq, "end=", endseq)
            else:
                if typ == 'CMAES' or typ == 'CMAE':
                    nb_mvts = len(datastructure[self.mvtSet][4][4])
                else:
                    nb_mvts = len(datastructure[self.mvtSet][4][3])
                if packetsize > 0:
                    nb_packets = ((endseq - startseq) + 1) / packetsize
                elif packetsize == 0:
                    nb_packets = nb_mvts
                self.rgpackt -= 1
                if self.rgpackt < 0:
                    self.mvtSet -= 1
                    if self.mvtSet < 0:
                        self.mvtSet = nbMvtSet-1
                    startseq = datastructure[self.mvtSet][1] - 1
                    endseq = datastructure[self.mvtSet][2] - 1
                    packetsize = datastructure[self.mvtSet][3]
                    if typ == 'CMAES' or typ == 'CMAE':
                        nb_mvts = len(datastructure[self.mvtSet][4][4])
                    else:
                        nb_mvts = len(datastructure[self.mvtSet][4][3])
                    if packetsize > 0:
                        nb_packets = ((endseq - startseq) + 1) / packetsize
                    elif packetsize == 0:
                        nb_packets = nb_mvts
                    self.rgpackt = nb_packets - 1
                if packetsize > 0:
                    runperpackt = packetsize
                else:
                    runperpackt = (endseq-startseq + 1) / nb_mvts
                startseq = startseq + (self.rgpackt*runperpackt)
                endseq = startseq + runperpackt - 1
                # endseq = startseq
                rgpackt = self.rgpackt
                print(self.mvtSet, rgpackt, "start=", startseq, "end=", endseq, end=' ')

            self.mvtcolor = self.mvtSet + 1
            typ = datastructure[self.mvtSet][0]
            conditions = datastructure[self.mvtSet][4]
            mvts_rgs = conditions[-1]
            print(mvts_rgs, end=' ')
            for idx, rg_mvt in enumerate(mvts_rgs):
                if rg_mvt in range(startseq, endseq+1, 1):
                    print(idx, rg_mvt, end=' ')
                    self.plotMvtSet(conditions, typ, idx,
                                    best=self.onlyBestInSet)
            paramserie = optSet.pairs[:, 0:self.nbpar]
            mse_coact = optSet.pairs[:, self.nbpar:]
            self.plotSetParam_mseCoact(paramserie, startseq, endseq, mse_coact,
                                       typ, best=self.onlyBestInSet)
            # print conditions
            comment = "Serie {}/{}".format(self.mvtSet+1, nbMvtSet)
            self.mvtPlot.serie_label.setText(comment)
            self.plotBhvSet(optSet.behavs, optSet.pairs, startseq, endseq)
        print()

    def showAllMvts(self):
        self.clearmvt()
        self.mvtcolor = 1
        rgpackt = -1    # -> plot all packets mvt chart in each run
        datastructure = optSet.datastructure
        for idx in range(len(datastructure)):
            typ = datastructure[idx][0]
            startseq = datastructure[idx][1] - 1
            endseq = datastructure[idx][2] - 1
            conditions = datastructure[idx][4]
            paramserie = optSet.pairs[:, 0:self.nbpar]
            mse_coact = optSet.pairs[:, self.nbpar:]
            if conditions[-2] != [100000]:
                self.plotMvtSet(conditions, typ, rgpackt,
                                best=self.onlyBestInSet)
            else:
                print("No good mvt found")
            self.plotSetParam_mseCoact(paramserie, startseq, endseq, mse_coact,
                                       typ, best=self.onlyBestInSet)
            self.plotBhvSet(optSet.behavs, optSet.pairs, startseq, endseq)
        self.mvtPlot.serie_label.setText("Show All Sets")

    def keepMvtSet(self, state):
        if state == QtCore.Qt.Checked:
            self.keepSet = 1
            print('Checked')
        else:
            self.keepSet = 0
            print('UnChecked')

    def onlyBest(self, state):
        if state == QtCore.Qt.Checked:
            self.onlyBestInSet = 1
            print('Checked')
        else:
            self.onlyBestInSet = 0
            print('UnChecked')

    def perPackt(self, state):
        if state == QtCore.Qt.Checked:
            self.perPacket = 1
            print('Checked')
        else:
            self.perPacket = 0
            print('UnChecked')

    # =========================================================================
    """
                               param graphs control
    """
    # =========================================================================

    def plotPar_Coact_Mvt(self, plot=0):
        """
        This method actualizes graphic windows on screen :
        Plots params and mse-coactpenality dots using
            self.plotSetParam_mseCoact),
        plots movements (using self.plotMvtSet)
        plots behaviors (using self.plotBhvSet)
        """
        self.clearMseCoact()
        nbpar = self.nbpar
        datastructure = optSet.datastructure
        self.parplt_itm.setXRange(0, 1)
        self.parplt_itm.setYRange(0, 1)
        self.mseplt_itm.setXRange(0, 2000)
        self.mseplt_itm.setYRange(0, 2000)
        rgpackt = -1    # -> plot all packets mvt chart in each run

        paramserie = optSet.pairs[:, 0:nbpar]
        mse_coact = optSet.pairs[:, nbpar:nbpar+2]
        if plot == 1:
            for idx in range(len(datastructure)):
                typ = datastructure[idx][0]
                startseq = datastructure[idx][1] - 1
                endseq = datastructure[idx][2] - 1
                conditions = datastructure[idx][4]
                self.plotSetParam_mseCoact(paramserie, startseq, endseq,
                                           mse_coact, typ)
                if (rgpackt >= 0):
                    self.plotMvtSet(conditions, typ, rgpackt, best=0)
                self.plotBhvSet(optSet.behavs, optSet.pairs, startseq, endseq)

    def read_listDicGraphs(self, listDicGraphsPath):
        """
        Looks for a listDicGraphs.pkl file in ResultFile directory; If exists,
        reads it and set the various parameters in the paramGraphs, accordingly
        """
        if os.path.exists(listDicGraphsPath):
            with open(listDicGraphsPath, 'rb') as f:
                self.listDicGraphs = pickle.load(f)

    def save_listDicGraphs(self, listDicGraphsPath):
        """
        saves the current listDicGraphs dctionary into a listDicGraphs.pkl file
        in ResultFile directory
        """
        with open(listDicGraphsPath, 'wb') as f:
            pickle.dump(self.listDicGraphs, f)

    def plotOtherParam(self, paramserie,  pen=None, symbol='o', symbolBrush=2):
        """
        When all param graphs are to be plotted, adds parGraphs in the list
        self.screen. It uses the self.listDicGraphs to set the parameters for
        X and Y axes on each graph.
        """
        namex = self.listDicGraphs[0]["abscissa"]
        namey = self.listDicGraphs[0]["ordinate"]
        # print "Maingraph     ", namex, "->\tparx: ", self.parx
        # print "              ", namey, "->\tpary: ", self.pary
        for pargr in range(self.nbactivepargraphs):
            namex = self.listDicGraphs[pargr+1]["abscissa"]
            namey = self.listDicGraphs[pargr+1]["ordinate"]
            parx = self.xparNameDict[namex[0]]
            pary = self.xparNameDict[namey[0]]
            # print "suplgraph N°", pargr, namex, "->\tparx: ", parx
            # print "              ", namey, "->\tpary: ", pary
            self.screen[pargr].plot_item.plot(paramserie[:, parx],
                                              paramserie[:, pary],
                                              pen=pen,
                                              symbol=symbol,
                                              symbolBrush=symbolBrush)
            # ==============================================================
            QtWidgets.QApplication.processEvents()
            # ==============================================================

    def param_in_blue(self, df_par):
        for pargr in range(self.nbactivepargraphs):
            """
            parx = 2 + int(2*pargr) + self.parx
            pary = 2 + int(2*pargr) + self.pary
            if pary > self.nbpar:
                pary = 2 + self.pary
            if parx > self.nbpar:
                parx = 2 + self.parx
            """
            namex = self.listDicGraphs[pargr+1]["abscissa"]
            namey = self.listDicGraphs[pargr+1]["ordinate"]
            parx = self.xparNameDict[namex[0]]
            pary = self.xparNameDict[namey[0]]
            print(parx, namex, pary, namey)
            self.plotParBlue(self.screen[pargr].plot_item, df_par, parx, pary)
        if self.main_mode is False:     # if called from ""makeGraphs""
            if self.nbactivepargraphs > 0:
                namex = self.listDicGraphs[0]["abscissa"]
                namey = self.listDicGraphs[0]["ordinate"]
                parx = self.xparNameDict[namex[0]]
                pary = self.xparNameDict[namey[0]]
                print(parx, namex, pary, namey)
                self.plotParBlue(self.screen[pargr+1].plot_item,
                                 df_par, parx, pary)

    def plotParBlue(self, parpltItm, df_par, parx, pary):
        optSet = self.optSet
        if self.main_mode is True:     # if called from "GEP_GUI"
            nbpar = self.nbpar
            print(nbpar)
            """
            datastructure = optSet.datastructure
            for idx in range(len(datastructure)):
                startseq = datastructure[idx][1]
                endseq = datastructure[idx][2]
                paramserie = optSet.pairs[:, 0:nbpar]
                symbol = "o"
                symbolBrush = 'c'
                parpltItm.setXRange(0, 1)
                parpltItm.setYRange(0, 1)
                parpltItm.plot(paramserie[startseq:endseq+1, parx],
                               paramserie[startseq:endseq+1, pary],
                               pen=3, symbol=symbol,
                               symbolBrush=symbolBrush)
                # ==========================================================
                QtWidgets.QApplication.processEvents()
                # ==========================================================
            """
        else:        # if called from "makeGraphs"
            dflist_x = df_par[optSet.xparName[parx]]
            dflist_y = df_par[optSet.xparName[pary]]
            symbol = "o"
            symbolBrush = 'c'
            symbolPen = 'b'
            pen = None
            # parpltItm.setXRange(0, 1)
            # parpltItm.setYRange(0, 1)
            # param_val_array = np.array(df_parremain)[:, [parx, pary]]
            parpltItm.plot(list(dflist_x),
                           list(dflist_y),
                           pen=pen, symbol=symbol,
                           symbolBrush=symbolBrush,
                           symbolPen=symbolPen,
                           markersize=15)
            # ==============================================================
            QtWidgets.QApplication.processEvents()
            # ==============================================================

    def plotPar_rainbow(self, listdf_par, codeCoul_df, lut):
        df_parremain = listdf_par[0]
        if len(df_parremain) != len(codeCoul_df):
            print("PB : length(df_parreman) different from length(codeCoul_df)")
            return
        # df_parremain = df_parremain.loc[codeCoul_df.index]
        parx = self.parx
        pary = self.pary
        dflist_x = df_parremain[optSet.xparName[parx]]
        dflist_y = df_parremain[optSet.xparName[pary]]
        for rgserie in codeCoul_df["rgserie"]:
            color = int(codeCoul_df.loc[rgserie]["color"])
            s = pg.ScatterPlotItem([dflist_x.loc[rgserie]],
                                   [dflist_y.loc[rgserie]],
                                   size=6, pen=pg.mkPen(None))
            coul = lut[color]
            r, v, b = coul[0], coul[1], coul[2]
            s.setBrush(QtWidgets.QBrush(QtWidgets.QColor(r, v, b)))
            if self.main_mode is True:      # if not called from "makeGraphs"
                self.parplt_itm.addItem(s)
            else:                           # if called from "makeGraphs"
                #                             default graph is re-created
                pargr = self.nbactivepargraphs  # nb of active graphs = last
                #                                 added graph
                self.screen[pargr].plot_item.addItem(s)
        # ==============================================================
        QtWidgets.QApplication.processEvents()
        # ==============================================================

    def plotPar_rainbow2(self, listdf_par, brushes):
        df_parremain = listdf_par[0]
        if len(df_parremain) != len(brushes):
            print("PB : length(df_parreman) differs from length(df_bhvremain)")
            return
        # df_parremain = df_parremain.loc[codeCoul_df.index]
        parx = self.parx
        pary = self.pary
        dflist_x = df_parremain[optSet.xparName[parx]]
        dflist_y = df_parremain[optSet.xparName[pary]]
        """
        data = []
        for i in range(len(dflist_x)):
            data.append([dflist_x[i], dflist_y[i]])
        """
        for idx, rgserie in enumerate(df_parremain["rgserie"]):
            s = pg.ScatterPlotItem([dflist_x.loc[rgserie]],
                                   [dflist_y.loc[rgserie]],
                                   size=3, pen=pg.mkPen(None))
            # s.setData(pos=data)
            s.setBrush(brushes[idx])
            self.parplt_itm.addItem(s)
        # ===========================================================
        QtWidgets.QApplication.processEvents()
        # ===========================================================

    def plotOtherParam_rainbow(self, listdf_par, codeCoul_df, lut):
        df_parremain = listdf_par[0]
        if len(df_parremain) != len(codeCoul_df):
            print("PB : length(df_parreman) different from length(codeCoul_df)")
            return
        for pargr in range(self.nbactivepargraphs):
            namex = self.listDicGraphs[pargr+1]["abscissa"]
            namey = self.listDicGraphs[pargr+1]["ordinate"]
            parx = self.xparNameDict[namex[0]]
            pary = self.xparNameDict[namey[0]]
            dflist_x = df_parremain[optSet.xparName[parx]]
            dflist_y = df_parremain[optSet.xparName[pary]]
            for rgserie in codeCoul_df["rgserie"]:
                color = int(codeCoul_df.loc[rgserie]["color"])
                s = pg.ScatterPlotItem([dflist_x.loc[rgserie]],
                                       [dflist_y.loc[rgserie]],
                                       size=6, pen=pg.mkPen(None))
                coul = lut[color]
                r, v, b = coul[0], coul[1], coul[2]
                s.setBrush(QtWidgets.QBrush(QtWidgets.QColor(r, v, b)))
                self.screen[pargr].plot_item.addItem(s)
                # ===========================================================
                QtWidgets.QApplication.processEvents()
                # ===========================================================

    def plotOtherParam_rainbow2(self, listdf_par, brushes):
        df_parremain = listdf_par[0]
        if len(df_parremain) != len(brushes):
            print("PB : length(df_parreman) differs from length(df_bhvremain)")
            return
        namex = self.listDicGraphs[0]["abscissa"]
        namey = self.listDicGraphs[0]["ordinate"]
        for pargr in range(self.nbactivepargraphs):
            namex = self.listDicGraphs[pargr+1]["abscissa"]
            namey = self.listDicGraphs[pargr+1]["ordinate"]
            parx = self.xparNameDict[namex[0]]
            pary = self.xparNameDict[namey[0]]
            dflist_x = list(df_parremain[optSet.xparName[parx]])
            dflist_y = list(df_parremain[optSet.xparName[pary]])
            data = []
            for i in range(len(dflist_x)):
                data.append([dflist_x[i], dflist_y[i]])
            s = pg.ScatterPlotItem(size=3, pen=pg.mkPen(None))
            s.setData(pos=data)
            s.setBrush(brushes)
            self.screen[pargr].plot_item.addItem(s)
            # ===========================================================
            QtWidgets.QApplication.processEvents()
            # ===========================================================

    def chooseParam(self):
        selectedListDicGraphs = []
        xparName_remain = copy.deepcopy(self.xparName)
        previous_dicGraphs = [self.listDicGraphs[0]]
        for grNb in range(self.nbactivepargraphs + 1):
            titleText = "Choose X and Y for graph " + str(grNb)
            rep = ChooseInList.listTransmit(parent=None,
                                            graphNo=0,
                                            listChoix=["abscissa", "ordinate"],
                                            items=xparName_remain,
                                            listDicItems=previous_dicGraphs,
                                            onePerCol=[1, 1],
                                            colNames=["X", "Y"],
                                            typ="chk",
                                            titleText=titleText)
            # self.listDicGraphs = rep[0]
            selectedDicGraph = rep[0]
            selectedxparNames = [selectedDicGraph[0]['abscissa'][0],
                                 selectedDicGraph[0]['ordinate'][0]]
            selectedListDicGraphs.append(selectedDicGraph[0])
            xparName_remain = [parName for parName in xparName_remain
                               if parName not in selectedxparNames]
            listDicGraphs_remain = []
            # listDicGraphs_remain.append(selectedDicGraph[0])
            for gr in range(int(len(xparName_remain)/2)):
                dicGraph_remain = {}
                for idx, choix in enumerate(["abscissa", "ordinate"]):
                    dicGraph_remain[choix] = [xparName_remain[idx + gr*2]]
                listDicGraphs_remain.append(dicGraph_remain)
            previous_dicGraphs = listDicGraphs_remain[:1]
            # print(rep)

            print("####   GRAPH N°", grNb, "  #####")
            namex = selectedxparNames[0]
            parx = self.xparNameDict[namex]
            print(namex, " -> ", 'param', parx, "in abscissa")
            namey = selectedxparNames[1]
            pary = self.xparNameDict[namey]
            print(namey, " -> ", 'param', pary, "in ordinate")
            print()
        self.listDicGraphs = selectedListDicGraphs
        resultFilePath = folders.animatlab_result_dir
        # resultFilePath = os.path.join(animatsimdir, "ResultFiles")
        listDicGraphsPath = os.path.join(resultFilePath, 'listDicGraphs.pkl')
        self.save_listDicGraphs(listDicGraphsPath)
        print("self.nbactivepargraphs =", self.nbactivepargraphs)
        self.affect_param_to_graph(self.listDicGraphs)
        # self.param_to_graph = selectedListDicGraphs

    def affect_param_to_graph(self, listDicGraphs):
        self.param_to_graph = listDicGraphs
        print("self.nbactivepargraphs =", self.nbactivepargraphs)
        namex = listDicGraphs[0]["abscissa"]
        parx = self.xparNameDict[namex[0]]
        namey = listDicGraphs[0]["ordinate"]
        pary = self.xparNameDict[namey[0]]
        self.parx = parx        # self.parx for the main graph
        self.pary = pary        # self.pary for the main graph
        self.parplt_itm.setLabel('left',
                                 self.xparName[pary],
                                 units='',
                                 color='black', size='12pt')
        self.parplt_itm.setLabel('bottom',
                                 self.xparName[parx],
                                 units='',
                                 color='black', size='12pt')
        if self.nbactivepargraphs > 0:
            for grNb in range(1, self.nbactivepargraphs + 1):
                namex = self.param_to_graph[grNb]["abscissa"]
                parx = self.xparNameDict[namex[0]]
                namey = self.param_to_graph[grNb]["ordinate"]
                pary = self.xparNameDict[namey[0]]
                self.screen[grNb-1].plot_item.setLabel('left',
                                                       self.xparName[pary],
                                                       units='',
                                                       color='black',
                                                       size='12pt')
                self.screen[grNb-1].plot_item.setLabel('bottom',
                                                       self.xparName[parx],
                                                       units='',
                                                       color='black',
                                                       size='12pt')
        # self.clearParam()   # erases all param plots
        self.plotPar(self.parplt_itm, self.parx, self.pary)

    def activateAllParGraphs(self, plot=0):
        self.nbactivepargraphs = self.nbpargraphs - 1
        self.bhvPlot.targetwin = self.nbactivepargraphs
        # the params in the main windows are not duplicated -> -1
        self.screen = []

        # =========  Create all paramGraphs with default parNames  ============
        self.listDicGraphs = [{"abscissa": [self.xparName[0]],
                               "ordinate": [self.xparName[1]]}]
        grName = ["graph{}".format(i) for i in range(self.nbactivepargraphs)]
        self.parx, self.pary = 0, 1
        for pargr in range(self.nbactivepargraphs):
            self.screen.append(param_GUI.ParamWin())
            self.screen[pargr].setObjectName(grName[pargr])
            parx = 2 + int(2*pargr) + self.parx
            pary = 2 + int(2*pargr) + self.pary
            if pary > self.nbpar:
                pary = 2 + self.pary
            if parx > self.nbpar:
                parx = 2 + self.parx
            dicGraph = {'abscissa': [self.xparName[parx]],
                        'ordinate': [self.xparName[pary]]}
            self.listDicGraphs.append(dicGraph)
            if plot == 1:
                self.plotPar(self.screen[pargr].plot_item, parx, pary)
            else:
                self.screen[pargr].hide()

        # ======  If listDicGraphs.pkl exists reaffect params in graphs =======
        # resultFilePath = os.path.join(animatsimdir, "ResultFiles")
        resultFilePath = folders.animatlab_result_dir
        listDicGraphsPath = os.path.join(resultFilePath, 'listDicGraphs.pkl')
        if os.path.exists(listDicGraphsPath):
            self.read_listDicGraphs(listDicGraphsPath)
            self.affect_param_to_graph(self.listDicGraphs)
        else:
            None
            # self.chooseParam()
            # self.save_listDicGraphs(listDicGraphsPath)

        if self.main_mode is False:     # if called from "makeGraphs"
            #                             an additional graph is built to plot
            #                             parameters self.parx and self.pary
            grName.append("graph{}".format(pargr+1))
            self.screen.append(param_GUI.ParamWin())
            if plot == 1:
                self.plotPar(self.screen[pargr+1].plot_item,
                             self.parx, self.pary)
                self.screen[pargr+1].setObjectName(grName[pargr+1])
            else:
                self.screen[pargr].hide()
            # ======================  adds a add ROI button ===================
            self.btn_addROI = QtWidgets.QPushButton('add ROI')
            # self.btn_addROI.setObjectName('add ROI')
            self.screen[pargr+1].buttonHLayout1.addWidget(self.btn_addROI)
            # ================== adds a select points  button =================
            self.btn_select = QtWidgets.QPushButton('select in ROI')
            # self.btn_addROI.setObjectName('select in ROI')
            self.screen[pargr+1].buttonHLayout1.addWidget(self.btn_select)
            # ================== adds a select points  button =================
            self.btn_initROI = QtWidgets.QPushButton('Init ROI')
            # self.btn_addROI.setObjectName('Init ROI')
            self.screen[pargr+1].buttonHLayout1.addWidget(self.btn_initROI)

            print(self.screen[pargr+1].plot_item.viewRange())
            self.btn_addROI.clicked.connect(lambda: self.addROI(pargr=pargr+1))
            self.btn_select.clicked.connect(lambda: self.selROI(pargr=pargr+1))
            self.btn_initROI.clicked.connect(self.initROI)

    def showAllParGraphs(self):
        self.activateAllParGraphs(plot=1)

    def clearParam(self):
        self.parplt_itm.clearPlots()
        # print "removing param graph"
        for pargr in range(self.nbactivepargraphs):
            self.screen[pargr].plot_item.clearPlots()
        if self.main_mode is False:     # if called from "makeGraphs"
            if self.nbactivepargraphs > 0:
                self.screen[pargr+1].plot_item.clearPlots()

    def prevpargraph(self):
        self.present_graph += 1
        if self.present_graph > self.nbpargraphs-1:
            self.present_graph = 0
        (self.parx, self.pary) = self.pargraph[self.present_graph]
        self.clearParam()
        # self.clearMseCoact()
        self.plotPar(self.parplt_itm, self.parx, self.pary)

    def nextpargraph(self):
        self.present_graph -= 1
        if self.present_graph < 0:
            self.present_graph = self.nbpargraphs-1
        (self.parx, self.pary) = self.pargraph[self.present_graph]
        self.clearParam()
        self.plotPar(self.parplt_itm, self.parx, self.pary)

    def totalRange(self):
        """
        Plot the param graphs with total scale
        """
        # print "set plot in whole scale range"
        self.parplt_itm.setXRange(0, 1)
        self.parplt_itm.setYRange(0, 1)
        for pargr in range(self.nbactivepargraphs):
            self.screen[pargr].plot_item.setXRange(0, 1)
            self.screen[pargr].plot_item.setYRange(0, 1)

    def addROI(self, pargr=-1):
        """
        add a ROI in sqarre shape. The size of ROI rectangle is adjusted to
        the range of the pargr plot window. SO it is recommended to adjust the
        zoom on the window before calling this method.
        NB: If pargr == 3 this means that this was the last appended screen
        thai is in reality the pargraph that was in the mainWindow.
        ATTENTION!!!!! pargr=3 is ok for the self.screen[pargr].plot_item
        but it corresponds to parx = self.parx and pary=self.pary that are
        by default 0 and 1 respectively. In the self.listDicGraphs the instance
        0 was added in last and therefore:
            pargr=3 corresponds listDicGraphs[0].
        For all other values of pargr:
            screen[pargr] <-> listDicGraphs[pargr+1]
        """
        # original coordinates of the roi
        print()
        print("pargr:", pargr)
        if pargr == -1:
            win_range = self.parplt_itm.viewRange()
        else:
            win_range = self.screen[pargr].plot_item.viewRange()
        print(win_range)
        xmin = win_range[0][0]
        xmax = win_range[0][1]
        ymin = win_range[1][0]
        ymax = win_range[1][1]
        print(" xmin:{}  xmax:{}".format(xmin, xmax))
        print(" ymin:{}  ymax:{}".format(ymin, ymax))
        xcenter = (xmin + xmax)/2
        ycenter = (ymin + ymax)/2
        xampl = xmax - xmin
        yampl = ymax - ymin
        xleft = xcenter - (0.25 * xampl)
        ylow = ycenter - (0.25 * yampl)
        """
        self.roi = pg.PolyLineROI([[xleft, ylow], [xright, ylow],
                                  [xright, yup], [xleft, yup]],
                                  closed=True,
                                  pen=pg.mkPen(color=(0, 201, 255, 255),
                                               width=3))

        # self.roi = pg.RectROI([xleft, ylow], [xright, yup], pen='y')

        self.roi = pg.TestROI([xleft, ylow], [xright, yup],
                              maxBounds=QtCore.QRectF(xmin-xampl/10,
                                                      ymin-yampl/10,
                                                      xampl*1.2, yampl*1.2),
                              pen=pg.mkPen(color=(0, 201, 255, 255), width=3))
        """
        self.roi = pg.TestROI([xleft, ylow], [xampl, yampl],
                              maxBounds=QtCore.QRectF(xmin-xampl/10,
                                                      ymin-yampl/10,
                                                      xampl*1.2, yampl*1.2),
                              pen=pg.mkPen(color=(0, 201, 255, 255), width=1),
                              removable=True)
        # connect to printing function when moving something
        self.roi.setZValue(100)  # in order roi to be above points
        # self.roi.sigRegionChanged.connect(self.roiMove)
        if pargr == -1:
            self.parplt_itm.addItem(self.roi)  # if called from mainWindow
        else:
            self.screen[pargr].plot_item.addItem(self.roi)
        # =============================================

    def selROI(self, pargr=-1):
        """
        selects the points that ar in the ROI rectangle and returns the list
        of their ranks in the df_list
        """
        listcolors = []
        for i in range(20):
            listcolors.append(pg.intColor(i, 6, maxValue=128))
        self.indexROIcolor += 1
        color = listcolors[self.indexROIcolor]
        optSet = self.optSet
        if pargr == -1:  # This should never happend!!!
            parx = self.parx
            pary = self.pary
            namex = self.listDicGraphs[0]["abscissa"]
            namey = self.listDicGraphs[0]["ordinate"]
        # if last screen ... -> first entry in self.listDicGraphs
        elif pargr == len(self.listDicGraphs)-1:  # This is the actual case
            namex = self.listDicGraphs[0]["abscissa"]
            namey = self.listDicGraphs[0]["ordinate"]
        else:
            namex = self.listDicGraphs[pargr]["abscissa"]
            namey = self.listDicGraphs[pargr]["ordinate"]
        parx = self.xparNameDict[namex[0]]
        pary = self.xparNameDict[namey[0]]
        # ====================================================================
        listdata = self.selectFromROI(parx, pary, self.df_parremain)
        print("##############################################################")
        print(listdata)
        self.selectedROI.append(listdata)
        # ====================================================================
        # Plots the selected data in red in the main param window (last screen)
        dflist_x = self.df_parremain[optSet.xparName[parx]][listdata]
        dflist_y = self.df_parremain[optSet.xparName[pary]][listdata]
        symbol = "o"
        symbolBrush = color
        pen = None
        parpltItm = self.screen[pargr].plot_item
        parpltItm.plot(list(dflist_x), list(dflist_y),
                       pen=pen, symbol=symbol, symbolBrush=symbolBrush)
        # Plots the selected data in red in the main param window (last screen)
        for pargr in range(self.nbactivepargraphs):
            parpltItm = self.screen[pargr].plot_item
            namex = self.listDicGraphs[pargr+1]["abscissa"]
            namey = self.listDicGraphs[pargr+1]["ordinate"]
            parx = self.xparNameDict[namex[0]]
            pary = self.xparNameDict[namey[0]]
            dflist_x = self.df_parremain[optSet.xparName[parx]][listdata]
            dflist_y = self.df_parremain[optSet.xparName[pary]][listdata]
            parpltItm.plot(list(dflist_x),
                           list(dflist_y),
                           pen=pen, symbol=symbol,
                           symbolBrush=symbolBrush)
        # plots the corresponding selected bhvpoints with similar color
        listdf_bhv = [self.df_bhvremain.loc[listdata]]
        self.plot_df_bhv(listdf_bhv, col=color)

    def selectFromROI(self, parx, pary, df_parremain):
        optSet = self.optSet
        # df_parremain = listdf_par[0]
        pts = self.roi.getSceneHandlePositions()
        handlePoints = [self.roi.mapSceneToParent(pt[1]) for pt in pts]
        # print(handlePoints)
        # roiShape = self.roi.mapToItem(s1, self.roi.shape())
        # selected = [pt for pt in s1.points() if roiShape.contains(pt)]
        # selected = self.roi.getArrayRegion()
        x_select_sup = handlePoints[1].x()
        y_select_sup = handlePoints[1].y()
        x_select_inf = handlePoints[2].x()
        y_select_inf = handlePoints[2].y()
        if verbose > 2:
            print("x_select_inf=\t", x_select_inf)
            print("x_select_sup=\t", x_select_sup)
            print("y_select_inf=\t", y_select_inf)
            print("y_select_sup=\t", y_select_sup)
        # dflist_x = list(df_parremain[optSet.xparName[parx]])
        # dflist_y = list(df_parremain[optSet.xparName[pary]])
        df_x = df_parremain[optSet.xparName[parx]]
        df_y = df_parremain[optSet.xparName[pary]]
        selected = []
        valid_j = [j for j in df_x.index if
                   (df_x[j] > x_select_inf and df_x[j] < x_select_sup)]
        valid_jj = [jj for jj in valid_j if
                    (df_y[jj] > y_select_inf and df_y[jj] < y_select_sup)]
        selected.append([df_x[i] for i in valid_jj])
        selected.append([df_y[i] for i in valid_jj])
        """
        valid_j = [j for j in range(len(dflist_x)) if
                   (dflist_x[j] > x_select_inf and dflist_x[j] < x_select_sup)]
        valid_jj = [jj for jj in valid_j if
                    (dflist_y[jj] > y_select_inf and
                     dflist_y[jj] < y_select_sup)]
        selected.append([dflist_x[j] for j in valid_jj])
        selected.append([dflist_y[j] for j in valid_jj])
        """
        if verbose > 2:
            print(selected)
            print(valid_jj)
        print(len(valid_jj), "points selected")
        self.selectedParams = valid_jj
        return valid_jj

        # Print the coordinates of the ROI.
        # pts = self.roi.getSceneHandlePositions()
        # print([self.roi.mapSceneToParent(pt[1]) for pt in pts])

    def initROI(self):
        self.selectedROI = []

    # =========================================================================
    """
                           mse_coact Graph Procedures
    """
    # =========================================================================

    def clearMseCoact(self):
        self.mseplt_itm.clear()
        # print("removing behav graph")

    # =========================================================================
    """
                          Behaviour Procedures
    """
    # =========================================================================

    def bhv_filterWithMse(self):
        optSet = self.optSet
        self.clearBhv()
        self.bhv_selectMseThr(oneOnly=0)   # oneOnly=0 -> multiple selection OK
        self.plotBhvSet(optSet.behavs, optSet.pairs, 0, len(optSet.behavs)-1,
                        dic_mse_filter=self.dicSelectedMseThr,
                        by_series="mse")

    def bhv_filterWithCoactP(self):
        optSet = self.optSet
        self.clearBhv()
        self.bhv_selectMseThr(oneOnly=1)   # oneOnly=0 -> multiple selection OK
        list_entry_name = ["Coactivztion_Penality"]
        list_entry_value = [str(0.01)]
        list_value_max = [5000]
        window_name = "Enter maxCoactP value"
        self.CoactPDialog = Enter_Values(self,
                                         list_entry_name,
                                         list_entry_value,
                                         list_value_max,
                                         window_name)
        self.CoactPDialog.show()
        self.CoactPDialog.exec_()  # Stops further processes
        #                                 until executed
        self.new_coacpP = float(self.list_value[0])
        self.plotBhvSet(optSet.behavs, optSet.pairs, 0, len(optSet.behavs)-1,
                        dic_mse_filter=self.dicSelectedMseThr,
                        by_series="mse",
                        max_coactP=self.new_coacpP)

    def bhv_filterWithCst(self):
        optSet = self.optSet
        self.clearBhv()
        self.bhv_selectMseThr(oneOnly=1)   # oneOnly=1 -> unique selection
        self.bhv_selectCstVal()
        self.plotBhvSet(optSet.behavs, optSet.pairs, 0, len(optSet.behavs)-1,
                        dic_mse_filter=self.dicSelectedMseThr,
                        dic_cst_filter=self.dicSelectedCstFilt,
                        by_series="cst")

    def cursorsONOFF(self, state):
        if state == QtCore.Qt.Checked:
            self.cursor_active = 1
            self.bhvPlot.set_region()
            print('Checked')
        else:
            self.cursor_active = 0
            self.bhvPlot.clear_region()
            print('UnChecked')
            self.clearBhv()
            self.clearParam()
            if self.main_mode is False:     # if called from "makeGraphs"
                self.param_in_blue(self.source_df_parremain)
                print(self.source_df_bhvremain)
                self.plot_df_bhv([self.source_df_bhvremain], col=None)
            else:
                datastructure = optSet.datastructure
                for idx in range(len(datastructure)):
                    typ = datastructure[idx][0]
                    startseq = datastructure[idx][1] - 1
                    endseq = datastructure[idx][2] - 1
                    paramserie = optSet.pairs[:, 0:self.nbpar]
                    mse_coact = optSet.pairs[:, self.nbpar:]
                    self.plotSetParam_mseCoact(paramserie, startseq, endseq,
                                               mse_coact,
                                               typ, best=self.onlyBestInSet)
                    self.plotBhvSet(optSet.behavs, optSet.pairs, startseq, endseq)

    def show_param_Curs(self):
        if self.cursor_active == 1:
            optSet = self.optSet
            self.bhvPlot.update()
            angmin = self.bhvPlot.minX
            angmax = self.bhvPlot.maxX
            txttmp = "selection of angles between {} and {}"
            print(txttmp.format(self.bhvPlot.minX, self.bhvPlot.maxX))
            self.mseplt_itm.clear()
            self.clearParam()

            self.bhvPlot.plot_item.clearPlots()
            if self.main_mode is False:     # if called from "makeGraphs"
                # self.source_df_bhvremain is given by "makeGraphs"
                df_bhvremain = copy.deepcopy(self.source_df_bhvremain)
                # print df_bhvremain
                df_parremain = copy.deepcopy(self.source_df_parremain)
                listdf_bhv = [df_bhvremain]
                listdf_par = [df_parremain]
            else:
                startseq = 0
                endseq = len(optSet.behavs)
                tup = self.get_df_remain(optSet.behavs, optSet.pairs,
                                         startseq, endseq,
                                         dic_mse_filter=self.dicSelectedMseThr,
                                         by_series="mse")
                listdf_bhv, listdf_par = tup
                df_bhvremain = copy.deepcopy(listdf_bhv[0])
                df_parremain = copy.deepcopy(listdf_par[0])

            endang_OK = df_bhvremain['endangle'] > angmin
            df_bhvremain = df_bhvremain[endang_OK]
            df_parremain = df_parremain[endang_OK]
            endang_OK = df_bhvremain['endangle'] < angmax
            df_bhvremain = df_bhvremain[endang_OK]
            df_parremain = df_parremain[endang_OK]
            df_bhvrest = copy.deepcopy(listdf_bhv[0])
            rgserie = np.array(df_bhvremain.rgserie)
            original_rgserie = np.array(df_bhvrest.rgserie)
            exc_rgser = np.array([i for i in original_rgserie
                                  if i not in rgserie])
            df_bhvrest_notOK = df_bhvrest.loc[exc_rgser]
            # ####################################################
            self.plot_df_bhv([df_bhvrest_notOK], col="y")
            # ####################################################
            self.bhvPlot.df_parremain = df_parremain
            self.df_parremain = df_parremain
            self.df_bhvremain = df_bhvremain
            if len(self.df_parremain) > 0:
                codeCoul_df, lut = set_rainbow_colors(self, [df_bhvremain])
                self.bhvPlot.codeCoul_df = codeCoul_df
                self.plot_df_bhv_rainbow([df_bhvremain], codeCoul_df, lut)
                self.plotPar_rainbow([df_parremain], codeCoul_df, lut)
                self.plotOtherParam_rainbow([df_parremain], codeCoul_df, lut)
                """
                varx = 'endangle'
                vary = 'dur_mvt2'
                varz = 'dur_mvt2'
                brushes = self.plot_df_bhv_rainbow2([df_bhvremain],
                                                    varx, vary, varz)

                self.plotPar_rainbow2([df_parremain], brushes)
                self.plotOtherParam_rainbow2([df_parremain], brushes)
                """
                # self.plotOtherParam_rainbow(self.select_paramSer[:],
                #                            pen=3, symbol="o", symbolBrush=2,
                #                            codeCoul_df=codeCoul_df)

            else:
                print("No behaviour with such criteria")

    def clearBhv(self):
        self.bhvPlot.plot_item.clearPlots()

    def showAllBhvs(self):
        optSet = self.optSet
        datastructure = optSet.datastructure
        for idx in range(len(datastructure)):
            # typ = datastructure[idx][0]
            startseq = datastructure[idx][1] - 1
            endseq = datastructure[idx][2] - 1
            # print startseq, endseq
            # conditions = datastructure[idx][4]
            self.plotBhvSet(optSet.behavs, optSet.pairs, startseq, endseq)

    def selctValidBehav(self, behavs, pairs, startseq, endseq,
                        stangl=0, st_err=1,
                        minampl=10, maxCoactP=0.01):
        if len(behavs) > 1:
            df_behav = pd.DataFrame(behavs[startseq:endseq], columns=self.bhv_names,
                                    index=np.arange(len(behavs[startseq:endseq])))
        elif len(behavs) == 1:
            df_behav = pd.DataFrame(behavs[:], columns=self.bhv_names,
                                    index=np.arange(len(behavs[:])))
        else:
            return (None, None)
        list_names = copy.deepcopy(self.xparName)
        list_names.append("mse")
        list_names.append("coactPen")
        df_param = pd.DataFrame(pairs[startseq:endseq],
                                columns=list_names,
                                index=np.arange(len(pairs[startseq:endseq])))
        """
        if len(optSet.pairs) > 1:
            df_param = pd.DataFrame(optSet.pairs[startseq:endseq],
                                    columns=list_names,
                                    index=np.arange(len(optSet.pairs[startseq:endseq])))
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

        # pd.set_option('precision', 3)
        pd.set_option("display.precision", 3)
        pd.set_option('expand_frame_repr', True)

        # ========    selection of data by startseq angle   =========
        # print(df_behav)
        startang_OK = abs(stangl - df_behav['startangle']) < st_err
        df_behav = df_behav[startang_OK]
        df_param = df_param[startang_OK]

        # =====    selection of data by minimum amplitude   ======
        # print(df_behav)
        ampl_OK = df_behav['endangle'] - df_behav['startangle'] > minampl
        df_behav = df_behav[ampl_OK]
        df_param = df_param[ampl_OK]

        # ========    selection of data by coactP level   =========
        # print(df_behav)
        coact_OK = df_behav['coactpen'] < maxCoactP
        df_behav = df_behav[coact_OK]
        df_param = df_param[coact_OK]
        # print('coactpen < 0.01')
        # print df_behav
        return (df_behav, df_param)

    def plotBhvSet(self, behavs, pairs, startseq, endseq,
                   dic_mse_filter={'mse_threshold1': 1.0},
                   dic_cst_filter={},
                   by_series=None,
                   max_coactP=0.01):
        """
        plots the duration against the amplitude of movements
        only movements for which    mse < mse_threshold
                                    startangle # 0°
                                    coactP < 0.01
        """
        listdf_bhv, listdf_par = self.get_df_remain(behavs, pairs,
                                                    startseq, endseq,
                                                    dic_mse_filter,
                                                    dic_cst_filter,
                                                    by_series,
                                                    max_coactP=max_coactP)
        if verbose > 2:
            print(listdf_bhv)
        self.plot_df_bhv(listdf_bhv)

# TODO : to continue GEP procedures

    def get_df_remain(self, behavs, pairs, startseq, endseq,
                      dic_mse_filter={'mse_threshold1': 1.0},
                      dic_cst_filter={},
                      by_series=None,
                      max_coactP=0.01):
        if len(dic_mse_filter) == 0:
            dic_mse_filter = {'mse_threshold1': 1.0}
        msethrname = list(dic_mse_filter.keys())[0]
        mseThr = dic_mse_filter[msethrname]

        # =====================================================================
        (df_behav, df_param) = self.selctValidBehav(behavs, pairs,
                                                    startseq, endseq+1,
                                                    maxCoactP=max_coactP)
        # =====================================================================

        listdf_bhv = []
        listdf_par = []
        df_bhvremain = copy.deepcopy(df_behav)
        df_parremain = copy.deepcopy(df_param)

        varmse_OK = df_bhvremain['varmse'] <= mseThr
        df_bhvremain = df_bhvremain[varmse_OK]
        df_parremain = df_parremain[varmse_OK]
        listdf_bhv.append(df_bhvremain)
        listdf_par.append(df_parremain)
        # print(df_bhvremain)

        if by_series == "mse":
            # ============    selection of data by mse    ============
            # print(df_behav)
            if len(dic_mse_filter) > 1:
                listdf_par = []
                listdf_bhv = []
                df_bhvremain = copy.deepcopy(df_behav)
                df_parremain = copy.deepcopy(df_param)
                list_mse = self.firstSelectedMseThr
                """
                for idx, msethrname in enumerate(self.list_mse_thr_names):
                    if msethrname in list_mse:
                """
                for msethrname in list_mse:
                    mseThr = dic_mse_filter[msethrname]
                    # print(idx, msethrname, mseThr)
                    varmse_OK = df_bhvremain['varmse'] <= mseThr
                    varmse_notOK = df_bhvremain['varmse'] > mseThr
                    print("mse <", mseThr)
                    if len(df_bhvremain[varmse_OK]) > 0:
                        print(df_bhvremain[varmse_OK])
                    else:
                        print("dataframe empty")
                    listdf_bhv.append(df_bhvremain[varmse_OK])
                    df_bhvremain = df_bhvremain[varmse_notOK]
                    # #
                    listdf_par.append(df_parremain[varmse_OK])
                    df_parremain = df_parremain[varmse_notOK]

        if by_series == "cst":
            # ========    selection of data by constant par    =======
            # print df_behav
            if len(dic_cst_filter) > 0:
                for grNb, constNam in enumerate(self.listParNamesFilter):
                    # listcst_df_par = []
                    list_const_lim = dic_cst_filter[constNam]
                    # df_parremain = copy.deepcopy(df_param)
                    """
                    for idx, constname in enumerate(self.list_const_items):
                        if constname in list_const_lim:
                    """
                    for idx_cstVal, cstVal in enumerate(list_const_lim):
                        # print idx, constname, cstVal
                        cst_OK = df_parremain[constNam] <= cstVal
                        cst_notOK = df_parremain[constNam] > cstVal
                        if idx_cstVal > 0:
                            print(constNam, list_const_lim[idx_cstVal-1], end=' ')
                            print("< cst < or =", cstVal)
                        else:
                            print("cst < or =", cstVal)
                        print(df_bhvremain[cst_OK])
                        listdf_bhv.append(df_bhvremain[cst_OK])
                        df_bhvremain = df_bhvremain[cst_notOK]
                        # #
                        # listcst_df_par.append(df_parremain[cst_OK])
                        # df_parremain = df_parremain[cst_notOK]
                        listdf_par.append(df_parremain[cst_OK])
                        df_parremain = df_parremain[cst_notOK]
        return listdf_bhv, listdf_par

    def plot_df_bhv_rainbow(self, listdf_bhv, codeCoul_df, lut):
        """
        Uses colors from a lut made by set_rainbow_color(df_bhv) that gives
        codeCoul (a df issued from df_bhv that contains a color code column)
        and the lut (corresponding to the color code)
        Works with active cursors
        """
        tmpbhv_df = listdf_bhv[0]
        # dflist_x = tmpbhv_df.endangle
        # dflist_y = tmpbhv_df.dur_mvt2
        dflist_x = tmpbhv_df.loc[:][self.bhv_names[self.behav_col[0]]]
        dflist_y = tmpbhv_df.loc[:][self.bhv_names[self.behav_col[1]]]
        for rg in codeCoul_df["rgserie"]:
            color = int(codeCoul_df.loc[rg]["color"])
            s = pg.ScatterPlotItem([dflist_x.loc[rg]],
                                   [dflist_y.loc[rg]],
                                   size=6, pen=pg.mkPen(None))
            coul = lut[color]
            r, v, b = coul[0], coul[1], coul[2]
            s.setBrush(QtWidgets.QBrush(QtWidgets.QColor(r, v, b)))
            self.bhvPlot.plot_item.addItem(s)

    def plot_df_bhv_rainbow2(self, listdf_bhv, varx, vary, varz):
        """
        Builds its list of brushes corresponding to a list of values (sequence)
        with the function get_brushes_from_gist(sequence).
        Uses pg.ScatterPlotItem to draw the scatter plot in the window
        and then colors the dots with the brushes
        ATTENTION!!! Does no Work with active cursors !!!!!!
        """
        tmpbhv_df = listdf_bhv[0]
        dflist_x = tmpbhv_df[varx]
        dflist_y = tmpbhv_df[vary]
        dflist_z = tmpbhv_df[varz]
        """
        data = []
        for i in range(len(dflist_x)):
            data.append([dflist_x[i], dflist_y[i]])
        """
        brushes = get_brushes_from_gist(dflist_z)
        # this first method build the whole grape in a single step
        """"
        s = pg.ScatterPlotItem(size=3, pen=pg.mkPen(None))
        # s.setData(pos=data, brush=brushes)    # in a single command...
        s.setData(pos=data)                     # or in two separated commands
        s.setBrush(brushes)
        self.bhvPlot.plot_item.addItem(s)
        """

        # This second method built the graph dot by dot
        for idx, rgserie in enumerate(tmpbhv_df["rgserie"]):
            s = pg.ScatterPlotItem([dflist_x.loc[rgserie]],
                                   [dflist_y.loc[rgserie]],
                                   size=3, pen=pg.mkPen(None))
            s.setBrush(brushes[idx])
            self.bhvPlot.plot_item.addItem(s)
        return brushes

    def clicked(self, plotdataitem, points_clicked):
        # print("clicked points", points_clicked)
        for p in points_clicked:
            p.setPen('b', width=2)
        x = points_clicked[0].pos().x()
        y = points_clicked[0].pos().y()
        print((x, y))
        self.selected_bhv.append([x, y])
        self.lastClicked.append(points_clicked)

    def unselect_clicked(self):
        lastClicked = self.lastClicked
        for p in lastClicked:
            p[0].resetPen()
        self.lastClicked = []
        self.selected_bhv = []

    def plot_df_bhv(self, listdf_bhv, col=None):
        listcolors = []
        for i in range(20):
            listcolors.append(pg.intColor(i, 6, maxValue=128))

        for idx, tmp_df in enumerate(listdf_bhv):
            if col is None:
                color = listcolors[idx]
            else:
                color = col
            behav_val_array = np.array(tmp_df)[:, self.behav_col]
            s1 = pg.ScatterPlotItem(size=7,
                                    symbol='o',
                                    symbolBrush=color,
                                    # pen=pg.mkPen(None),
                                    # brush=pg.mkBrush(255, 255, 255, 120),
                                    brush=color
                                    )

            # self.bhvPlot.plot_item.plot(behav_val_array[:, 0],
            #                             behav_val_array[:, 1],
            #                             pen=None, symbol='o',
            #                             symbolBrush=color)
            pos = np.array([behav_val_array[:, 0], behav_val_array[:, 1]])
            s1.addPoints(x=pos[0], y=pos[1])
            self.bhvPlot.plot_item.addItem(s1)
            s1.sigClicked.connect(self.clicked)
            # ==============================================================
            QtWidgets.QApplication.processEvents()
            # ==============================================================

    def makeDensityMap(self, rel_behavs_cues, step=0.05):
        """
        builds a matrix containing the number of elements in each unit surface
        (squarre step x step) covering the X and the Y range of behavs_cues
        """
        # make a copy of the datafrae rel_behavs_cues
        df = copy.deepcopy(rel_behavs_cues)
        if len(rel_behavs_cues) == 1:
            None
            xgr = max(df[df.columns[0]])
            ygr = max(df[df.columns[1]])
            density_map = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
            listx = np.linspace(xgr - step, xgr + step, 3)
            listy = np.linspace(ygr - step, ygr + step, 3)
        else:
            # we get the min value in the first column of the dataframe
            xmin = min(df[df.columns[0]]) - step
            # we get the max value in the first column of the dataframe
            xmax = max(df[df.columns[0]])
            xmin_gr = int(xmin/step) * step
            xmax_gr = (int(xmax/step) + 1) * step
            print(xmin, xmax)
            ymin = min(df[df.columns[1]]) - step
            ymax = max(df[df.columns[1]])
            ymin_gr = int(ymin/step) * step
            ymax_gr = (int(ymax/step) + 1) * step
            print(ymin, ymax)
            listx = np.linspace(xmin_gr, xmax_gr,
                                int((xmax_gr-xmin_gr)/step)+2)
            listy = np.linspace(ymin_gr, ymax_gr,
                                int((ymax_gr-ymin_gr)/step)+2)

            density_map = []
            xmin = min(df[df.columns[0]])
            xmax = max(df[df.columns[0]])
            print(xmin, xmax)
            ymin = min(df[df.columns[1]])
            ymax = max(df[df.columns[1]])
            print(ymin, ymax)
            for yval in listy:
                res = []
                for xval in listx:
                    # print(x*step, y*step)
                    tmp_df = copy.deepcopy(df)
                    onTheSpotx1 = (tmp_df[tmp_df.columns[0]] > xval)
                    tmp_df = tmp_df[onTheSpotx1]
                    onTheSpotx2 = (tmp_df[tmp_df.columns[0]] < xval+step)
                    tmp_df = tmp_df[onTheSpotx2]
                    onTheSpoty1 = (tmp_df[tmp_df.columns[1]] > yval)
                    tmp_df = tmp_df[onTheSpoty1]
                    onTheSpoty2 = (tmp_df[tmp_df.columns[1]] < yval+step)
                    tmp_df = tmp_df[onTheSpoty2]
                    # print(len(tmp_df))
                    res.append(len(tmp_df))
                density_map.append(res)
        return density_map, listx, listy

    def test_for_save_map_bhv(self, df_bhvremain, affich=0):
        """
        Saves map_behav only once for each level (according to
        self.list_save_steps)
        """
        if affich == 1:
            print("list_save_steps: ", self.list_save_steps)
            print("list_save_flags: ", optSet.list_save_flags)
        for stp_idx in range(len(self.list_save_steps)):
            rg = len(self.list_save_steps) - stp_idx - 1
            stp = self.list_save_steps[rg]
            if affich == 1:
                print(rg, stp, end=' ')
            if len(df_bhvremain) < stp:
                None
                if affich == 1:
                    print(" > df_bhvramain size (", len(df_bhvremain), end=' ')
                    print(") => don't save")
            else:
                if affich == 1:
                    print(" < df_bhvramain size(", len(df_bhvremain), ")", end=' ')
                if optSet.list_save_flags[rg] == 0:
                    name = ""
                    if self.GEP_rootname != "":  # data saved on the same file
                        print(self.GEP_rootname)
                        name = self.GEP_rootname
                    else:                        # data saved on a new file
                        GEP_rootname = getGEPdataFileName(optSet)
                        name = GEP_rootname
                    GEP_graph_dir = os.path.join(self.animatsimdir, "GEPdata")
                    self.save_map_behav(df_bhvremain, GEP_graph_dir, name)
                    optSet.list_save_flags[rg] = 1
                    for i in range(rg):
                        optSet.list_save_flags[i] = 1
                    print("************** bhvplot saved **************")
                else:
                    None
                    if affich == 1:
                        print("not saved")

    def save_map_behav(self, df_bhvremain, GEP_graph_dir, name,
                       max_x=1.2, max_y=1.4):
        """
        saves the df_bhvremain dataframe
        """
        length = len(df_bhvremain)
        if length < 0:
            exit()
        behavs_cues = df_bhvremain[df_bhvremain.columns[self.behav_col]]
        rel_behavs_cues = behavs_cues/[self.scale_x, self.scale_y]
        nameX = rel_behavs_cues.columns[0]
        nameY = rel_behavs_cues.columns[1]
        valX = rel_behavs_cues[nameX]
        valY = rel_behavs_cues[nameY]
        figure, ax = plt.subplots(figsize=(7, 7))
        # figure, ax = plt.subplots()
        plt.scatter(valX, valY, marker='o', s=4)
        if self.behav_col[1] == 8:      # if ordonate is duration...
            labelnameX = nameX + "(x 0.01)"
            labelnameY = nameY
        elif self.behav_col[1] == 6:
            labelnameX = nameX + "(x 0.01)"
            labelnameY = nameY + "(x 0.01)"
        ax.set_xlabel(labelnameX)
        ax.set_ylabel(labelnameY)
        ax.set_axisbelow(True)
        ax.set_xlim(0, max_x)
        ax.set_ylim(0, max_y)
        ax.grid(linestyle='-', linewidth='0.5', color='gray')
        # GEP_graph_dir = os.path.join(dest, "GEPdata")
        if not os.path.exists(GEP_graph_dir):
            os.makedirs(GEP_graph_dir)
        pdfFileName = r'{0}\{1}_{2}.pdf'.format(GEP_graph_dir,
                                                name,
                                                length)
        epsFileName = r'{0}\{1}_{2}.eps'.format(GEP_graph_dir,
                                                name,
                                                length)
        if not os.path.exists(pdfFileName):
            plt.savefig(pdfFileName)
        else:
            print("file already exists")
            n = 0
            while os.path.exists(r'{0}\{1}_{2}({3}).pdf'.format(GEP_graph_dir,
                                                                name,
                                                                length,
                                                                n)):
                n += 1
            pdfFileName = r'{0}\{1}_{2}({3}).pdf'.format(GEP_graph_dir,
                                                         name,
                                                         length,
                                                         n)
            plt.savefig(pdfFileName)

        if not os.path.exists(epsFileName):
            plt.savefig(epsFileName)
        else:
            n = 0
            while os.path.exists(r'{0}\{1}_{2}({3}).eps'.format(GEP_graph_dir,
                                                                name,
                                                                length,
                                                                n)):
                n += 1
            epsFileName = r'{0}\{1}_{2}({3}).eps'.format(GEP_graph_dir,
                                                         name,
                                                         length,
                                                         n)
            plt.savefig(epsFileName)
        plt.show()

    def plot_map_behav(self, df_bhvremain, aimbhv=[]):
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
        if self.behav_col[1] == 8:      # if ordonate is duration...
            labelnameX = nameX + "(x 0.01)"
            labelnameY = nameY
        elif self.behav_col[1] == 6:
            labelnameX = nameX + "(x 0.01)"
            labelnameY = nameY + "(x 0.01)"
        # figure, ax = plt.subplots()
        plt.scatter(valX, valY, marker='o', s=4)
        ax.set_xlabel(labelnameX)
        ax.set_ylabel(labelnameY)
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

    def plot_3D_density_map(self, df_bhvremain, step=0.02,
                            incline=60, rot=-90):
        """
        Plots a 3D-Graph using the density_map and the listx, listy to build
        a X, Y grid
        """
        behavs_cues = df_bhvremain[df_bhvremain.columns[self.behav_col]]
        rel_behavs_cues = behavs_cues/[self.scale_x, self.scale_y]
        nameX = rel_behavs_cues.columns[0]
        nameY = rel_behavs_cues.columns[1]
        if self.behav_col[1] == 8:      # if ordonate is duration...
            labelnameX = nameX + "(x 0.01)"
            labelnameY = nameY
        elif self.behav_col[1] == 6:
            labelnameX = nameX + "(x 0.01)"
            labelnameY = nameY + "(x 0.01)"
        density_map, listx, listy = self.makeDensityMap(rel_behavs_cues,
                                                        step=step)
        X, Y = np.meshgrid(listx, listy)
        Z = np.array(density_map)
        fig = plt.figure(figsize=(7, 7), dpi=100)
        ax = plt.axes(projection='3d')
        ax.contour3D(X, Y, Z, 50, cmap='cool')
        # ax.contour3D(X, Y, Z, 50, cmap='binary')
        # ax.contour3D(X, Y, Z, 50, cmap='viridis')
        ax.set_xlabel(labelnameX)
        ax.set_ylabel(labelnameY)
        ax.set_zlabel("Nb evts")
        ax.view_init(incline, rot)
        fig.show()

    def plot_2D_density_map(self, df_bhvremain, step=0.02, aimbhv=[]):
        """
        Plots a 2D-Graph using the density_map and the listx, listy to build
        a X, Y grid
        """
        behavs_cues = df_bhvremain[df_bhvremain.columns[self.behav_col]]
        rel_behavs_cues = behavs_cues/[self.scale_x, self.scale_y]
        if self.behav_col[1] == 8:      # if ordonate is duration...
            nameX = rel_behavs_cues.columns[0] + "(x 0.01)"
            nameY = rel_behavs_cues.columns[1]
        elif self.behav_col[1] == 6:
            nameX = rel_behavs_cues.columns[0] + "(x 0.01)"
            nameY = rel_behavs_cues.columns[1] + "(x 0.01)"
        density_map, listx, listy = self.makeDensityMap(rel_behavs_cues,
                                                        step=step)
        X, Y = np.meshgrid(listx, listy)
        Z = np.array(density_map)
        Z[Z == 0] = -10   # replace all 0 by -10
        fig = plt.figure(figsize=(7, 6), dpi=100)
        nbniv = int(np.amax(Z))
        plt.contourf(X, Y, Z, nbniv, cmap='cool')
        # plt.contourf(X, Y, Z, nbniv, cmap=mpl.colormaps['Blues'](30))
        plt.colorbar()
        plt.xlabel(nameX)
        plt.ylabel(nameY)
        for point in aimbhv:
            x = point[0]-self.scale_x*step/2
            y = point[1]-self.scale_y*step/2
            relx, rely = x/self.scale_x, y/self.scale_y
            plt.plot(relx, rely, '-p', color='gray',
                     markersize=5, linewidth=4,
                     markerfacecolor='white',
                     markeredgecolor='gray',
                     markeredgewidth=2)
        fig.show()

    def update_df_bhvremain(self, mseThr=1.0,
                            stangl=0, st_err=1,
                            minampl=10, maxCoactP=0.01,
                            default=True):
        df_bhvremain = []
        behavs = optSet.behavs
        pairs = optSet.pairs
        if len(behavs) > 0:
            startseq = 0
            endseq = len(behavs)
            # =====================================================================
            res = self.selctValidBehav(behavs, pairs, startseq, endseq,
                                       stangl=stangl, st_err=st_err,
                                       minampl=minampl,
                                       maxCoactP=maxCoactP)
            (df_behav, df_param) = res
            # =====================================================================
            df_bhvremain = copy.deepcopy(df_behav)
            df_parremain = copy.deepcopy(df_param)
            varmse_OK = df_bhvremain['varmse'] <= mseThr
            df_bhvremain = df_bhvremain[varmse_OK]
            df_parremain = df_parremain[varmse_OK]
            if default is True:
                self.df_bhvremain = df_bhvremain
                self.df_parremain = df_parremain
                self.source_df_bhvremain = df_bhvremain
                self.source_df_parremain = df_parremain
            # print(df_bhvremain)
        return df_bhvremain

    def find_df_bvh_2ndChoice(self):
        print()
        print("######################################################")
        print(" No behavior data in memory !! --> look for best vmse")
        print("######################################################")
        df_bhvremain2 = self.update_df_bhvremain(mseThr=100,
                                                 st_err=20,
                                                 minampl=0,
                                                 maxCoactP=100,
                                                 default=False)
        if len(df_bhvremain2) > 0:
            ser_bhv2_sorted = df_bhvremain2.varmse.sort_values(ascending=True)
            indexes = ser_bhv2_sorted.index
            if len(indexes) > 10:
                indexes2 = indexes[:10]
            else:
                indexes2 = indexes
            df_bhv_selected = df_bhvremain2.loc[indexes2]
        else:
            df_bhv_selected = []
        return df_bhv_selected

    def bhv_selectMseThr(self, oneOnly=0):
        if oneOnly == 1:
            self.listDicItBhvMse = [{'mse_threshold': []}]
        listChoix = list(self.listDicItBhvMse[0].keys())
        titleText = "select mse_thresholds and set their values"
        rep = ChooseInList.listTransmit(parent=None,
                                        graphNo=0,
                                        listChoix=listChoix,
                                        items=self.list_mse_thr_names,
                                        listDicItems=self.listDicItBhvMse,
                                        onePerCol=[oneOnly],
                                        colNames=["mse", "Value"],
                                        dicValues=self.listdicmsethr[0],
                                        typ="val",
                                        titleText=titleText)
        self.listDicItBhvMse = rep[0]
        if len(rep[1]) == 0:    # No values entered,  ESC button was used
            return
        self.firstSelectedMseThr = []
        self.dicSelectedMseThr = {}
        for i in range(len(self.listDicItBhvMse[0][listChoix[0]])):
            itemName = self.listDicItBhvMse[0][listChoix[0]][i]
            self.firstSelectedMseThr.append(itemName)
            self.listdicmsethr[0][itemName] = float(rep[1][itemName])
            self.dicSelectedMseThr[itemName] = float(rep[1][itemName])
            print(itemName, rep[1][itemName])

    def chooseParamFilters(self):
        # self.listDicParamFilter = [{"paramFilter": []}]
        listChoix = ["paramFilter"]
        titleText = "select parameters to filter GEP data"
        rep = ChooseInList.listTransmit(parent=None,
                                        graphNo=0,
                                        listChoix=listChoix,
                                        items=self.xparName,
                                        listDicItems=self.listDicParamFilter,
                                        onePerCol=[1],
                                        colNames=["paramFilter"],
                                        typ="chk",
                                        titleText=titleText)
        self.listDicParamFilter = rep[0]
        self.listParNamesFilter = self.listDicParamFilter[0]['paramFilter']

    def bhv_selectCstVal(self):
        # if len(self.listParNamesFilter) == 0:
        self.chooseParamFilters()
        self.lstDicBhvCst_itm = []
        for constNam in self.listParNamesFilter:
            self.lstDicBhvCst_itm.append({constNam: []})
        self.dicSelectedCstFilt = {}

        for grNb, constNam in enumerate(self.listParNamesFilter):
            listChoix = [constNam]
            titleText = "select constant params and set their values"
            rep = ChooseInList.listTransmit(parent=None,
                                            graphNo=grNb,
                                            listChoix=listChoix,
                                            items=self.list_const_items,
                                            listDicItems=self.lstDicBhvCst_itm,
                                            onePerCol=[0],
                                            colNames=[constNam, "Value"],
                                            dicValues=self.listdiccstFlt[grNb],
                                            typ="val",
                                            titleText=titleText)
            self.lstDicBhvCst_itm = rep[0]
            if len(rep[1]) == 0:    # No values entered,  ESC button was used
                return
            self.firstSelectedConstFilt = []

            list_sel_CstVals = []
            print(constNam)
            for idx, itm in enumerate(self.lstDicBhvCst_itm[grNb][constNam]):
                list_sel_CstVals.append(float(rep[1][itm]))
                self.firstSelectedConstFilt.append(itm)
                self.listdiccstFlt[grNb][itm] = float(rep[1][itm])
                print("\t", itm, rep[1][itm])
            self.dicSelectedCstFilt[constNam] = list_sel_CstVals

    # =========================================================================
    """
                           Simulations Procedures
    """
    # =========================================================================

    def do_syst_param(self):
        if self.modelchanged != 1:
            exec_syst_param(self, optSet)
        else:
            print("This is a different model: run animatLabOptimSettings")

# TODO : debut GEP_rand

    def do_GEP_rand(self):
        self.nbGEPextend = int(self.value_nbExt.text())
        self.nbGEPfill = int(self.value_nbFill.text())
        optSet.gravity = float(self.editValueGravity.text())
        setGravity(model, optSet.gravity)
        self.chk_varmse.setChecked(True)  # self.randParEvol --> "varmse"
        if self.modelchanged != 1:
            self.btn_GEPrand.setStyleSheet('QPushButton {background-color: #A3C1DA;\
                                                         color: red;}')
            # df_bhvremain = self.update_df_bhvremain(mseThr=1.0)
            if self.GEPauto == 0:
                self.exec_gep_rand(optSet)
            else:
                df_bhvremain = self.update_df_bhvremain(mseThr=1.0)
                if len(df_bhvremain) > 0:
                    find_aim_behav(self, optSet)
                else:
                    print("NO VALID BEHAVIOR to start rGEP")
            # self.save_paramNames_bhvNames()
            self.btn_GEPrand.setStyleSheet('QPushButton {background-color: #A3C1DA;\
                                                         color: blue;}')
            self.save_paramNames_bhvNames()
        else:
            print()
            print()
            print("*****************************************************")
            print("This is a different model: run animatLabOptimSettings")
            print("*****************************************************")

    def do_rand_param(self):
        # if self.scrip_mode == "GEP":
        #     self.randParEvol = "varmse"
        self.btnstate_MSE()     # verify the status of randParEvol
        self.btnstate_varmse()  # verify the status of randParEvol
        optSet.gravity = float(self.editValueGravity.text())
        setGravity(model, optSet.gravity)
        if self.modelchanged != 1:
            self.btn_randParam.setStyleSheet('QPushButton {background-color: #A3C1DA;\
                                                           color: red;}')
            exec_rand_param(self, "rdparam", optSet)
            self.btn_randParam.setStyleSheet('QPushButton {background-color: #A3C1DA;\
                                                           color: blue;}')
        else:
            print()
            print()
            print("*****************************************************")
            print("This is a different model: run animatLabOptimSettings")
            print("*****************************************************")

    def runCMAeFromGUI(self):
        if self.modelchanged != 1:
            self.btn_CMAes.setStyleSheet('QPushButton {background-color: #A3C1DA;\
                                                       color: red;}')
            optSet.gravity = float(self.editValueGravity.text())
            setGravity(model, optSet.gravity)
            exec_CMAeFromGUI(self, optSet, projMan)
            self.btn_CMAes.setStyleSheet('QPushButton {background-color: #A3C1DA;\
                                                       color: blue;}')
        else:
            print()
            print()
            print("*****************************************************")
            print("This is a different model: run animatLabOptimSettings")
            print("*****************************************************")

    def runVSCDFromGUI(self):
        self.btn_VSCD.setStyleSheet('QPushButton {background-color: #A3C1DA;\
                                                  color: red;}')
        optSet.nbepoch = int(self.nbepochValueLine.text())
        optSet.deltacoeff = float(self.deltacoeffValue.text())
        # optSet.nbsyntrials = int(self.nbsyntrialsValue.text())
        optSet.nbsteps = int(self.nbstepsValue.text())
        optSet.xCoactPenality1 = float(self.valueCoactPen1.text())
        optSet.xCoactPenality2 = float(self.valueCoactPen2.text())
        optSet.gravity = float(self.editValueGravity.text())
        setGravity(model, optSet.gravity)
        print("optSet.nbepoch", optSet.nbepoch)
        print("optSet.nbsteps", optSet.nbsteps)
        print("optSet.deltacoeff", optSet.deltacoeff)
        print("optSet.xCoactPenality1", optSet.xCoactPenality1)
        print("optSet.xCoactPenality2", optSet.xCoactPenality2)
        exec_VSCD_from_gui(self, optSet, projMan, folders, model)
        self.btn_VSCD.setStyleSheet('QPushButton {background-color: #A3C1DA;\
                                                  color: blue;}')

    def get_paramserie(self, x, rgpar, step, Lst_deltaCo, span):
        """
        Method get_paramserie
            In : self
                x : A set of parameters
                rgpar : The rank of the parameter we're looking at
                step : The iteration we're at
                Lst_deltaCo : the list of the delta coeff used in execVSCD
                span : the variability allowed to our parameters
            Out : paramserie : a list of list of parameters value composed of
                            paramsetminus : the parameter set with lower values
                            paramsetplus : the parameter set with higher values
                            paramsetbase : the first values of the parameters
                lstvals : a list which contains the values of the parameter to
                        test, 3 values : base, minus, plus
            This method modify the parameter so we can test 2 sets around the
            the base value
        """
        # We get the parameters's value
        paramset = np.array(x[:])
        # We create an array which will contain the lower parameters
        paramsetminus = np.array(paramset[:])
        # We create an array which will contain the higher parameters
        paramsetplus = np.array(paramset[:])
        # We create an array which contains the unchanged parameters
        paramsetbase = np.array(paramset[:])
        # We get the type of the parameter we're changing
        typ_par = optSet.struct_param[self.shuffledpar[rgpar]]
        # We get the delta_coeff of the parameter we're changing
        delta = Lst_deltaCo[self.shuffledpar[rgpar]]
        # We get the value of the parameter we're changing
        val_base = x[self.shuffledpar[rgpar]]
        # If the parameter is a stimulus we just add or substract the value of
        # delta
        if typ_par == "st":
            val_minus = val_base - delta
            val_plus = val_base + delta
        # If the parameter is a synapse we divide or multiply the weight of the
        # synapse by delta
        else:
            val_minus = val_base / (delta+1)
            val_plus = val_base * (delta+1)
        paramserie = []
        # We set the value of the lower parameter to explore
        paramsetminus[self.shuffledpar[rgpar]] = val_minus
        # We set the value of the higher parameter to explore
        paramsetplus[self.shuffledpar[rgpar]] = val_plus
        # We concatenate those array in on list
        paramserie.append(paramsetminus)
        paramserie.append(paramsetplus)
        if step == 0:
            # If we're on the first step, we want to keep the base values
            paramserie.append(paramsetbase)
            # Since we have 3 sets of parameters, we randomize a table of size
            # 3*nbpar
            randset = np.ones((3, self.nbpar))
            listvals = [val_minus, val_plus, val_base]
        else:
            # paramserie.append(paramsetbase)
            # Since we have 2 sets of parameters, we randomize a table of size
            # 2*nbpar
            randset = np.ones((2, self.nbpar))
            listvals = [val_minus, val_plus]
        # We convert the list paramserie into an np array
        paramserie = np.array(paramserie)
        randset = randset*0.0001
        # We then verify that none of the parameters are below or above the
        # limits we've set
        paramserie = set_limits(paramserie, randset,
                                span, 0, 1, optSet,
                                stim_liminf=True,
                                stim_limsup=True,
                                syn_liminf=True,
                                syn_limsup=True
                                )

        return (paramserie, listvals)

    #
    #
    #
    #
    # =========================================================================
    """
                                  Other procedures
    """
    # =========================================================================

    def getNbPacket(self, packetSize, nbRandTrial):

        """
        Organizes the runs in epochs of packets. Each pacquet is subdivided in
        funtion of the number of processors
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

        nb_procs = self.nb_procs
        nbRunParam = []
        paramserieSlicesAllEpochs = []
        # reads run nb from the GUI
        if nbRandTrial > packetSize:
            nbEpochParam = int(nbRandTrial/packetSize)
            for ep in range(nbEpochParam):
                nbRunParam.append(packetSize)
                paramserieSlices = makeSliceParams(packetSize, nb_procs)
                paramserieSlicesAllEpochs.append(paramserieSlices)
            last_nbRunParam = nbRandTrial % packetSize
            if last_nbRunParam > 0:
                nbRunParam.append(last_nbRunParam)
                paramserieSlices = makeSliceParams(last_nbRunParam, nb_procs)
                paramserieSlicesAllEpochs.append(paramserieSlices)
        else:
            nbEpochParam = 1
            nbRunParam.append(nbRandTrial)
            paramserieSlices = makeSliceParams(nbRandTrial, nb_procs)
            paramserieSlicesAllEpochs.append(paramserieSlices)
        nbEpochParam = len(nbRunParam)
        return nbEpochParam, nbRunParam, paramserieSlicesAllEpochs

    def set_span(self):
        """
        """
        dicSpanVal_file = win.animatsimdir + "/GEPdata/DicSpanVal.txt"        
        if os.path.exists(dicSpanVal_file):
            dicSpanVal, listspanval = readSpan_from_DicSpanVal(dicSpanVal_file)
            self.listDicSpanVal = [dicSpanVal]
        self.listDicItspan =[{'span': self.xparName}]   
        listChoix = ['span']
        titleText = "select params with their span values"
        rep = ChooseInList.listTransmit(parent=None,
                                        graphNo=0,
                                        listChoix=listChoix,
                                        items=self.xparName,
                                        listDicItems=self.listDicItspan,
                                        onePerCol=[0],
                                        colNames=["span", "Value"],
                                        dicValues=self.listDicSpanVal[0],
                                        typ="val",
                                        titleText=titleText)
        # self.listDicItems = rep[0]
        self.listDicItspan = rep[0]
        if len(rep[1]) == 0:    # No values entered,  ESC button was used
            return
        self.listspanNames = []
        self.dicspanParam = {}
        for i in range(len(self.listDicItspan[0][listChoix[0]])):
            itemName = self.listDicItspan[0][listChoix[0]][i]
            self.listspanNames.append(itemName)
            # self.listDicSpanVal[0][itemName] = float(rep[1][itemName])
            self.dicspanParam[itemName] = float(rep[1][itemName])
            print(itemName, rep[1][itemName])
            # spanparnb = self.xparNameDict[itemName]
            # optSet.x0[spanparnb] = float(self.dicspanParam[itemName])
        zbeub = [{}]
        zbeub[0] = rep[1]
        self.refresh_span(zbeub)

    def span_setup(self):
        self.glob_span = float(self.glob_span_val.text())
        lst_fork = [{}]
        if self.chkBx_glob_span.checkState():
            print(self.chkBx_glob_span.checkState())
            for nam in self.xparName:
                # lst_fork[0][nam] = self.listDicSpanVal[0][self.xparName[0]]
                lst_fork[0][nam] = self.glob_span
            self.refresh_span(lst_fork)
            print("single span value for all", self.glob_span)
            span = self.glob_span
            optSet.spanStim, optSet.spanSyn = span, span
            self.glob_span_val.setStyleSheet("color: black;")
        else:
            self.set_span()
            self.listspanVal = [float(self.listDicSpanVal[0][nam])
                                for nam in [self.xparName][0]]
            minFork = min(self.listspanVal)
            maxFork = max(self.listspanVal)
            if minFork == maxFork:
                print("all span values equal to", self.listspanVal[0])
                self.chkBx_glob_span.setCheckState(2)
                print(self.chkBx_glob_span.checkState())
                self.glob_span_val.setStyleSheet("color: black;")
            else:
                print("span values different:", self.listspanVal)
                self.glob_span_val.setStyleSheet("color: lightgray;")

    def refresh_span(self, val):
        self.listDicSpanVal = [{}]
        for name in list(val[0].keys()):
            self.listDicSpanVal[0][name] = float(val[0][name])
        print(self.listDicSpanVal)
        self.listspanVal = [float(self.listDicSpanVal[0][nam])
                            for nam in [self.xparName][0]]

    def reset_span(self):
        self.listDicSpanVal[0][self.xparName[0]] = self.DEFAULT_span_VALUE
        self.span_setup()

# TODO : continuer l'implementation du GEP créer de nouveaux charts
    def build_charts(self):
        print("\nCreate new charts...")
        title = "                   *** INSTRUCTIONS ***                       "
        info = "Create new charts from valid params.\n"
        info += "A new subdirectory 'trial-0_sampledCharts' "
        info += "will be created, with all required sub-diretories "
        message =  "1- GEPdata00.par file must be opened first.\n"
        message += "2- Choose the number of Charts you want to extract from "
        message += "this experiment.\n"
        message += "3- The script will extract the required number of charts "
        message += "from the list of valid parameters, by choosing regularly "
        message += "spaced parameter sets and runing them.\n"
        InfoWindow(title, info, message=message)
        titre = "Creatioin of New Charts"
        info = "Do you want to launch creation?"
        details = "This will execute the number of runs you will indicate"
        rep = dialogWindow(titre, info, details=details)
        if rep == True:
            print("c'est parti!!!")
            if len(self.df_parremain) > 0:
                print(self.df_parremain)
                nb_bhvOK = len(self.df_parremain)
                
                winscr = DialogBoxValues()
                nbRunsStr = str(nb_bhvOK)
                text = "max= {}   Edit value".format(nbRunsStr)
                rep = winscr.editText("Nb New Charts", text, nbRunsStr)
                print(type(rep))
                if rep != None:
                    nbNewCharts = int(rep)
                    self.launch_CreateNewCharts(nbNewCharts)

    def launch_CreateNewCharts(self, nbNewCharts):
        self.newDestFolder = self.create_new_folder_for_GEP(typ="_forCharts")
        self.select_df_bhvremain = self.df_bhvremain
        nb_bhvOK = len(self.df_parremain)
        lstIndex = list(self.df_bhvremain.index)
        rg_start = int(optSet.datastructure[0][2])
        step = round((nb_bhvOK - rg_start)/nbNewCharts)
        selected = []
        self.rg_bhv_selected = []
        for idx, rg in enumerate(range(rg_start, nb_bhvOK, step)):
            print(rg, " ", end="")
            selected.append(rg)
            self.rg_bhv_selected.append(lstIndex[rg])
        self.run_selected_param()
        self.saves_newGEPdata(seedDirCreate=False)
        

    def get_seeds(self):
        """
        Prepares a simulation environment (directory with aproj, asim and
        aform) and subdirectories:  GEPdata and ResultFile
        GEPdata folder contains:
            GEPdata00.par indicating the seeds in a datastructure form
            GEPdata00.txt contains the parameters of the seeds
            GEPdata00bhv.txt contains the behaviours of the seeds
        and saves it in the directory given by the user
        The GEPdata00.par datastructure is build after selecting a series of
        behaviors from a previous simulation folder (gives also the associated
        parameters). The movements produced by these parameters are produced
        and stored in the GEPChartFiles folder and the associated asim files
        are stored in the GEPAsimFiles folder, and the associated aproj files
        are stored in the AprojFiles folder (YYYYYYY_bestGEP-XX.aproj)
        """
        optSet.xCoactPenality1 = float(self.valueCoactPen1.text())
        optSet.xCoactPenality2 = float(self.valueCoactPen2.text())
        optSet.gravity = float(self.editValueGravity.text())
        seeds = self.choose_seeds()
        if len(seeds) > 0:
            self.newDestFolder = self.create_new_folder_for_GEP(typ="_seeds")
            self.run_selected_param()
            self.search_list_spanValues()
            self.saves_newGEPdata(seedDirCreate=True)

    def editText(self, text):
        text, okPressed = QtWidgets.QInputDialog.getText(self,
                                                         "Give Source Dir",
                                                         "Source Dir:",
                                                    QtWidgets.QLineEdit.Normal,
                                                     text)
        if okPressed:
            textOK = text
            # self.close()
        return textOK

    def get_folder_name(self, animatsimdir, typ="_seeds"):
        """
        Opens a window asking for text (filename) and returns folder name.
        """
        rootdir = os.path.dirname(animatsimdir)
        # listDir = [name for name in os.listdir(rootdir)
        #            if os.path.isdir(os.path.join(rootdir, name))]
        # listDir.sort()
        subdir = os.path.split(animatsimdir)[-1]
        rootName = self.editText(subdir)
        rootName = rootName + typ
        listDirGEPfromTyp = [name for name in os.listdir(rootdir)
                               if (os.path.isdir(os.path.join(rootdir, name))
                                   and name[0:len(rootName)] == rootName)]
        if len(listDirGEPfromTyp) < 10:
            newGEPDir_fromTyp = rootName+'0'+str(len(listDirGEPfromTyp))
        else:
            newGEPDir_fromTyp = rootName + str(len(listDirGEPfromTyp))

        return newGEPDir_fromTyp

    def create_new_folder_for_GEP(self, typ="_seeds"):
        """
        The working folder is set by animatsimdir = readAnimatLabDir()
        A new folder is created in which aproj, asim and aform files are copied
        from animatsimdir.
        Sub-directories are created (GEPdata and ResultFile)
        GEPdata folder contains:
            GEPdata00.par indicating the seeds in a datastructure form
            GEPdata00.txt contains the parameters of the seeds
            GEPdata00bhv.txt contains the behaviours of the seeds
        resultFile folder contains:
            paramOpt.pkl
            template.txt
        """
        animatsimdir = self.animatsimdir
        rootdir = os.path.dirname(animatsimdir)
        newGEPDir_fromTyp = self.get_folder_name(animatsimdir, typ=typ)
        newExpeFolder= os.path.join(rootdir, newGEPDir_fromTyp)


        os.makedirs(newExpeFolder)
        list_ext = [".aproj", ".asim", ".aform"]
        copyFileDir_ext(animatsimdir, newExpeFolder, list_ext, copy_dir=0)
        folders = FolderOrg(animatlab_root=rootdir,
                            python27_source_dir=animatLabV2ProgDir,
                            subdir=newGEPDir_fromTyp)
        # folders.affectDirectories()
        aprojSaveDir = os.path.join(folders.animatlab_rootFolder,
                                    "AprojFiles")
        if not os.path.exists(aprojSaveDir):
            os.makedirs(aprojSaveDir)
            copyFileDir(newExpeFolder,
                        aprojSaveDir,
                        copy_dir=0)
        aprojCMAeDir = os.path.join(folders.animatlab_rootFolder,
                                    "CMAeSeuilAprojFiles")
        if not os.path.exists(aprojCMAeDir):
            os.makedirs(aprojCMAeDir)
            copyFileDir(newExpeFolder,
                        aprojCMAeDir,
                        copy_dir=0)
        dirGEPdata = os.path.join(folders.animatlab_rootFolder,
                                  "GEPdata")
        if not os.path.exists(dirGEPdata):
            os.makedirs(dirGEPdata)
        src = os.path.join(self.animatsimdir, "ResultFiles")
        dst = os.path.join(newExpeFolder, "ResultFiles")
        # copyFile("paramOpt.pkl", src, dst)
        copyFile("template.txt", src, dst)
        copyFileWithExt(src, dst, ".pkl")   # copy all pickle files
        return newExpeFolder

    def choose_seeds(self):
        # rg_bhv_selected = self.choose_seeds_old()
        if len(self.selected_bhv) < 1:
            print("NO seed selected!!!!!")
            print("**** Select bhvs in bhv_window with mouse left clicks ****")
        print(self.selected_bhv)
        df_bhvremain = self.df_bhvremain
        # if len(df_bhvremain) == 0:
        try:
            startseq = 0
            endseq = len(optSet.behavs)
            tup = self.get_df_remain(optSet.behavs, optSet.pairs,
                                     startseq, endseq,
                                     dic_mse_filter=self.dicSelectedMseThr,
                                     by_series="mse")
            listdf_bhv, listdf_par = tup
            tmp_df_bhvremain = pd.concat(listdf_bhv)
            tmp_df_bhvremain.sort_values(by=['rgserie'], inplace=True)
            df_bhvremain = copy.deepcopy(tmp_df_bhvremain)
            # df_parremain = copy.deepcopy(listdf_par[0])
            self.select_df_bhvremain = df_bhvremain
            # self.select_df_parremain = df_parremain
        # else:
        #     self.select_df_bhvremain = self.df_bhvremain
        # behavs_cues = df_bhvremain[df_bhvremain.columns[self.behav_col]]
        except Exception as e:
            print(e)
        df_x = df_bhvremain[df_bhvremain.columns[self.behav_col[0]]]
        df_y = df_bhvremain[df_bhvremain.columns[self.behav_col[1]]]
        rg_bhv_selected = []
        for idx, sel in enumerate(self.selected_bhv):
            print(sel)
            valid_j = [j for j in list(df_x.index) if
                       (abs(df_x[j] - sel[0]) < 0.01)]
            valid_jj = [jj for jj in valid_j if
                        (abs(df_y[jj] - sel[1]) < 0.01)]
            if valid_jj != []:
                rg_bhv_selected.append(valid_jj[0])
        if verbose > 2:
            print(rg_bhv_selected)
        self.rg_bhv_selected = rg_bhv_selected
        for idx in self.rg_bhv_selected:
            self.varmse_selected.append(df_bhvremain["varmse"][idx])
        return self.rg_bhv_selected

    def checkChartComment(self, chartdir, chartname, idx):
        completeName = os.path.join(chartdir, chartname)
        sp = ""
        with open(completeName, 'r+') as fich:
            titre = fich.readline()
            chartname_inFic = titre[:titre.find('.txt')]
            nb_spaces = len(chartname_inFic) + len(".txt") - len(chartname)
            for i in range(nb_spaces):
                sp += " "
            print(chartname_inFic, " --> ", end=" ")
            if idx < 10:
                newchartname = "GEP_chart" + "0" + str(idx)
            else:
                newchartname = "GEP_chart" + str(idx)
            print(newchartname)
            newtitre = newchartname + titre[titre.find('.txt'):-1] + sp + "\n"
            # print(titre)
            # print(newtitre)
            fich.seek(0)
            fich.write(newtitre)
            fich.close()

    def run_selected_param(self):
        # self=MyWin.graph_settings.GUI_Gr_obj.mafen
        animatsimdir = self.animatsimdir
        nbrun = len(self.rg_bhv_selected)
        org = self.getNbPacket(1, nbrun)
        nbEpochParam, nbRunParam, paramserieSlicesAllEpochs = org
        self.previousStartEval = 0

        self.newtabBehavElts = []
        self.lst_varmse = []
        selected_pairs = []
        selected_bhv = []
        lst_paramserie = []        
        listpairs = []
        for sel in self.rg_bhv_selected:
            selected_pairs.append(optSet.pairs[sel])
            lst_paramserie.append(optSet.pairs[sel][0: self.nbpar])
            selected_bhv.append(optSet.behavs[sel])
        selected_pairs = np.array(selected_pairs)
        selected_bhv = np.array(selected_bhv)
        lst_paramserie = np.array(lst_paramserie)
        self.lst_paramserie = lst_paramserie
        
        bestchartList = []
        bestparamList = np.arange(len(self.rg_bhv_selected))
        bestparamList = list(bestparamList)
        # ========== prepares the folder of source directoty ==================
# TODO : continuer
        temp_aprojSaveDir = os.path.join(optSet.folders.animatlab_rootFolder,
                                         "tmp_AprojFiles")
        copyFileDir(animatsimdir, temp_aprojSaveDir, copy_dir=0)
        # =============  Run each paramset individually  ======================
        for epoch in range(nbEpochParam):
            paramserieSlices = paramserieSlicesAllEpochs[epoch]
            print(paramserieSlices)
            procName = "GEP"
            self.procName = procName
            paramserie = [lst_paramserie[epoch]]
            result = runTrials(self, paramserie, paramserieSlices,
                               savechart=1, procName="GEP",
                               runType="selected_seeds", randParEvol="")
            mse_coact = result[0]
            # lst_err = result[2]
            newtabBehavElts = result[3]
            for idx in range(nbRunParam[epoch]):
                pair_param_mseCoact = np.concatenate([paramserie[idx],
                                                      mse_coact[idx]])
                behav = newtabBehavElts[idx]
                # print(idx, behav)
                self.add_pair(pair_param_mseCoact, behav)
                listpairs.append(pair_param_mseCoact)

            self.newtabBehavElts.append(newtabBehavElts[0])

            """
            df_bhvremain = self.update_df_bhvremain(mseThr=1.0)
            for err in lst_err:
                self.lst_varmse.append(err)
            for idx, chartName in enumerate(self.lst_chartName):
                bestchartList.append(chartName)
                besterrList.append(self.lst_varmse[idx])
                bestparamList.append(self.lst_bestParNb[idx])
            """
            self.startEval += 1

            # =========== moves seed charts to the self.newDestFolder =========
            chart_glob_name = procName + "_chart"
            if self.lst_chartName != []:    
                srcfile = self.lst_chartName[0]
            else:
                srcfile = "GEP_chart00.txt"
            src_numbertxt = srcfile.replace(".txt", "")[len(chart_glob_name):]
            src_number = int(src_numbertxt)
            # print(srcfile, src_number)

            if int(src_numbertxt) < 10:
                src_nb = src_numbertxt[1]  # Eliminates the "0" before number
            else:
                src_nb = src_number
            if epoch < 10:
                zero = "0"
            else:
                zero = ""
            dstfile = chart_glob_name + zero + str(epoch)
            srcdir = os.path.join(self.animatsimdir, "GEPChartFiles")
            dstdir = os.path.join(self.newDestFolder, "GEPChartFiles")
            if not os.path.exists(dstdir):
                os.makedirs(dstdir)
            copyRenameFilewithExt(srcdir, srcfile, dstdir, dstfile,
                                  ".txt", "", replace=1)
            filetoremove = os.path.join(srcdir, srcfile)
            os.remove(filetoremove)
            bestchartList.append(dstfile+".txt")

            # ========= moves seed .asim files to the self.newDestFolder ======
            simN = os.path.splitext((os.path.split(model.asimFile)[-1]))[0]
            srcfile = simN + "-" + str(src_nb) + ".asim"
            dstfile = simN + "-" + str(epoch)
            srcdir = os.path.join(self.animatsimdir, "GEPAsimFiles")
            dstdir = os.path.join(self.newDestFolder, "GEPAsimFiles")
            if not os.path.exists(dstdir):
                os.makedirs(dstdir)
            copyRenameFilewithExt(srcdir, srcfile, dstdir, dstfile,
                                  ".asim", "", replace=1)
            filetoremove = os.path.join(srcdir, srcfile)
            os.remove(filetoremove)

            # ========= moves seed .aproj files to the self.newDestFolder =====
            name = os.path.splitext(aprojFicName)[0]
            ext = os.path.splitext(aprojFicName)[1]
            srcfile = name + "_bestGEP-" + str(src_nb) + ext
            dstfile = name + "_bestGEP-" + str(epoch) + ext
            srcdir = os.path.join(self.animatsimdir, "AprojFiles")
            dstdir = os.path.join(self.newDestFolder, "AprojFiles")
            if not os.path.exists(dstdir):
                os.makedirs(dstdir)
            copyRenameFilewithExt(srcdir, srcfile, dstdir, dstfile,
                                  ".aproj", "", replace=1)
            filetoremove = os.path.join(srcdir, srcfile)
            os.remove(filetoremove)   
            self.bestchartList = bestchartList
            selected_pairs = []
            selected_bhv = []
            lst_paramserie = []
        
            for sel in self.rg_bhv_selected:
                selected_pairs.append(optSet.pairs[sel])
                lst_paramserie.append(optSet.pairs[sel][0: self.nbpar])
                selected_bhv.append(optSet.behavs[sel])
            self.selected_pairs = np.array(selected_pairs)
            self.selected_bhv = np.array(selected_bhv)
            lst_paramserie = np.array(lst_paramserie)
            self.lst_paramserie = lst_paramserie

    def search_list_spanValues(self):
        """
        creates and saves self.listspanval 
        """
        seedsOK = False
        rep = False
        for idx, behav in enumerate(self.newtabBehavElts):
            if behav[9] >= 1:  # if selectedseedOK varmse>1 -> replaced by 0.0
                self.newtabBehavElts[idx][9] = 0
            else:
                seedsOK = True
        self.selectedSeedsOK = []
        lst_good_parSet = []

        if seedsOK:
            titre = "Search list_spanValues"
            info = "Do you want to launch search?"
            rep = dialogWindow(titre, info, details="")
            nbrun = len(self.rg_bhv_selected)
            org = self.getNbPacket(1, nbrun)
            nbEpochParam, nbRunParam, paramserieSlicesAllEpochs = org

        if rep == True:
            for idx, behav in enumerate(self.newtabBehavElts):
                if behav[9] < 1:
                    self.selectedSeedsOK.append(idx)
                    lst_good_parSet.append(idx)
            if self.selectedSeedsOK != []:
                lst_param_OK = [self.lst_paramserie[x] for x in lst_good_parSet]
                rep = get_good_span_list(self, lst_param_OK)
                self.lst_paramserie = lst_param_OK
                self.spanlistfound,  self.listspanVal = rep
            else:
                self.reset_span()
                self.spanlistfound = False

    def saves_newGEPdata(self, seedDirCreate=False):
        nbrun = len(self.rg_bhv_selected)
        org = self.getNbPacket(1, nbrun)
        nbEpochParam, nbRunParam, paramserieSlicesAllEpochs = org

        bestparamList = np.arange(len(self.rg_bhv_selected))
        bestparamList = list(bestparamList)
        chart_glob_name = self.procName + "_chart"

        filename = "GEPdata00.txt"
        dirGEPdata = os.path.join(self.newDestFolder, "GEPdata")
        completename = os.path.join(dirGEPdata, filename)
        f = open(completename, 'a')
        for idx, pair in enumerate(self.selected_pairs):
            s = ""
            for idy, tmpval in enumerate(pair):
                s += "{:4.8f}".format(tmpval) + '\t'
            # s += "{:4.8f}".format(optSet.pairs[idx][idy+1]) + '\t'
            s += str(self.startSerie + idx) + '\n'
            # print(s, end=" ")
            f.write(s)
        f.close()

        # ========= writes the correct "GEPdata00bhv.txt" file ================
        """
        # ["mse", "coactpen", "startangle", "endangle", "oscil1",
        #  "oscil2", "max_speed", "end_mvt2", "duree", "varmse"]
        """
        bhvfilename = "GEPdata00bhv.txt"
        dirGEPdata = os.path.join(self.newDestFolder, "GEPdata")
        completebhvname = os.path.join(dirGEPdata, bhvfilename)
        fbhv = open(completebhvname, 'a')
        # self.selectedSeedsOK = []
        for idx, behav in enumerate(self.newtabBehavElts):
            s = ""
            for idy, tmpval in enumerate(behav):
                s += "{:4.8f}".format(tmpval) + '\t'
            s += str(self.startSerie + idx) + '\n'
            # print s,
            fbhv.write(s)
            # if behav[9] < 1:
            #    self.selectedSeedsOK.append(idx)
        fbhv.close()

        list_varmse = extract_err(self.newtabBehavElts)[0]
        self.lst_varmse = list_varmse

        # ===========  cleans the source ResultFiles directory ================
        if len(self.lst_paramserie) > 9:
            pre = "0"
        else:
            pre = ""
        cleanChartsFromResultDir(optSet, 1, len(self.lst_paramserie), pre)
        subdir = os.path.join("ResultFiles", "tmpBestChart")
        cleanChartsFromResultDir(optSet, 1, len(self.lst_paramserie), pre,
                                 directory=subdir)
        cleanAsimsFromResultDir(optSet, 1, len(self.lst_paramserie), pre,
                                directory=subdir)

        # ================= saves movements from charts =======================
        df_bhvremain = self.select_df_bhvremain.loc[self.rg_bhv_selected]
        name = "GEPdata00"
        GEP_graph_dir = os.path.join(self.newDestFolder, "GEPdata")
        self.save_map_behav(df_bhvremain, GEP_graph_dir, name)
        resultdir = os.path.join(self.newDestFolder, "ResultFiles")
        templateFileName = os.path.join(resultdir, "template.txt")
        chartdir = os.path.join(self.newDestFolder, "GEPChartFiles")
        for idx in range(len(df_bhvremain)):
            print(idx)
            if idx < 10:
                zero = "0"
            else:
                zero = ""
            dstfile = chart_glob_name + zero + str(idx)
            chartName = dstfile + ".txt"
            self.checkChartComment(chartdir, chartName, idx)
            graphfromchart(optSet, chartdir, chartName, templateFileName)

        # =================  creates and saves datastructure  =================
        datastructure = {}
        structNb = 0
        runType = "selected_seeds"
        lastrun = 0
        nbsim = nbEpochParam
        besterrList = self.lst_varmse

        # directory = self.newDestFolder
        # saveAnimatLabSimDir(directory)
        if min(self.listspanVal) != max(self.listspanVal):
            """
            conditions = [self.listspanVal,
                          [optSet.xCoactPenality1, optSet.xCoactPenality2],
                          besterrList, self.bestchartList, bestparamList,
                          [optSet.gravity]]
            """
            conditions = [["DicSpanVal.txt"],
                          [optSet.xCoactPenality1, optSet.xCoactPenality2],
                          besterrList, self.bestchartList, bestparamList,
                          [optSet.gravity]]
        else:
            conditions = [optSet.spanStim, optSet.spanSyn,
                          [optSet.xCoactPenality1, optSet.xCoactPenality2],
                          besterrList, self.bestchartList, bestparamList,
                          [optSet.gravity]]

        startseq = lastrun + 1
        endseq = lastrun + nbsim
        packetsize = 1
        val = {structNb: [runType, startseq, endseq, packetsize, conditions]}
        datastructure.update(val)

        dirGEPdata = os.path.join(self.newDestFolder, "GEPdata")
        parfilename = "GEPdata00.par"
        completeparfilename = os.path.join(dirGEPdata, parfilename)
        print(datastructure)
        self.datastructure_seeds = datastructure
        save_datastructure(datastructure, completeparfilename)
        save_listDicSpanVal(dirGEPdata, "DicSpanVal.txt", self.listDicSpanVal)
        
        srcdir = os.path.join(self.animatsimdir, "FinalModel")
        dstdir = os.path.join(self.newDestFolder, "FinalModel")
        copyFileDir(srcdir, dstdir, copy_dir=0)

        # ==============  Create 0_IDname_seeds0x directory  =================
        if seedDirCreate:
            copyTo_0_idXXX_Seeds0x(self.newDestFolder, self.animatsimdir)


    def add_pair(self, pair, behav):
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
            # print behav
        else:
            print("ATTENTION! limit array size reached.", end=" ")
            print("The first pairs will be suppressed...")
            temp = optSet.pairs[1:]
            optSet.pairs = temp
            optSet.pairs = np.vstack((temp, pair))

            temp = optSet.behavs[1:]
            optSet.behavs = temp
            optSet.behavs = np.vstack((temp, behav))
        self.optSet = optSet

    def save_pairs(self, runType):
        """
        Asks for directory to save data in
        Then saves a textfile containing the table (optSet.pairs)
        The first rows are the parameters, the 2 last are the behaviour
        """
        if self.GEP_rootname != "":     # data will be saved on the same file
            print(self.GEP_rootname)
        else:                           # data will be saved on a new file
            self.GEP_rootname = getGEPdataFileName(optSet)

        self.mydir = os.path.join(folders.animatlab_rootFolder, "GEPdata")
        filename = self.GEP_rootname + ".txt"
        completename = os.path.join(self.mydir, filename)
        bhvfilename = self.GEP_rootname + "bhv" + ".txt"
        completebhvname = os.path.join(self.mydir, bhvfilename)

        print(completename)
        if runType != "systRand":  # This is not a "syst-param" run
            #                           -> the whole sets of pairs are saved
            f = open(completename, 'w')
            self.startSerie = 0
            fbhv = open(completebhvname, 'w')
        else:
            f = open(completename, 'a')  # in "syst-param" run, each startserie
            #                               is appened to the file
            fbhv = open(completebhvname, 'a')

        for idx, pair in enumerate(optSet.pairs):
            s = ""
            for idy, tmpval in enumerate(pair):
                s += "{:4.8f}".format(tmpval) + '\t'
            # s += "{:4.8f}".format(optSet.pairs[idx][idy+1]) + '\t'
            s += str(self.startSerie + idx) + '\n'
            # print(s, end=" ")
            f.write(s)
        f.close()

        self.startSerie = len(optSet.pairs) - len(optSet.behavs)
        for idx, behav in enumerate(optSet.behavs):
            s = ""
            for idy, tmpval in enumerate(behav):
                s += "{:4.8f}".format(tmpval) + '\t'
            s += str(self.startSerie + idx) + '\n'
            # print(s, end=" ")
            fbhv.write(s)
        fbhv.close()

        if verbose > 2:
            list_names = copy.deepcopy(self.xparName)
            list_names.append("mse")
            list_names.append("coactPen")
            comment = listNamesToComment(list_names, col_width=13)
            ecrit_tab(optSet.pairs, startseq=0, all=0,
                      comment=comment, col_width=14)
            # ecritpairs(optSet.pairs, startseq=0)

        parfilename = self.GEP_rootname + ".par"
        completeparfilename = os.path.join(self.mydir, parfilename)
        datastructure = optSet.datastructure
        save_datastructure(datastructure, completeparfilename)
        print("data saved to:", completename)
        if verbose > 2:
            print(optSet.datastructure)

# TODO : continuer à vérifier
    def load_pairs(self):
        """
        Reads a textFile (fname) containing previous pairs (parameters, behav)
        in order to show the param and behav in the GUI.
        Starts opening a graphic window to choose the directory and file
        Reads the file and prints the pairs, and places corresponding dots on
        the graphs
        """

        res = (QtWidgets.QFileDialog.
               getOpenFileName(self,
                               "Choose a GEPdata file",
                               self.mydir,
                               "GEPdata Files (*.par)"))
        if type(res) == tuple:
            fname, __tmp = res
        else:
            fname = res
        # print(fname)
        self.mvtSet = 0
        if fname:
            self.gepdata_filename = fname
            self.read_pairs(fname)
            sourceDir = os.path.split(fname)[0:-1][0]
            rootDir = os.path.split(sourceDir)[0:-1][0]
            resultFilePath = os.path.join(rootDir, "ResultFiles")
            listDicGraphsPath = os.path.join(resultFilePath,
                                             'listDicGraphs.pkl')
            self.read_listDicGraphs(listDicGraphsPath)
            self.getSimConditions()  # gets coacP, gravity from datastructure

    def read_pairs(self, fname, plot=1):
        global folders, model, sims, projMan, aprojFicName, optSet
        self.mydir = os.path.join(optSet.folders.animatlab_rootFolder,
                                  "GEPdata")
        sameaproj = True
        print(fname)
        fname = str(fname).format()
        ficname = os.path.split(fname)[-1]
        nomfic = os.path.splitext(ficname)[0] + ".txt"
        nombhvfic = os.path.splitext(ficname)[0] + "bhv.txt"
        sourceDir = os.path.split(fname)[0:-1][0]
        self.filename = os.path.join(sourceDir, nomfic)
        rootDir = os.path.split(sourceDir)[0:-1][0]
        prevRootDir = os.path.split(optSet.folders.
                                    animatlab_rootFolder)[0:-1][0]
        rootDir = os.path.normcase(rootDir)
        prevRootDir = os.path.normcase(prevRootDir)
        finrootDir = os.path.split(rootDir)[-1:][0]

        # ----- if we are in a 'trial-xx' directory ------
        if finrootDir.find('-') < 0:
            if finrootDir[:finrootDir.find('-')] == "trial":
                baserootDir = os.path.split(rootDir)[0:-1][0]
                prevbaserootDir = os.path.split(prevRootDir)[0:-1][0]
                if baserootDir == prevbaserootDir:
                    sameaproj = True
                else:
                    sameaproj = False
        else:
            if str(rootDir) != str(prevRootDir):
                sameaproj = False
            else:
                sameaproj = True
        if str(rootDir) != str(prevRootDir) or not sameaproj:
            print("DIRECTORY CHANGED!!!!!!!")
            print("rootDir:", rootDir)
            print("prevRootDir:", prevRootDir)
            quit()
            return
            self.modelchanged = 1
            animatsimdir = rootDir
            animatLabV2ProgDir, nb_procs = getInfoComputer()
            res = initAnimatLab(animatsimdir, animatLabV2ProgDir)
            OK = res[0]
            if OK:
                folders = res[1]
                model = res[2]
                projMan = res[3]
                aprojFicName = res[4]
                optSet = res[5]
            # projMan = optSet.projMan
            # projMan.set_aproj(model)    # Assign the animatLabModel obj
            # projMan.set_simRunner(sims)    # Assign the simulationSet obj
            # self.initialiseParam()
            self.clearmvt()
            self.clearBhv()
            self.clearMseCoact()
            self.mydir = os.path.join(folders.animatlab_rootFolder,
                                      "GEPdata")
            self.filename = fname
            self.nb_procs = nb_procs
            optSet.nb_processors = nb_procs
            ficname = os.path.split(fname)[-1]
            nomfic = os.path.splitext(ficname)[0] + ".txt"
            sourceDir = os.path.split(fname)[0:-1][0]
            rootDir = os.path.split(sourceDir)[0:-1][0]
        tab_bhv = readTablo(sourceDir, nombhvfic)
        tab_bhv = np.array(tab_bhv)
        if len(tab_bhv) == 0:
            print("no other behaviour elements than MSE and coactivation")
        tab_par = readTablo(sourceDir, nomfic)
        tab_par = np.array(tab_par)
        nbpar = self.nbpar
        if tab_par[0][-1] != 0.0:
            nbparfromtab = len(tab_par[0]) - 2
            self.formatpairs = 0
            optSet.pairs = np.array(tab_par[:, :nbpar])
        else:
            nbparfromtab = len(tab_par[0]) - 2 - 1
            self.formatpairs = 1    # new pairs format includes number
            optSet.pairs = np.array(tab_par[:, 0:-1])
        optSet.behavs = np.array(tab_bhv[:, 0:-1])
        # self.lookforconstpar(tab_par[:, 0:nbpar])

        optSet.nbsim = len(optSet.pairs)
        if nbpar != nbparfromtab:
            message = "ERROR : numbers of params in file " + nomfic
            message += "(n=" + str(nbparfromtab) + ")"
            message += " and in memory (self.nbpar = "
            message += str(nbpar) + ") do not match"
            print(message)
        self.nbpar = nbparfromtab
        optSet.x0 = optSet.pairs[0, 0:nbpar]
        # in newpair format, 0 is pair number
        list_names = copy.deepcopy(self.xparName)
        list_names.append("mse")
        list_names.append("coactPen")
        comment = listNamesToComment(list_names, col_width=13)
        ecrit_tab(optSet.pairs, startseq=0, all=0,
                  comment=comment, col_width=14)
        # ecritpairs(optSet.pairs, all=0)
        list_names = copy.deepcopy(self.bhv_names)
        comment = listNamesToComment(list_names, col_width=13)
        ecrit_tab(optSet.behavs, startseq=0, all=0,
                  comment=comment, col_width=14)

        self.GEP_rootname = os.path.splitext(nomfic)[0]
        parfilename = self.GEP_rootname + ".par"
        completeparfilename = os.path.join(self.mydir, parfilename)
        optSet.datastructure = load_datastructure(completeparfilename)
        if verbose > 2:
            print(optSet.datastructure)
        self.plotPar_Coact_Mvt(plot=plot)
        self.optSet = optSet
        print("data loaded from:", self.filename)
        runType = optSet.datastructure[self.mvtSet][0]
        print(runType)

        # ====== creation of self.df_parremain and df_bhvremain ======
        df_bhvremain = self.update_df_bhvremain(mseThr=1.0)
        print("{} movements with good varmse".format(len(df_bhvremain)))

    def getSimConditions(self):
        datastructure = optSet.datastructure
        xCoactPenality = readCoacPenality(datastructure)
        xCoactPenality1, xCoactPenality2 = xCoactPenality
        optSet.xCoactPenality1 = xCoactPenality1
        optSet.xCoactPenality2 = xCoactPenality2
        self.valueCoactPen1.setText(str(xCoactPenality1))
        self.valueCoactPen2.setText(str(xCoactPenality2))
        gravity = readGravity(datastructure)
        optSet.gravity = gravity
        self.editValueGravity.setText(str(gravity))
        setGravity(model, optSet.gravity)
        gepdatadir = self.animatsimdir + "/GEPdata"
        dicSpanVal_file = gepdatadir + "/DicSpanVal.txt"
        rep = readSpan(datastructure, dicSpanVal_file)
        if type(rep) is tuple:
            spanStim, spanSyn = rep
            optSet.spanStim = spanStim
            optSet.spanSyn = spanSyn
            minFork = min(spanStim, spanSyn)
            maxFork = max(spanStim, spanSyn)
        else:
            self.listspanVal = rep
            minFork = min(self.listspanVal)
            maxFork = max(self.listspanVal)
        if minFork == maxFork:
            # print("all span values equal to", self.listspanVal[0])
            print("all span values equal to", minFork)
            # self.chkBx_glob_span.setCheckState(True)
            # self.glob_span = self.listspanVal[0]
            self.glob_span = minFork
            self.glob_span_val.setText(str(self.glob_span))
            self.chkBx_glob_span.setCheckState(2)
            print(self.chkBx_glob_span.checkState())
            self.span_setup()
        else:
            print("span values different:", self.listspanVal)

    def plotSetParam_mseCoact(self, paramserie, startseq, endseq, mse_coact,
                              typ, best=0):
        rgMin = np.argmin(mse_coact[startseq:endseq+1, 0] +
                          mse_coact[startseq:endseq+1, 1])
        rgMin = rgMin + startseq
        minErr = min(mse_coact[startseq:endseq+1, 0] + mse_coact[startseq:endseq+1, 1])
        if typ == 'rdbehav':
            symbol = "o"
            symbolBrush = 'r'
        elif typ == 'CMAES' or typ == 'CMAE':
            symbol = "o"
            symbolBrush = 'b'
        elif typ == 'VSCD':
            symbol = "o"
            symbolBrush = 'c'
        else:
            symbol = "o"
            symbolBrush = 2

        if self.main_mode is False:     # if called from ""makeGraphs""
            pargr = self.nbactivepargraphs
            parpltItm = self.screen[pargr].plot_item
        else:                          # if called from ""GEP_GUI""
            parpltItm = self.parplt_itm

        if best != 1:   # if not plot only best...
            # plot param serie
            parpltItm.plot(paramserie[startseq:endseq+1, self.parx],
                           paramserie[startseq:endseq+1, self.pary],
                           pen=None, symbol=symbol,
                           symbolBrush=symbolBrush)
        else:
            # the two lollowing lines are used to link dots on graph
            self.listbestparamset.append(list(paramserie[rgMin]))
            nparrbestpar = np.array(self.listbestparamset)
            parpltItm.plot(nparrbestpar[:, self.parx],
                           nparrbestpar[:, self.pary],
                           pen=None, symbol=symbol,
                           symbolBrush='m')
        # plot only the best of the serie
        parpltItm.plot(paramserie[rgMin:rgMin+1, self.parx],
                       paramserie[rgMin:rgMin+1, self.pary],
                       pen=None, symbol=symbol,
                       symbolBrush='m')

        if verbose > 2:
            print("typ=", typ, "color:", symbolBrush, end=' ')
            print(paramserie[rgMin:rgMin+1, self.parx], end=' ')
            print(paramserie[rgMin:rgMin+1, self.pary], end=' ')
            print("rg=", rgMin, "minErr=", minErr)
        # ==============================================================
        QtWidgets.QApplication.processEvents()
        # ==============================================================
        if best != 1:   # if not plot only best...
            self.plotOtherParam(paramserie[startseq:endseq+1],
                                pen=None, symbol=symbol,
                                symbolBrush=symbolBrush)
        else:
            # the two lollowing lines are used to link dots on graph
            # self.listbestparamset.append(list(paramserie[rgMin]))
            self.plotOtherParam(np.array(self.listbestparamset),
                                pen=None, symbol=symbol,
                                symbolBrush='m')
        self.plotOtherParam(paramserie[rgMin:rgMin+1],
                            pen=None, symbol=symbol,
                            symbolBrush='m')

        if best != 1:   # if not plot only best...
            self.mseplt_itm.plot(mse_coact[startseq:endseq+1, 0],
                                 mse_coact[startseq:endseq+1, 1],
                                 pen=None, symbol=symbol,
                                 symbolBrush=symbolBrush)

        self.mseplt_itm.plot(mse_coact[rgMin:rgMin+1, 0],
                             mse_coact[rgMin:rgMin+1, 1],
                             pen=None, symbol=symbol,
                             symbolBrush='m')
        # ==============================================================
        QtWidgets.QApplication.processEvents()
        # ==============================================================

    def plotMvtSet(self, conditions, typ, rgpackt, best=0):
        plotcurve = False
        # rgErrList = 0
        rgMinErr = -1
        minErr = -1
        # errList = []
        chartList = []
        errList = []
        if type(conditions[-1][0]) is float:  # this is gravity value
            # rgErrList = conditions[-2]
            chartList = conditions[-3]
            errList = conditions[-4]
        else:
            # rgErrList = conditions[-1]
            chartList = conditions[-2]
            errList = conditions[-3]
        if best != 1 or rgpackt != -1:
            for idex, chartFile in enumerate(chartList):
                if typ == 'CMAES' or typ == 'CMAE':
                    if chartFile[:-6] == 'CMAeMinChart':
                        chartDir = os.path.join(folders.animatlab_rootFolder,
                                                "CMAeMinChartFiles")
                    else:
                        chartDir = os.path.join(folders.animatlab_rootFolder,
                                                "CMAeSeuilChartFiles")
                elif typ == 'VSCD':
                    chartDir = os.path.join(folders.animatlab_rootFolder,
                                            "VSCDChartFiles")
                elif typ == 'rdparam_MSE':
                    chartDir = os.path.join(folders.animatlab_rootFolder,
                                            "MSEChartFiles")
                elif typ == 'rdparam_varmse':
                    chartDir = os.path.join(folders.animatlab_rootFolder,
                                            "GEPChartFiles")
                elif typ == 'rdparam_noEvol':
                    chartDir = os.path.join(folders.animatlab_rootFolder,
                                            "GEPChartFiles")
                else:
                    chartDir = os.path.join(folders.animatlab_rootFolder,
                                            "GEPChartFiles")
                chart = readTablo(chartDir, chartFile)
                if rgpackt == -1:
                    plotcurve = True
                else:
                    if idex == rgpackt:
                        plotcurve = True
                    else:
                        plotcurve = False
                # print "plot Curve:", plotcurve
                if plotcurve:
                    print(chartFile, "\t", end=' ')
                    self.plotmvt(chart)
                    # ======================================================
                    QtWidgets.QApplication.processEvents()
                    # ======================================================

        else:
            if errList != []:
                minErr = min(errList)
                rgMinErr = errList.index(minErr)
                # print "min =", minErr, "rang:", rgMinErr
                chartFile = chartList[rgMinErr]
                if typ == 'CMAES' or typ == 'CMAE':
                    if chartFile[:-6] == 'CMAeMinChart':
                        chartDir = os.path.join(folders.animatlab_rootFolder,
                                                "CMAeMinChartFiles")
                    else:
                        chartDir = os.path.join(folders.animatlab_rootFolder,
                                                "CMAeSeuilChartFiles")
                elif typ == 'VSCD':
                    chartDir = os.path.join(folders.animatlab_rootFolder,
                                            "VSCDChartFiles")
                elif typ == 'rdparam_MSE':
                    chartDir = os.path.join(folders.animatlab_rootFolder,
                                            "MSEChartFiles")
                elif typ == 'rdparam_varmse':
                    chartDir = os.path.join(folders.animatlab_rootFolder,
                                            "GEPChartFiles")
                elif typ == 'rdparam_noEvol':
                    chartDir = os.path.join(folders.animatlab_rootFolder,
                                            "GEPChartFiles")
                else:
                    chartDir = os.path.join(folders.animatlab_rootFolder,
                                            "GEPChartFiles")
                chart = readTablo(chartDir, chartFile)
                self.plotmvt(chart)
                # ==========================================================
                QtWidgets.QApplication.processEvents()
                # ==========================================================
            else:
                print("No list of Err values in Condition")

    def plotPar(self, parpltItm, parx, pary, plot=0):
        optSet = self.optSet
        if self.main_mode is True:     # if not called from "GUI_Graph"
            nbpar = self.nbpar
            datastructure = optSet.datastructure
            for idx in range(len(datastructure)):
                typ = datastructure[idx][0]
                startseq = datastructure[idx][1]
                endseq = datastructure[idx][2]
                paramserie = optSet.pairs[:, 0:nbpar]
                if typ == 'rdbehav':
                    symbol = "o"
                    symbolBrush = 'r'
                elif typ == 'CMAES' or typ == 'CMAE':
                    symbol = "o"
                    symbolBrush = 'b'
                elif typ == 'VSCD':
                    symbol = "o"
                    symbolBrush = 'c'
                else:
                    symbol = "o"
                    symbolBrush = 2

                parpltItm.setXRange(0, 1)
                parpltItm.setYRange(0, 1)
                parpltItm.plot(paramserie[startseq-1:endseq, parx],
                               paramserie[startseq-1:endseq, pary],
                               pen=None, symbol=symbol,
                               symbolBrush=symbolBrush)
                # ==============================================================
                QtWidgets.QApplication.processEvents()
                # ==============================================================
        else:        # if called from "GUI_Graph"
            """
            namex = self.listDicGraphs[0]["abscissa"]
            namey = self.listDicGraphs[0]["ordinate"]
            for pargr in range(self.nbactivepargraphs):
            """
            dflist_x = self.df_parremain[optSet.xparName[parx]]
            dflist_y = self.df_parremain[optSet.xparName[pary]]
            symbol = "o"
            symbolBrush = 'c'
            pen = None
            parpltItm.setXRange(0, 1)
            parpltItm.setYRange(0, 1)
            # param_val_array = np.array(df_parremain)[:, [parx, pary]]
            parpltItm.plot(list(dflist_x),
                           list(dflist_y),
                           pen=pen, symbol=symbol,
                           symbolBrush=symbolBrush)
            # ==============================================================
            QtWidgets.QApplication.processEvents()
            # ==============================================================

        parpltItm.setLabel('left', self.xparName[pary], units='',
                           color='black', size='12pt')
        parpltItm.setLabel('bottom', self.xparName[parx], units='',
                           color='black', size='12pt')
        parnamex = self.xparName[parx]
        parnamey = self.xparName[pary]
        print("in x: ", parnamex, "\t in y:", parnamey)
        # ==============================================================
        QtWidgets.QApplication.processEvents()
        # ==============================================================

    def exec_gep_rand(self, optSet, aim_list=[], typ_gep="",
                      df_bhv_selected=None):
        """
        Runs n behav trials and add the data(param, behaviour) to optSet.pairs
        Each behav trial looks for the closest behav in the list and
        proposes a new behav in its vicinity
        For each run, the chart is saved in a temporary directory.
        When the n runs are done, the best result chart is saved in "GEP_Chart"
        under an incremented name.
        """
        self.err = []
        self.tabBehavElts = []
        self.glob_span = float(self.glob_span_val.text())
    #       span = float(self.valueLine4.text())
    #       optSet.spanStim, optSet.spanSyn = span, span
        optSet.xCoactPenality1 = float(self.valueCoactPen1.text())
        optSet.xCoactPenality2 = float(self.valueCoactPen1.text())
        nb_neighbours = int(self.valueLine2a.text())
        # sigma = float(self.valueLine2b.text())
        # sigma_span = sigma * span / 200
        # print("sigma=", sigma, "sigma_span", sigma_span)
        start_bhv_x = float(self.aimBhvValueX.text())  # reads X startseq behav
        start_bhv_y = float(self.aimBhvValueY.text())  # reads Y startseq behav
        startseq = 0   # line to startseq from in the GEPdataxxbhv.txt list
        run_type = "GEPrand"

        # print(aim_list)
        if len(aim_list) > 0:
            lst_closest_bhv = []
            lst_closest_par = []
            lst_rg = []
            for aim_bhv in aim_list:
                # print(aim_bhv)
                (closest_behav, closest_dist, pairs_rg,
                 order_series) = findClosestPair_behav(self, aim_bhv,
                                                       df_bhv_selected,
                                                       startseq, self.behav_col,
                                                       self.mseThr, optSet)
                closest_param_set = optSet.pairs[pairs_rg][0:len(optSet.x0)]
                paramserie = closest_param_set
                lst_closest_bhv.append(closest_behav)
                lst_closest_par.append(paramserie)
                lst_rg.append(pairs_rg)

            bhv_aim = np.array(aim_list)
            self.bhvPlot.plot_item.plot(bhv_aim[:, 0], bhv_aim[:, 1],
                                        pen=None, symbol='+',
                                        markersize=25, symbolBrush='b')
            behav_obj = np.array(lst_closest_bhv)
            self.bhvPlot.plot_item.plot(behav_obj[:, 0], behav_obj[:, 1],
                                        pen=None,
                                        symbol='+', markersize=40,
                                        symbolBrush='g')
            # =============================================================
            QtWidgets.QApplication.processEvents()
            # =============================================================
            lst_closest_par = np.array(lst_closest_par)
            self.lst_closest_par = lst_closest_par
            self.lst_closest_bhv = lst_closest_bhv
            self.lst_rg = lst_rg
            self.valueLine1a.setText(str(len(lst_closest_par)))
            self.valueLine1b.setText(str(len(lst_closest_par)))
    # #########################################################################
            exec_rand_param(self, run_type, optSet,
                            lst_parset=lst_closest_par, typGEP=typ_gep)
    # #########################################################################

        elif self.GEPauto == 0:
            # self.behav_col = [3, 8]  # 3 is "endangle"; 8 is "dur_mvt2"
            self.behav_aim[0] = start_bhv_x
            self.behav_aim[1] = start_bhv_y
            bhv_aim = np.array(self.behav_aim).reshape(1, 2)
            self.bhvPlot.plot_item.plot(bhv_aim[:, 0], bhv_aim[:, 1],
                                        pen=None, symbol='+',
                                        markersize=25, symbolBrush='b')
            # for idx in range(nbRunBehav):
            df_bhv_selected = self.update_df_bhvremain(mseThr=1.0)
            if not df_bhv_selected.empty:
                (closest_behav, closest_dist, pairs_rg,
                 order_series) = findClosestPair_behav(self, self.behav_aim,
                                                       df_bhv_selected,
                                                       startseq,
                                                       self.behav_col,
                                                       self.mseThr, optSet)
                if closest_behav is not None:
                    # behav_obj = findRandObjective(closestDist,
                    #                               closest_behav, span)
                    behav_obj = np.array(closest_behav).reshape(1, 2)
                    print('rg=', pairs_rg, self.behav_aim, '->', behav_obj)
                    self.bhvPlot.plot_item.plot(behav_obj[:, 0],
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
                                                   0, len(optSet.x0), affich,
                                                   optSet)
                    parx = self.parx
                    pary = self.pary
                    self.parplt_itm.plot(paramserie[:, parx],
                                         paramserie[:, pary],
                                         pen=None, symbol='o', symbolBrush=5)
                    pairs_rg = order_series.index[0]
                    closest_param_set = optSet.pairs[pairs_rg]
                    paramserie = closest_param_set
                    print(paramserie)
                    self.startSet = paramserie[0:self.nbpar]
                    # self.prefix = ""
    # #########################################################################
                    exec_rand_param(self, run_type, optSet)
    # #########################################################################
                    df_bhvremain = self.update_df_bhvremain(mseThr=1.0)
                    if not df_bhvremain.empty:
                        self.test_for_save_map_bhv(df_bhvremain, affich=1)
                    self.startSet = []
                    self.startEval = 0
                    # self.prefix = ""
            else:
                print()
                print("######################################################")
                print(" No behavior data in memory !! --> look for best vmse")
                print("######################################################")

# TODO : continuer l'implementation
    def make_save_eps(self):
        None
        # self.grchart = GUI_Graph()
        # self.grchart.GEP_GUI_win = self


# ****************************************************************************
#                            General Procedures
# ****************************************************************************

def copyTo_0_idXXX_Seeds0x(sourcedir, destpath):
    txt = destpath[destpath.find('_ID'):]
    txt = txt[1:]
    IDName = txt[:txt.find('_')]
    if os.path.split(destpath)[-1][:5] == 'trial':
        rootpath1 = os.path.split(destpath)[0]
        nomdir1 = os.path.split(rootpath1)[-1]
        if nomdir1[:2] == "an" and nomdir1[nomdir1.find('_'):][:4] == "_dur":
            rootpath2 = os.path.split(rootpath1)[0]
            nomdir2 = os.path.split(rootpath2)[-1]
            if nomdir2[:2] == "1_" or nomdir2[:2] == "2_"\
                or nomdir2[:2] == "0_":
                rootpath3 = os.path.split(rootpath2)[0]
    else:
        rootpath3 = os.path.split(destpath)[0]
    rootpath = rootpath3

    filenames= os.listdir(rootpath) # get all files' and folders' names in dir
    result = []
    for filename in filenames: # loop through all the files and folders
        # check object is a folder or not
        if os.path.isdir(os.path.join(os.path.abspath(rootpath), filename)):
            result.append(filename)
    result.sort()
    # print(result)
    lst_seeds_folders = []
    for folder in result:
        if folder[:2] == "0_" and folder[folder.find("_seed"):][:5] == "_seed":
            lst_seeds_folders.append(folder)
    lst_seeds_folders.sort()
    print(lst_seeds_folders)
    seedsdirNb = len(lst_seeds_folders)
    if seedsdirNb < 10:
        nbtxt = "0" + str(seedsdirNb)
    else:
        nbtxt = str(seedsdirNb)
    newSeedsFolder_name = "0_" + IDName + "_seeds" + nbtxt
    destdir = rootpath + "/" + newSeedsFolder_name
    completename = sourcedir + "/GEPdata" + "/seeds_origin.txt"
    with open(completename, 'w') as f:
        f.write(newSeedsFolder_name + "\t" + sourcedir + "\n")
        f.close()
    copyDirectory(sourcedir, destdir)
    print("{} has been copied to {}".format(sourcedir, newSeedsFolder_name))


def set_rainbow_colors(win, listdf_bhv):
    """
    Build a dataframe (codeCoul) that contains a color code column
    constructed from one column of the given dataframe ("dur-mvt2")
    The df is first sorted according to this column, and a new color
    column is added (an array of inceasing numbers from 1 to the lentgh
    of the df). Then the df is sorted again according to index.
    A lut (corresponding to the color code) is built from cmap gist_rainbow
    both code_coul dataframe and lut are returned.
    """
    tmpbhv_df = listdf_bhv[0]
    # ===============     generates codeCoul_df   ===================
    codeCoul_df = copy.deepcopy(tmpbhv_df[[win.bhv_names[win.behav_col[0]],
                                           win.bhv_names[win.behav_col[1]],
                                           "rgserie"]])
    codeCoul_df.sort_values(win.bhv_names[win.behav_col[1]],
                            axis=0, ascending=True,
                            inplace=True, na_position='last')
    # list_ang = np.array(codeCoul_df.endangle)
    # ======    creates one new "color" column    =============
    listcolnb = np.arange(1, len(codeCoul_df)+1)
    codeCoul_df.loc[:, 'color'] = listcolnb
    # ======    reagange df according to rgserie   ============
    codeCoul_df.sort_values("rgserie", axis=0, ascending=True,
                            inplace=True, na_position='last')
    # ===========     generates rainbow color map   ==============

    nb_levels = len(codeCoul_df)+1
    my_palette = []
    cmap = plt.get_cmap('gist_rainbow')
    for i in range(nb_levels):
        # print(cmap(float(i)/nb_levels, float(10)/10))
        my_palette.append(cmap(float(i)/nb_levels, float(10)/10))
    lut = []
    for i, pal in enumerate(my_palette):
        red = int(pal[0]*255)
        green = int(pal[1]*255)
        blue = int(pal[2]*255)
        lut.append([red, green, blue])
    return codeCoul_df, lut


# ============================================================================
#                               SIMULATIONS
# ============================================================================


def exec_rand_param(win, runType, optSet, lst_parset=[], typGEP=""):
    """
    Runs nbRunParam random params generated around optSet.x0
    with a width of span/100 and add the data(param, behaviour)
    to optSet.pairs
    """
    procName = ""
    parx = win.parx
    pary = win.pary
    bestparamList = []
    bestchartList = []
    besterrList = []
    win.err = []
    win.tabBehavElts = []
    win.glob_span = float(win.glob_span_val.text())
    # span = float(self.valueLine4.text())
    # optSet.spanStim, optSet.spanSyn = span, span
    optSet.xCoactPenality1 = float(win.valueCoactPen1.text())
    optSet.xCoactPenality2 = float(win.valueCoactPen2.text())
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
        win.previousStartEval = len(optSet.pairs)
        listpairs = []
        randpar = np.random.random_sample((nbRunParam[epoch],
                                           len(optSet.x0)))
        randpar = (randpar - 0.5) * 2     # paramserie in range (-1, 1)
        # recalculate paramserie centered on x0, width = span
        if len(win.listDicSpanVal) > 0:
            for i in range(len(randpar)):
                for idx, name in enumerate(win.xparName):
                    if verbose == 3:
                        print(randpar[i][idx], '\t', end=" ")
                        print(win.listDicSpanVal[0][name], '\t', end=' ')
                    randpar[i][idx] = randpar[i][idx] *\
                        float(win.listDicSpanVal[0][name])/200
                    lst_span[i][idx] = float(win.listDicSpanVal[0][name])
                    if verbose == 3:
                        print(randpar[i][idx])
        else:
            randpar = randpar * win.glob_span / 200
        if runType == "rdparam":
            if win.randParEvol == "MSE":
                procName = "MSE"
                res = findClosestPair_mse([0, 0], win.startEval, optSet)
                closestMseCoact = res[0]
                closestDist = res[1]
                pairs_rg = res[2]

            elif win.randParEvol == "varmse":
                procName = "GEP"
                res = findClosestPair_varmse(win.startEval, optSet)
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
                    txt = "best varmse:{} at rg={} [MSE,CoactP]:{}"
                    print(txt.format(bestvarmse, pairs_rg,
                                                  plotMSECoact))
                elif win.randParEvol == "MSE":
                    txt = "best MSE:{} at rg={} [MSE,CoactP]:{}"
                    print(txt.format(closestMseCoact[0],
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
                paramset = win.startSet

        elif runType == "systRand":
            paramset = win.startSet
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
                                # print(name)
                                tmptab.append(float((win.dicConstParam[name])))
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
                                optSet, stim_liminf=True,
                                stim_limsup=True, syn_liminf=True,
                                syn_limsup=True)

        if typGEP == "extend":
            print(typGEP, win.extend_nb, "/ last = ", win.nbGEPextend-1)
        elif typGEP == "fill":
            print(typGEP, win.fill_nb, "/ last = ", win.nbGEPfill - 1)
        if runType == "rdparam":
            print("epoch =", epoch, "/ last =", nbEpochParam - 1)
        win.parplt_itm.plot(paramserie[:, parx], paramserie[:, pary],
                            pen=None, symbol='o', symbolBrush=2)
        # in MainWindow, we plot only the two first parameters
        win.plotOtherParam(paramserie, pen=None, symbol='o', symbolBrush=2)
        # -----------------------------------
        QtWidgets.QApplication.processEvents()
        # -----------------------------------
        paramserieSlices = paramserieSlicesAllEpochs[epoch]
        # ###############################################################
        # if procName == "GEP":
        #    result = runGEP(self, paramserie, paramserieSlices)
        # else:
        result = runTrials(win, paramserie, paramserieSlices,
                           savechart=1, procName=procName,
                           runType=runType,
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
        # ["mse", "coactpen", "startangle", "endangle", "oscil1",
        #  "oscil2", "max_speed", "end_mvt2", "duree", "varmse"]
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
        win.startEval = win.previousStartEval
        # saveBestpairtoAproj(self, optSet, "")

    print("===================================================")
    print("    End of", nbRandTrial, runType, "parameter runs")
    print("===================================================")
    packetsize = win.packetRand
    if min(win.listspanVal) != max(win.listspanVal):
        conditions = [["DicSpanVal.txt"],
                      [optSet.xCoactPenality1, optSet.xCoactPenality2],
                      besterrList, bestchartList, bestparamList,
                      [optSet.gravity]]
    else:
        conditions = [optSet.spanStim, optSet.spanSyn,
                      [optSet.xCoactPenality1, optSet.xCoactPenality2],
                      besterrList, bestchartList, bestparamList,
                      [optSet.gravity]]
    mise_a_jour(optSet, datastructure, structNb,
                runType + "_" + win.randParEvol,
                lastrun+1, lastrun + nbRandTrial, packetsize,
                conditions)
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
    win.startSerie = lastrun
    print("self.startSerie: ", win.startSerie)
    win.save_pairs(runType)



# TODO : continuer l'implementation et tester
"""
ATTENTION NOuvelle procedure non encore testée
L'autre possibilité serait d'utiliser win.run_selected_param()
en donnant la liste des rangs des param à utiliser () 
et le répertoire de destination ()
"""
def exec_syst_param(win, optSet):
    """
    Resets the program (prepares a new set of simulations) and Runs
    systematic nbRunParam params generated around optSet.x0 with a width of
    span/100 and add the data(param, behaviour) to optSet.pairs
    """
    win.reset()    # starts a new structure, new pairs...
    span = win.listDicSpanVal[0][win.xparName[0]]
    optSet.xCoactPenality1 = float(win.valueCoactPen1.text())
    optSet.xCoactPenality2 = float(win.valueCoactPen2.text())
    randRuntxt = win.valueLine1b.text()     # reads run nb from the GUI
    nbRandRun = int(randRuntxt)
    win.packetRand = int(win.valueLine1a.text())
    # reads run nb run from the GUI
    nbTrialParam = int(win.valueLine0b.text())
    nbruneach = 1
    nbpar = len(optSet.x0)
    nbVarPar = nbpar - len(win.dicConstParam)
    while True:
        # the number of parameters is (nbpar - constant parameters)
        nbparamset = nbruneach**nbVarPar
        if nbparamset >= nbTrialParam:
            break
        else:
            nbruneach = nbruneach + 1
    setpar = np.ones(dtype=float, shape=(nbparamset, nbVarPar))
    if nbruneach < 4:
        step = 1. / (nbruneach + 1)
        setval = np.arange(step, 0.9999, step)
    else:
        step = 1. / (nbruneach - 1)
        setval = np.arange(0, 1.001, step)

    span = step * 100
    optSet.spanStim, optSet.spanSyn = span, span
    # self.valueLine4.setText(str(span))
    # setval = np.array([0.2, 0.8])
    stepfilltab = [nbruneach**x for x in range(nbVarPar)]

    for par in range(nbVarPar):
        saut = stepfilltab[par]
        rgset = 0
        while rgset < nbparamset:
            for val in setval:
                for n in range(saut):
                    setpar[rgset, par] = val
                    rgset += 1

    win.valueLine0b.setText(str(nbparamset))
    print("there will be", nbparamset, "runs (", nbruneach, "values/param)")
    nbTrialParam = nbparamset

    info = "Nb of startingSets: " + str(nbparamset)
    # info += "  (" + str(nbruneach) + " values/param)"
    details = "Nb of startingSets: " + str(nbparamset) + "  ( = "
    details += str(nbruneach) + "**" + str(len(optSet.x0)) + ")"
    details += "\n Values for each param:"
    details += "\n" + string(setval)
    details += "\nspan = " + str(span) + "% of [0, 1]"
    details += "\nfor each startingSet, " + str(nbRandRun/win.packetRand)
    details += " x " + str(win.packetRand) + " random runs"
    # details += "\nTotal: " + str(nbRandRun * nbparamset)
    details += "\nEstimated time: "
    duration = float(nbRandRun * nbparamset / win.packetRand) * 3
    nb_jours = int(duration / (3600 * 24))
    nb_heures = int(duration % (3600 * 24)) / 3600
    nb_min = (int(duration % (3600 * 24)) % 3600) / 60
    temps = str(nb_jours) + " j " + str(nb_heures) + " h "
    temps += str(nb_min) + " min"
    info += "\n(" + temps + ")"
    details += temps
    rep = showdialog("Systematic parameter exploration", info, details)
    print(rep)
    if rep == 1024:
        info = "ARE YOU SURE you want running \n"
        info += str(nbparamset) + " simulations !!!!"
        rep = showdialog("Systematic parameter exploration", info, "")
        print(rep)

        if rep == 1024:
            print("c'est parti pour {} runs".format(nbparamset))

            # ======= starting systematic exploration ========
            if win.systWithRand == 1:
                for jeu in range(nbparamset):
                    print("jeu =", jeu)
                    optSet.pairs = []   # we startseq a new pair series
                    win.startSet = setpar[jeu]
                    win.startEval = 0
                    # self.prefix = "syst"
                    runType = "systRand"
# ############################################################################
                    exec_rand_param(win, runType, optSet)
# ############################################################################
            else:
                win.packetCMA_Size = 8
                win.packetCMA_Nb = int(nbparamset / win.packetCMA_Size)
                for pack in range(win.packetCMA_Nb):
                    win.packetCMA_Set = []
                    for siz in range(win.packetCMA_Size):
                        jeu = pack * win.packetCMA_Size + siz
                        # print jeu
                        win.packetCMA_Set.append(setpar[jeu])
                    win.packetCMA_Set = np.array(win.packetCMA_Set)
                    print(win.packetCMA_Set)
    win.startSet = []
    win.startEval = 0
    # self.prefix = ""



def exec_list_paramSets(paramserie):
    nbRandTrial = 1
    datastructure = optSet.datastructure  # dictionary for data structure
    if len(datastructure) > 0:
        structNb = len(datastructure)
        lastinfo = datastructure[structNb-1]
        lastrun = lastinfo[2]
    else:
        structNb = 0
        lastrun = 0
    org = win.getNbPacket(int(win.valueLine1a.text()),  # Nbof processors
                          len(paramserie))             # Nb of param sets
    nbEpochParam, nbRunParam, paramserieSlicesAllEpochs = org
    bestparamList = []
    bestchartList = []
    besterrList = []
    win.err = []
    win.tabBehavElts = []
    runType = "GEPrand"
    procName = "GEP"
    for epoch in range(nbEpochParam):
        listpairs = []
        paramserieSlices = paramserieSlicesAllEpochs[epoch]
        # ==========================================================
        result = runTrials(win, paramserie, paramserieSlices,
                           savechart=1, procName=procName,
                           runType=runType,
                           randParEvol=win.randParEvol)   
        # ==========================================================
        mse_coact = result[0]
        lst_err = result[2]
        tabBehavElts = result[3]  # list of behaviour variables sets
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
        # ["mse", "coactpen", "startangle", "endangle", "oscil1",
        #  "oscil2", "max_speed", "end_mvt2", "duree", "varmse"]
        """
        nptabBehavElts = np.array(tabBehavElts)
        np_pairs = np.array(listpairs)
        win.plotBhvSet(nptabBehavElts, np_pairs, 0, nbRunParam[epoch])
        for err in lst_err:
            win.err.append(err)
        win.tabBehavElts.append(tabBehavElts)

        for idx, chartName in enumerate(win.lst_chartName):
            bestchartList.append(chartName)
            besterrList.append(win.err[idx])
            bestparamList.append(win.lst_bestParNb[idx])
        win.startEval = win.previousStartEval
        # saveBestpairtoAproj(self, optSet, "")
    print("===================================================")
    print("    End of", nbRandTrial, runType, "parameter runs")
    print("===================================================")
    packetsize = win.packetRand
    if min(win.listspanVal) != max(win.listspanVal):
        conditions = [["DicSpanVal.txt"],
                      [optSet.xCoactPenality1, optSet.xCoactPenality2],
                      besterrList, bestchartList, bestparamList,
                      [optSet.gravity]]
    else:
        conditions = [optSet.spanStim, optSet.spanSyn,
                      [optSet.xCoactPenality1, optSet.xCoactPenality2],
                      besterrList, bestchartList, bestparamList,
                      [optSet.gravity]]
    mise_a_jour(optSet, datastructure, structNb,
                runType + "_" + win.randParEvol,
                lastrun+1, lastrun + nbRandTrial, packetsize,
                conditions)
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
    win.startSerie = lastrun
    print("self.startSerie: ", win.startSerie)
    win.save_pairs(runType)



class ShowFileContent(QtWidgets.QMainWindow):
    """
    extends QtWidgets.QMainWindow
    Create a window which show the content of the selected script
    Constructor : self
                mydir : directory to the script
                the name of the script
                Set the size and the title of the window to show
    """
    def __init__(self, mydir, parent=None, fname=""):
        # super(ShowFileContent, self).__init__(parent)
        super(ShowFileContent, self).__init__()
        # This is enough to create the window
        # tabscript, text = ReadsScriptFile(fname)
        self.mydir = mydir
        self.fname = ""
        self.text = ""
        self.OK = 0
        self.title = 'Show text File Content'
        self.left = 100
        self.top = 100
        self.width = 400
        self.height = 140
        self.initUI()
        self.getTxtFile()
    """
    Method initUI
        This method set the different elements of the window to show
    """
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setMinimumSize(QtCore.QSize(900, 400))

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        self.textwin = QtWidgets.QPlainTextEdit(self)
        self.textwin.insertPlainText(self.text)
        # self.textwin.move(10, 10)
        # self.textwin.resize(400, 200)

        # Create a button in the window
        self.OKBtn = QtWidgets.QPushButton("&Accept", self)
        self.OKBtn.clicked.connect(self.accept)

        self.ChangeFileBtn = QtWidgets.QPushButton("&Change File", self)
        self.ChangeFileBtn.clicked.connect(self.changefile)

        self.gridLayout.addWidget(self.textwin, 1, 1, 5, 1)
        self.gridLayout.addWidget(self.OKBtn, 6, 1)
        self.gridLayout.addWidget(self.ChangeFileBtn, 6, 2)

        self.setCentralWidget(self.centralwidget)
        self.setLayout(self.gridLayout)

    def readFile(self, filename):
        tabfinal = []
        text = ""
        if os.path.exists(filename):
            f = open(filename, 'r')
            while 1:
                # We could set txt before entering the loop
                # and change its value before the concatenation =>
                # While txt != '' => avoid the use of a break statement
                # + a few lines
                # print(i)
                tab1 = []
                tab2 = []
                txt = f.readline()
                # print(txt)
                if txt == '':
                    break
                else:
                    text += txt
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
            f.close()
            # print(tabfinal)
        return tabfinal, text

    def getTxtFile(self):
        """
        This method open a popup window for you to chose the script file to use
        """
        # self.mydir = os.getcwd()
        # print(self.mydir)
        res = (QtWidgets.QFileDialog.
               getOpenFileName(self,
                               "Choose a script File to run GEP_GUI",
                               self.mydir,
                               "Script Text Files (*.txt)"))
        if type(res) == tuple:
            ficname, __tmp = res
        else:
            ficname = res
        print(ficname)

        # self.fname = os.path.split(ficname)[-1]
        self.fname = ficname
        tabText, text = self.readFile(self.fname)
        self.text = text
        self.textwin.clear()
        self.textwin.insertPlainText(self.text)

    def accept(self):
        """
        This method verify if the user has validated the chosen script
        """
        self.OK = 1
        print("file accepted")
        self.close()

    def changefile(self):
        """
        This method allows the user to change the script file
        """
        self.OK = 0
        print("file refused")
        self.getTxtFile()

    def choice(self):
        """
        return the value of the OK variable
        """
        return self.OK
        self.close()


def calculate_coact_from_chart():
    winLoad = ShowFileContent(animatsimdir)
    fname = winLoad.fname
    print(fname)
    dirname = os.path.split(fname)[0]
    ficname = os.path.split(fname)[-1]
    tab = readTablo(dirname, ficname)
    quality = testquality(optSet, tab, optSet.template, "", affich="MSE")
    mse, coactpenality, otherpenality = quality[0], quality[1], quality[2]
    txt = "\terr:{:4.4f}; mse:{:4.4f}; coactpenality:{};"
    txt = txt + " otherpenality:{:4.8f}"
    err = mse+coactpenality
    comment0 = txt.format(err, mse, coactpenality, otherpenality)
    print(comment0)

    resbehav = getbehavElts(optSet, tab, "varmse")
    varmse = resbehav[7]
    varcoactpenality = resbehav[8]
    varotherpenality = resbehav[9]
    err = varmse+varcoactpenality
    txt = "\terr:{:4.4f}; varmse:{:4.4f}; coactpenality:{};"
    txt = txt + " otherpenality:{:4.8f}"
    comment1 = txt.format(err, varmse, varcoactpenality, varotherpenality)
    resbehav = resbehav[:8]
    print(comment1)


def initAnimatLab(animatsimdir, animatLabV2ProgDir):
    if animatsimdir != "":
        subdir = os.path.split(animatsimdir)[-1]
        print(subdir)
        rootdir = os.path.dirname(animatsimdir)
        # rootdir += "/"
        folders = FolderOrg(animatlab_root=rootdir,
                            python27_source_dir=animatLabV2ProgDir,
                            subdir=subdir)
        # folders.affectDirectories()
        aprojSaveDir = os.path.join(folders.animatlab_rootFolder,
                                    "AprojFiles")
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

    else:
        print("No selected directory  run GUI_AnimatPar.py")
        return [False]

    if animatsimdir != "":
        sims = AnimatLabSimRunner.AnimatLabSimulationRunner("Test Sims",
            rootFolder = folders.animatlab_rootFolder,
            commonFiles = folders.animatlab_commonFiles_dir,
            sourceFiles = folders.python27_source_dir,
            simFiles = folders.animatlab_simFiles_dir,
            resultFiles = folders.animatlab_result_dir)
        model = AnimatLabModel.AnimatLabModel(folders.animatlab_commonFiles_dir)
        projMan = ProjectManager.ProjectManager('Test Project')
        aprojFicName = os.path.split(model.aprojFile)[-1]
        optSet = OptimizeSimSettings(folders=folders, model=model,
                                     projMan=projMan, sims=sims)
        projMan = optSet.projMan
        #
        collectInterval = optSet.chart[0].find("CollectInterval").text
        if collectInterval != '0.01':
            print("==========================================================")
            print("        !!! PROBLEM with collectInterval !!!")
            print("It should be '0.01 and it is ", collectInterval)
            print("In AnimatLab, change collectInterval in .aproj file")
            print("and save the .aproj file. Recreate StandAlone .asim file")
            print("then copy the .aproj, .asim and .aform files to replace")
            print("those files in all directories of the model")
            print("program will abort")
            print("==========================================================")
            sys.exixt()
        else:
            print("collectInterval:", collectInterval)
        # listparNameOpt = optSet.paramVSCDName
        setPlaybackControlMode(model, mode=0)   # 0: fastest Possible;
        #                                       # 1: match physics
        setMotorStimsOff(model, optSet.motorStimuli)
        # setGravity(model, optSet.gravity)       # by default = -9.81
        gravity = readGravityfromAsim(model)
        optSet.gravity = gravity
        # Looks for a parameter file in the chosen directory
        fileName = 'paramOpt.pkl'
        if loadParams(os.path.join(folders.animatlab_result_dir, fileName),
                      optSet):

            optSet.actualizeparamVSCD()
            optSet.actualizeparamMarquez()
            optSet.ideal_behav = [0, 0]
        else:
            print("paramOpt.pkl MISSING !!",
                  "run 'GUI_animatlabOptimization.py'")
            print()
        optSet.tab_motors = affichMotor(model, optSet.motorStimuli, 1)
        # optSet.tab_chartcolumns = affichChartColumn(optSet.ChartColumns, 1)
        optSet.tab_neurons = affichNeurons(optSet, optSet.Neurons, 1)
        optSet.tab_neuronsFR = affichNeuronsFR(optSet, optSet.NeuronsFR, 1)
        checknonzeroSyn(model, optSet)
        optSet.tab_connexions = affichConnexions(model, optSet,
                                                 optSet.Connexions, 1)
        checknonzeroSynFR(model, optSet)
        optSet.tab_connexionsFR = affichConnexionsFR(model, optSet,
                                                     optSet.SynapsesFR, 1)
        checknonzeroExtStimuli(optSet)
        optSet.tab_stims = affichExtStim(optSet, optSet.ExternalStimuli, 1)
        #
        print()
        # ###################################################################
        model.saveXML(overwrite=True)
        # ###################################################################
        writeTitres(folders, 'stim', optSet.allPhasesStim,
                    optSet.tab_stims, optSet.seriesStimParam)
        writeTitres(folders, 'syn', optSet.allPhasesSyn,
                    optSet.tab_connexions, optSet.seriesSynParam)
        writeTitres(folders, 'synFR', optSet.allPhasesSynFR,
                    optSet.tab_connexionsFR, optSet.seriesSynFRParam)
        """
        print("spanStim:", optSet.spanStim)
        print("spanSyn", optSet.spanSyn)
        print("cmaes_sigma", optSet.cmaes_sigma)
        print("seuilMSEsave", optSet.seuilMSEsave)
        """
    return [True, folders, model, projMan, aprojFicName, optSet]


# ==========================================================================
#                                   MAIN
# ==========================================================================
if __name__ == '__main__':
    import sys
    previousanimatsimdir = readAnimatLabDir()
    import tkinter, tkinter.filedialog

    root = tkinter.Tk()
    root.withdraw()
    dirname = tkinter.filedialog.askdirectory(parent=root,
                                              initialdir=previousanimatsimdir,
                                              title='Please select a directory')
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

# TODO : Comprendre pourquoi setAnimatLabSimDir(None) fait planter les simuls
    # With setAnimatLabSimDir(None) impossible to launch simulations !!!!!!
    # animatsimdir = setAnimatLabSimDir(None)

    # animatLabV2ProgDir = readAnimatLabV2ProgDir()
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

    res = initAnimatLab(animatsimdir, animatLabV2ProgDir)
    OK = res[0]
    if OK:
        # folders = res[1]
        # model = res[2]
        # projMan = res[3]
        aprojFicName = res[4]
        optSet = res[5]
        optSet.list_save_flags = [0, 0, 0, 0]
        # pg.mkQApp()

        ag = QtWidgets.QDesktopWidget().availableGeometry()
        sg = QtWidgets.QDesktopWidget().screenGeometry()

        win = MaFenetre(aprojFicName, optSet)
        optSet.win = win
        win_height = win.geometry().height()
        win_width = win.geometry().width()
        win.location_on_the_screen(xshift=10, yshift=sg.height()-win_height)

        win.nb_procs = nb_procs
        optSet.nb_processors = nb_procs
        win.animatsimdir = animatsimdir
        win.mydir = os.path.join(animatsimdir, "GEPdata")

        mvtplot_height = win.mvtPlot.geometry().height()
        win.mvtPlot.location_on_the_screen(xshift=win_width+15,
                                           yshift=sg.height()-mvtplot_height)

        # win.bhvPlot.resize(mvtplot_width, win_height-mvtplot_height-40)
        mvtplot_width = win.mvtPlot.geometry().width()
        bhvPlot_height = win.bhvPlot.geometry().height()
        win.bhvPlot.location_on_the_screen(xshift=win_width + mvtplot_width+20,
                                           yshift=sg.height()-bhvPlot_height)
        win.show()

        list_elem = ["duration", "maxSpeed"]
        typ = "ordinate"
        title = "choose Ordinate for bhv Window"
        behav_ord = choose_one_element_in_list(title, list_elem, typ)
        behav_ord = "maxSpeed"
        if behav_ord == "duration":
            win.chkBx_bhv_duration.setChecked(True)
            win.chkBx_bhv_maxSpeed.setChecked(False)
            win.mvt_ord_duration = 1
            win.mvt_ord_maxSpeed = 0
        else:
            win.chkBx_bhv_duration.setChecked(False)
            win.chkBx_bhv_maxSpeed.setChecked(True)
            win.mvt_ord_duration = 0
            win.mvt_ord_maxSpeed = 1
        win.configureforbhvcriteria()
        gravity = readGravityfromAsim(model)
        optSet.gravity = gravity
        win.editValueGravity.setText(str(optSet.gravity))
        print("Nb parameters:", win.nbpar)
        # win.save_paramNames_bhvNames()
        win.save_neuron_properties()
        win.animatsimdir = animatsimdir
        # Start Qt event loop unless running interaction mode or using pyside
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtWidgets.QApplication.instance().exec_()
