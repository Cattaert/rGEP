# -*- coding: utf-8 -*-
"""
Created on Wed Mar 01 10:25:16 2017
Class that contains all parameters, stimuli and synapses for optimization
@author: cattaert
Translated in Python 3.8 Jan 2023 (D. Cattaert)
Modified February 20, 2023 (D. Cattaert):
    fourchSyn nd fourchStim have been replaced by spanSyn and spanStim
Modified July 19, 2024 (D. Cattaert):
    enableSynNS() introduced to set to 0 SynAmp of disblaed synapses.
    This call is made in actualizeparamVSCD() method, that is called in 
    GUI_AnimatPar.py before savinf the parameters
    
Modified February 20, 2025 (D. Cattaert):
    Four elements added:
        self.dic_stim, self.sorted_dic_stim,
        self.dic_syn, self.sorted_dic_syn
"""

import random
from math import pi
import numpy as np
import class_animatLabModel as AnimatLabModel
import class_projectManager as ProjectManager
import class_animatLabSimulationRunner as AnimatLabSimRunner

from optimization import liste, findFirstType
from optimization import affichChartColumn, affichExtStim
from optimization import affichMotor
from optimization import affichNeurons, affichNeuronsFR
from optimization import affichConnexions, affichConnexionsFR
from optimization import enableStims, enableSynNS
from optimization import formTemplateSmooth, savecurve

from FoldersArm import FolderOrg
folders = FolderOrg()
# folders.affectDirectories()


class OptimizeSimSettings():
    """
    Creates and sets all variables needed in optimization process
    """
    def __init__(self, folders=FolderOrg,
                 model=AnimatLabModel.AnimatLabModel,
                 projMan=ProjectManager.ProjectManager,
                 sims=AnimatLabSimRunner.AnimatLabSimulationRunner,
                 pkFileName="paramOpt.pkl",
                 paramVSCDName=["nom1", "nom2"],
                 paramVSCDValue=[1, 2], paramVSCDType=[int, int],
                 paramVSCDCoul=['white', 'white'],
                 paramMarquezName=["nom1", "nom2"],
                 paramMarquezValue=[1, 2], paramMarquezType=[int, int],
                 paramMarquezCoul=['white', 'white']):

        self.folders = folders
        self.model = model
        self.projMan = projMan
        self.sims = sims
        self.pkFileName = pkFileName
        self.paramFicName = folders.animatlab_result_dir + self.pkFileName
        self.nb_processors = 1
        self.chart = model.getElementByType("Chart")
        self.chartName = []
        for ch in list(self.chart):
            self.chartName.append(ch.find("Name").text)
        self.selectedChart = 0
        self.collectInterval = self.chart[0].find("CollectInterval").text
        self.rateAsim = int(1/float(self.collectInterval))
        self.rate = self.rateAsim
        self.chartStart = float(self.chart[0].find("StartTime").text)
        self.ChartColumns = model.getElementByType("ChartCol0")
        self.ExternalStimuli = model.getElementByType("ExternalStimuli")
        self.motorP = model.getElementByType("MotorPosition")
        self.motorV = model.getElementByType("MotorVelocity")
        self.motorStimuli = [self.motorP, self.motorV]
        self.gravity = -9.81
        self.joints = model.getElementByType("Joint")
        self.jointName = []
        self.jointType = []
        self.jointLimUp = []
        self.jointLimDwn = []
        print("\n optSet: ANALYZING body segments and joints...")
        for jointNb in range(len(self.joints)):
            self.jointName.append(self.joints[jointNb].find("Name").text)
            print(self.jointName[jointNb], end=' ')
            self.jointType.append(self.joints[jointNb].find("Type").text)
            print(self.jointType[jointNb], end=' ')
            if self.jointType[jointNb] != "Hinge":
                print("No limits found")
                self.jointLimUp.append(0)
                self.jointLimDwn.append(0)
            else:
                #print "limits (deg) :",
                print("No limits found")
                limDwn = self.joints[jointNb].find("LowerLimit")
                self.jointLimDwn.append(float(limDwn.find("LimitPos").text))
                angle = self.jointLimDwn[jointNb] * 180 / pi
                # print "{:3.2f}".format(angle), "\t -->",
                print("{:3.2f}".format(angle), "\t -->", end=' ')
                limUp = self.joints[jointNb].find("UpperLimit")
                self.jointLimUp.append(float(limUp.find("LimitPos").text))
                angle = self.jointLimUp[jointNb] * 180 / pi
                # print "{:3.2f}".format(angle)
                print("{:3.2f}".format(angle))
        self.Neurons = model.getElementByType("Neurons")
        self.NeuronsFR = model.getElementByType("NeuronsFR")
        self.Adapters = model.getElementByType("Adapters")
        self.Synapses = model.getElementByType("Synapses")
        self.SynapsesFR = model.getElementByType("SynapsesFR")
        self.Connexions = model.getElementByType("Connexions")
        self.nbStims = len(self.ExternalStimuli)
        self.nbmotors = len(self.motorP) + len(self.motorV)
        self.nbNeurons = len(self.Neurons)
        self.nbAdapters = len(self.Adapters)
        self.nbSynapses = len(self.Synapses)
        self.nbConnexions = len(self.Connexions)
        self.nbNeuronsFR = len(self.NeuronsFR)
        self.nbSynapsesFR = len(self.SynapsesFR)
        self.tab_motors = affichMotor(model, self.motorStimuli, 0)
        self.tab_chartcolumns = affichChartColumn(self.ChartColumns, 0)
        self.tab_stims = affichExtStim(self, self.ExternalStimuli, 0)
        self.tab_neurons = affichNeurons(self, self.Neurons, 0)
        self.listeNeurons = liste(self.Neurons)
        self.tab_connexions = affichConnexions(model, self,
                                               self.Connexions, 0)
        self.tab_neuronsFR = affichNeuronsFR(self, self.NeuronsFR, 0)  # idem
        self.listeNeuronsFR = liste(self.NeuronsFR)
        self.tab_connexionsFR = affichConnexionsFR(model, self,
                                                   self.SynapsesFR, 0)
        
        self.win = None
        self.synSimSet = None
        self.stimSimSet = None
        self.mse_base = -1000
        self.coact_base = -1000
        self.mse_minus = -1000
        self.coact_minus = -1000
        self.mse_plus = -1000
        self.coact_plus = -1000

        self.rank_stim = {}
        self.rank_neuron = {}
        self.rank_syn = {}
        self.rank_neuronFR = {}
        self.rank_synFR = {}
        self.rank_chart_col = {'TimeSplice': 0, 'Time': 1}  # dictionnary
        self.chartColNames = ['TimeSplice', 'Time']  # chart column names
        self.stimParam = ["CurrentOn", "StartTime", "EndTime"]
        self.synParam = ["G"]
        self.synFRParam = ["Weight"]
        self.model.asimFile    # See where the .asim XML file is saved --
        # this is the file that is loaded to generate AnimatLab model object
        self.projMan.set_aproj(self.model)    # Assign the animatLabModel obj
        self.projMan.set_simRunner(self.sims)    # Assign the simulationSet obj
        # self.chart[0].find("StartTime").text = '0'  # sets chart start to 0
# TODO: consequences a verifier

        # creation of a dictionary to handle column names in the chart file
        for i in range(len(self.tab_chartcolumns)):
            self.rank_chart_col[self.tab_chartcolumns[i][0]] = i + 2
            self.chartColNames.append(self.tab_chartcolumns[i][0])

        # creation of a dictionary "rank_stim" to handle stimulus rank
        self.rank_stim = {}
        for i in range(len(self.tab_stims)):
            self.rank_stim[self.tab_stims[i][0]] = i

        # creation of a dictionary "rank_neuron" to handle neurons' rank
        self.rank_neuron = {}
        for i in range(len(self.tab_neurons)):
            self.rank_neuron[self.tab_neurons[i][0]] = i
        # creation of a dictionary "rank_syn" to handle connexions rank
        self.rank_syn = {}
        for i in range(len(self.tab_connexions)):
            self.rank_syn[self.tab_connexions[i][0]] = i

        # creation of a dictionary "rank_neuronFR" to handle neuronsFR' rank
        self.rank_neuronFR = {}
        for i in range(len(self.tab_neuronsFR)):
            self.rank_neuronFR[self.tab_neuronsFR[i][0]] = i
        # creation of a dictionary "rank_synFR" to handle connexionsFR rank
        self.rank_synFR = {}
        for i in range(len(self.tab_connexionsFR)):
            self.rank_synFR[self.tab_connexionsFR[i][0]] = i

        # Marquez parameters
        self.paramMarquezName = paramMarquezName
        self.paramMarquezValue = paramMarquezValue
        self.paramMarquezType = paramMarquezType
        self.paramMarquezCoul = paramMarquezCoul
        self.paramMarquez = {}
        self.startTest = 0.0
        self.startTwitch = 5.0
        self.endTwitch = 5.1
        self.endTest = 8.0
        self.twitStMusclesStNbs = [0, 1]
        self.sensoryNeuronNbs = []
        self.sensoryNeuronNames = []
        self.motorNeuronNbs = []
        self.motorNeuronNames = []
        self.sensoryNeuronFRNbs = [0, 6, 12, 14, 16, 19]
        self.motorNeuronFRNbs = [5, 11]
        self.sensColChartNbs = [17, 18, 19, 20, 21, 22]
        self.sensColChartNames = []
        self.mnColChartNbs = [2, 4]
        self.mnColChartNames = []
        self.twitStMusclesStNames = []
        self.nbruns = 3
        self.timeMes = 0.08
        self.delay = 0.02
        self.eta = 1000.0

        # VSCD parameters
        self.paramVSCDName = paramVSCDName
        self.paramVSCDValue = paramVSCDValue
        self.paramVSCDType = paramVSCDType
        self.paramVSCDCoul = paramVSCDCoul
        self.paramOpt = {}
        self.mvtcolumn = 6
        self.mvtColChartName = []
        self.startMvt1 = 0
        self.endMvt1 = 0
        self.endPos1 = 0
        self.angle1 = 0
        self.startMvt2 = 5
        self.endMvt2 = 5
        self.endPos2 = 5.3
        self.angle2 = 60
        self.startEQM = 3
        self.endEQM = 8
        self.allstim = 1
        self.dontChangeStimNbs = []
        self.dontChangeStimName = []
        self.disabledStimNbs = []
        self.disabledStimNames = []
        self.allsyn = 1
        self.dontChangeSynNbs = []
        self.dontChangeSynNames = []
        self.disabledSynNbs = []
        self.disabledSynNames = []
        self.dontChangeSynFRNbs = []
        self.dontChangeSynFRNames = []
        self.disabledSynFRNbs = []
        self.disabledSynFRNames = []
        self.seriesStimParam = ['CurrentOn']
        self.seriesSynParam = ['G']
        self.seriesSynNSParam = ['SynAmp']
        self.seriesSynFRParam = ['Weight']
        self.nbepoch = 1
        self.nbstimtrials = 1
        self.nbsyntrials = 1
        self.nbsteps = 4
        self.deltaStimCoeff = 1.5
        self.maxDeltaStim = 50
        self.multSynCoeff = 1.5
        self.maxMultSyn = 50
        self.coactivityFactor = 1000.0
        self.xCoactPenality1 = 100.0
        self.xCoactPenality2 = 1.0
        self.activThr = -0.06
        self.maxStim = 2e-08
        self.maxSynAmp = 50.0
        self.maxG = 10.0
        self.maxWeight = 5e-07
        self.limQuality = 0.0001
        self.defaultval = 100000
        self.limits = []
        self.mvtTemplate = formTemplateSmooth(self.rate, self.startMvt1,
                                              self.endMvt1, self.angle1,
                                              self.startMvt2, self.endMvt2,
                                              self.angle2, self.endPos2)

        # calculates the chart lines corresponding to time events
        self.lineStart1 = int((self.startEQM-self.chartStart)*self.rate)
        self.lineEnd1 = int((self.endPos1-self.chartStart)*self.rate)
        self.lineStart2 = int((self.endMvt2-self.chartStart)*self.rate)
        self.lineEnd2 = int((self.endEQM-self.chartStart)*self.rate)
        self.lineStartTot = int((self.startEQM-self.chartStart)*self.rate)
        self.lineEndTot = int((self.endEQM-self.chartStart)*self.rate)
        self.stimsTot = []
        self.enabledstimList = []
        self.stimList = []  # list of stim to be explored in the optimization
        self.orderedstimsTot = []
        self.shuffledstimsTot = []
        self.total = [self.stimsTot, self.shuffledstimsTot,
                      self.lineStartTot, self.lineEndTot, self.mvtTemplate]
        self.allPhasesStim = [self.total]
        self.synsTot, self.synsTotFR = [], []
        self.synList = []
        self.orderedsynsTot = []
        self.shuffledsynsTot = random.sample(self.orderedsynsTot,
                                             len(self.orderedsynsTot))
        self.totalsyn = [self.synsTot, self.shuffledsynsTot,
                         self.lineStartTot, self.lineEndTot, self.mvtTemplate]
        self.synListFR = []
        self.synsTotFR = self.synListFR  # excluded syns are removed from list
        self.orderedsynsTotFR = []
        self.shuffledsynsTotFR = random.sample(self.orderedsynsTotFR,
                                               len(self.orderedsynsTotFR))
        self.totalsynFR = [self.synsTotFR, self.shuffledsynsTotFR,
                           self.lineStartTot, self.lineEndTot,
                           self.mvtTemplate]
        # for two separate phases
        # self. allPhasesSyn = [self.phase1syn, self.phase2syn]
        # for only one phase
        # self.allPhasesSyn = [self.phase1syn]
        # self.allPhasesSyn = [self.phase2syn]
        self.allPhasesSyn = [self.totalsyn]
        self.allPhasesSynFR = [self.totalsynFR]

        # CMAes parameters
        self.seuilMSEsave = 100
        self.x0, self.realx0 = [], []
        self.lower, self.upper = [], []
        self.reallower, self.realupper = [], []
        self.stimParName = []
        self.synParName = []
        self.synNSParName = []
        self.synFRParName = []
        self.struct_param = []
        self.stimMin = []
        self.stimMax = []
        self.synMin = []
        self.synMax = []
        self.realxMin = []
        self.realxMax = []
        self.xparNameDict = {}
        self.cmaes_sigma = 0.0035
        self.fourchetteStim = 5.0
        self.fourchetteSyn = 5.0
        self.spanStim, self.spanSyn = 100, 100
        self.stimName = []
        self.nbevals = 100
        self.fromAsim = 0
        self.pairs = np.array([])
        self.behavs = np.array([])
        self.nbsim = 0
        self.chosen = "base"
        self.nbMaxPairs = 10000
        self.ideal_behav = [0, 0]
        self.seuilMSETyp = "Var"
        self.datastructure = {}
        self.bestparamList = []
        self.bestchartList = []
        self.besterrList = []
        self.parx = 0
        self.pary = 1
        # --------  variables used in GEPrand -----------------
        self.list_save_steps = [100, 500, 1000, 2000]
        self.list_save_flags = [0, 0, 0, 0]
        # -----------------------------------------------------
        for i in range(len(self.tab_stims)):
            self.stimName.append(self.tab_stims[i][0])
        self.motorName = []
        for i in range(len(self.tab_motors)):
            self.motorName.append(self.tab_motors[i][0])
        self.connexName = []
        for i in range(len(self.tab_connexions)):
            self. connexName.append(self.tab_connexions[i][0])
        self.connexFRName = []
        for i in range(len(self.tab_connexionsFR)):
            self.connexFRName.append(self.tab_connexionsFR[i][0])
        self.neuronNames = []
        for i in range(len(self.tab_neurons)):
            self.neuronNames.append(self.tab_neurons[i][0])
        self.neuronFRNames = []
        for i in range(len(self.tab_neuronsFR)):
            self.neuronFRNames.append(self.tab_neuronsFR[i][0])
        self.other_constraints = {'max_endangle': 115,
                                  'min_endangle' : 10,
                                  'max_endMN_pot': -0.061}
        self.otherconstraints_names = ['max_endangle', 'min_endangle',
                                       'max_endMN_pot']
        self.otherconstraints_short_names = ['MaxA', 'minA', 'EndMNV']
        self.dic_oc_short = {}
        for idx, name in enumerate(self.otherconstraints_names):
            self.dic_oc_short[name] = self.otherconstraints_short_names[idx]
        
        # ################################################################
        #                   ATTENTION !!!
        for phase in range(len(self.allPhasesStim)):
            [listSt, shuffledstims,
             self.lineStart, self.lineEnd,
             self.template] = self.allPhasesStim[phase]
        self.listSt = listSt
        # here we use only onse phase => phase = 0
        # ################################################################

    def actualizeparamMarquez(self):
        print()
        print("optSet: actualizing Marquez params")
        # Creation of a dictionary for Marquez parameter handling
        self.paramMarquez = {}
        i = 0
        for par in (self.paramMarquezName):
            self.paramMarquez[par] = self.paramMarquezValue[i]
            i += 1
        # ##############################################################
        #  Selection of "SensoryNeurons" & "MotoNeurons"  for Marquez  #
        # ##############################################################
        self.sensoryNeuronNbs = self.paramMarquez['sensoryNeuronNbs']
        self.sensoryNeuronNames = []
        for i in self.sensoryNeuronNbs:
            self.sensoryNeuronNames.append(self.neuronNames[i])
        self.sensoryNeuronFRNbs = self.paramMarquez['sensoryNeuronFRNbs']
        self.sensoryNeuronFRNames = []
        for i in self.sensoryNeuronFRNbs:
            self.sensoryNeuronFRNames.append(self.neuronFRNames[i])
        self.motorNeuronNbs = self.paramMarquez['motorNeuronNbs']
        self.motorNeuronNames = []
        for i in self.motorNeuronNbs:
            self.motorNeuronNames.append(self.neuronNames[i])
        self.motorNeuronFRNbs = self.paramMarquez['motorNeuronFRNbs']
        self.motorNeuronFRNames = []
        for i in self.motorNeuronFRNbs:
            self.motorNeuronFRNames.append(self.neuronFRNames[i])
        self.sensColChartNbs = self.paramMarquez['sensColChartNbs']
        self.sensColChartNames = []
        for i in self.sensColChartNbs:
            self.sensColChartNames.append(self.chartColNames[i])
        self.mnColChartNbs = self.paramMarquez['mnColChartNbs']
        self.mnColChartNames = []
        for i in self.mnColChartNbs:
            self.mnColChartNames.append(self.chartColNames[i])
        self.twitStMusclesStNbs = self.paramMarquez['twitStMusclesStNbs']
        self.twitStMusclesStNames = []
        print("   ======================")
        print("   twitStMusclesStNb stName")
        for i in self.twitStMusclesStNbs:
            self.twitStMusclesStNames.append(self.stimName[i])
            print("   ", i, self.stimName[i])
        print("   ======================")
        self.nbruns = self.paramMarquez['nbruns']
        self.timeMes = self.paramMarquez['timeMes']
        self.delay = self.paramMarquez['delay']
        self.eta = self.paramMarquez['eta']
        
        

    def actualizeparamVSCD(self):
        print()
        print("optSet: actualizing VSCD params")
        # Creation of a dictionary for optimization parameter handling
        self.paramOpt = {}
        i = 0
        for par in (self.paramVSCDName):
            self.paramOpt[par] = self.paramVSCDValue[i]
            i += 1
        self.selectedChart = self.paramOpt['selectedChart']
        typ = "ChartCol" + str(self.selectedChart)
        self.ChartColumns = self.model.getElementByType(typ)
        self.tab_chartcolumns = affichChartColumn(self.ChartColumns, 0)
        self.rank_chart_col = {'TimeSplice': 0, 'Time': 1}  # dictionnary
        self.chartColNames = ['TimeSplice', 'Time']  # chart column names
        for i in range(len(self.tab_chartcolumns)):
            self.rank_chart_col[self.tab_chartcolumns[i][0]] = i + 2
            self.chartColNames.append(self.tab_chartcolumns[i][0])
        self.chartStart = float(self.chart[self.selectedChart].
                                find("StartTime").text)
        self.collectInterval = self.chart[self.selectedChart].\
            find("CollectInterval").text
        self.rateAsim = int(1/float(self.collectInterval))
        self.rate = self.rateAsim
        self.mvtcolumn = self.paramOpt['mvtcolumn']
        self.mvtColChartName.append(self.chartColNames[self.mvtcolumn])
        self.startMvt1 = self.paramOpt['startMvt1']
        self.endMvt1 = self.paramOpt['endMvt1']
        self.endPos1 = self.paramOpt['endPos1']
        self.angle1 = self.paramOpt['angle1']
        self.startMvt2 = self.paramOpt['startMvt2']
        self.endMvt2 = self.paramOpt['endMvt2']
        self.endPos2 = self.paramOpt['endPos2']
        self.angle2 = self.paramOpt['angle2']
        self.startEQM = self.paramOpt['startEQM']
        self.endEQM = self.paramOpt['endEQM']
        self.allstim = self.paramOpt['allstim']
        # calculates the chart lines corresponding to time events
        self.lineStart1 = int((self.startEQM-self.chartStart)*self.rate)
        self.lineEnd1 = int((self.endPos1-self.chartStart)*self.rate)
        self.lineStart2 = int((self.endMvt2-self.chartStart)*self.rate)
        self.lineEnd2 = int((self.endEQM-self.chartStart)*self.rate)
        self.lineStartTot = int((self.startEQM-self.chartStart)*self.rate)
        self.lineEndTot = int((self.endEQM-self.chartStart)*self.rate)
        
        print("optSet.chartStart=", self.chartStart, "\t", end=' ')
        print("optSet.lineStart1=", self.lineStart1, end=' ')
        print("optSet.lineEnd1=", self.lineEnd1, end=' ')
        print("optSet.lineStart2=", self.lineStart2, end=' ')
        print("optSet.lineEnd2=", self.lineEnd2)

        # self.allsyn = self.paramOpt['allsyn']
        print("   #################################")
        print("   chart File : ", self.chartName[self.selectedChart])
        print('   column',  '\t', 'name')
        for i in range(len(self.rank_chart_col)):
            print("   ", end=' ')
            print(self.rank_chart_col[self.chartColNames[i]], '\t', end=' ')
            print(self.chartColNames[i])
        print("   #################################")

        self.mvtTemplate = formTemplateSmooth(self.rate, self.startMvt1,
                                              self.endMvt1, self.angle1,
                                              self.startMvt2, self.endMvt2,
                                              self.angle2, self.endPos2)
        savecurve(self.mvtTemplate,
                  self.folders.animatlab_result_dir, "template.txt")
        print("   mvtTemplate.txt saved in", end=' ')
        print(self.folders.animatlab_result_dir)
        """
        # ##############################################################
        #   Selection of "dontChange" & "disabled" for Optimization    #
        # ##############################################################
        """
        # ========================= Stimuli ============================
        self.dontChangeStimNbs = self.paramOpt['dontChangeStimNbs']
        self.dontChangeStimName = []
        for i in self.dontChangeStimNbs:
            self.dontChangeStimName.append(self.stimName[i])
        self.disabledStimNbs = self.paramOpt['disabledStimNbs']
        self.disabledStimNames = []
        for i in self.disabledStimNbs:
            self.disabledStimNames.append(self.stimName[i])

        self.stimsTot = []
        for i in range(len(self.tab_stims)):
            self.stimsTot.append(i)    # selects all stimulis
        self.enabledstimList = []
        for stim in range(len(self.stimsTot)):
            stimRank = self.stimsTot[stim]
            if stimRank not in self.disabledStimNbs:
                self.enabledstimList.append(stimRank)
        """
        # --------------------------------------------------------------
        #           enabled external stimuli --> 'true'
        #           disabled external stimuli.--> 'false'
        # --------------------------------------------------------------
        """
        enableStims(self.ExternalStimuli, self.enabledstimList)
        print("   optSet : Enabled external stimuli set to 'true'", end=' ')
        print("   and excluded to 'false'")
        # self.tab_stims = affichExtStim(self.ExternalStimuli, 0)
        #
        self.stimList = []  # list of stim to be explored in the optimization
        for stim in range(len(self.enabledstimList)):
            stimRank = self.enabledstimList[stim]
            if stimRank not in self.dontChangeStimNbs:  # do not includes
                self.stimList.append(stimRank)           # 'dontChangeStimNbs'
        # After changing a property, the updated model (.asim and .aproj)
        # will be saved in the FinalModel dir when the param file will be
        # saved in GUI_AnimatPar.py

        self.orderedstimsTot = []
        for i in range(len(self.stimList)):
            self.orderedstimsTot.append(i)
        self.shuffledstimsTot = random.sample(self.orderedstimsTot,
                                              len(self.orderedstimsTot))
        self.total = [self.stimList, self.shuffledstimsTot,
                      self.lineStartTot, self.lineEndTot, self.mvtTemplate]
        self.allPhasesStim = [self.total]

        # ======================== Synapses ============================
        self.dontChangeSynNbs = self.paramOpt['dontChangeSynNbs']
        self.dontChangeSynNames = []
        for i in self.dontChangeSynNbs:
            self.dontChangeSynNames.append(self.connexName[i])
        self.disabledSynNbs = self.paramOpt['disabledSynNbs']
        self.disabledSynNames = []
        for i in self.disabledSynNbs:
            self.disabledSynNames.append(self.connexName[i])
        model= self.model
        Connexions = self.Connexions
        disabledSynNbs = self.disabledSynNbs
        enableSynNS(model, Connexions, disabledSynNbs, show=1)

        self.dontChangeSynFRNbs = self.paramOpt['dontChangeSynFRNbs']
        self.dontChangeSynFRNames = []
        for i in self.dontChangeSynFRNbs:
            self.dontChangeSynFRNames.append(self.connexFRName[i])
        self.disabledSynFRNbs = self.paramOpt['disabledSynFRNbs']
        self.disabledSynFRNames = []
        for i in self.disabledSynFRNbs:
            self.disabledSynFRNames.append(self.connexFRName[i])


        self.tab_motors = affichMotor(self.model, self.motorStimuli, 0)
        self.tab_chartcolumns = affichChartColumn(self.ChartColumns, 0)
        self.tab_stims = affichExtStim(self, self.ExternalStimuli, 0)
        self.tab_neurons = affichNeurons(self, self.Neurons, 0)
        self.tab_neuronsFR = affichNeuronsFR(self, self.NeuronsFR, 0)

        
        self.synsTot, self.synsTotFR = [], []
        # ###########   Connexions   #########################
        # --------------------------------------
        # Synapses between 'voltage' neurons
        # --------------------------------------
        for i in range(len(self.tab_connexions)):
            self.synsTot.append(i)    # selects all synapses
        self.synList = []
        for syn in range(len(self.synsTot)):
            synRank = self.synsTot[syn]
            if synRank not in self.disabledSynNbs + self.dontChangeSynNbs:
                self.synList.append(synRank)
        # self.synList  : list without excluded syns and dontChange syns
        self.orderedsynsTot = []
        for i in range(len(self.synList)):
            self.orderedsynsTot.append(i)
        self.shuffledsynsTot = random.sample(self.orderedsynsTot,
                                             len(self.orderedsynsTot))
        self.totalsyn = [self.synList, self.shuffledsynsTot,
                         self.lineStartTot, self.lineEndTot, self.mvtTemplate]
        # --------------------------------------
        # Synapses between 'rate' neurons
        # --------------------------------------
        for i in range(len(self.tab_connexionsFR)):
            self.synsTotFR.append(i)    # selects all stimuli
        self.synListFR = []
        for syn in range(len(self.synsTotFR)):
            synRank = self.synsTotFR[syn]
            if synRank not in self.disabledSynFRNbs + self.dontChangeSynFRNbs:
                self.synListFR.append(synRank)
        # self.synListFR  : list without excluded synFRs and dontchange synFRs
        self.orderedsynsTotFR = []
        for i in range(len(self.synListFR)):
            self.orderedsynsTotFR.append(i)
        self.shuffledsynsTotFR = random.sample(self.orderedsynsTotFR,
                                               len(self.orderedsynsTotFR))
        self.totalsynFR = [self.synListFR, self.shuffledsynsTotFR,
                           self.lineStartTot, self.lineEndTot,
                           self.mvtTemplate]
        # for two separate phases
        # self. allPhasesSyn = [self.phase1syn, self.phase2syn]
        # for only one phase
        # self.allPhasesSyn = [self.phase1syn]
        # self.allPhasesSyn = [self.phase2syn]
        self.allPhasesSyn = [self.totalsyn]
        self.allPhasesSynFR = [self.totalsynFR]
        self.seriesStimParam = self.paramOpt['seriesStimParam']
        self.seriesSynParam = self.paramOpt['seriesSynParam']
        self.seriesSynNSParam = self.paramOpt['seriesSynNSParam']
        self.seriesSynFRParam = self.paramOpt['seriesSynFRParam']
        self.nbepoch = self.paramOpt['nbepoch']
        self.nbstimtrials = self.paramOpt['nbstimtrials']
        self.nbsyntrials = self.paramOpt['nbsyntrials']
        self.nbsteps = self.paramOpt['nbsteps']
        self.deltaStimCoeff = self.paramOpt['deltaStimCoeff']
        self.maxDeltaStim = self.paramOpt['maxDeltaStim']
        self.multSynCoeff = self.paramOpt['multSynCoeff']
        self.maxMultSyn = self.paramOpt['maxMultSyn']
        self.coactivityFactor = self.paramOpt['coactivityFactor']
        self.activThr = self.paramOpt['activThr']
        self.limQuality = self.paramOpt['limQuality']

        self.maxStim = self.paramOpt['maxStim']
        self.maxSynAmp = self.paramOpt['maxSynAmp']
        self.maxG = self.paramOpt['maxG']
        self.maxWeight = self.paramOpt['maxWeight']
        self.defaultval = self.paramOpt['defaultval']
        self.limits = [self.maxStim, self.maxSynAmp,
                       self.maxG, self.maxWeight]
        self.cmaes_sigma = self.paramOpt['cmaes_sigma']
        self.spanStim = self.paramOpt['fourchetteStim']
        self.spanSyn = self.paramOpt['fourchetteSyn']
        self.actualizeparamCMAes(realx0=[])

    def actualizeparamCMAes(self, realx0=[]):
        self.x0 = []
        self.realx0 = realx0
        self.lower, self.upper = [], []
        self.reallower, self.realupper = [], []
        self.stimParName = []
        self.synParName = []
        self.synNSParName = []
        self.synFRParName = []
        self.struct_param = []
        self.xparName = []
        self.xparNameDict = {}
        self.stimMin = []
        self.stimMax = []
        self.synMin = []
        self.synMax = []
        self.realxMin = []
        self.realxMax = []
        if realx0 == []:
            self.fromAsim = 1
        else:
            self.fromAsim = 0
        # ################################################################
        #                   ATTENTION !!!
        for phase in range(len(self.allPhasesStim)):
            [listSt, self.shuffledstims,
             self.lineStart, self.lineEnd,
             self.template] = self.allPhasesStim[phase]
        self.listSt = listSt
        # here we use only onse phase => phase = 0
        # ################################################################
        self.dic_stim = {}
        if self.fromAsim:
            print("stim from asim:")
        else:
            print("stim from realx0:")
        for param in range(len(self.seriesStimParam)):
            paramTyp = self.seriesStimParam[param]
            if paramTyp == "StartTime":
                for stim in range(len(listSt)):
                    stimMax = self.endPos2
                    stimMin = 0.
                    self.realxMax.append(stimMax)
                    self.realxMin.append(stimMin)
                    if self.fromAsim:
                        rx0 = self.tab_stims[listSt[stim]][1]
                        self.realx0.append(rx0)
                    else:
                        rx0 = self.realx0[stim]
                    realdelta = float(stimMax - stimMin) * self.spanStim / 100
                    reallower = max((rx0 - realdelta), stimMin)
                    self.reallower.append(reallower)
                    realupper = min((rx0 + realdelta), stimMax)
                    self.realupper.append(realupper)
                    temp = self.tab_stims[listSt[stim]][0] + "." + paramTyp
                    self.stimParName.append(temp)
                    self.xparName.append(temp)
                    print(temp, rx0)
                    # self.upper.append(1.)
                    # self.lower.append(0.)
                    x0 = (rx0-stimMin)/(stimMax-stimMin)
                    self.x0.append(x0)
                    delta = self.spanStim / 100
                    lower = max((x0 - delta), 0)
                    self.lower.append(lower)
                    # upper = min((x0 + delta), 1)
                    upper = x0 + delta
                    self.upper.append(upper)

            elif paramTyp == "EndTime":
                for stim in range(len(listSt)):
                    stimMax = self.endPos2
                    stimMin = 0.
                    self.realxMax.append(stimMax)
                    self.realxMin.append(stimMin)
                    if self.fromAsim:
                        rx0 = self.tab_stims[listSt[stim]][2]
                        self.realx0.append(rx0)
                    else:
                        rx0 = self.realx0[stim]
                    realdelta = float(stimMax - stimMin) * self.spanStim\
                        / 100
                    reallower = max((rx0 - realdelta), stimMin)
                    self.reallower.append(reallower)
                    realupper = min((rx0 + realdelta), stimMax)
                    self.realupper.append(realupper)
                    temp = self.tab_stims[listSt[stim]][0] + "." + paramTyp
                    self.stimParName.append(temp)
                    self.xparName.append(temp)
                    print(temp, rx0)
                    # self.upper.append(1.)
                    # self.lower.append(0.)
                    x0 = (rx0-stimMin)/(stimMax-stimMin)
                    self.x0.append(x0)
                    delta = self.spanStim / 100
                    lower = max((x0 - delta), 0)
                    self.lower.append(lower)
                    # upper = min((x0 + delta), 1)
                    upper = x0 + delta
                    self.upper.append(upper)

            elif paramTyp == "CurrentOn":
                for stim in range(len(listSt)):
                    stimMax = self.maxStim
                    stimMin = - stimMax
                    self.realxMax.append(stimMax)
                    self.realxMin.append(stimMin)
                    if self.fromAsim:
                        rx0 = self.tab_stims[listSt[stim]][3]
                        self.realx0.append(rx0)
                    else:
                        rx0 = self.realx0[stim]
                    realdelta = float(stimMax - stimMin) * self.spanStim\
                        / 100
                    reallower = max((rx0 - realdelta), stimMin)
                    self.reallower.append(reallower)
                    realupper = min((rx0 + realdelta), stimMax)
                    self.realupper.append(realupper)
                    temp = self.tab_stims[listSt[stim]][0] + "." + paramTyp
                    self.stimParName.append(temp)
                    self.xparName.append(temp)
                    print(temp, rx0)
                    self.dic_stim[temp] = rx0
                    # self.upper.append(1.)
                    # self.lower.append(0.)
                    x0 = (rx0-stimMin)/(stimMax-stimMin)
                    self.x0.append(x0)
                    delta = self.spanStim / 100
                    # lower = max((x0 - delta), 0)
                    lower = x0 - delta
                    self.lower.append(lower)
                    # upper = min((x0 + delta), 1)
                    upper = x0 + delta
                    self.upper.append(upper)

        self.dic_spiking_syn = {}
        deb = len(self.stimParName)
        for synparam in range(len(self.seriesSynParam)):
            synparamName = self.seriesSynParam[synparam]
            if synparamName == 'G':
                if self.tab_connexions != []:
                    firstConnexion = findFirstType(self.model, "Connexions")
                    if self.fromAsim:
                        print("syn from asim:")
                    else:
                        print("syn from realx0:")
                    for idx, syn in enumerate(self.synList):
                        if self.tab_connexions[syn][5] == 'SpikingChemical':
                            rg = syn + firstConnexion
                            temp = self.model.lookup["Name"][rg] +\
                                "." + synparamName
                            print(self.tab_connexions[syn][5], end=' ')
                            print(temp, end=' ')
                            self.synParName.append(temp)
                            self.xparName.append(temp)
                            synMax = self.maxG
                            synMin = 0.
                            self.realxMax.append(synMax)
                            self.realxMin.append(synMin)
                            if self.fromAsim:
                                rx0 = self.tab_connexions[syn][3]
                                self.realx0.append(rx0)
                            else:
                                rx0 = self.realx0[deb + idx]
                            print(rx0, "uS")
                            self.dic_spiking_syn[temp] = rx0
                            realdelta = float(synMax - synMin) *\
                                self.spanSyn / 100
                            reallower = max((rx0 - realdelta), synMin)
                            self.reallower.append(reallower)
                            realupper = min((rx0 + realdelta), synMax)
                            self.realupper.append(realupper)
                            # self.upper.append(1.)
                            # self.lower.append(0.)
                            x0 = (rx0-synMin)/(synMax-synMin)
                            self.x0.append(x0)
                            delta = self.spanSyn / 100
                            lower = max((x0 - delta), 0)
                            self.lower.append(lower)
                            # upper = min((x0 + delta), 1)
                            upper = x0 + delta
                            self.upper.append(upper)

        self.dic_nonspiking_syn = {}
        deb = len(self.stimParName) + len(self.synParName)
        try:
            for synparam in range(len(self.seriesSynNSParam)):
                synparamName = self.seriesSynNSParam[synparam]
                if synparamName == 'SynAmp':
                    if self.tab_connexions != []:
                        tabvalrealsynxO = []
                        if self.fromAsim:
                            print("synNS from asim:")
                        else:
                            print("synNS from realx0:")
                        for idx, syn in enumerate(self.synList):
                            if self.tab_connexions[syn][5] == 'NonSpikingChemical':
                                synMax = self.maxSynAmp
                                rx0 = self.tab_connexions[syn][1]
                                tabvalrealsynxO.append(rx0)
                            maxval = max(tabvalrealsynxO)
                            if maxval > synMax:
                                    synMax = maxval
                                    self.maxSynAmp = maxval
                                    print("WARNING: SynAmp larger than synMax...")
                        for idx, syn in enumerate(self.synList):
                            synapseTempID = self.Connexions[syn].\
                                find("SynapseTypeID").text
                            synapseTempName = self.model.\
                                getElementByID(synapseTempID).\
                                find("Name").text
                            temp = synapseTempName + "." + synparamName
                            print(self.tab_connexions[syn][5], end=' ')
                            print(temp, end=' ')
                            self.synNSParName.append(temp)
                            self.xparName.append(temp)
                            synMin = 0.
                            self.realxMax.append(synMax)
                            self.realxMin.append(synMin)
                            if self.fromAsim:
                                rx0 = self.tab_connexions[syn][1]
                                self.realx0.append(rx0)
                            else:
                                rx0 = self.realx0[deb + idx]
                            print(rx0, "uS")
                            self.dic_nonspiking_syn[temp] = rx0
                            realdelta = float(synMax - synMin) *\
                                self.spanSyn / 100
                            reallower = max((rx0 - realdelta), synMin)
                            self.reallower.append(reallower)
                            realupper = min((rx0 + realdelta), synMax)
                            self.realupper.append(realupper)
                            # self.upper.append(1.)
                            # self.lower.append(0.)
                            x0 = (rx0-synMin)/(synMax-synMin)
                            self.x0.append(x0)
                            delta = self.spanSyn / 100
                            lower = max((x0 - delta), 0)
                            self.lower.append(lower)
                            # upper = min((x0 + delta), 1)
                            upper = x0 + delta
                            self.upper.append(upper)
        except Exception as e:
            print(e)

        self.dic_FR_syn = {}
        deb = len(self.stimParName) + len(self.synParName) +\
            len(self.synNSParName)
        for synparam in range(len(self.seriesSynFRParam)):
            synparamName = self.seriesSynFRParam[synparam]
            if synparamName == "Weight":
                if self.tab_connexionsFR != []:
                    firstConnexion = findFirstType(self.model, "SynapsesFR")
                    if self.fromAsim:
                        print("synFR from asim:")
                    else:
                        print("synFR from realx0:")
                    for idx, synFR in enumerate(self.synListFR):
                        rg = self.synListFR[idx] + firstConnexion
                        temp = self.model.lookup["Name"][rg] +\
                            "." + synparamName
                        print(temp, end=' ')
                        self.synFRParName.append(temp)
                        self.xparName.append(temp)
                        if self.fromAsim:
                            rx0 = self.tab_connexionsFR[synFR][1]
                            self.realx0.append(rx0)
                        else:
                            rx0 = self.realx0[deb + idx]
                        print(rx0)
                        self.dic_FR_syn[temp] = rx0
                        if rx0 >= 0:
                            synMax = self.maxWeight
                            synMin = 0.
                        else:
                            synMax = 0.
                            synMin = -self.maxWeight
                        self.realxMax.append(synMax)
                        self.realxMin.append(synMin)
                        realdelta = float(synMax - synMin) *\
                            self.spanSyn / 100
                        reallower = max((rx0 - realdelta), synMin)
                        self.reallower.append(reallower)
                        realupper = min((rx0 + realdelta), synMax)
                        self.realupper.append(realupper)
                        # self.upper.append(1.)
                        # self.lower.append(0.)
                        x0 = (rx0-synMin)/(synMax-synMin)
                        self.x0.append(x0)
                        delta = self.spanSyn / 100
                        lower = max((x0 - delta), 0)
                        self.lower.append(lower)
                        # upper = min((x0 + delta), 1)
                        upper = x0 + delta
                        self.upper.append(upper)
        """
        self.dic_stim = {}
        for stim in self.tab_stims:
            if stim[5] == 'True':
                st_name = stim[0]
                curr = stim[3]*1e9
                curr = round(curr * 1000)/1000
                self.dic_stim[st_name] = curr
        sorted_stim_list = sorted(self.dic_stim.items())
        self.sorted_dic_stim = {}
        [self.sorted_dic_stim.update({k:v}) for k,v in sorted_stim_list] 
        
        self.dic_syn = {}
        for idx, syn in enumerate(self.tab_connexions):
            if idx not in self.disabledSynNbs + self.dontChangeSynNbs:
                syn_name = syn[0]
                cond = syn[1]
                cond = round(cond * 1000)/1000
                self.dic_syn[syn_name] = cond
        sorted_syn_list = sorted(self.dic_syn.items())
        self.sorted_dic_syn = {}
        [self.sorted_dic_syn.update({k:v}) for k,v in sorted_syn_list]
        """
        self.struct_param = []
        for st in range(len(self.stimParName)):
            self.struct_param.append("st")
        for sy in range(len(self.synParName)):
            self.struct_param.append("sy")
        for syNS in range(len(self.synNSParName)):
            self.struct_param.append("syNS")
        for syFR in range(len(self.synFRParName)):
            self.struct_param.append("syFR")

        print(self.realx0)
        for idx, xname in enumerate(self.xparName):
            self.xparNameDict[xname] = idx

    def build_paramserieFrom_simset(self, x0, simSet):
        listparams = []
        for idx, dic in enumerate(simSet.samplePts):
            x = []
            x[:] = x0[:]
            # parName = dic.keys()[0]
            parName = list(dic.keys())[0]
            val = dic[parName]
            valMin = 100000
            rgpar = self.xparNameDict[parName]
            parTyp = parName[parName.find(".") + 1:]
            if parTyp == "CurrentOn":
                valMax = self.maxStim
                valMin = -self.maxStim
            elif parTyp == "StartTime":
                valMax = self.endPos2
                valMin = 0.
            elif parTyp == "EndTime":
                valMax = self.endPos2
                valMin = 0.
            elif parTyp == "SynAmp":
                valMax = self.maxSynAmp
                valMin = 0
            elif parTyp == "Weight":
                if val >= 0:
                    valMax = self.maxWeight
                    valMin = 0.
                else:
                    valMax = 0.
                    valMin = -self.maxWeight
            elif parTyp == "G":
                valMax = self.maxG
                valMin = 0.
            if valMin != 100000:
                valN = (val-valMin)/(valMax-valMin)
                x[rgpar] = valN
            # print valN
                listparams.append(x)
                paramserie = np.array(listparams)
        # print paramserie
        return paramserie

    def update_optSetParamVSCD(self):
        """
        This procedure adapts paramVSCD to upgraded version that includes
        seriesSynNSParam and in which "allsyns" has been removed
        """
        self.paramVSCDName[16] = self.paramVSCDName[17]
        self.paramVSCDType[16] = self.paramVSCDType[17]
        self.paramVSCDValue[16] = self.paramVSCDValue[17]
        self.paramVSCDName[17] = self.paramVSCDName[18]
        self.paramVSCDType[17] = self.paramVSCDType[18]
        self.paramVSCDValue[17] = self.paramVSCDValue[18]
        self.paramVSCDName[18] = self.paramVSCDName[19]
        self.paramVSCDType[18] = self.paramVSCDType[19]
        self.paramVSCDValue[18] = self.paramVSCDValue[19]
        self.paramVSCDName[19] = self.paramVSCDName[20]
        self.paramVSCDType[19] = self.paramVSCDType[20]
        self.paramVSCDValue[19] = self.paramVSCDValue[20]
        self.paramVSCDName[20] = self.paramVSCDName[21]
        self.paramVSCDType[20] = self.paramVSCDType[21]
        self.paramVSCDValue[20] = self.paramVSCDValue[21]
        self.paramVSCDName[21] = 'seriesSynNSParam'
        self.paramVSCDType[21] = list
        self.paramVSCDValue[21] = ['SynAmp']

    def printParams(self, paramName, paramValue):
        for rg in range(len(paramValue)):
            if len(paramName[rg]) <= 11:
                tab = "\t\t\t= "
            # elif len(self.paramName[rg]) <= 7:
            #    tab = "\t\t\t= "
            elif len(paramName[rg]) <= 18:
                tab = "\t\t= "
            elif len(paramName[rg]) <= 29:
                tab = "\t= "
            if rg < 10:
                no = '0' + str(rg)
            else:
                no = str(rg)
            print(no, paramName[rg], tab, end=' ')
            print(type(paramValue[rg]), "\t", paramValue[rg])

    def realFromNorm(self, parName, norm):
        rgpar = self.xparNameDict[parName]
        rxmin = self.realxMin[rgpar]
        rxmax = self.realxMax[rgpar]
        rval = norm*(rxmax-rxmin) + rxmin
        None
        return rval

    def normFromReal(self, parName, rval):
        rgpar = self.xparNameDict[parName]
        rxmin = self.realxMin[rgpar]
        rxmax = self.realxMax[rgpar]
        norm = (rval-rxmin)/(rxmax-rxmin)
        None
        return norm
