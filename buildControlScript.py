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
"""

import os
import tkinter, tkinter.filedialog

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


def get_elts_optim_procedure(model_short_ID, base_path):
    # ================= OPTIMIZATION to get seeds ============================
    base_root = os.path.split(base_path)[0]
    cP1 = 0
    cP2 = 0
    if base_path != "":
        base_root_name = os.path.split(base_root)[-1]
        prev_cP = base_root_name[base_root_name.find("cP"):]
        cP1 = int(prev_cP[2:prev_cP.find("_")])
        cP2 = int(prev_cP[prev_cP.find("_")+1:])
    list_elem = ["CMAes", "VSCD"]
    typ = "Optimizations tool"
    title = "Choose one Optimization method"
    optimiz = choose_one_element_in_list(title, list_elem, typ)
    print("optimization method:", optimiz)

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
        scriptFile_name += "_" + cP + ".txt"
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
        scriptFile_name += "_" + cP + ".txt"
        scriptFile_name = get_control_script_filename(scriptFile_name)
        s = "VSCD" + '\t' + "xCoactPenality1=" + str(coactP1) + '\t'
        s += "xCoactPenality2=" + str(coactP2) + '\t'
        s += "deltacoeff=" + str(dicValues["deltacoeff"]) +'\t'
        s += "nbsteps=" + str(int(dicValues["nbsteps"])) + '\t' 
        s += "nbepoch=" + str(int(dicValues["nbepoch"])) + '\n'
        txt_optimiz = s
    return optimiz, txt_optimiz, scriptFile_name, cP, span


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
    print("GEP procedure preparation")
    cP1 = 0
    cP2 = 0
    if base_path != "":
        base_root_name = os.path.split(base_root)[-1]
        prev_cP = base_root_name[base_root_name.find("cP"):]
        cP1 = int(prev_cP[2:prev_cP.find("_")])
        cP2 = int(prev_cP[prev_cP.find("_")+1:])
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
    scriptFile_name += "_" + cP + ".txt"
    scriptFile_name = get_control_script_filename(scriptFile_name)
    s = "GEPrand" + '\t' + "xCoactPenality1=" + str(coactP1) + '\t'
    s += "xCoactPenality2=" + str(coactP2) + '\t'
    s += "neighbours=1" + '\t' + "auto=1" + '\t' 
    s += "nbextend=" + str(int(dicValues["nbextend"])) + '\t'
    s += "nbfill=" + str(int(dicValues["nbfill"])) + '\n'
    txt_GEP = s

    return txt_GEP, scriptFile_name, cP, span, seeds_dirname


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
    model_identification = model_short_ID + "_WM1aDyn20_B150"
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
    optimiz, txt_optimiz, scriptFile_name, cP, span = rep2
    if bhvCriteria == "maxSpeed":
        bhvord = "bhvMSpeed"
    else:
        bhvord = "bhvDuration"
    model_completeidentification = modeldirname + "_" + model_identification
    model_completeidentification += "_" + bhvord + "_" + cP
    newmodel_root = root_path + "/" + model_completeidentification
    newbase_dirname = "0_" + model_short_ID + "_base"
    newbase_path = newmodel_root + "/" + newbase_dirname
    if os.path.exists(newbase_path):
        print(newbase_dirname, "already exists")
    else:
        os.makedirs(newbase_path)
        copyDirectory(model_path, newbase_path)
        print(newbase_path, "created")
        
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
            s5 = txt_optimiz
            print(s5)
            f.write(s5)
            s6 = "span=" + str(span) + "\n"
            print(s6)
            f.write(s6)
            s7 = "transfert_from_workDir" + "\t" + "PathDest="
            s7 += newmodel_root + "/" + "1_CMAes_" + model_short_ID + "_"
            s7 += "span" + str(span) + "_" + cP + "\n"
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
            s5 = txt_optimiz
            print(s5)
            f.write(s5)
            s6 = "span=" + str(span) + "\n"
            print(s6)
            f.write(s6)
            s7 = "transfert_from_workDir" + "\t" + "PathDest="
            s7 += newmodel_root + "/" + "1_VSCD_" + model_short_ID + "_"
            s7 += "span" + str(span) + "_" + cP + "\n"
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
    txt_GEP, scriptFile_name, cP, span, seeds_dirname = rep2
    if seeds_dirname[seeds_dirname.find("seeds"):] != "":
        seeds = seeds_dirname[seeds_dirname.find("seeds"):]
    else:
        seeds = seeds_dirname
    if bhvCriteria == "maxSpeed":
        bhvord = "bhvMSpeed"
    else:
        bhvord = "bhvDuration"
    model_completeidentification = modeldirname + "_" + model_identification
    model_completeidentification += "_" + bhvord + "_" + cP
    newmodel_root = root_path + "/" + model_completeidentification
    seeds_path = newmodel_root + "/" + seeds_dirname
    completename = os.path.join(scriptFile_path, scriptFile_name)
    if not os.path.exists(scriptFile_path):
        os.makedirs(scriptFile_path)
    titre = "Graphics Builder"
    info = "Do you want Graphics?"
    rep3 = dialogWindow(titre, info, details="")

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
