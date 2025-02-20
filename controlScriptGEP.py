# -*- coding: utf-8 -*-
"""
ControlScriptGEP.py
Created on Thu May 24 12:50:30 2018
Used tu run GEP_GUI.py with a script file specifying the parameters to use in
animatLab simulations.
The scripts are of the form:
First line indicates the mode for running the script:
    scrip_mode are :  GEP, save_separate_data, append_data_nosave
        savePrevious_restartfrom0

        "GEP" mode: runs the script without saving at the end. The best behav
            in the list is the one with the smallest varmse
        "save_separate_data": For each angle_dur set, the results are saved in
            the indicated directory with increments trial numbers
        "append_data_nosave": runs the script withour saving. The best behav
            in the list is the one with the smallest err (for the template)
        "savePrevious_restartfrom0": Saves the specified working directory to
            specified saved folders, with incremental trials directories.
            Erases the working directory and restarts from scratch on the
            working directory.
//mac/Home/Documents/Labo/Scripts/AnimatLabV2/Human/test/ArmNS10forControlScript
//mac/Home/Documents/Labo/Scripts/AnimatLabV2/Human/saved/ArmNS10f
angle	0	40	mvtdur	0.400
const	NS1_IaExt-ExtAlMn.SynAmp=0.01	NS1_IaFlx-FlxAlMn.SynAmp=0.020
random	xCoactPenality1=500	nbByPacket=8	nbTotRandRuns=32
span=10

angle	0	40	mvtdur	0.400
const	NS1_IaExt-ExtAlMn.SynAmp=0.01	NS1_IaFlx-FlxAlMn.SynAmp=0.025
random	xCoactPenality1=500	nbByPacket=8	nbTotRandRuns=32
span=10
random	xCoactPenality1=500	nbByPacket=8	nbTotRandRuns=16
span=5
GEPrand	xCoactPenality1=500	neighbours=1	sigmaGEP=0.1	nbToBehavRuns=10
span=from_file
CMAES	xCoactPenality1=500	threshold=Var	cmaes_sigma=0.001	nbTotCMAesRuns=20
span=100
angle	0	60	mvtdur	0.400
const	NS1_IaExt-ExtAlMn.SynAmp=0.01	NS1_IaFlx-FlxAlMn.SynAmp=0.035
random	span=5	xCoactPenality1=500	nbByPacket=8	nbTotRandRuns=16

angle	0	80	mvtdur	0.400
const	NS1_IaExt-ExtAlMn.SynAmp=0.01	NS1_IaFlx-FlxAlMn.SynAmp=0.045
random	xCoactPenality1=500	nbByPacket=8	nbTotRandRuns=16
span=5-

The two folder lines specify:
    the path to the "working directory" containing .proj, .asim, .aform files,
    and "save directory" in which the whole working directory will be saved

Various script modes may be executed one after the other and saved in
diffferent directories. Each saved directory is specified by angle and const
parameters.
    For example "angle  0   40" will create a sub-directory angle_0-40
in the "ArmNS10f" directory
    "const par.var1=0.010     par2.var=0.020" will create a sub-sub-directory
    named const_0.010-0.020 in the sub-directory angle_0-40.

"random	span=10	xCoactPenality1=500	nbByPacket=8	nbTotRandRuns=32"  will
be used to run a "do_rand_param" with the specified parameters

Several random runs can be chained in the same run and the results will be
saved in the same directory.
"rand_behav" can also be chained with "rand_param" and "CMAES"

Each time a new set of angles is specified, the previous data are saved and
a new set of simulations is initiated according to the const, and series of
simulation types ("random", "GEPrand", or "CMAES")

If two simulations with the same angles and constant specifications are to be
run they will be saved at the same "saveirectory/angle_x-y/const_0.0a-0.0b"
directory but in two sub-directories: "trial-0x", and "trial-0x+1"

IMPORTANT in the script file separators are <tabulation> (and "=" in const)
@author: cattaert

Translated in Python 3.8 Jan 2023 (D. Cattaert)


===============================================================================
        modifications of the script after January 01, 2023
===============================================================================

modfied January 20, 2023 (D. Cattaert):
    gravity is now re from asm file (line 1473, in main):
        gravity = readGravityfromAsim(model)
modified February 3, 2023 (D. Cattaert):
    Command added in control script file: span=from_file
    This command allows to read the listspanval and the span_dic from a file
    placed in the GEPdata folder (DicSpanVal.txt). It is processed in the 
    set_span_par_name() procedure called from SetsRandParam():
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
Modified February 27, 2023 (D. Cattaert):
    transfertData() procedure modified to count only trial-O, trial-1 and not
    trial-0_seeds00 ...
Modified February 28, 2023 (D. Cattaert):
    transfertData() procedure imprived to check what directories trial-x are
    present, to increment (don't take into account trial-x_seedsOO)
Modified May 16, 2023 (D. Cattaert):
    In readCommand() procedure:
        if par == "GEPMetrixGraphs" ... bhv Graph are now build with a correct
        scale (for x and y).
        save_density_map_metrics() added in the list of graphs.
        MakeGraphs.py modified accordingly.
Modified February 10, 2025 (D.Cattaert):
    other_constraints dictionary is now red from optSet.other_constraints.
    other_constraints is used to define the cost function additional
    constraints such as "max_endangle"  and  "max_endMN_pot"
    A new procedure "set_other_constraints()" reads the line starting with
    "other_constraints" in the scriptFile and creates the other_constraints
    dictionary, and copy it into optSet.other_constraints
    Thereby, these other constraints are taken into account in the calcylation
    of the cost funcion.
    buildControlScript.py, optimization.py and animatlabOptimSetting.py have
    been modified accordingly.
Modified February 11, 2025 (D.Cattaert):
    New procedures added :
        check_collectInterval(dirname)
        check_collectInterval_in_all_subdirs(directory)
        These procedures check and correct collectinterval in aform and asim
        files in the base directory (and its subdirectories AprojFiles  &
                                     FinalModel)
        before executing the copy_to_workDir command, in the srcdir (base)
Modified February 20, 2025 (D. Cattaert):
    A nex parameter added in other constraints: "min_endangle"
    The procedure "set_other_constraints(tabscript, line)" has been modified so
    that other constraints are red from the striptfile and interpreted
    automatically:       
        otherconstraints_names = optSet.otherconstraints_names
        other_constraints = {}
        for idx, val in enumerate(tabscript[line][1:]):
            nomPar, valPar = extractParam(val)
            if nomPar in otherconstraints_names:
                other_constraints[nomPar] = float(valPar)
        print(other_constraints)
        optSet.other_constraints = other_constraints  
"""
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from pyqtgraph.Qt import QtWidgets

from GEP_GUI import MaFenetre, initAnimatLab

import os
import shutil
import numpy as np
import copy

from optimization import copyFile
from optimization import copyFileDir
from optimization import copyRenameFilewithExt
from optimization import copyDirectory
from optimization import getValuesFromText
from optimization import calculateMvtdurFromMax_Speed
from optimization import load_datastructure
from optimization import readGravity
from optimization import readGravityfromAsim
from optimization import readSpan
from optimization import readSpan_from_DicSpanVal
from optimization import getInfoComputer
from SaveInfoComputer import SetComputerInfo

from GUI_AnimatPar import saveParams
from GUI_AnimatPar import readColIntervalFromAform
from GUI_AnimatPar import changeCollIntervalAform
from GUI_AnimatPar import readColIntervalFromAsim
from GUI_AnimatPar import changeCollIntervalAsim

global verbose
verbose = 1

pg.setConfigOption('background', 'w')


def changeMvtTemplate(optSet, angle1, angle2, mvtdur):
    """
    In : optSet : Object
        angle1 : Start Angle of the sim
        angle2 : End Angle of the sim
        mvtdur : Duration of the sim
   This procedure updates the values contained in optSet and saves them in the
   pickle file situated in the ResultFiles directory
   """
    optSet.paramVSCDValue[5] = angle1
    optSet.paramVSCDValue[9] = angle2
    optSet.paramVSCDValue[7] = optSet.paramVSCDValue[6] + mvtdur
    filename = os.path.join(animatsimdir, "ResultFiles", "paramOpt.pkl")
    saveParams(filename, optSet)
    optSet.actualizeparamVSCD()     # actualizes the mvt template too
    win.mvtTemplate = np.array(optSet.mvtTemplate)
    print()
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    print(optSet.paramVSCDName[5], ":", optSet.paramVSCDValue[5], "\t", end=' ')
    print(optSet.paramVSCDName[9], ":", optSet.paramVSCDValue[9], "\t", end=' ')
    print(optSet.paramVSCDName[7], ":", optSet.paramVSCDValue[7], end=' ')
    print("  have been modified in pickle file, optSet and template")
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")


def ReadsScriptFile(scriptfilename):
    """
    In : scriptfilename : A string containing the name of the file we want to
        open
    Out : tabfinal : A list of String in which you have the
        (name_of_the_param=its_value") in each case. In the end, this variable
        contains all the param with their values described in the file.
        The table follow the structure tabfinal[line][param_of_the_line] since
        each line is a list of parameters.
        text : A string containing the whole text of the opened file
    This function Open a file specified with scriptfilename, reads each of its
    line and concatenates them in the variable text. Then it extracts the
    values from the current line thanks to the function getValuesFromText
    called on the current line and appends the result to a list called tabfinal
    """
    tabfinal = []
    text = ""
    if os.path.exists(scriptfilename):
        f = open(scriptfilename, 'r')
        while 1:
            # We could set txt before entering the loop
            # and change its value before the concatenation =>
            # While txt != '' => avoid the use of a break statement
            # + a few lines
            # print i
            tab1 = []
            tab2 = []
            txt = f.readline()
            # print txt
            if txt == '':
                break
            else:
                text += txt
                tab1 = getValuesFromText(txt)
                # print tab1
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


# This function appears to do three things at the same time, could be
# separated in two different functions
def SetsConstParam(tabscript, line):
    """
    In : tabscript : list containing the couples
        ("the_name_of_the_parameter=its_value") as exctracted in the function
        ReadScriptFile
        line : The number of the line we seek to read the parameters from.
    Out : nomdir :
    This function separate the parameters'name from their value then put it in
    a dictionnary so we could access parameters' values by
    win.dicConstParam[Param_name]
    Update the object to be saved as a pickle OptSet with the correspondig
    values between the UI, the script and the animatlab aproj file
    Update the name of the directory with the_name_of_the_parameter=its_value
    """
    nomdir = "const"
    cstxt = "const"
    listConstParnb = []
    listConstParVal = []
    win.listConstantNames = []
    constValFromParnb = {}
    win.dicConstParam = {}
    for idx, val in enumerate(tabscript[line][1:]):
        # For each elem of a line we take the name of the param
        nomPar, valPar = extractParam(val)
        # nomPar = val[:val.find("=")]
        # And its value
        # valPar = float(val[val.find("=")+1:])
        # That we put in a dictionnary
        win.dicConstParam[nomPar] = valPar
    for i in range(len(win.dicConstParam)):
        # For each elem in the dictionnary
        # constparnb=the value of the parameter in the window identified by
        # the key of the current param
        # xparName contains the the name of the parameters as presented in
        # animatlab
        constparnb = win.xparNameDict[list(win.dicConstParam.keys())[i]]
        # listConstParnb contains the keys of the dictionnary
        listConstParnb.append(constparnb)
        # paramConstVal=value of the param for the key
        paramConstVal = win.dicConstParam[list(win.dicConstParam.keys())[i]]
        # lsitConstParVal contains the values of the param
        listConstParVal.append(paramConstVal)
        win.listConstantNames.append(list(win.dicConstParam.keys())[i])
        print("\t", constparnb, list(win.dicConstParam.keys())[i], paramConstVal)
        # Save the association param_nam/val in the var optSet
        optSet.x0[constparnb] = float(paramConstVal)
    for idex, valu in enumerate(listConstParnb):
        constValFromParnb[valu] = listConstParVal[idex]
    if len(win.dicConstParam) > 0:
        for i in range(len(win.dicConstParam)):
            parnb = list(constValFromParnb.keys())[i]
            cstxt = cstxt + "_%d=%2.3f" % (parnb,
                                           float(constValFromParnb[parnb]))
            nomdir = nomdir + "_%d" % (parnb)
            win.listDicItConst = [{'constant': win.listConstantNames}]
            constName = win.xparName[parnb]
            win.listDicParVal[0][constName] = constValFromParnb[parnb]
            win.chkBox_const.setCheckState(True)
    else:
        nomdir = nomdir + "_none"

    return nomdir, cstxt


def SetsRandParam(tabscript, line):
    """
    In : tabscript : list containing the couples
        ("the_name_of_the_parameter=its_value") as exctracted in the function
        ReadScriptFile
        line : The number of the line we seek to read the parameters from.
    This procedure start a search with randomParameters on the criterion given
    in the script
    """
    # Those lines appears several time, we could create a function to avoid
    # code redundancy
    for idx, val in enumerate(tabscript[line][1:]):
        nomPar, valPar = extractParam(val)
        if nomPar == "randParEvol":
            print(nomPar, valPar)
            randParEvol = valPar
            # Chose which parameter to use as comparison for the best solution
            # either MSE, varmse, none
            if randParEvol == "MSE":
                win.chk_MSE.setChecked(True)
                win.chk_varmse.setChecked(False)
            elif randParEvol == "varmse":
                win.chk_varmse.setChecked(True)
                win.chk_MSE.setChecked(False)
            else:
                randParEvol = "no"
                win.chk_varmse.setChecked(False)
                win.chk_MSE.setChecked(False)
            win.randParEvol = randParEvol
            print("randParEvol:", randParEvol)
        # Set the weight of the penality of the coactivity in our reward
        # function
        if nomPar == "xCoactPenality1":
            xCoactPenality1 = int(valPar)
            win.valueCoactPen1.setText(str(xCoactPenality1))
            optSet.xCoactPenality1 = int(valPar)
            optSet.xCoactPenality2 = int(valPar)   # for old scripts
            print("xCoactPenality1:", xCoactPenality1)
        if nomPar == "xCoactPenality2":
            xCoactPenality2 = int(valPar)
            win.valueCoactPen2.setText(str(xCoactPenality2))
            optSet.xCoactPenality2 = int(valPar)
            print("xCoactPenality2:", xCoactPenality2)
        # Set the amount of thread to start on one run
        if nomPar == "nbByPacket":
            nbByPacket = int(valPar)
            win.valueLine1a.setText(str(nbByPacket))
            print("nbByPacket:", nbByPacket)
        # Set the amount of runs to do
        if nomPar == "nbTotRandRuns":
            nbTotRandRuns = int(valPar)
            win.valueLine1b.setText(str(nbTotRandRuns))
            print("nbTotRandRuns:", nbTotRandRuns)
    nomPar, valPar = extractParam(tabscript[line+1][0])
    set_span_par_name(valPar)
    win.do_rand_param()                 # exectutes Random runs


def set_span_par_name(valPar):
    """
    Procedure set_span_par_name
    In : span : the list of couples param_value and their variability
    This procedure give the list of varaibility to the GUI so any algorithm
    could use the variability we've set in the script
    """
    fouch_comp = copy.deepcopy(valPar)
    if valPar == "from_datastructure":
        completeGEPdatapar00name = win.animatsimdir + "/GEPdata/GEPdata00.par"
        datastructure = load_datastructure(completeGEPdatapar00name)
        rep = readSpan(datastructure)
        if type(rep) is tuple:
            spanStim, spanSyn = rep
            optSet.spanStim = spanStim
            optSet.spanSyn = spanSyn
            minFork = min(spanStim, spanSyn)
            maxFork = max(spanStim, spanSyn)
        else:
            win.listspanVal = rep
            minFork = min(win.listspanVal)
            maxFork = max(win.listspanVal)
        if minFork == maxFork:
            print("all span values equal to", win.listspanVal[0])
            win.chkBx_glob_span.setCheckState(True)
            print(win.chkBx_glob_span.checkState())
            win.glob_span = win.listspanVal[0]
            win.glob_span_val.setText(str(win.glob_span))
            win.span_setup()
        else:
            lstspan = rep
            lst_span_dic = [{}]
            for idx, nomPar in enumerate(win.xparName):
                lst_span_dic[0][nomPar] = float(lstspan[idx])
            win.refresh_span(lst_span_dic)
            win.listspanVal = [float(win.listDicSpanVal[0][nam])
                               for nam in win.xparName]
    elif valPar == "from_file":
        dicSpanVal_file = win.animatsimdir + "/GEPdata/DicSpanVal.txt"
        dicSpanVal, listspanval = readSpan_from_DicSpanVal(dicSpanVal_file)
        if listspanval != []:
            win.listspanVal = listspanval
            lst_span_dic = [dicSpanVal]
            win.refresh_span(lst_span_dic)
        else:
            sys.exit()
            
        
    else:
        lst_span_dic = [{}]
        if fouch_comp.find(',') == -1:
            win.glob_span = float(fouch_comp)
            print("span=", fouch_comp)
            win.glob_span_val.setText(str(fouch_comp))
            win.chkBx_glob_span.setCheckState(True)
            # win.listDicspanVal[0][win.xparName[0]] = float(span)
            win.span_setup()
            optSet.spanStim = float(fouch_comp)
            optSet.spanSyn = float(fouch_comp)
        else:
            i = 0
            while len(fouch_comp) > 0:
                idx = fouch_comp.find(',')
                if idx == -1:
                    idx = len(fouch_comp)
                nomPar, val = extractParam(fouch_comp[:idx])
                fouch_comp = fouch_comp[idx+2:]
                lst_span_dic[0][nomPar] = float(val)
                i += 1
            win.refresh_span(lst_span_dic)
            win.listspanVal = [float(win.listDicSpanVal[0][nam])
                               for nam in win.xparName]


def sets_randGEPParam(tabscript, line):
    """
    In : tabscript : list containing the couples
        ("the_name_of_the_parameter=its_value") as exctracted in the function
        ReadScriptFile
        line : The number of the line we seek to read the parameters from.
    This procedure start a search with GEP on the criterion given in the script
    """
    for idx, val in enumerate(tabscript[line][1:]):
        nomPar, valPar = extractParam(val)
        # Set the range of variablity allowed in the randomisation of our
        # parameters
        # Set the weight of the penality of the coactivity in our reward
        # function
        if nomPar == "xCoactPenality1":
            xCoactPenality1 = int(valPar)
            win.valueCoactPen1.setText(str(xCoactPenality1))
            optSet.xCoactPenality1 = int(valPar)
            optSet.xCoactPenality2 = int(valPar)   # for old scripts
            print("xCoactPenality1:", xCoactPenality1)
        if nomPar == "xCoactPenality2":
            xCoactPenality2 = int(valPar)
            win.valueCoactPen2.setText(str(xCoactPenality2))
            optSet.xCoactPenality2 = int(valPar)
            print("xCoactPenality2:", xCoactPenality2)

        # Set the amount of node we look at to determine our starting
        # parameters
        if nomPar == "neighbours":
            neighbours = int(valPar)
            win.valueLine2a.setText(str(neighbours))
            print("neighbours:", neighbours)
        # Define the amount of time we want to use the GEP to extend the
        # explored set
        if nomPar == "nbextend":
            win.nbGEPextend = int(valPar)
            win.value_nbExt.setText(str(win.nbGEPextend))
            print("nbextend:", win.nbGEPextend)
        # Define the amount of time we want to run the GEP to fill the gaps in
        # the explored set
        if nomPar == "nbfill":
            win.nbGEPfill = int(valPar)
            win.value_nbFill.setText(str(win.nbGEPfill))
            print("nbfill:", win.nbGEPfill)
        if nomPar == "sigmaGEP":
            sigmaGEP = float(valPar)
            # win.valueLine2b.setText(str(sigmaGEP))
            print("sigmaGEP:", sigmaGEP, "--> deprecated not used anymore")
        # Define if we want the GEP to find its own goals
        if nomPar == "auto":
            win.GEPauto = int(valPar)
            if win.GEPauto == 1:
                win.chkBx_autoGEP.setChecked(True)

        # =====================   In case auto = 0   =========================
        # Define the parameters of the goal to reach
        # The angle the algorithm will try to reach
        if nomPar == "ang":
            aimAngle = float(valPar)
            win.aimBhvValueX.setText(str(aimAngle))
            print("aimAngle:", aimAngle)
        # The duration of the movement to perform
        if nomPar == "dur":
            aimDuration = float(valPar)
            win.aimBhvValueY.setText(str(aimDuration))
            print("aimDuration:", aimDuration)
        # The amount of thread to start per run
        if nomPar == "nbByPacket":
            nbByPacket = int(valPar)
            win.valueLine1a.setText(str(nbByPacket))
            print("nbByPacket:", nbByPacket)
        # The amoun of run to do
        if nomPar == "nbTotRandRuns":
            nbTotRandRuns = int(valPar)
            win.valueLine1b.setText(str(nbTotRandRuns))
            print("nbTotRandRuns:", nbTotRandRuns)
        # ====================================================================
    # toExtract = tabscript[line+1]
    nomPar, valPar = extractParam(tabscript[line+1][0])
    if nomPar == "span" or nomPar == "fourch":
        set_span_par_name(valPar)
    GEPdata_name = "GEPdata00.par"
    win.mydir = os.path.join(optSet.folders.animatlab_rootFolder, "GEPdata")
    fname = os.path.join(win.mydir, GEPdata_name)
    win.read_pairs(fname)
    win.do_GEP_rand()                 # exectutes Behav runs


def SetsCMAEsParam(tabscript, line):
    """
    In : tabscript : list containing the couples
        ("the_name_of_the_parameter=its_value") as exctracted in the function
        ReadScriptFile
        line : The number of the line we seek to read the parameters from.
    This procedure start a search with CMAES on the criterion given in the
    script
    """
    for idx, val in enumerate(tabscript[line][1:]):
        nomPar, valPar = extractParam(val)
        # Set the weight of the penality of the coactivity in our reward
        # function
        if nomPar == "xCoactPenality1":
            xCoactPenality1 = int(valPar)
            win.valueCoactPen1.setText(str(xCoactPenality1))
            optSet.xCoactPenality1 = int(valPar)
            optSet.xCoactPenality2 = int(valPar)   # for old scripts
            print("xCoactPenality1:", xCoactPenality1)
        if nomPar == "xCoactPenality2":
            xCoactPenality2 = int(valPar)
            win.valueCoactPen2.setText(str(xCoactPenality2))
            optSet.xCoactPenality2 = int(valPar)
            print("xCoactPenality2:", xCoactPenality2)
        if nomPar == "threshold":
            threshold = valPar
            win.valueLine4b.setText(str(threshold))
            print("threshold:", threshold)
            try:
                optSet.seuilMSEsave = float(valPar)
                optSet.seuilMSETyp = "Fix"
            except Exception as e:
                if (verbose > 1):
                    print(e)
                optSet.seuilMSETyp = "Var"
                win.valueLine4b.setText(str("Var"))
                optSet.seuilMSEsave = 5000
        if nomPar == "cmaes_sigma":
            cmaes_sigma = float(valPar)
            win.valueLine5.setText(str(cmaes_sigma))
            optSet.cmaes_sigma = float(valPar)
            print("cmaes_sigma:", cmaes_sigma)
        if nomPar == "nbTotCMAesRuns":
            nbTotCMAesRuns = int(valPar)
            win.valueLine3.setText(str(nbTotCMAesRuns))
            print("nbTotCMAesRuns:", nbTotCMAesRuns)
    nomPar, valPar = extractParam(tabscript[line+1][0])
    if nomPar == "span" or nomPar == "fourch":
        set_span_par_name(valPar)
    win.runCMAeFromGUI()                # executes CMAES runs
    if os.path.exists(animatsimdir + "/ResultFiles/chart_plot.pkl"):
        src = animatsimdir + "/ResultFiles/chart_plot.pkl"
        tgt = optSet.srcdir + "/ResultFiles/chart_plot.pkl"
        shutil.copyfile(src, tgt)


def SetsVSCDParam(tabscript, line):
    """
    In : tabscript : list containing the couples
        ("the_name_of_the_parameter=its_value") as exctracted in the function
        ReadScriptFile
        line : The number of the line we seek to read the parameters from.
    This procedure perform a search with the VSCD process (descente de
    gradient avec prior sur l'accélération) on the criterion given in the
    script
    """
    for idx, val in enumerate(tabscript[line][1:]):
        nomPar, valPar = extractParam(val)
        if nomPar == "xCoactPenality1":
            xCoactPenality1 = int(valPar)
            win.valueCoactPen1.setText(str(xCoactPenality1))
            optSet.xCoactPenality1 = int(valPar)
            optSet.xCoactPenality2 = int(valPar)   # for old scripts
            print("xCoactPenality1:", xCoactPenality1)
        if nomPar == "xCoactPenality2":
            xCoactPenality2 = int(valPar)
            win.valueCoactPen2.setText(str(xCoactPenality2))
            optSet.xCoactPenality2 = int(valPar)
            print("xCoactPenality2:", xCoactPenality2)
        if nomPar == "deltacoeff":
            optSet.deltacoeff = float(valPar)
            win.deltacoeffValue.setText(str(optSet.deltacoeff))
            print("deltacoeff:", optSet.deltacoeff)
        if nomPar == "nbsteps":
            optSet.nbsteps = int(valPar)
            win.nbstepsValue.setText(str(optSet.nbsteps))
            print("nbsteps:", optSet.nbsteps)
        if nomPar == "nbepoch":
            optSet.nbepoch = int(valPar)
            win.nbepochValueLine.setText(str(optSet.nbepoch))
            print("nbepoch:", optSet.nbepoch)
    nomPar, valPar = extractParam(tabscript[line+1][0])
    if nomPar == "span" or nomPar == "fourch":
        set_span_par_name(valPar)
    win.runVSCDFromGUI()                # executes VSCD runs
    if os.path.exists(animatsimdir + "/ResultFiles/chart_plot.pkl"):
        src = animatsimdir + "/ResultFiles/chart_plot.pkl"
        tgt = optSet.srcdir + "/ResultFiles/chart_plot.pkl"
        shutil.copyfile(src, tgt)


def set_other_constraints(tabscript, line):
    """
    In : tabscript : list containing the couples
        ("the_name_of_the_parameter=its_value") as exctracted in the function
        ReadScriptFile
        par : String containing the type of algorithm to run
        line : the number of the line on which we are
    This procedure will set the other constraints of the cost function by
        reading the dictionnary and affect it to optSet.other_constraints
        optSet.other_constraints is then red when the process starts
    """
    otherconstraints_names = optSet.otherconstraints_names
    other_constraints = {}
    for idx, val in enumerate(tabscript[line][1:]):
        nomPar, valPar = extractParam(val)
        if nomPar in otherconstraints_names:
            other_constraints[nomPar] = float(valPar)
    print(other_constraints)
    optSet.other_constraints = other_constraints    
    

def savemapbehav():
    start = 0
    end = len(optSet.behavs)
    listdf_bhv, listdf_par = win.get_df_remain(optSet.behavs, optSet.pairs,
                                               start, end)
    df_bhvremain = copy.deepcopy(listdf_bhv[0])
    dest = animatsimdir
    name = "GEPdata00"
    win.save_map_behav(df_bhvremain, dest, name)


def readCommand(tabscript, par, line, angles, const):
    """
    In : tabscript : list containing the couples
        ("the_name_of_the_parameter=its_value") as exctracted in the function
        ReadScriptFile
        par : String containing the type of algorithm to run
        line : the number of the line on which we are
    This procedure start another procedure depending on the parameters of
    the line
    """
    if par == "bhvCriteria":
        print("Behavior citeria: ")
        set_bhv_criteria(tabscript, line)
    if par == "random":
        SetsRandParam(tabscript, line)
    if par == "GEPrand":
        sets_randGEPParam(tabscript, line)
    if par == "CMAES" or par == "cmaes":
        SetsCMAEsParam(tabscript, line)
    if par == "loeb" or par == "Loeb" or par == "VSCD":
        SetsVSCDParam(tabscript, line)
    if par == "other_constraints":
        set_other_constraints(tabscript, line)
    if par == "loadGEPdata":
        loadPreviousExploredData(animatsimdir)
    if par == "CreateDir":
        dirName = prepareCreateDir(tabscript, line)
        createDir(dirName)
        initWorkingDirectory(dirName)
    if par == "copyData":
        print("copydata from", tabscript[line][1])
        simdir, pathDest = prepareCopyData(tabscript, line)
        copyDirectory(simdir, pathDest)
        checkCreateDir(optSet.folders)
    if par == "copy_to_workDir":
        print("copy_to_workDir", tabscript[line][1])
        srcdir, pathDest = prepareCopyData(tabscript, line)
        pathDest = animatsimdir
        copyDirectory(srcdir, pathDest)
        checkCreateDir(optSet.folders)
# TODO Modify the CopyData so it takes only two inputs or put an option
    if par == "transfertData":
        savemapbehav()  # before transfert => saves map of behaviors
        # ************************************************************
        pathSrc, pathDest = prepareTransfertData(tabscript, line)
        transfertData(pathSrc, pathDest, 0, angle=angles, const=const)
        # ************************************************************
        #       after trasfert of the trial reinitialization is needed
        win.reset()     # dataStructure, optSet.pairs, optSet.behavs, x0...
    if par == "transfert_from_workDir":
        savemapbehav()  # before transfert => saves map of behaviors
        # ************************************************************
        src, dest = prepareTransfertData(tabscript, line)
        src = animatsimdir
        transfertData(src, dest, 0, angle=angles, const=const)
        # ************************************************************
        #       after trasfert of the trial reinitialization is needed
        win.reset()     # dataStructure, optSet.pairs, optSet.behavs, x0...
# TODO Modify TranfertData so it takes only two parameters or put an option

    if par == "GEPMetrixGraphs":
        from makeGraphs import GUI_Graph
        from makeGraphs import GEPGraphsMetrics
        MyWin = GUI_Graph()
        MyWin.optSet = optSet
        MyWin.behav_col = win.behav_col
        win.hide()
        win.mvtPlot.hide()
        win.bhvPlot.hide()
        if win.df_bhvremain is not None:
            # pathGEP = MyWin.listGEPFolders[0]
            # root_path = os.path.split(pathGEP)[0]
            root_path = win.animatsimdir
            graph_path = os.path.join(root_path, "graphs")
            graph_path = root_path + "/graphs"
            MyWin.graph_path = graph_path
            # df_bhvremain = win.update_df_bhvremain(mseThr=1.0)
            win.df_bhvremain.loc[:, "orig_rg"] = win.df_bhvremain["rgserie"]
            win.df_bhvremain.loc[:, "rgserie"] = win.df_bhvremain.index
            win.df_parremain.loc[:, "orig_rg"] = win.df_parremain["rgserie"]
            win.df_parremain.loc[:, "rgserie"] = win.df_parremain.index
            MyWin.df_bhvremain = win.df_bhvremain
            MyWin.df_parremain = win.df_parremain
            MyWin.listGEPFolders = [animatsimdir+"/GEPdata"]
            MyWin.scale_x, MyWin.scale_y = win.scale_x, win.scale_y
            MyWin.prevListGEPFiles = ["GEPdata00.par"]

            MyWin.makeGEPMetrics = GEPGraphsMetrics(MyWin)
            MyWin.makeGEPMetrics.GUI_Gr_obj = MyWin
            MyWin.makeGEPMetrics.behav_col = win.behav_col
            # MyWin.behav_col = win.behav_col
            MyWin.makeGEPMetrics.GUI_Gr_obj.mafen = win
            print("Saving bhv graph")
            MyWin.makeGEPMetrics.saveplot_bhv()

            MyWin.makeGEPMetrics.autoscale = True
            print("Saving par graphs")
            win.activateAllParGraphs(plot=0)
            MyWin.makeGEPMetrics.saveplot_bhvparam()

            print("Saving density map contour")
            MyWin.makeGEPMetrics.plot_save_2D_densitymap_contour()
            
            print("Saving density map_metrics")
            MyWin.makeGEPMetrics.plot_save_density_map_metrics()

            # MyWin.plot_2D_stability_map(win.df_bhvremain, win.df_parremain)

            print("Saving rGEP time course")
            MyWin.makeGEPMetrics.grid_method()
        MyWin.closeIt()


def readsConst_Exec(tabscript, startLine, endLine, angles):
    """
    In : startLine : the number of the line on which we start the settings
        of the search algorithms
        endline : the number of the last line containing the settings of the
        search algorithms
    Out : const : contains the valuer returned by the function
        SetsConstParam
    This function reads each line of the block of instructions of the script
    file, and starts the selected search algorithm with the function
    readCommand
    """
    line = startLine
    const = ""
    while line <= endLine:
        print(line, end=' ')
        par = tabscript[line][0]
        print(par)
        cval = []
        if par == "const":
            for val in tabscript[line][1:]:
                # nomPar = val[:val.find("=")]
                cval.append(float(val[val.find("=")+1:]))
            const, cstxt = SetsConstParam(tabscript, line)
        print("----------------------------------------------------------")
        print(const)
        print("----------------------------------------------------------")
        readCommand(tabscript, par, line, angles, const)
        line += 1
    return const


# We could probably separate several features of this procedure in different
# functions
def runSeriesMvts(tabscript, listNewMvtline):
    """
    For each angle_duration movement (tabscript[listNewMvtline[i]]), runs a
    series of animatlab simulations according to parameters set in tabscript.
    In : tabscript : list containing the couples
        ("the_name_of_the_parameter=its_value") as exctracted in the function
        ReadScriptFile
        listNewMvtline : list containing all the movements produced by the
        search algorithm we've chosen; plot the behavior of the movement on the
        GEP_GUI
    This procedure load the data contained in GEPdata00.par
    """
    for idx, startnewMvt in enumerate(listNewMvtline):
        optSet.list_save_flags = [0, 0, 0, 0]
        if len(tabscript[startnewMvt]) == 5:
            angle1 = float(tabscript[startnewMvt][1])
            angle2 = float(tabscript[startnewMvt][2])
            print()
            print("angle1", angle1, "angle2", angle2)
            if tabscript[startnewMvt][3] == "mvtdur":
                mvtdur = float(tabscript[startnewMvt][4])
                angles = 'ang%d-%d_dur%d' % (angle1, angle2, int(mvtdur*1000))
            elif tabscript[startnewMvt][3] == "max_speed":
                max_speed = float(tabscript[startnewMvt][4])
                amplitude = angle2 - angle1
                mvtdur = calculateMvtdurFromMax_Speed(optSet, max_speed,
                                                      amplitude)
                angles = 'ang%d-%d_dur%d' % (angle1, angle2, int(mvtdur*1000))
            changeMvtTemplate(optSet, angle1, angle2, mvtdur)
            win.mvtPlot.pw_mvt.clearPlots()
            win.mvtPlot.pw_mvt.plot(win.mvtTemplate[:, 1],
                                    win.mvtTemplate[:, 2],
                                    pen='k')
            # line = startnewMvt+1
            startLine = startnewMvt+1
            if idx < len(listNewMvtline)-1:  # we are not in the last angle Set
                endLine = listNewMvtline[idx+1]
            else:       # This is the last angle set
                endLine = len(tabscript)-1

            newName = saveScriptFile(scriptfilename, animatsimdir,
                                     startLine, endLine)
            print("scriptFile saved to :", newName)
            # sets and executes run
            # ###################################
            readsConst_Exec(tabscript, startLine, endLine, angles)
            # ###################################

            list_err = win.err
            print(list_err)

            """
            sourcedir = animatsimdir
            destdir = os.path.join(savedatadir, angles, const)
            print sourcedir, "->", destdir
            """
            print()
            print("Number associated with each param:")
            for npar, name in enumerate(win.xparName):
                print(npar, "\t", name)
        else:
            print("error /script file: should be 'angle <tab> 0 <tab> 80", end=' ')
            print("<tab> mvtdur <tab> 0.400'")
            break


def loadPreviousExploredData(animatsimdir):
    dirGEPdata = os.path.join(animatsimdir, "GEPdata")
    fname = os.path.join(dirGEPdata, "GEPdata00.par")
    win.read_pairs(fname, plot=0)
    win.start = optSet.datastructure[len(optSet.datastructure)-1][2] + 1


def extractParam(val):
    """
    In : val : the combined ("the_name_of_the_parameter=its_value")
    Out : nomPar : the extracted name of the parameter
        valPar : the extracted value of the parameter
    This function separate the name of the parameter from its value
    """
    nomPar = val[:val.find("=")]
    valPar = val[val.find("=")+1:]
    return nomPar, valPar


def set_bhv_criteria(tabscript, line):
    for idx, val in enumerate(tabscript[line][1:]):
        nomPar, valPar = extractParam(val)
        print(nomPar, valPar)
        if nomPar == "bhv_ordinate":
            bhv_ord = valPar
            if bhv_ord == "duration":
                win.mvt_ord_duration = 1
                win.mvt_ord_maxSpeed = 0
            else:
                win.mvt_ord_duration = 0
                win.mvt_ord_maxSpeed = 1
            win.configureforbhvcriteria()


def prepareCreateDir(tabscript, line):
    """
    In : tabscript : list containing the couples
        ("the_name_of_the_parameter=its_value") as exctracted in the function
        ReadScriptFile
        line : the number of the line on which we are
    Out : the full name of the directory
    This function concatenate the path to the name of the directory we want to
    create so we can give this param to the function createDir
    """
    for idx, val in enumerate(tabscript[line][1:]):
        nomPar, valPar = extractParam(val)
        print(nomPar, valPar)
        if nomPar == "Path":
            path = valPar
        elif nomPar == "DirName":
            dirName = valPar
        else:
            raise ValueError("Wrong parameter entered in the line CreateDir")
# TODO allow the user to only specify the name of the folder so he could create
# it in the directory of the seeds
    return (path+dirName)


def createDir(dirName):
    """
    In : dirName : the name of the directory to create
    This procedure create a new directory

    """
    if os.path.exists(dirName):
        for fileName in os.listdir(dirName):
            file_path = os.path.join(dirName, fileName)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('failed to delete %s. Reason: %s' % (file_path, e))
    else:
        try:
            os.makedirs(dirName)
        except Exception as e:
            print(e)
            txt = "Check the path you've provided, "
            txt += "especially the orientation of the slashes"
            raise ValueError(txt)


def prepareCopyData(tabscript, line):
    """
    In : tabscript : list containing the couples
        ("the_name_of_the_parameter=its_value") as exctracted in the function
        ReadScriptFile
        line : the number of the line on which we are
    Out : pathSrc : the path of the source folder
        pathDest : the path to the folder where we want to copy the source
    This function extract the parameters of the CopyData commande
    from tabscript and return them
    """
    pathSrc, pathDest = None, None
    for idx, val in enumerate(tabscript[line][1:]):
        # print idx, val
        nomPar, valPar = extractParam(val)
        if nomPar == "PathSrc":
            pathSrc = valPar
        elif nomPar == "PathDest":
            pathDest = valPar
        else:
            raise ValueError("Wrong parameter in the line copyData")
    return pathSrc, pathDest


def prepareTransfertData(tabscript, line):
    """
    In : tabscript : list containing the couples
        ("the_name_of_the_parameter=its_value") as exctracted in the function
        ReadScriptFile
        line : the number of the line on which we are
    Out : pathSrc : the path of the source folder
    This function extract the parameters of the transfertData commande
    from tabscript and return them
    """
    pathSrc, pathDest = None, None
    for idx, val in enumerate(tabscript[line][1:]):
        nomPar, valPar = extractParam(val)
        if nomPar == "PathSrc":
            pathSrc = valPar
        elif nomPar == "PathDest":
            pathDest = valPar
        else:
            raise ValueError("Wrong parameter in the line transferData")
    return pathSrc, pathDest


def transfertData(animatsimdir, savedatadir, idx, angle='0', const='0',
                  iteration=0):
    """
    In : animatsimdir : the path to the directory of animatlab
        savedatadir : the path to the directory in which we'd like to save the
        results of the algorithms performed with the current script
        angles : The value of the angle we asked the algorithm to perform
        const : the value of the weight of the synapses if we specified any
    This procedure move the file from the animatsimdir to the folder in
    which we'd like to save the results
    """
    sourcedir = animatsimdir
    if idx != 0:
        destdir = os.path.join(savedatadir)
    else:
        destdir = os.path.join(savedatadir, angle, const)
        if not os.path.exists(destdir):
            os.makedirs(destdir)
        listsubdir = os.listdir(destdir)
        ix = 0
        for index, sdir in enumerate(listsubdir):
            if os.path.isdir(os.path.join(destdir, sdir)):
                ix += 1
        print(ix, "sub-directories")
        print("Existing trial-XX directories")
        list_trialdir = []
        for fold in listsubdir:
            if int(fold.find("_seed")) == -1:
                print(fold)
                list_trialdir.append(fold)
        ix = len(list_trialdir)
        newname = "trial" + '-{0:d}'.format(ix)
        print("New directory :", newname)
        destdir = os.path.join(destdir, newname)
        # To avoid overwrite a preceeding trial folder
        while os.path.exists(destdir):
                ix += 1
                newname = "trial" + '-{0:d}'.format(ix)
                destdir = os.path.join(destdir, newname)

        # print(sourcedir, "->", destdir)
        if not os.path.exists(destdir) and idx == 0:
            os.makedirs(destdir)
    for subdir in os.listdir(sourcedir):
        src = os.path.join(sourcedir, subdir)
        tgt = os.path.join(destdir, subdir)
        # print "tgt: ", tgt
        if len(tgt) > 255:
            tgt = tgt[:255]
        if os.path.isdir(src):
            if not os.path.exists(tgt):
                os.makedirs(tgt)
            transfertData(src, tgt, idx+1)
            shutil.rmtree(src)
        else:
            os.rename(src, tgt)


def saveScriptFile(scriptfilename, animatsimdir, start, end):
    """
    In : scriptfilenamle : the name of the file
        animatsimdir : the directory in which we'll save the file
        start : the number of the starting line of the script
        end : the number of the end line of the script
    Out : newName : the new name of the copied file
    This function copy the currently executed file in a new folder
    """
    sourcefile = os.path.split(scriptfilename)[-1]
    sourcedir = os.path.split(scriptfilename)[0]
    destfile = sourcefile
    GEPdatadir = os.path.join(animatsimdir, "GEPdata")
    destdir = os.path.join(GEPdatadir, "GEPdata_scriptFiles")
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    comment = ""
    newName = copyRenameFilewithExt(sourcedir, sourcefile,
                                    destdir, destfile,
                                    ".txt", comment, replace=0)
    ficScript = os.path.join(destdir, "dataScript.par")
    if not os.path.exists(ficScript):
        print("dataScript.par do not exist", end=' ')
        with open(ficScript, 'w') as fich:
            fich.write("start: {}\t end: {}\t script: {}\n".format(start, end,
                                                                   newName))
            fich.close()
        print("-> created")
    else:
        with open(ficScript, 'a') as fich:
            fich.write("start: {}\t end: {}\t script: {}\n".format(start, end,
                                                                   newName))
            fich.close()
    return newName


def prepareSetWorkingDir(tabscript, line):
    """
    In : tabscript : list containing the couples
        ("the_name_of_the_parameter=its_value") as exctracted in the function
        ReadScriptFile
        line : the number of the line on which we are
    Out : the full name of the directory
    This function return the path we'd like to set as our working directory
    """
    global animatsimdir

    for idx, val in enumerate(tabscript[line][1:]):
        nomPar, valPar = extractParam(val)
        print(nomPar, valPar)
        if nomPar == "Path":
            path = valPar
        elif nomPar == "DirName":
            dirName = valPar
        else:
            raise ValueError("Wrong parameter entered in the line workingDir")
    if path == "":
        if animatsimdir is None:
            animatsimdir = readAnimatLabDir()
        rootDir = os.path.split(animatsimdir)[0]
        animatsimdir = chooseDirectory(rootDir)
    else:
        animatsimdir = path+dirName
    return (animatsimdir)


def initWorkingDirectory(animatsimdir):
    """
    In : animatsimdir : Path to the directory containing the animatLab files
    This procedure set the working directory
    """
    folders = optSet.folders
    resultDir = folders.animatlab_result_dir
    tempDir = os.path.join(folders.animatlab_rootFolder, 'temp')
    os.makedirs(tempDir)
    copyFile("paramOpt.pkl", resultDir, tempDir)
    for subdir in os.listdir(animatsimdir):
        dirpath = os.path.join(animatsimdir, subdir)
        if os.path.isdir(dirpath):
            if os.path.split(dirpath)[1] != "temp":
                print(dirpath)
                shutil.rmtree(dirpath, ignore_errors=True)
    checkCreateDir(folders)
    copyFile("paramOpt.pkl", tempDir, resultDir)
    shutil.rmtree(tempDir, ignore_errors=True)
    print("animatlab working directory initialised")
    for i in range(20):
        print("*", end=' ')
    # os.rename(tempDir, resultDir)


def checkCreateDir(folders):
    """
    In : folders : Path to the folder we'f like to save our data
    This procedure verify if the given path leads to a folder if not, it
    creates the folders "AprojFiles"; "CMAeSeuilAprojFiles"; "SimFiles"
    """
    folders.affectDirectories()
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
    SimFiles = os.path.join(folders.animatlab_rootFolder,
                            "SimFiles")
    if not os.path.exists(SimFiles):
        os.makedirs(SimFiles)
        copyFileDir(animatsimdir,
                    SimFiles,
                    copy_dir=0)


def realFromNorm(xparName, norm):
    """
    In : xparName : the name of the reference parameter
        norm : the normalized value
    Out : rval : the unnormalized value
    This function return the real value of a previously normalized number
    """
    rgpar = optSet.xparNameDict[xparName]
    rxmin = optSet.realxMin[rgpar]
    rxmax = optSet.realxMax[rgpar]
    rval = norm*(rxmax-rxmin) + rxmin
    None
    return rval


def normFromReal(xparName, rval):
    """
    In : xparName : the name of the reference parameter
        rval : the value to normalize
    Out : norm : the normalized value
    This function normalize a value based on the max and the min value of the
    parameter
    """
    rgpar = optSet.xparNameDict[xparName]
    rxmin = optSet.realxMin[rgpar]
    rxmax = optSet.realxMax[rgpar]
    norm = (rval-rxmin)/(rxmax-rxmin)
    None
    return norm


class ChooseDir(QtWidgets.QWidget):
    """
    """
    def __init__(self, mydir, parent=None):
        # super(ShowContent, self).__init__(parent)
        super(ChooseDir, self).__init__()
        # This is enough to create the window
        # tabscript, text = ReadsScriptFile(fname)
        self.mydir = mydir
        self.text = ""
        self.OK = 0
        self.title = 'Select a sim directory'
        self.left = 100
        self.top = 100
        self.width = 200
        self.height = 100
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setMinimumSize(QtCore.QSize(100, 200))

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        # self.textwin = QtWidgets.QPlainTextEdit(self)
        # self.textwin.insertPlainText(self.text)
        # self.textwin.move(10, 10)
        # self.textwin.resize(400, 200)

        # Create a button in the window
        self.OKBtn = QtWidgets.QPushButton("&Accept", self)
        self.OKBtn.clicked.connect(self.accept)

        self.ChangeDirBtn = QtWidgets.QPushButton("&Change File", self)
        self.ChangeDirBtn.clicked.connect(self.getdirpath)

        # self.gridLayout.addWidget(self.textwin, 1, 1, 5, 1)
        self.gridLayout.addWidget(self.OKBtn, 6, 1)
        self.gridLayout.addWidget(self.ChangeDirBtn, 6, 2)

        self.setCentralWidget(self.centralwidget)
        self.setLayout(self.gridLayout)
        self.getdirpath()

    def getdirpath(self):
        self.model_dir = QtWidgets.QFileDialog.\
            getExistingDirectory(self, "sim root folder to build graphs",
                                 self.mydir)

    def accept(self):
        """
        This method verify if the user has validated the chosen dir
        """
        self.OK = 1
        print("file accepted")
        self.close()


def chooseDirectory(myDir):
    """
    """
    app = QtWidgets.QApplication(sys.argv)
    # winLoad = WinLoadFile()
    Getdirectory = ChooseDir(myDir)
    Getdirectory.show()
    app.exec_()
    dirname = Getdirectory.model_dir
    return dirname


class ShowContent(QtWidgets.QWidget):
    """
    extends QtWidgets.QMainWindow
    Create a window which show the content of the selected script
    Constructor : self
                mydir : directory to the script
                the name of the script
                Set the size and the title of the window to show
    """
    def __init__(self, mydir, parent=None, fname=""):
        # super(ShowContent, self).__init__(parent)
        super(ShowContent, self).__init__()
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

        #self.setCentralWidget(self.centralwidget)
        self.setLayout(self.gridLayout)

    def getTxtFile(self):
        """
        This method open a popup window for you to chose the script file to use
        """
        # self.mydir = os.getcwd()
        # print self.mydir
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
        tabscript, text = ReadsScriptFile(self.fname)
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


class WinLoadFile(QtWidgets.QWidget):
    """
    extends QtWidgets.QMainWindow
    Constructor : self
    """
    def __init__(self):
        super(WinLoadFile, self).__init__()
        # self.setupUi(self)      # le 2eme self est pour l'argument PlotWindow
        #                       qui est la fenetre elle-meme -> donc self
        self.fname = ""
        self.OK = 1
        self.left = 10
        self.top = 40
        self.width = 200
        self.height = 100
        # self.resize(300, 150)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        # Create a series of button widgets to be placed inside
        self.choose_file_Button = QtWidgets.QPushButton("&ChooseFile")
        self.quit_Button = QtWidgets.QPushButton("&Quit")

        # Add QHBoxlayout to place the buttons
        buttonLayout1 = QtWidgets.QVBoxLayout()

        # Add widgets to the layout in their proper positions
        buttonLayout1.addWidget(self.choose_file_Button)
        buttonLayout1.addWidget(self.quit_Button)
        self.setCentralWidget(self.centralwidget)
        self.setLayout(self.gridLayout)
        self.setWindowTitle("Choose a file to process")
        self.gridLayout.addLayout(buttonLayout1, 0, 1)

        self.choose_file_Button.clicked.connect(self.getTxtFile)
        self.quit_Button.clicked.connect(self.closeIt)

    def getTxtFile(self):
        """
        This mehtod opens a windows to chose a script file
        """
        self.mydir = os.getcwd()
        print(self.mydir)
        res = (pg.QtWidgets.QFileDialog.
               getOpenFileName(self,
                               "Choose a script File to run GEP_GUI",
                               self.mydir,
                               "Script Text Files (*.txt)"))
        if type(res) == tuple:
            ficname, __tmp = res
        else:
            ficname = res
        print(ficname)
        self.fname = os.path.split(ficname)[-1]

        self.content = ShowContent(self, ficname)
        # self.OK = self.content.choice()
        self.OK = self.content.OK
        if self.OK == 1:
            print("file accepted")
        else:
            print("ERROR get another file")

    def closeIt(self):
        """
        This method close the window which let you chose a script file
        """
        # print "Fermeture de la fenetre"
        self.close()


def loadTextFile(script_dir):
    """
    In : script_dir : the directory in which we find the script to execute
    Out : fname : the name of the script we want to execute
    This function show the window allowing the user to select a script
    """
    app = QtWidgets.QApplication(sys.argv)
    # winLoad = WinLoadFile()
    winLoad = ShowContent(script_dir)
    winLoad.show()
    app.exec_()
    fname = winLoad.fname
    return fname, winLoad


def check_collectInterval(dirname):
    chartNames = []
    for ficname in os.listdir(dirname):
        if ficname.endswith("aform"):
            # print(ficname)
            chartNames.append(ficname)
    if len(chartNames) > 0:
        for aformFile in chartNames:
            chartPathName = dirname + "/" + aformFile
            collIntervalAform = readColIntervalFromAform(chartPathName)
            if collIntervalAform != '0.01':
                changeCollIntervalAform(chartPathName)

    asimNames = []
    for simname in os.listdir(dirname):
        if simname.endswith("asim"):
            print(simname)
            asimNames.append(simname)
    if len(asimNames) > 0:
        for asimFile in asimNames:
            asimPathName = dirname + "/" + asimFile
            collIntervalAsim = readColIntervalFromAsim(asimPathName)
            if collIntervalAsim != '0.01':
                changeCollIntervalAsim(asimPathName)

def check_collectInterval_in_all_subdirs(directory):
    check_collectInterval(directory)
    dirname = directory + "/AprojFiles"
    check_collectInterval(dirname)
    dirname = directory + "/FinalModel"
    check_collectInterval(dirname)


def readscriptfile(scriptfilename):
    # =======   Reads the start and end angles (angle1 & angle2   ===========
    gravity = 1000
    listNewMvtline = []
    if scriptfilename != "":
        tabscript, text = ReadsScriptFile(scriptfilename)
        for line in range(1, len(tabscript)):
            if tabscript[line][0] == "angle":
                listNewMvtline.append(line)
        for idx, line_tabscript in enumerate(tabscript):
            print(line_tabscript)
        # ====== reads the first lines before first NewMvtLine =======
        pre_lines = []
        if listNewMvtline != []:
            pre_lines = list(range(listNewMvtline[0]))
        else:
            pre_lines = list(range(len(tabscript)))
        for line in pre_lines:
            tmptext = tabscript[line][0]
            print(line, tmptext)
            # TODO Needs to put this part inside the function readPar
            if tmptext == "create_workDir":
                dirName = prepareCreateDir(tabscript, line)
                createDir(dirName)
                animatsimdir = dirName
            if tmptext == "copyData":
                print("copydata from", tabscript[line][1])
                simdir, pathDest = prepareCopyData(tabscript, line)
                copyDirectory(simdir, pathDest)
            if tmptext == "copy_to_workDir":
                print("copy_to_workDir", tabscript[line][1])
                srcdir, pathDest = prepareCopyData(tabscript, line)
                check_collectInterval_in_all_subdirs(srcdir)
                pathDest = dirName
                copyDirectory(srcdir, pathDest)
            if tmptext == "workingDir":
                animatsimdir = prepareSetWorkingDir(tabscript, line)
                # sourcedir = pathSrc
                # destdir = pathDest
            if tmptext == "transfertData":
                src, dest = prepareTransfertData(tabscript, line)
                transfertData(src, dest, 0)
            if tmptext == "transfert_from_workDir":
                src, dest = prepareTransfertData(tabscript, line)
                src = dirName
                transfertData(src, dest, 0)
            if tmptext == "gravity":
                for idx, val in enumerate(tabscript[line][1:]):
                    nomPar, valPar = extractParam(val)
                    gravity = float(valPar)
    return (listNewMvtline, tabscript, pre_lines,
            animatsimdir, srcdir, gravity)


# =============================================================================
#                                   MAIN
# =============================================================================
if __name__ == '__main__':
    import sys
    global folders, model, projMan, aprojFicName, optSet, animatsimdir
    from mainOpt import readAnimatLabDir
    animatsimdir = None
    # scriptfilename = "script00.txt"
    cwd = os.getcwd()
    script_dir = os.path.join(cwd, "scriptFiles")
    scriptfilename, winLoad = loadTextFile(script_dir)
    print(scriptfilename)
    if scriptfilename != "":
        rep = readscriptfile(scriptfilename)
        (listNewMvtline, tabscript, pre_lines,
         animatsimdir, srcdir, gravity) = rep
        # ================  Initialises with infoComputer  ==================
        animatLabV2ProgDir, nb_procs = getInfoComputer()
        if animatLabV2ProgDir == '':
            print("first instance to access to animatLab V2/bin")
            appl = QtWidgets.QApplication(sys.argv)
            dialogue = "Choose the 'animatLab V2' folder (includes/bin)"
            ComputInfoWin = SetComputerInfo(dialogue)
            ComputInfoWin.show()   # Show the form
            appl.exec_()     # and execute the appl
            print("animatLab V2/bin path and nb_processors have been saved", end=' ')
            print("in infos_computer.txt")
            animatLabV2ProgDir, nb_procs = getInfoComputer()
        # ===================================================================
        line = 0

        res = initAnimatLab(animatsimdir, animatLabV2ProgDir)
        
        OK = res[0]
        if OK:
            # folders = res[1]
            model = res[2]
            # projMan = res[3]
            aprojFicName = res[4]
            optSet = res[5]
            try:
                optSet.srcdir = srcdir
            except Exception as e:
                print(e)
            pg.mkQApp()
            ag = QtWidgets.QDesktopWidget().availableGeometry()
            sg = QtWidgets.QDesktopWidget().screenGeometry()

            win = MaFenetre(aprojFicName, optSet)
            win_height = win.geometry().height()
            win_width = win.geometry().width()
            win.location_on_the_screen(xshift=10,
                                       yshift=sg.height()-win_height)
            win.nb_procs = nb_procs
            optSet.nb_processors = nb_procs
            win.animatsimdir = animatsimdir
            mvtpl_height = win.mvtPlot.geometry().height()
            mvtpl_width = win.mvtPlot.geometry().width()
            win.mvtPlot.location_on_the_screen(xshift=win_width+15,
                                               yshift=sg.height()-mvtpl_height)

            # win.bhvPlot.resize(mvtplot_width, win_height-mvtplot_height-40)
            mvtpl_height = win.mvtPlot.geometry().height()
            mvtpl_width = win.mvtPlot.geometry().width()
            win.bhvPlot.location_on_the_screen(xshift=win_width+mvtpl_width+20,
                                               yshift=sg.height()-mvtpl_height)
            win.show()
            win.animatsimdir = animatsimdir
            win.save_paramNames_bhvNames()
            if gravity == 1000:     #  No gravity indicated in scriptFile
                gravity = readGravityfromAsim(model)
            optSet.gravity = gravity
            win.editValueGravity.setText(str(gravity))
            runSeriesMvts(tabscript, listNewMvtline)
            win.closeWindows()
            sys.exit()
            # ===============================================================
            if (sys.flags.interactive != 1) or not hasattr(QtCore,
                                                           'PYQT_VERSION'):
                QtWidgets.QApplication.instance().exec_()

            # win.closeWindows()
