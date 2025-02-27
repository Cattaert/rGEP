# -*- coding: utf-8 -*-
"""
Created on Sat Jan 21 09:23:56 2023

@author:D. Cattaert
Modified January 26, 2023 (D. Cattaert):
    Several bugs fixed
    Controls if scriptFile_path exits before saving the sriptFile
    Extracts model_short_ID from base directory name (if exists)
Modified Jnuary 30, 2023 (D. Cattaert):
    get_model_caracteristics() procedure improved -> returns the base_path as
    first argument
    base_path is used in get_elts_GEP_procedure() to facilitate selection of
    seed directory in tkinter.filedialog.askdirectory
Modified February 6, 2023 (D. Cattaert):
    Accept now the option "from file" for command "span"
Modified February 14, 2023 (D. Cattaert):
    In write_optim_scriptFile()  if os.path.exists(newbase_path) false, the
    newbase_directory was created but stayed emty. Now the content of modeldir
    is copied into the newbase_directory
Modified Febrary 20, 2023 (D. Cattaert):
    Bug fixed: pg.QtGui.QMessageBox() replaced by pg.QtWidgets.QMessageBox()
Modified February 28, 2023 (D. Cattaert):
    get_elts_optim_procedure() has been improved to get the cactPenality1 and 2
    from the nale of the directory in which is the base folder.(  cP100_0).
    get_elts_GEP_procedure() has been changed similarly.
Modifie (D. Cattaert):
    A default ID name is now Proposed
            in VSCD_tool_box.py called by GEP_GUI (MaFenetre)
Modified February 10, 2025 (D.Cattaert):
    other_constraints dictionary is now red from optSet.other_constraints and
    its parameters can be activated or deactivated in a new procedure
    set_other_constraints()
    The values of the chosen parameters can be modified in the process of
    building the scriptFile. If no other parameters were retained by the user,
    the line "other_constraints" contains only "None"
    other_constraints is used to define the cost function additional
    constraints such as "max_endangle"  and  "max_endMN_pot"
    Additional constraints may be added on demand, by adding the new
    constraints names in optSet.other_constraints_names list
    and their default values in optSet.other_constraints
    controlScript.py, optimization.py and animatlabOptimSetting.py have been
    modified accordingly.
Modified February 11, 2025 (D. Cattaert):
    When a new script for GEP is created, the cost function parameters are
    taken from the new root directory name... for eample:
        "NS32NG_52(sim)_ID222NGC_bhvMSpeed_cP100_100_MAng115EndMNV-60"
    A CSV file ("CostFunctionParam.csv") containing all costFunction paramters
    is created in the base directory (in the resultfile folder)
Modified February 20, 2025 4D; Cattaert):
    Thanks to modifications in animatlabOptimSettings.py, names and short names 
    of the other constraints  can be obtained from:
        optSet.otherconstraints_short_names and optSet.otherconstraints_names
    These names and short_names are used in set_other_constraints()
    and get_oc().
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
    titre = "ScriptFileName"
    info = "Edit text"
    scriptFile_name = winscr.editText(titre, info, scriptFile_name)
    winscr.close()
    return  scriptFile_name


def get_oc(other_constraints):
    otherconstraints_short_names = optSet.otherconstraints_short_names
    oc = ""
    if other_constraints != {}:
        for idx, key in enumerate(other_constraints.keys()):
            if key == "max_endMN_pot":
                oc += "EndMNV{}".format(int(other_constraints[key]*1000))
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
    if newdicValues != {}:   
        dicValues = set_values_in_list(newdicValues, selected, typ, text)
    else:
        dicValues = {}
    other_constraints = dicValues
    print(other_constraints)
    optSet.other_constraints = other_constraints
    oc = get_oc(other_constraints)
    return other_constraints, oc



def get_elts_optim_procedure(model_short_ID, base_path):
    # ================= OPTIMIZATION to get seeds ============================
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
    list_elem = ["CMAes", "VSCD"]
    typ = "Optimizations tool"
    title = "Choose one Optimization method"
    optimiz = choose_one_element_in_list(title, list_elem, typ)
    print("optimization method:", optimiz)
    other_constraints = optSet.other_constraints
    other_constraints, oc = set_other_constraints(other_constraints)

    if optimiz == "CMAes":
        dicValues = {'coactP1':cP1, 'coactP2':cP2, 'sigma':0.01,
                     'nbRuns':1000, 'span':100}
        selected = list(dicValues.keys())
        typ = "CMAes settings"
        text = "set settings values"
        dicValues = set_values_in_list(dicValues, selected, typ, text)
        print(dicValues)
        span = int(dicValues["span"])
        scriptFile_name = optimiz + "_" + model_short_ID
        scriptFile_name += "_" + "span" + str(int(dicValues["span"]))
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
        scriptFile_name += "_" + cP + oc + ".txt"
        scriptFile_name = get_control_script_filename(scriptFile_name)
        s = "cmaes" + '\t' + "xCoactPenality1=" + str(coactP1) + '\t'
        s += "xCoactPenality2=" + str(coactP2) + '\t'
        s += "threshold=Var" + '\t' + "cmaes_sigma=" 
        s += str(dicValues["sigma"]) + '\t' 
        s += "nbTotCMAesRuns=" + str(int(dicValues["nbRuns"])) + '\n'
        txt_optimiz = s    

    elif optimiz == "VSCD":
        dicValues = {'coactP1':cP1, 'coactP2':cP2, 'deltacoeff':0.01,
                     'nbsteps':3, 'nbepoch':2, 'span':100}
        selected = list(dicValues.keys())
        typ = "VSCD settings"
        text = "set settings values"
        dicValues = set_values_in_list(dicValues, selected, typ, text)
        print(dicValues)
        span = int(dicValues["span"])
        scriptFile_name = optimiz + "_" +  model_short_ID
        scriptFile_name += "_" + "span" + str(int(dicValues["span"]))
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
        scriptFile_name += "_" + cP + oc + ".txt"
        scriptFile_name = get_control_script_filename(scriptFile_name)
        s = "VSCD" + '\t' + "xCoactPenality1=" + str(coactP1) + '\t'
        s += "xCoactPenality2=" + str(coactP2) + '\t'
        s += "deltacoeff=" + str(dicValues["deltacoeff"]) +'\t'
        s += "nbsteps=" + str(int(dicValues["nbsteps"])) + '\t' 
        s += "nbepoch=" + str(int(dicValues["nbepoch"])) + '\n'
        txt_optimiz = s
    return optimiz, txt_optimiz, scriptFile_name, cP, oc, span, dicValues


def get_elts_GEP_procedure(model_short_ID, base_path):
    base_root = os.path.split(base_path)[0]
    root = tkinter.Tk()
    root.withdraw()
    seeds_path = tkinter.filedialog.askdirectory(parent=root,
                                            initialdir=base_root,
                                            title='Select seed directory')
    seeds_dirname = os.path.split(seeds_path)[-1]
    # ================= GEP PROCEDUR SETTINGS ============================
    list_elem = ["unique span value", "list of span values"]
    title = "¨Choose span type"
    typ = "span types"
    span_type = choose_one_element_in_list(title, list_elem, typ)
    winscr = DialogBoxValues()
    if span_type == "unique span value":
        span = str(5)
        span = winscr.editText("span","Edit span value", span)
        span = float(span)
    else:
        dicSpanVal_file = seeds_path + "/GEPdata/DicSpanVal.txt"
        rep = readSpan_from_DicSpanVal(dicSpanVal_file)
        listspanval = rep[1]
        print(listspanval)
        if listspanval == []:
            print("Default value for span: 5")
            span = 5
            span_type = "unique span value"
        else:
            span = "from_file"
    print("\nGEP procedure preparation")
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

    dicValues = {'coactP1':cP1, 'coactP2':cP2, 'neighbours':1, 'auto':1,
                 'nbextend':100, 'nbfill':20}
    selected = list(dicValues.keys())
    typ = "GEP settings"
    text = "set settings values"
    dicValues = set_values_in_list(dicValues, selected, typ, text)
    dicValues["span"] = span
    print(dicValues)
    
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
    
    # previousanimatsimdir = readAnimatLabDir()
    seeds_txt = seeds_dirname[seeds_dirname.find('seed'):]
    scriptFile_name = "rGEP" + "_" + model_short_ID
    scriptFile_name += "_" + seeds_txt
    if span_type == "unique span value":
        span = float(dicValues["span"])
        if span > 5:
            span = int(span)
        scriptFile_name += "_" +"span" + str(span)
    else:
        scriptFile_name += "_" +"spanAuto"
    scriptFile_name += "_" + cP + oc + ".txt"
    scriptFile_name = get_control_script_filename(scriptFile_name)
    s = "GEPrand" + '\t' + "xCoactPenality1=" + str(coactP1) + '\t'
    s += "xCoactPenality2=" + str(coactP2) + '\t'
    s += "neighbours=1" + '\t' + "auto=1" + '\t' 
    s += "nbextend=" + str(int(dicValues["nbextend"])) + '\t'
    s += "nbfill=" + str(int(dicValues["nbfill"])) + '\n'
    txt_GEP = s
    return txt_GEP, scriptFile_name, cP, oc, span, seeds_dirname


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
    winscr.close()
    list_elem = ["maxSpeed", "Duration"]
    title = "Choose Behav graph ordinate"
    typ = "Graph Ordinate"
    bhvCriteria = choose_one_element_in_list(title, list_elem, typ)
    return (base_path, model_short_ID, model_identification,
            gravity, angles, bhvCriteria)


def write_optim_scriptFile(optSet, root_path, modeldirname):
    rep1 = get_model_caracteristics(optSet, modeldirname, root_path)
    (base_path, model_short_ID, model_identification,
     gravity, angles, bhvCriteria) = rep1
    cwd = os.getcwd()
    scriptFile_path = os.path.join(cwd, "Script_files")
    rep2 = get_elts_optim_procedure(model_short_ID, base_path)
    optimiz, txt_optimiz, scriptFile_name, cP, oc, span, dicValues = rep2
    if bhvCriteria == "maxSpeed":
        bhvord = "bhvMSpeed"
    else:
        bhvord = "bhvDuration"
    model_completeidentification = modeldirname + "_" + model_identification
    model_completeidentification += "_" + bhvord + "_" + cP + "_" + oc
    newmodel_root = root_path + "/" + model_completeidentification
    newbase_dirname = "0_" + model_short_ID + "_base"
    newbase_path = newmodel_root + "/" + newbase_dirname
    if os.path.exists(newbase_path):
        print(newbase_dirname, "already exists")
    else:
        os.makedirs(newbase_path)
        copyDirectory(model_path, newbase_path)
        print(newbase_path, "created")
    # ============= Save costfunction parameters in .csv and .json ===========
    other_constraints = optSet.other_constraints
    costFunctionDic = {"coactP1" : dicValues["coactP1"],
                       "coactP2" : dicValues["coactP2"]}
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
        completename = os.path.join(scriptFile_path, scriptFile_name)
        if not os.path.exists(scriptFile_path):
            os.makedirs(scriptFile_path)
        with open(completename, 'w') as f:
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
            s7 = "transfert_from_workDir" + "\t" + "PathDest="
            s7 += newmodel_root + "/" + "1_CMAes_" + model_short_ID + "_"
            s7 += "span" + str(span) + "\n"
            print(s7)
            f.write(s7)
            f.close()
    elif optimiz == "VSCD":
        completename = os.path.join(scriptFile_path, scriptFile_name)
        with open(completename, 'w') as f:
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
            s7 = "transfert_from_workDir" + "\t" + "PathDest="
            s7 += newmodel_root + "/" + "1_VSCD_" + model_short_ID + "_"
            s7 += "span" + str(span) + "\n"
            print(s7)
            f.write(s7)
            f.close()
    print("\n", scriptFile_name, "saved into", scriptFile_path)
    return newmodel_root, newbase_dirname


def write_GEP_scriptFile(optSet, root_path, modeldirname):
    rep1 = get_model_caracteristics(optSet, modeldirname, root_path)
    (base_path, model_short_ID, model_identification,
     gravity, angles, bhvCriteria) = rep1
    cwd = os.getcwd()
    scriptFile_path = os.path.join(cwd, "Script_files")
    rep2 = get_elts_GEP_procedure(model_short_ID, base_path)
    txt_GEP, scriptFile_name, cP, oc, span, seeds_dirname = rep2
    if seeds_dirname[seeds_dirname.find("seeds"):] != "":
        seeds = seeds_dirname[seeds_dirname.find("seeds"):]
    else:
        seeds = seeds_dirname
    if bhvCriteria == "maxSpeed":
        bhvord = "bhvMSpeed"
    else:
        bhvord = "bhvDuration"
    model_completeidentification = modeldirname + "_" + model_identification
    model_completeidentification += "_" + bhvord + "_" + cP + "_" + oc
    newmodel_root = root_path + "/" + model_completeidentification
    seeds_path = newmodel_root + "/" + seeds_dirname
    completename = os.path.join(scriptFile_path, scriptFile_name)
    if not os.path.exists(scriptFile_path):
        os.makedirs(scriptFile_path)
    titre = "Graphics Builder"
    info = "Do you want Graphics?"
    rep3 = dialogWindow(titre, info, details="")
    other_constraints = optSet.other_constraints

    with open(completename, 'w') as f:
        s0 = "create_workDir" + "\t" + "Path=" + newmodel_root + "/" + "\t"
        s0 += "DirName=workDir_animatlab" + "\n"
        print(s0)
        f.write(s0)
        s1 = "copy_to_workDir" + "\t" + "PathSrc=" + seeds_path + "\n"
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
        s8 = "transfert_from_workDir" + "\t" + "PathDest="
        s8 += newmodel_root + "/" + "2_rGEP_" + model_short_ID + "_"
        s8 += seeds + "_" + "span" + str(span) + "\n"
        print(s8)
        f.write(s8)
        f.close()
    return newmodel_root, seeds_path


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
    list_elem = ["optimization", "GEP"]
    title = "¨Choose Process"
    typ = "process types"
    process = choose_one_element_in_list(title, list_elem, typ)
    if process == "optimization":
        rep3 = write_optim_scriptFile(optSet, root_path, modeldirname)
        newmodel_root, newbase_dirname = rep3
    elif process == "GEP" :
        rep4 = write_GEP_scriptFile(optSet, root_path, modeldirname)
        newmodel_root, seeds_path = rep4
        if not os.path.exists(seeds_path):
            os.makedirs(seeds_path)
            seed_dirname = os.path.split(seeds_path)[-1]
            print("Seed directory saved:", seeds_path)

    sys.exit()

    # Start Qt event loop unless running interaction mode or using pyside
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()
