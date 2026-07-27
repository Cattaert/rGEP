# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 08:16:58 2026

@author: dcatt
"""


import tkinter, tkinter.filedialog
import sys
import os
from os import listdir
from os.path import isfile, join
import shutil
import copy

from sklearn.cluster import DBSCAN

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from pyqtgraph.Qt import QtWidgets


import numpy as np
import pandas as pd

from optimization import copyFile
from optimization import copyDirectory
from optimization import copyFileDir_ext
from optimization import copyFileWithExt
from optimization import cleanChartsFromNewResultDir
from optimization import calculateMvtdurFromMax_Speed
from optimization import getInfoComputer
from optimization import readGravityfromAsim

from GEP_GUI import MaFenetre, initAnimatLab


def find_seed_without_family(data_csv):
    """
    data_csv est le fichier doit au moins contenir les jeux de paramètres
    ainsi que le rang de chaque mouvements 
    """
    ### créer la colonne cluster et met toutes les valeurs à -1 par défaut 
    if "cluster" not in data_csv.columns:
        data_csv["cluster"] = -1  

    ### ne pas prendre en compte les mouvements appartenant au cluster -2,
    ### protection en cas d'anomalies (mouvements extrêmement instable)
    csv_temp = data_csv[data_csv["cluster"] != -2]   
    

    columns_to_keep = []            ### DBScan uniquement sur les paramètres 
    for col in csv_temp.columns:       
        if ".SynAmp" in col or ".CurrentOn" in col:   
            columns_to_keep.append(col)
    csv_temp_features = csv_temp[columns_to_keep]  


    """
    DBSCAN sur tableau nettoyé 
    """
    ### parametres a modifier potentiellement, pour un span de 0.1, la distance
    ### euclidienne max pour 50 paramètres est de 0.00707 (d'où eps = 0.007)
    db = DBSCAN(eps=0.007, min_samples=30) 
    labels = db.fit_predict(csv_temp_features)
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = np.sum(labels == -1)  ### les outliers = graine sans famille


    print(f"\n {n_clusters} clusters trouvés, {n_noise} points bruit (-1)")
    data_csv.loc[csv_temp.index, "cluster"] = labels
    for index, row in data_csv.iterrows():
        if row["cluster"]==-1:
            return row["rgserie"]
    # retourne le rang de la graine sur laquelle il faut faire tourner un GEP
    
    print("No more GEP to run, every points belong to a family")
    return 0 ### Fin de la procédure quand find_seed_without_family retourne 0 


def get_folder_name(base_dir, typ="_seeds"):
    """
    Opens a window asking for text (filename) and returns folder name.
    """
    
    # listDir = [name for name in os.listdir(rootdir)
    #            if os.path.isdir(os.path.join(rootdir, name))]
    # listDir.sort()
    
    base_dir_name = os.path.split(base_dir)[-1]
    rootName = base_dir_name[:-5]
    rootName = rootName + typ
    
    sim_model_dir = os.path.split(base_dir)[0]
    listDirGEPfromTyp = [name for name in os.listdir(sim_model_dir)
                           if (os.path.isdir(os.path.join(sim_model_dir, name))
                               and name[0:len(rootName)] == rootName)]
    if len(listDirGEPfromTyp) < 10:
        newGEPDir_fromTyp = rootName+'0'+str(len(listDirGEPfromTyp))
    else:
        newGEPDir_fromTyp = rootName + str(len(listDirGEPfromTyp))

    return newGEPDir_fromTyp


def build_bvs_and_pairs_from_GEPdata(GEPdata_dir):
    # =========================================================================
    #       Builds bhvs from GEPdata00bhv.txt
    # =========================================================================
    bhv_names = win.bhv_names
    bhv_col = copy.deepcopy(bhv_names)
    bhv_col.append("rg")
    GEPdata00parFile = os.path.join(GEPdata_dir, "GEPdata00.txt")
    GEPdata00bhvFile = os.path.join(GEPdata_dir, "GEPdata00bhv.txt")
    df_bhvs = pd.read_csv(GEPdata00bhvFile, sep="\t", header=None,
                         names=bhv_col)
    df_bhvrem = copy.deepcopy(df_bhvs)
    # df_bhvremain = df_validbhvs[df_validbhvs["rg"]==rg].iloc[:, :-1]
    # df_bhvremain = df_validbhvs[df_validbhvs["rg"]==rg]
    win.df_bhvremain = df_bhvrem.set_index("rg", drop=False)
    
    df_behavs = win.df_bhvremain.iloc[:, :-1]
    behavs = np.array(df_behavs)
    optSet.behavs = behavs
    
    # =========================================================================
    #       Builds pairs from GEPdata00.txt
    # =========================================================================
    par_names = win.xparName
    par_col = copy.deepcopy(par_names)
    par_col.append("mse")
    par_col.append("coactpen")
    par_col.append("rg")
    df_pars = pd.read_csv(GEPdata00parFile, sep="\t", header=None,
                         names=par_col)
    
    df_parrem = copy.deepcopy(df_pars)
    
    df_parremain = df_parrem.iloc[:, :-1]
    """
    df_pairs = copy.deepcopy(data_csv).iloc[:, 1:-2]
    df_pair = df_pairs[df_pairs["rgserie"]==rg].iloc[:, :-1]
    """
    pairs = np.array(df_parremain)
    optSet.pairs = pairs
    win.optSet = optSet
    

def build_seed_dir_from_param_rg(rg):
    # =========================================================================
    #       run the seed parameters and savec the single seed dir 
    # =========================================================================
    sim_model_dir = os.path.split(base_dir)[0]
    newGEPDir_fromTyp = get_folder_name(base_dir, typ="_seeds")
    newseedFolder = sim_model_dir + "/" + newGEPDir_fromTyp
    
    destdir = newseedFolder
    dest_AprojFiles = destdir + "/AprojFiles"
    if not os.path.exists(dest_AprojFiles):
        os.makedirs(dest_AprojFiles)
    list_ext = [".aproj", ".asim", ".aform"]
    copyFileDir_ext(animatsimdir, dest_AprojFiles, list_ext,copy_dir=0)    
    win.newDestFolder = newseedFolder     
    win.rg_bhv_selected = [rg]
    # =================================================================
    win.run_list_selected_param(saveAproj=True, saveAsim=True)
    # =================================================================
    # ================== make graphs for each selected bhv ============
    win.select_df_bhvremain = win.df_bhvremain
    dest_ResultFiles = destdir + "/ResultFiles"
    if not os.path.exists(dest_ResultFiles):
        os.makedirs(dest_ResultFiles)
    NewResultFilePath = dest_ResultFiles
    src = os.path.join(animatsimdir, "ResultFiles")
    dst = os.path.join(destdir, "ResultFiles")
    # copyFile("paramOpt.pkl", src, dst)
    copyFile("template.txt", src, dst)
    copyFileWithExt(src, dst, ".pkl")
    copyFileWithExt(src, dst, ".txt")
    # templateFileName = resultdir + "/template.txt"
    cleanChartsFromNewResultDir(optSet, NewResultFilePath)

    saveGraphs = True
    win.seeds_selected = [rg]
    win.optSet.spanStim = 5
    win.optSet.spanSyn = 5            
    dest_GePdata = destdir + "/GEPdata"
    if not os.path.exists(dest_GePdata):
        os.makedirs(dest_GePdata)
    win.saves_newGEPdata(seedDirCreate=False,
                         saveGrFromChart=saveGraphs)
    
    dest_SimFiles = destdir + "/SimFiles"
    if not os.path.exists(dest_SimFiles):
        os.makedirs(dest_SimFiles)
    
    return newseedFolder
    

def get_first_seed_from_csv(data_csv):
    rg = data_csv["rgserie"][0]
    newseedFolder = build_seed_dir_from_param_rg(rg)
    return newseedFolder
   

def RunGEPfromSeed(seed_dir):
    animatsimdir = sim_model_dir + "/workDir_animatlab"
    if os.path.exists(animatsimdir):
        shutil.rmtree(animatsimdir)
    copyDirectory(seed_dir, animatsimdir)
    
    win.valueCoactPen1.setText(str(100))
    win.valueCoactPen2.setText(str(100))
    optSet.xCoactPenality1 = 100
    optSet.xCoactPenality2 = 100   # for old scripts
    print("xCoactPenality1:", 100)
    print("xCoactPenality2:", 100)
    
    neighbours = 1
    win.valueLine2a.setText(str(neighbours))
    print("neighbours:", neighbours)
    win.nbGEPextend = 200
    win.value_nbExt.setText(str(win.nbGEPextend))
    print("nbextend:", win.nbGEPextend)
    win.nbGEPfill = 20
    win.value_nbFill.setText(str(win.nbGEPfill))
    print("nbfill:", win.nbGEPfill)
    win.GEPauto = 1
    if win.GEPauto == 1:
        win.chkBx_autoGEP.setChecked(True)
    errThr = 1.
    win.editValueErrThr.setText(str(errThr))
    print("errThr:", errThr)
    win.errThr = errThr
    coactThr = 0.01
    win.editValueCoactThr.setText(str(coactThr))
    print("coactThr:", coactThr)
    win.coactThr = coactThr
    
    fouch_comp = 0.1
    win.glob_span = fouch_comp
    print("span=", fouch_comp)
    win.glob_span_val.setText(str(fouch_comp))
    win.chkBx_glob_span.setCheckState(True)
    # win.listDicspanVal[0][win.xparName[0]] = float(span)
    win.span_setup()
    optSet.spanStim = float(fouch_comp)
    optSet.spanSyn = float(fouch_comp)
    GEPdata_name = "GEPdata00.par"
    win.mydir = os.path.join(optSet.folders.animatlab_rootFolder, "GEPdata")
    fname = os.path.join(win.mydir, GEPdata_name)
    win.read_pairs(fname)
    win.do_GEP_rand() 
    
    
def save_df_to_csv(df, pathGEP, file_name, typ=None):
    completeName = os.path.join(pathGEP, file_name + '.csv')
    df.to_csv(completeName, sep=",")

    
def save_newGEP_csv(win):
    if win.bhv_names[win.behav_col[0]] == 'endangle':
        nomx = "amp"
        win.bhv_xmin = min(win.df_bhvremain["endangle"])
        win.bhv_xmax = max(win.df_bhvremain["endangle"])
    if win.bhv_names[win.behav_col[1]] == 'dur_mvt2':
        nomy = "dur"
        win.bhv_ymin = min(win.df_bhvremain["dur_mvt2"])
        win.bhv_ymax = max(win.df_bhvremain["dur_mvt2"])
    if win.bhv_names[win.behav_col[1]] in ('max_speed', 'speed_mvt2'):
        nomy = "vit"
        win.bhv_ymin = min(win.df_bhvremain["max_speed"])
        win.bhv_ymax = max(win.df_bhvremain["max_speed"])
    str_bhvSet = "{}{:.2f}-{:.2f}_{}{:.2f}-{:.2f}".format(nomx, win.bhv_xmin,
                                                          win.bhv_xmax,
                                                          nomy, win.bhv_ymin,
                                                          win.bhv_ymax)
    graph_path = win.animatsimdir + "/graphs"
    if not os.path.exists(graph_path):
        os.makedirs(graph_path)
    NbSelectedBhv = len(win.df_parremain)
    file_name = "{}_bhv{}".format(str_bhvSet, NbSelectedBhv)
    save_df_to_csv(win.df_bhvremain, graph_path,
                   file_name, typ='bhv')
    file_name = "{}_par{}".format(str_bhvSet, NbSelectedBhv)
    save_df_to_csv(win.df_parremain, graph_path,
                   file_name, typ='par')


def prepareTransfer_GEP(win, seed_dir):
    seed_name = os.path.split(seed_dir)[-1]
    seeds = seed_name.split("_", 1)[1]
    Th = "errT{}coT{}".format(str(win.errThr), str(win.coactThr))
    destdir = sim_model_dir + "/" + "2_rGEP_" + seeds + "_"
    destdir += "span" + str(win.glob_span) + Th
    return destdir
    

def get_ang_txt(win):
    optSet = win.optSet
    angle1 = win.optSet.angle1
    angle2 = win.optSet.angle2
    if win.bhv_names[win.behav_col[1]] == "dur_mvt2":
        mvtdur = win.optSet.endMvt2 -win.optSet.startMvt2
        ang_txt = 'ang%d-%d_dur%d' % (angle1, angle2, int(mvtdur*1000))
    elif win.bhv_names[win.behav_col[1]] == "max_speed":
        max_speed = 138.
        amplitude = angle2 - angle1
        mvtdur = calculateMvtdurFromMax_Speed(optSet, max_speed,
                                              amplitude)
        ang_txt = 'ang%d-%d_dur%d' % (angle1, angle2, int(mvtdur*1000))
        print(ang_txt)
    return ang_txt
    

def transfertData(animatsimdir, savedatadir, idx, ang_txt='0', const='0',
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
        destdir = os.path.join(savedatadir, ang_txt, const)
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

    

    
    
# ==========================================================================
#                                   MAIN
# ==========================================================================
if __name__ == '__main__':
    global folders, model, projMan, aprojFicName, optSet, animatsimdir
    from mainOpt import readAnimatLabDir
    animatsimdir = readAnimatLabDir()
    animatLabV2ProgDir, nb_procs = getInfoComputer()
    
    
    root_path = animatsimdir
    root = tkinter.Tk()
    root.withdraw()
    base_dir = tkinter.filedialog.askdirectory(parent=root,
                                               initialdir=root_path,
                                               title='Select base directory')
    root.destroy()
    
    
    base_path = base_dir
    base_name = os.path.split(base_path)[-1]
    txt1 = base_name[base_name.find("_")+1:]
    model_short_ID = txt1[:txt1.find("_")]
    
    sim_model_dir = os.path.split(base_dir)[0]
    
    root_path = sim_model_dir
    root = tkinter.Tk()
    root.withdraw()
    all_seeds_csv = tkinter.filedialog.askopenfilename(parent=root,
                                               initialdir=root_path,
                                               title='Select seeds _par csv',
                                               filetypes=(("CSV", "*.csv"),
                                                          ("Tous les fichiers", "*.*")))
    root.destroy()
    graphs_dir = os.path.split(all_seeds_csv)[0]
    root_dir = os.path.split(graphs_dir)[0]
    GEPdata_dir= root_dir + "/GEPdata"
    
    animatsimdir = sim_model_dir + "/workDir_animatlab"
    if os.path.exists(animatsimdir):
        shutil.rmtree(animatsimdir)
    
    data_csv = pd.read_csv(all_seeds_csv, sep=',', decimal='.')
    copyDirectory(root_dir, animatsimdir)
    
    origin_animatsimdir = animatsimdir
    res = initAnimatLab(animatsimdir, animatLabV2ProgDir)


    OK = res[0]
    if OK:
        # folders = res[1]
        model = res[2]
        # projMan = res[3]
        aprojFicName = res[4]
        optSet = res[5]
        try:
            optSet.srcdir = root_dir
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
        win.mydir = animatsimdir + "/GEPdata"
        win.save_paramNames_bhvNames()
    
        gravity = readGravityfromAsim(model)
        optSet.gravity = gravity
        win.editValueGravity.setText(str(gravity))
        build_bvs_and_pairs_from_GEPdata(GEPdata_dir)
        
        cluster = find_seed_without_family(data_csv)
        
        # =====================================================================
        seed_dir = get_first_seed_from_csv(data_csv)
        # =====================================================================
        RunGEPfromSeed(seed_dir)
        save_newGEP_csv(win)
        
        pathSrc = win.animatsimdir
        pathDest = prepareTransfer_GEP(win, seed_dir)
        ang_txt = get_ang_txt(win)
        const=""
        transfertData(pathSrc, pathDest, 0, ang_txt=ang_txt, const=const)
        
# TODO : continuer le script : data_csv= concatenate(data_csv, data_newGEP_csv) ;
        # cluster = find_seed_without_family(data_csv) ... etc.
        
        """
        win.closeWindows()
        sys.exit()
        """
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtWidgets.QApplication.instance().exec_()
    
    
    
    
    