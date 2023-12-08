# -*- coding: utf-8 -*-
"""
Test to ensure that animatlabRunner is working OK
Created on Wed Nov 14 11:32:25 2018
@author: D. Cattaert
Translated in Python 3.8 Jan 2023 (D. Cattaert)
"""

import os

import class_animatLabModel as AnimatLabModel
import class_animatLabSimulationRunner as AnimatLabSimRunner
import class_simulationSet as SimulationSet
import class_projectManager as ProjectManager

from FoldersArm import FolderOrg
from animatlabOptimSetting import OptimizeSimSettings

from optimization import getInfoComputer
from optimization import setPlaybackControlMode
from optimization import affichMotor
from optimization import affichNeurons, affichNeuronsFR
from optimization import affichExtStim
from optimization import affichConnexions, affichConnexionsFR
from optimization import writeTitres
# from optimization import setMotorStimsOff
from optimization import setMotorStimsON
from optimization import copyFileDir
from optimization import findTxtFileName
from optimization import readTablo

from mainOpt import checknonzeroExtStimuli
from mainOpt import checknonzeroSyn
from mainOpt import checknonzeroSynFR
from mainOpt import loadParams
from mainOpt import readAnimatLabDir
# from mainOpt import readAnimatLabV2ProgDir


def initAnimatLab(animatsimdir, animatLabV2ProgDir):
    if animatsimdir != "":
        subdir = os.path.split(animatsimdir)[-1]
        print(subdir)
        rootdir = os.path.dirname(animatsimdir)
        folders = FolderOrg(animatlab_root=rootdir,
                            python27_source_dir=animatLabV2ProgDir,
                            subdir=subdir)
        # folders.affectDirectories()

        ResultDir = os.path.join(folders.animatlab_rootFolder,
                                 "ResultFiles")
        if not os.path.exists(ResultDir):
            os.makedirs(ResultDir)
            copyFileDir(animatsimdir,
                        ResultDir,
                        copy_dir=0)
        FinalDir = os.path.join(folders.animatlab_rootFolder, "FinalModel")

        if not os.path.exists(FinalDir):
            os.makedirs(FinalDir)
            copyFileDir(animatsimdir,
                        FinalDir,
                        copy_dir=0)
        SimFilesDir = os.path.join(folders.animatlab_rootFolder, "SimFiles")

        if not os.path.exists(SimFilesDir):
            os.makedirs(SimFilesDir)
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

    else:
        print("No selected directory  run GUI_AnimatLabOptimization.py")
        return [False]

    if animatsimdir != "":
        """
        folders.animatlab_rootFolder = animatsimdir + '/'
        folders.animatlab_commonFiles_dir = animatsimdir + '/FinalModel/'
        folders.animatlab_simFiles_dir = animatsimdir + '/SimFiles/'
        folders.animatlab_result_dir = animatsimdir + '/ResultFiles/'

        print folders.animatlab_rootFolder
        print folders.animatlab_commonFiles_dir
        print folders.animatlab_simFiles_dir
        print folders.animatlab_result_dir
        """
        sims = AnimatLabSimRunner.AnimatLabSimulationRunner("Test Sims",
            rootFolder = folders.animatlab_rootFolder,
            commonFiles = folders.animatlab_commonFiles_dir,
            sourceFiles = folders.python27_source_dir,
            simFiles = folders.animatlab_simFiles_dir,
            resultFiles = folders.animatlab_result_dir)
        model = AnimatLabModel.AnimatLabModel(folders.animatlab_commonFiles_dir)
        projMan = ProjectManager.ProjectManager('Test Project')
        projMan.set_aproj(model)
        # Assign the simulationSet object
        projMan.set_simRunner(sims)

        aprojFicName = os.path.split(model.aprojFile)[-1]
        optSet = OptimizeSimSettings(folders=folders, model=model,
                                     projMan=projMan, sims=sims)
        #
        # listparNameOpt = optSet.paramLoebName
        setPlaybackControlMode(model, mode=0)   # 0: fastest Possible;
        #                                       # 1: match physics
        # ====================================================================
        setMotorStimsON(model, optSet.motorStimuli)
        # ====================================================================
        # Looks for a parameter file in the chosen directory
        fileName = 'paramOpt.pkl'
        if loadParams(os.path.join(folders.animatlab_result_dir, fileName),
                      optSet):
            optSet.actualizeparamLoeb()
            optSet.actualizeparamMarquez()
            optSet.ideal_behav = [0, 0]
        else:
            print("paramOpt.pkl MISSING !!, run 'GUI_animatlabOptimization.py'")
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
        print("fourchetteStim:", optSet.fourchetteStim)
        print("fourchetteSyn", optSet.fourchetteSyn)
        print("cmaes_sigma", optSet.cmaes_sigma)
        print("seuilMSEsave", optSet.seuilMSEsave)
        """
    return [True, folders, model, projMan, aprojFicName, optSet]


if __name__ == '__main__':
    animatsimdir = readAnimatLabDir()
    # animatLabV2ProgDir = readAnimatLabV2ProgDir()
    animatLabV2ProgDir, nb_procs = getInfoComputer()
    res = initAnimatLab(animatsimdir, animatLabV2ProgDir)
    OK = res[0]
    if OK:
        folders = res[1]
        model = res[2]
        projMan = res[3]
        aprojFicName = res[4]
        optSet = res[5]
        simSet = SimulationSet.SimulationSet()

        simSet.set_by_range({'1ExtAlpha_St1.CurrentOn': [0e-09],
                             '1FlxAlpha_St1.CurrentOn': [0e-09]})
        print(simSet.samplePts)

        # Generate .asim files
        print("\n\nMAKING ASIM FILES")
        projMan.make_asims(simSet)

        # Run simulations
        print("\n\nRUNNING ANIMATLAB SIMULATIONS")
        projMan.run(cores=-1)
        chartResultName = findTxtFileName(model, optSet, "", 1)
        tab = readTablo(folders.animatlab_result_dir, chartResultName)
