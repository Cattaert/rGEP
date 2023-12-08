# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 09:38:33 2016
Modified on Fri Oct 07 17:47:25 2016
handle the directories necessary to run the animatLab model
@author: Daniel cattaert
Translated in Python 3.8 Jan 2023 (D. Cattaert)
"""
import os
import shutil


def copyFileDir(sourcedir, destdir, copy_dir=0):
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    for f in os.listdir(sourcedir):
        src = os.path.join(sourcedir, f)
        tgt = os.path.join(destdir, f)
        if os.path.isdir(src):
            if copy_dir:
                shutil.copytree(src, tgt)
        else:
            shutil.copy(src, tgt)


class FolderOrg():
    """

    """
    def __init__(self, animatlab_root="chemin",
                 python27_source_dir="C:/Program Files (x86)/AnimatLab V2/bin",
                 subdir="montest"):
        """

        """
        foldername = subdir
        # self.animatlab_rootFolder = os.path.join(animatlab_root, foldername)
        self.animatlab_rootFolder = animatlab_root + "/" + foldername + "/"
        self.python27_source_dir = python27_source_dir
        self.subdir = subdir
        self.animatlab_commonFiles_dir = ""
        self.animatlab_simFiles_dir = ""
        self.animatlab_result_dir = ""
        if self.subdir != "montest":
            self.affectDirectories()

    def affectDirectories(self):
        """

        """
        # comdir = os.path.join(self.animatlab_rootFolder, "FinalModel")
        comdir = self.animatlab_rootFolder + "FinalModel/"
        self.animatlab_commonFiles_dir = comdir
        # simdir = os.path.join(self.animatlab_rootFolder, "SimFiles")
        simdir = self.animatlab_rootFolder + "SimFiles/"
        self.animatlab_simFiles_dir = simdir
        # resdir = os.path.join(self.animatlab_rootFolder, "ResultFiles")
        resdir = self.animatlab_rootFolder + "ResultFiles/"
        self.animatlab_result_dir = resdir
        # if self.python27_source_dir == "":
        #  self.python27_source_dir = "C:/Program Files (x86)/AnimatLab V2/bin"
        if self.subdir != "montest":
            print(self.animatlab_rootFolder)
            print(self.animatlab_commonFiles_dir)
            print(self.animatlab_simFiles_dir)
            print(self.animatlab_result_dir)
            print(self.python27_source_dir)

        if not os.path.exists(self.animatlab_commonFiles_dir):
            os.makedirs(self.animatlab_commonFiles_dir)
            copyFileDir(self.animatlab_rootFolder,
                        self.animatlab_commonFiles_dir,
                        copy_dir=0)
        if not os.path.exists(self.animatlab_simFiles_dir):
            os.makedirs(self.animatlab_simFiles_dir)
        if not os.path.exists(self.animatlab_result_dir):
            os.makedirs(self.animatlab_result_dir)

        if not os.path.exists(self.animatlab_rootFolder + "AprojFiles/"):
            os.makedirs(self.animatlab_rootFolder + "AprojFiles/")
            copyFileDir(self.animatlab_rootFolder,
                        self.animatlab_rootFolder + "AprojFiles/",
                        copy_dir=0)


if __name__ == '__main__':
    monchemin = '//mac/Home/Documents/Labo/Scripts/AnimatLabV2/Human/test'
    masimul = 'ArmNS10_0-60'
    folders = FolderOrg(animatlab_root=monchemin, subdir=masimul)
    # folders.affectDirectories()
    animatlab_rootFolder = folders.animatlab_rootFolder
    animatlab_commonFiles_dir = folders.animatlab_commonFiles_dir
    animatlab_simFiles_dir = folders.animatlab_simFiles_dir
    animatlab_result_dir = folders.animatlab_result_dir
    python27_source_dir = folders.python27_source_dir

    print("animatlab_rootFolder =", animatlab_rootFolder)
    print("animatlab_commonFiles_dir =", animatlab_commonFiles_dir)
    print("animatlab_simFiles_dir =", animatlab_simFiles_dir)
    print("animatlab_result_dir =", animatlab_result_dir)
    print("python27_source_dir =", python27_source_dir)
