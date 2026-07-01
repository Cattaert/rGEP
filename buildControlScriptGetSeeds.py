# -*- coding: utf-8 -*-
"""
Created on Wednesday July 01 17:23:56 2026

@author:D. Cattaert
This new script was built from "buildControlScript.py" and allows to create
runScripts that contain a CMAES and a series of GEP with a series of errThr and
coactThr that goes from large to small values. After the CMAes is finished, the
30 best behaviors are used to build a "autoseed00 directory".
After each GEP the same procedure is applied to build seeds that are moroe and
more constrained. The idea is to finaly get the greatest variety of seeds the
would represent different families.
"""

import os
import tkinter, tkinter.filedialog
import csv, json


import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
from pyqtgraph.Qt import QtCore
# from pyqtgraph.Qt import QtGui
from PyQt5.QtWidgets import QInputDialog, QLineEdit

from optimization import showdialog
from optimization import readAnimatLabDir
from optimization import copyDirectory
from optimization import getInfoComputer
from optimization import readGravityfromAsim
from optimization import readSpan_from_DicSpanVal
from optimization import calculateMvtdurFromMax_Speed
from optimization import getValuesFromText
#from GUI_AnimatLabOptimization import saveAnimatLabSimDir

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

from controlScriptGEP import transfertData


def getValuesFromTxtAngles(angles):
    table = getValuesFromText(angles)
    angle1 = float(table[1])
    angle2 = float(table[2])
    print()
    print("angle1", angle1, "angle2", angle2)
    if table[3] == "mvtdur":
        mvtdur = float(table[4])
        ang_txt = 'ang%d-%d_dur%d' % (angle1, angle2, int(mvtdur*1000))
    elif table[3] == "max_speed":
        max_speed = float(table[4])
        amplitude = angle2 - angle1
        mvtdur = calculateMvtdurFromMax_Speed(optSet, max_speed,
                                              amplitude)
        ang_txt = 'ang%d-%d_dur%d' % (angle1, angle2, int(mvtdur*1000))
    return ang_txt    

def get_newtrial_dir(trial_root):
    listsubdir = os.listdir(trial_root)
    ix = 0
    for index, sdir in enumerate(listsubdir):
        if os.path.isdir(os.path.join(trial_root, sdir)):
            ix += 1
    print(ix, "sub-directories")
    print("Existing trial-XX directories")
    list_trialdir = []
    for fold in listsubdir:
        if int(fold.find("_seed")) == -1:
            print(fold)
            list_trialdir.append(fold)
    ix = len(list_trialdir)
    new_trialname = "trial" + '-{0:d}'.format(ix)
    print("New directory :", new_trialname)
    return new_trialname


def dialogWindow(titre, info, details=""):
    rep = showdialog(titre, info, details)
    # print(rep)
    if rep == 1024:
        OK = True
    else:
        OK = False
    return OK


def SetModelDir(root_path):
    winscr = DialogBoxValues()
    winscr.getText('Subdirectory for Model (default is "")', root_path, "")
    modeldirname = winscr.text
    if modeldirname != "":
        model_path = root_path +"/" + modeldirname
        print("model subdirectory:", modeldirname)
        txtdirname = "sub-dir:\n{}".format(modeldirname)
    else:
        model_path = root_path
        print("no subdirectory for model_path: ", model_path)
        txtdirname = "no sub directory"
    winscr.close()
    return model_path, modeldirname, txtdirname


def ValidateModelDir(root_path, model_path, txtdirname):
    titre = "Root path of the simlation series OK?"
    info = model_path
    details = "rootpath:\n {} \n\n{}".format(root_path, txtdirname)

    """
    # ============ we can  call showdialog directly ===================
    rep = showdialog("Systematic parameter exploration", info, details)
    print(rep)
    """
    winscr = DialogBoxValues()
    # ==== we can also call showdialog from a QMainwindow class =======
    winscr.Boxdialog(titre, info, details)
    rep = winscr.rep
    winscr.close()
    if rep == 1024:
        print("model_path validated:\n{}".format(model_path))


def Warningindow(dirname):
    title = "     WARNING!!!"
    info = "check {} content is OK".format(dirname)
    message = "The model sub-dir should contain the .aproj from animatLab.\n"
    message += "Check the meshPath is OK in this .aproj file. If not, modify "
    message += "the meshPath by running: \n GUI_AnimatPar.py"
    message += " -> change Meshpath\n\n"
    message += "The model sub-dir should also contain the .aform lineChart(s)"
    message += "\n\nBefore going ahead,\n run GUI_AnimatPar.py -> "
    message += " Pick a Folder\n  on this subdirectory if not already done.\n"
    
    mb = MyMessageBox()     # This a resizeable QMessageBox
    mb.setText(title)
    mb.setInformativeText(info)
    mb.setDetailedText(message)
    mb.exec_()


def go_on_or_stop():
    titre = "GO ON?"
    info = "Do we go on? (model dir content is OK)"
    details = ""
    # ============ we can  call showdialog directly ===================
    rep = showdialog(titre, info, details)
    # print(rep)
    if rep == 1024:
        OK = True
    else:
        OK = False
    return OK


def get_rootpath_modeldir():
    previousanimatsimdir = readAnimatLabDir()
    root = tkinter.Tk()
    root.withdraw()
    
    model_path = tkinter.filedialog.askdirectory(parent=root,
                                         initialdir=previousanimatsimdir,
                                         title='Select model directory')
    root.destroy()
    root_path = os.path.split(model_path)[0]

    if len(model_path ) > 0:
        print("You chose %s" % model_path)
    modeldirname = os.path.split(model_path)[-1]
    # txtdirname = "sub-dir:\n{}".format(modeldirname)
    # model_path, modeldirname, txtdirname = SetModelDir(root_path)
    # ValidateModelDir(root_path, model_path, txtdirname)
    Warningindow(modeldirname)
    OK = go_on_or_stop()
    if not OK :
        print("Process stopped by user")
        sys.exit()
    else:
        print("We go on...")
        animatLabV2ProgDir, nb_procs = getInfoComputer()
        subdir = os.path.split(model_path)[-1]
        print(subdir)
        rootdir = os.path.dirname(model_path)
        # rootdir += "/"
        folders = FolderOrg(animatlab_root=rootdir,
                            python27_source_dir=animatLabV2ProgDir,
                            subdir=subdir)
        model = AnimatLabModel.AnimatLabModel(folders.animatlab_commonFiles_dir)
        sims = AnimatLabSimRunner.AnimatLabSimulationRunner("Test Sims",
            rootFolder = folders.animatlab_rootFolder,
            commonFiles = folders.animatlab_commonFiles_dir,
            sourceFiles = folders.python27_source_dir,
            simFiles = folders.animatlab_simFiles_dir,
            resultFiles = folders.animatlab_result_dir)
        # model = AnimatLabModel.AnimatLabModel(folders.animatlab_commonFiles_dir)
        projMan = ProjectManager.ProjectManager('Test Project')
        optSet = OptimizeSimSettings(folders=folders, model=model,
                                     projMan=projMan, sims=sims)
        optSet.model = model
    return optSet, root_path, model_path, modeldirname



def get_control_script_filename(scriptFile_name):
    winscr = DialogBoxValues()
    titre = "Validate ScriptFileName"
    info = "    " + scriptFile_name + "    "
    scriptFile_name = winscr.editText(titre, info, scriptFile_name)
    winscr.close()
    return  scriptFile_name


def get_oc(other_constraints):
    otherconstraints_short_names = optSet.otherconstraints_short_names
    oc = ""
    tmp1 = ""
    tmp2 = ""
    if other_constraints != {}:
        for idx, key in enumerate(other_constraints.keys()):
            if key == "max_endMN_pot":
                oc += "MNV{}".format(int(other_constraints[key]*1000))
            elif key == "min_endangle":
                tmp1 = "A{}".format(int(other_constraints[key]))
                oc += tmp1 + tmp2
            elif key == "max_endangle":
                tmp2 = "-{}".format(int(other_constraints[key]))
            else:
                oc += "{}{}".format(otherconstraints_short_names[idx],
                                    int(other_constraints[key]))
            print(oc)    
    return oc


def set_other_constraints(other_constraints):
    otherconstraints_names = optSet.otherconstraints_names
    otherconstraints_short_names = optSet.otherconstraints_short_names
    dicValues = other_constraints
    selected = list(dicValues.keys())
    typ = "Other constraints"
    text = "select other constraints"
    choice = choose_elements_in_list(otherconstraints_names,
                                     typ, selected, text)
    newdicValues = {}
    for key in choice:
        if key in dicValues.keys(): 
            newdicValues[key] = dicValues[key]
        else:
            newdicValues[key] = 0
    """
    if newdicValues != {}:   
        dicValues = set_values_in_list(newdicValues, selected, typ, text)
    else:
        dicValues = {}
    """
    other_constraints = dicValues
    print(other_constraints)
    optSet.other_constraints = other_constraints
    oc = get_oc(other_constraints)
    return other_constraints, oc


def get_general_constraints(base_path, process):
    if process == "GEP":
        base_root = os.path.split(base_path)[0]
        dicCostFileName = "CostFunctionParam.json"
        CompleteDicCostFileName = base_path + "/ResultFiles/" + dicCostFileName
        if os.path.exists(CompleteDicCostFileName):
            print("CostFunctionParam.json found... READING")
            f = open(CompleteDicCostFileName,)
            # returns JSON object as 
            # a dictionary
            costFunctionDic = json.load(f)
            cP1 = costFunctionDic["coactP1"]
            cP2 = costFunctionDic["coactP2"]
            other_constraints = {}
            for name in optSet.otherconstraints_names:
                if name in costFunctionDic.keys():
                    other_constraints[name] = costFunctionDic[name]
            optSet.other_constraints = other_constraints
            oc = get_oc(other_constraints)
        else:
            print("No CostFunctionParam.json file found...")
            cP1 = 0
            cP2 = 0   
            if base_path != "":
                base_root_name = os.path.split(base_root)[-1]
                prev_cP = base_root_name[base_root_name.find("cP"):]
                cP1 = int(prev_cP[2:prev_cP.find("_")])
                prev_cP2 = prev_cP[prev_cP.find("_")+1:]
                cP2 = int(prev_cP2[:prev_cP2.find("_")])
                
                # other_constraints = optSet.other_constraints
                # other_constraints, oc = set_other_constraints(other_constraints)
                other_constraints = {}
                oc = ""
                remain = prev_cP2[prev_cP2.find("_")+1:]
                otherConstraints = []
                if remain != "":
                    oc = remain
                    balises_lst = ["MAng", "EndMNV"]
                    OC_lst = []
                    for idx, bal in enumerate(balises_lst):
                        OC_lst.append(remain.find(bal))
                    idy = 0
                    while idy < len(OC_lst)-1:
                        otherConstraints.append(remain[OC_lst[idy]:OC_lst[idy+1]])
                        idy += 1
                    otherConstraints.append(remain[OC_lst[idy]:])
                    for idx, chain in enumerate(otherConstraints):
                        if chain[0:4] in ["MAng", "MaxA"] :
                            other_constraints["max_endangle"] = chain[4:]
                        if chain[0:4] in ["minxA"] :
                            other_constraints["min_endangle"] = chain[4:]    
                        if chain[0:6] == "EndMNV":
                            other_constraints["max_endMN_pot"] = float(chain[6:])/1000
                    optSet.other_constraints = other_constraints

    elif process == "optimization":
        dicCostFileName = "CostFunctionParam.json"
        CompleteDicCostFileName = base_path + "/ResultFiles/" + dicCostFileName
        # Opening JSON file
        if os.path.exists(CompleteDicCostFileName):
            f = open(CompleteDicCostFileName,)
            # returns JSON object as 
            # a dictionary
            costFunctionDic = json.load(f)
            cP1 = costFunctionDic["coactP1"]
            cP2 = costFunctionDic["coactP2"]
        else:
            cP1 = 0
            cP2 = 0
        dicValues = {'coactP1':cP1, 'coactP2':cP2}
        selected = list(dicValues.keys())
        typ = "General settings"
        text = "set settings values"
        dicValues = set_values_in_list(dicValues, selected, typ, text)
        coactP1 = dicValues["coactP1"]
        coactP2 = dicValues["coactP2"]
        if coactP1 < 0.001:
            coactP1 = 0
        if coactP2 < 0.001:
            coactP2 = 0
        if coactP1 > 5:
            coactP1 = int(coactP1)
        if coactP2 > 5:
            coactP2 = int(coactP2)
        cP = "cP{}_{}".format(str(coactP1), str(coactP2))
        other_constraints = optSet.other_constraints
        other_constraints, oc = set_other_constraints(other_constraints)
    
    return coactP1, coactP2, cP, other_constraints, oc


def get_elts_optim_procedure(model_short_ID, base_path):
    # ================= OPTIMIZATION to get seeds ============================
    """
    list_elem = ["CMAes", "VSCD"]
    typ = "Optimizations tool"
    title = "Choose one Optimization method"
    optimiz = choose_one_element_in_list(title, list_elem, typ)
    print("optimization method:", optimiz)
    other_constraints = optSet.other_constraints
    other_constraints, oc = set_other_constraints(other_constraints)
    """
    optimiz = "CMAes"
    #Æres = get_general_constraints(base_path, "optimization")
    #coactP1, coactP2, cP, other_constraints, oc = res
    if optimiz == "CMAes":
        dicValues = {'sigma':0.01, 'nbRuns':3000,
                     'span':100, "errThr":10, "coactThr":2}
        selected = list(dicValues.keys())
        typ = "CMAes settings"
        text = "set settings values"
        dicValues = set_values_in_list(dicValues, selected, typ, text)
        print(dicValues)
        
        span = int(dicValues["span"])
        # scriptFile_name = optimiz + "_" + model_short_ID
        # scriptFile_name += "_" + "span" + str(int(dicValues["span"]))
        scriptFile_name = "autoSeekSeeds_" + model_short_ID
        scriptFile_name += "_" + optimiz
        
        errThr = dicValues["errThr"]
        coactThr = dicValues["coactThr"]
        Th = "errT{}coT{}".format(str(errThr), str(coactThr))
        
        # scriptFile_name += "_" + cP + oc + Th + ".txt"
        scriptFile_name += "_GEP" + "_" + cP + oc + Th + ".txt"
        scriptFile_name = get_control_script_filename(scriptFile_name)
        s = "cmaes" + '\t' + "xCoactPenality1=" + str(coactP1) + '\t'
        s += "xCoactPenality2=" + str(coactP2) + '\t'
        s += "threshold=Var" + '\t' + "cmaes_sigma=" 
        s += str(dicValues["sigma"]) + '\t' 
        s += "nbTotCMAesRuns=" + str(int(dicValues["nbRuns"])) + '\t'
        s += "errThr=" + str(dicValues["errThr"]) + '\t'
        s += "coactThr=" + str(dicValues["coactThr"]) + '\n'
        txt_optimiz = s    

    elif optimiz == "VSCD":
        dicValues = {'deltacoeff':0.01,
                     'nbsteps':3, 'nbepoch':2, 'span':100,
                     "errThr":1.0, "coactThr":0.01}
        selected = list(dicValues.keys())
        typ = "VSCD settings"
        text = "set settings values"
        dicValues = set_values_in_list(dicValues, selected, typ, text)
        print(dicValues)
        
        span = int(dicValues["span"])
        scriptFile_name = optimiz + "_" +  model_short_ID
        scriptFile_name += "_" + "span" + str(int(dicValues["span"]))
        
        errThr = dicValues["errThr"]
        coactThr = dicValues["coactThr"]
        Th = "errT{}coT{}".format(str(errThr), str(coactThr))
        
        scriptFile_name += "_" + cP + oc + Th + ".txt"
        scriptFile_name = get_control_script_filename(scriptFile_name)
        s = "VSCD" + '\t' + "xCoactPenality1=" + str(coactP1) + '\t'
        s += "xCoactPenality2=" + str(coactP2) + '\t'
        s += "deltacoeff=" + str(dicValues["deltacoeff"]) +'\t'
        s += "nbsteps=" + str(int(dicValues["nbsteps"])) + '\t' 
        s += "nbepoch=" + str(int(dicValues["nbepoch"])) + '\t'
        s += "errThr=" + str(dicValues["errThr"]) + '\t'
        s += "coactThr=" + str(dicValues["coactThr"]) + '\n'
        txt_optimiz = s    
    return optimiz, txt_optimiz, cP, oc, Th, span, dicValues


def get_elts_GEP_procedure(model_short_ID, base_path, GEP_dicValues):
    # ================= GEP PROCEDUR SETTINGS ============================
    span_type = "unique span value"
    span = 5

    print("\nGEP procedure preparation")
    #res = get_general_constraints(base_path, "GEP")
    #coactP1, coactP2, cP, other_constraints, oc = res
    
    dicValues = GEP_dicValues
    """
    selected = list(dicValues.keys())
    typ = "GEP settings"
    text = "set settings values"
    dicValues = set_values_in_list(dicValues, selected, typ, text)
    """
    dicValues["span"] = span
    print(dicValues)
    errThr = dicValues["errThr"]
    coactThr = dicValues["coactThr"]
    Th = "errT{}coT{}".format(str(errThr), str(coactThr))
    
    # previousanimatsimdir = readAnimatLabDir()
    # seeds_txt = seeds_dirname[seeds_dirname.find('seed'):]
    # scriptFile_name = "rGEP" + "_" + model_short_ID
    # scriptFile_name += "_" + seeds_txt
    if span_type == "unique span value":
        span = float(dicValues["span"])
        if span > 5:
            span = int(span)
        # scriptFile_name += "_" +"span" + str(span)
    else:
        None
        # scriptFile_name += "_" +"spanAuto"
    # scriptFile_name += "_" + cP + oc + Th +".txt"
    # scriptFile_name = get_control_script_filename(scriptFile_name)
    s = "GEPrand" + '\t' + "xCoactPenality1=" + str(coactP1) + '\t'
    s += "xCoactPenality2=" + str(coactP2) + '\t'
    s += "neighbours=1" + '\t' + "auto=1" + '\t' 
    s += "nbextend=" + str(int(dicValues["nbextend"])) + '\t'
    s += "nbfill=" + str(int(dicValues["nbfill"])) + '\t'
    s += "errThr=" + str(dicValues["errThr"]) + '\t'
    s += "coactThr=" + str(dicValues["coactThr"]) + '\n'
    txt_GEP = s
    return txt_GEP, cP, oc, Th, span


def get_model_caracteristics(optSet, modeldirname, root_path):
    root = tkinter.Tk()
    root.withdraw()
    base_path = tkinter.filedialog.askdirectory(parent=root,
                                                initialdir=root_path,
                                                title='Select base directory')
    root.destroy()

    winscr = DialogBoxValues()
    if base_path == "":
        model_short_ID = "ID124NGC"
    else:
        base_name = os.path.split(base_path)[-1]
        txt1 = base_name[base_name.find("_")+1:]
        model_short_ID = txt1[:txt1.find("_")]
    model_short_ID = winscr.editText("Model shortID", "Edit shortID",
                                     model_short_ID)
    model_identification = model_short_ID # + "_WM1aDyn20_B150"
    model_identification = winscr.editText("Model caracteristics",
                                           "Edit caracteristics",
                                           model_identification)
    model = optSet.model
    gravity_txt = readGravityfromAsim(model)
    gravity=float(gravity_txt)
    optSet.gravity = gravity
    gravity_txt = winscr.editText("Gravity","Edit gravity value 0 or -9.81",
                                  gravity_txt)
    gravity = float(gravity_txt)
    print("gravity: ", gravity)
    
    angles = "angle	0	90	max_speed	138"
    angles = winscr.editText("Aim movement", "Edit Mvt caracteristics",
                             angles)
    ang_txt = getValuesFromTxtAngles(angles)
    winscr.close()
    list_elem = ["maxSpeed", "Duration"]
    title = "Choose Behav graph ordinate"
    typ = "Graph Ordinate"
    bhvCriteria = choose_one_element_in_list(title, list_elem, typ)
    return (base_path, model_short_ID, model_identification,
            gravity, angles, ang_txt, bhvCriteria)


def write_optim_scriptFile(optSet, root_path, modeldirname, seeds_path,
                           newbase_path):
    # ============= Save costfunction parameters in .csv and .json ===========
    other_constraints = optSet.other_constraints
    costFunctionDic = {"coactP1" : coactP1,
                       "coactP2" : coactP2}
    costFunctionDic.update(other_constraints)
    dicCostFileName = "CostFunctionParam.csv"
    CompleteDicCostFileName = newbase_path + "/ResultFiles/" + dicCostFileName
    with open(CompleteDicCostFileName, "w", newline="") as f:
        w = csv.DictWriter(f, costFunctionDic.keys())
        w.writeheader()
        w.writerow(costFunctionDic)
    dicCostFileName = "CostFunctionParam.json"
    CompleteDicCostFileName = newbase_path + "/ResultFiles/" + dicCostFileName
    with open(CompleteDicCostFileName, "w") as file:
        json.dump(costFunctionDic, file)
    # =========================================================================    
    if optimiz == "CMAes":
        completeScriptName = os.path.join(scriptFile_path, scriptFile_name)
        if not os.path.exists(scriptFile_path):
            os.makedirs(scriptFile_path)
        with open(completeScriptName, 'w') as f:
            s0 = "create_workDir" + "\t" + "Path=" + newmodel_root + "/" + "\t"
            s0 += "DirName=workDir_animatlab" + "\n"
            print(s0)
            f.write(s0)
            s1 = "copy_to_workDir" + "\t" + "PathSrc=" + newbase_path + "\n"
            print(s1)
            f.write(s1)
            s2 = "gravity" + "\t" + "g=" + str(gravity) + "\n"
            print(s2)
            f.write(s2)
            s3 = angles + "\n"
            print(s3)
            f.write(s3)
            s4 = "bhvCriteria" + "\t" + "bhv_ordinate=" + bhvCriteria + "\n"
            print(s4)
            f.write(s4)
            oc_txt = "other_constraints"
            if other_constraints == {}:
                oc_txt += '\t' + 'None\n'
            else:
                oc_txt += '\t'
                for key in other_constraints.keys():
                    print(key)
                    oc_txt += key + '=' + str(other_constraints[key]) + '\t'
                oc_txt = oc_txt[:-1]    # suppress the last '\t' 
                oc_txt += '\n'
            f.write(oc_txt)
            s5 = txt_optimiz
            print(s5)
            f.write(s5)
            s6 = "span=" + str(span) + "\n"
            print(s6)
            f.write(s6)
            s7 = "Get30Bestbhv" + "\t" + "seed_path=" + seeds_path + "\n"
            print(s7)
            f.write(s7)
            s8 = "transfert_from_workDir" + "\t" + "PathDest="
            s8 += newmodel_root + "/" + "1_autoCMAes_" + model_short_ID
            # s8 += "_" +"span" + str(span) + Th
            s8 += "\n\n"
            print(s8)
            f.write(s8)
            f.close()
    elif optimiz == "VSCD":
        completeScriptName = os.path.join(scriptFile_path, scriptFile_name)
        with open(completeScriptName, 'w') as f:
            s0 = "create_workDir" + "\t" + "Path=" + newmodel_root + "/" + "\t"
            s0 += "DirName=workDir_animatlab" + "\n"
            print(s0)
            f.write(s0)
            s1 = "copy_to_workDir" + "\t" + "PathSrc=" + newbase_path + "\n"
            print(s1)
            f.write(s1)
            s2 = "gravity" + "\t" + "g=" + str(gravity) + "\n"
            print(s2)
            f.write(s2)
            s3 = angles + "\n"
            print(s3)
            f.write(s3)
            s4 = "bhvCriteria" + "\t" + "bhv_ordinate=" + bhvCriteria + "\n"
            print(s4)
            f.write(s4)
            oc_txt = "other_constraints"
            if other_constraints == {}:
                oc_txt += '\t' + 'None\n'
            else:
                oc_txt += '\t'
                for key in other_constraints.keys():
                    print(key)
                    oc_txt += key + '=' + str(other_constraints[key]) + '\t'
                oc_txt = oc_txt[:-1]    # suppress the last '\t' 
                oc_txt += '\n'
            f.write(oc_txt)
            s5 = txt_optimiz
            print(s5)
            f.write(s5)
            s6 = "span=" + str(span) + "\n"
            print(s6)
            f.write(s6)
            s7 = "Get30Bestbhv" + "\t" + "seed_path=" + seeds_path + "\n"
            print(s7)
            f.write(s7)
            s8 = "transfert_from_workDir" + "\t" + "PathDest="
            s8 += newmodel_root + "/" + "1_VSCD_" + model_short_ID + "_"
            s8 += "span" + str(span) + Th + "\n\n"
            print(s8)
            f.write(s8)
            f.close()
    print("\n", scriptFile_name, "saved into", scriptFile_path)
    return newmodel_root, newbase_dirname, s8, rep1, completeScriptName


def get30bestbhv(model_short_ID, newmodel_root, autoSeed_number):
    # typ = rootdir[:11]
    if autoSeed_number < 10:
        tx = "0"
    else:
        tx = ""
    strautoSeed_number = tx + str(autoSeed_number)
    seedsDirName = "0_" + model_short_ID + "_autoSeeds" + strautoSeed_number
    seeds_path = newmodel_root + "/" + seedsDirName
    # df = pd.read_csv("mon_fichier.txt", sep="\t")
    return seeds_path


def write_GEP_scriptFile(optSet, root_path, modeldirname, rep1,
                         completeScriptName, prev_seeds_path, seeds_path,
                         SeedSearch_dicVal, autoSeed_number):
    # rep1 = get_model_caracteristics(optSet, modeldirname, root_path)
    (base_path, model_short_ID, model_identification,
     gravity, angles, ang_txt, bhvCriteria) = rep1
    # cwd = os.getcwd()
    # scriptFile_path = os.path.join(cwd, "Script_files")
    errThr = SeedSearch_dicVal['errThr' + str(autoSeed_number-1)]
    coactThr = SeedSearch_dicVal['coactThr' + str(autoSeed_number-1)]
    GEP_dicValues = {'neighbours':1, 'auto':1, 'nbextend':200, 'nbfill':20,
                     'errThr':errThr, 'coactThr':coactThr}

    rep2 = get_elts_GEP_procedure(model_short_ID, base_path, GEP_dicValues)
    txt_GEP, cP, oc, Th, span = rep2
    
    if bhvCriteria == "maxSpeed":
        bhvord = "MxSp"
    else:
        bhvord = "Dur"
    model_completeidentification = modeldirname + "_" + model_identification
    model_completeidentification += "_" + bhvord +"_"+ cP +"_"+ oc
    newmodel_root = root_path + "/" + model_completeidentification
    """
    completename = os.path.join(scriptFile_path, scriptFile_name)
    if not os.path.exists(scriptFile_path):
        os.makedirs(scriptFile_path)
    """
    titre = "Graphics Builder"
    info = "Do you want Graphics?"
    rep3 = dialogWindow(titre, info, details="")
    other_constraints = optSet.other_constraints
    seedsDirName = os.path.split(prev_seeds_path)[-1]
    seedsName = seedsDirName[seedsDirName.find("auto"):]

    with open(completeScriptName, 'a') as f:
        s0 = "create_workDir" + "\t" + "Path=" + newmodel_root + "/" + "\t"
        s0 += "DirName=workDir_animatlab" + "\n"
        print(s0)
        f.write(s0)
        s1 = "copy_to_workDir" + "\t" + "PathSrc=" + prev_seeds_path + "\n"
        print(s1)
        f.write(s1)
        s2 = "gravity" + "\t" + "g=" + str(gravity) + "\n"
        print(s2)
        f.write(s2)
        s3 = angles + "\n"
        print(s3)
        f.write(s3)
        s4 = "bhvCriteria" + "\t" + "bhv_ordinate=" + bhvCriteria + "\n"
        print(s4)
        f.write(s4)
        oc = "other_constraints"
        if other_constraints == {}:
            oc += '\t' + 'None\n'
        else:
            oc += '\t'
            for key in other_constraints.keys():
                print(key)
                oc += key + '=' + str(other_constraints[key]) + '\t'
            oc = oc[:-1]    # suppress the last '\t' 
            oc += '\n'
        f.write(oc)
        s5 = txt_GEP
        print(s5)
        f.write(s5)
        s6 = "span=" + str(span) + "\n"
        print(s6)
        f.write(s6)
        if rep3:
            s7 = "GEPMetrixGraphs"  + "\n"
            print(s7)
            f.write(s7)
        s7 = "Get30Bestbhv" + "\t" + "seed_path=" + seeds_path + "\n"
        print(s7)
        f.write(s7)
        s8 = "transfert_from_workDir" + "\t" + "PathDest="
        s8 += newmodel_root + "/" + "2_AutorGEP_" + model_short_ID 
        s8 += "_" + seedsName + "_" + "span" + str(span) + Th + "\n\n"
        print(s8)
        f.write(s8)
        f.close()
    return newmodel_root, s8


def organize_folders(model_path, newmodel_root, newbase_dirname):
    newbase_path = newmodel_root + "/" + newbase_dirname
    if not os.path.exists(newmodel_root):
        os.makedirs(newmodel_root)
    if not os.path.exists(os.path.join(newmodel_root, newbase_dirname)):
        os.makedirs(os.path.join(newmodel_root, newbase_dirname))
    copyDirectory(model_path, newbase_path)


def main():
    None


# =============================================================================
#                                   MAIN
# =============================================================================
if __name__ == '__main__':
    import sys
    pg.mkQApp()
    # main()
    optSet, root_path, model_path, modeldirname = get_rootpath_modeldir()
    cwd = os.getcwd()
    scriptFile_path = os.path.join(cwd, "Script_files")
    
    rep1 = get_model_caracteristics(optSet, modeldirname, root_path)
    (base_path, model_short_ID, model_identification,
     gravity, angles, ang_txt, bhvCriteria) = rep1
    if bhvCriteria == "maxSpeed":
        bhvord = "MxSp"
    else:
        bhvord = "Dur"
    scriptFile_name = "AutomaticSeedSearch.txt"
    process = "optimization"
    res = get_general_constraints(base_path, process)
    coactP1, coactP2, cP, other_constraints, oc = res
    
    completeScriptName = os.path.join(scriptFile_path, scriptFile_name)  
    model_completeidentification = modeldirname + "_" + model_identification
    model_completeidentification += "_"+ bhvord + "_"+ cP + "_"+ oc
    newmodel_root = root_path + "/" + model_completeidentification
    newbase_dirname = "0_" + model_short_ID + "_base"
    newbase_path = newmodel_root + "/" + newbase_dirname


    # =========================================================================
    process = "optimization"
    # =========================================================================
    rep2 = get_elts_optim_procedure(model_short_ID, base_path)
    optimiz, txt_optimiz, cP, oc, Th, span, dicValues = rep2
    
    if os.path.exists(newbase_path):
        print(newbase_dirname, "already exists")
    else:
        os.makedirs(newbase_path)
        copyDirectory(model_path, newbase_path)
        print(newbase_path, "created")
    """
    ATTENTION Potentiel PB car chemin 'autoSeed_number' rentré en dur !!!
    """ 
    autoSeed_number = 0
    seeds_path = get30bestbhv(model_short_ID, newmodel_root, autoSeed_number)
    prev_seeds_path = seeds_path
    rep3 = write_optim_scriptFile(optSet, root_path, modeldirname,
                                  seeds_path, newbase_path)
    newmodel_root, newbase_dirname, s8, rep1, completeScriptName = rep3
    start = len("transfert_from_workDir\tPathDest=")
    CMAESpath = s8[start:-1]
    model_short_ID = rep1[1]
    ang_txt = rep1[5]
    trial_root = CMAESpath + "/" + ang_txt
    """
    GEPdataPath = trial_root + "/trial-0/GEPdata"
    if os.path.exists(GEPdataPath):
        trial_root = os.path.split(GEPdataPath)[0]
        new_trialname = get_newtrial_dir(trial_root)
        GEPdataPath = trial_root + "/" + new_trialname + "/GEPdata"
    """
    
    # =========================================================================
    process = "GEP"
    # =========================================================================
    SeedSearch_dicVal = {}
    GEPNb = 5
    errThr = [10,5,3,2,1,1]
    coactThr = [2,1,0.6,0.3,0.1,0.01]
    for gep in range(GEPNb+1):
        nom_err_thr = "errThr" + str(gep)
        nom_coact_thr = "coactThr" + str(gep)
        SeedSearch_dicVal[nom_err_thr] = errThr[gep]
        SeedSearch_dicVal[nom_coact_thr] = coactThr[gep]
    selected = list(SeedSearch_dicVal.keys())
    typ = "General settings"
    text = "set settings values"
    SeedSearch_dicVal = set_values_in_list(SeedSearch_dicVal, selected,
                                           typ, text)
    
    while autoSeed_number < GEPNb:
        autoSeed_number += 1
        seeds_path = get30bestbhv(model_short_ID, newmodel_root,
                                  autoSeed_number)
        rep4 = write_GEP_scriptFile(optSet, root_path, modeldirname, rep1,
                                    completeScriptName, prev_seeds_path,
                                    seeds_path, SeedSearch_dicVal,
                                    autoSeed_number)
        newmodel_root, s8 = rep4
        prev_seeds_path = seeds_path

    autoSeed_number += 1
    rep4 = write_GEP_scriptFile(optSet, root_path, modeldirname, rep1,
                                completeScriptName, prev_seeds_path,
                                seeds_path, SeedSearch_dicVal,
                                autoSeed_number)

    
    sys.exit()

    # Start Qt event loop unless running interaction mode or using pyside
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()
