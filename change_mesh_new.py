# -*- coding: utf-8 -*-
"""
Created on Thu May 23 10:41:18 2024

@author: cattaert
"""
import os
import glob
import xml.etree.ElementTree as elementTree
import shutil

from pyqtgraph.Qt import QtCore
from pyqtgraph.Qt import QtGui
from pyqtgraph.Qt import QtWidgets

from PyQt5.QtWidgets import QInputDialog, QLineEdit

global verbose
verbose = 1


def showdialog(title="dialog", info="info", details="details"):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText(title)
    msg.setInformativeText(info)
    msg.setWindowTitle("MessageBox")
    msg.setDetailedText(details)
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
    msg.buttonClicked.connect(msgbtn)
    retval = msg.exec_()
    print("value of pressed message box button:", retval)
    return retval


def msgbtn(i):
    print("Button pressed is:", i.text())




class DialogBoxValues(QtWidgets.QMainWindow):
    def __init__(self):
        super(DialogBoxValues, self).__init__()
        
    def Boxdialog(self, titre="titre", info="info", details="details"):
        rep = showdialog(titre, info, details)
        self.rep = rep

    def getText(self, titre="titre", info="info", text="text"):
        self.text = text
        # print(self.text)
        text, okPressed = QInputDialog.getText(self, titre,
                                               info,
                                               QLineEdit.Normal,
                                               self.text)
        if okPressed:
            self.text = text
            self.close()

    def editText(self, titre, info, text):
        text, okPressed = QtWidgets.QInputDialog.getText(self, titre, info,
                                                         QtWidgets.QLineEdit.Normal,
                                                         text)
        if okPressed:
            textOK = text
            # self.close()
        else:
            textOK = None
        return textOK


def convertPath2Text(meshPath):
    txt = ""
    for i in range(len(meshPath)):
        if meshPath[i] == "/":
            txt += "\\"
        else:
            txt += meshPath[i]
    return txt


def changeMeshPath(aprojdirname, meshPathTxt):

    def changeDir(oldDir, meshPathTxt, meshDir):
        newPath = meshPathTxt[:meshPathTxt.find(meshDir)] + \
                 oldDir[oldDir.find(meshDir):]
        return newPath

    def findmesh(branch, sp, changeAproj):
        for elt in branch:
            print(sp + "elt", elt)
            try:
                meshpath = elt.find("MeshFile").text
                print(sp + meshpath)
                new = changeDir(meshpath, meshPathTxt, "MaleSkeleton")
                elt.find("MeshFile").text = new
                print(sp + new)
                if meshpath != new:
                    changeAproj = True
                    print("\t\t\t==========> Mesh path modified!!")
            except Exception as e:
                if (verbose > 1):
                    print(e)
                pass
            try:
                cb = list(elt.find("ChildBodies"))
                print(sp + "childbodies found")
                sp = sp + "\t"
                changeAproj = findmesh(cb, sp, changeAproj)
            except Exception as e:
                if (verbose > 1):
                    print(e)
                pass
                pass
        return changeAproj

    sp = ""
    changeAproj = False
    folder = aprojdirname
    if folder == '':
        projectFolder = os.getcwd()
    else:
        projectFolder = folder
    try:
        # # Check for AnimatLab project file
        aprojFilePathList = glob.glob(os.path.join(projectFolder, '*.aproj'))
        if len(aprojFilePathList) == 0:
            error = "No AnimatLab project file exists with extension " \
                    "*.aproj in folder:  %s" +\
                    "  Check AnimatLab project folder for consistency."
            raise GUI_AnimatLabError(error % projectFolder)
        elif len(aprojFilePathList) > 1:
            error = "Multiple AnimatLab aproj files exist with extension" \
                    " *.aproj in folder: %s" +\
                    "  Check AnimatLab project folder for consistency."
            raise GUI_AnimatLabError(error % projectFolder)
        aprojFileName = os.path.split(aprojFilePathList[0])[-1]
        aprojFilePath = os.path.join(projectFolder, aprojFileName)
        aprojName = os.path.splitext(os.path.split(aprojFilePath)[-1])[0]
        asimName = aprojName + ".asim"
        ProjectPath = projectFolder + "/" + aprojName
        projectPathTxt = convertPath2Text(ProjectPath)
    except GUI_AnimatLabError as e:
        print("Error initializing AnimatLab model object:\n\n %s" % e.value)
        raise

    # -----------  finds and modifies all MeshFile instances --------------
    aprojtree = elementTree.parse(aprojFilePath)
    root = aprojtree.getroot()
    path = "Simulation/Environment/Organisms"
    organisms = list(root.find(path))
    for organism in organisms:
        print(organism.find("Name").text)
        changeAproj = findmesh(organism, sp, changeAproj)

    # -------  finds and modifies all aproj/asim name/path instances ------
    if root.find("ProjectName").text != aprojName:
        changeAproj = True
        print("aprojName acutalized ->", aprojName)
        root.find("ProjectName").text = aprojName
    if root.find("SimulationFile").text != asimName:
        changeAproj = True
        print("asimName acutalized ->", asimName)
        root.find("SimulationFile").text = asimName
    if root.find("Simulation/ProjectPath").text != projectPathTxt:
        changeAproj = True
        print("ProjectPath acutalized ->", projectPathTxt)
        root.find("Simulation/ProjectPath").text = projectPathTxt
    """
    for child_of_root in root:
        print child_of_root.tag, child_of_root.attrib
        if child_of_root.tag == "ProjectName":
            print("\t", root.find("ProjectName").text)
        if child_of_root.tag == "Simulation":
            for child2 in child_of_root:
                print("\t", child2.tag)
                if child2.tag == "ProjectPath":
                    print("\t\t", child_of_root.find("ProjectPath").text)
    """
    return [aprojFilePath, aprojtree, changeAproj]


def readAnimatLabDir():
    filename = "animatlabSimDir.txt"
    try:
        f = open(filename, 'r')
        directory = f.readline()
        f.close()
    except Exception as e:
        if (verbose > 2):
            print(e)
        directory = ""
    return directory


def EditMeshPath(maleskeleton_path):
    winscr = DialogBoxValues()
    winscr.getText('Edit MaleSkeleton_path ', "  " + maleskeleton_path + "  ",
                   maleskeleton_path)
    maleskeleton_path = winscr.text
    winscr.close()
    return maleskeleton_path


class GUI_AnimatLabError(Exception):
    """
    This class manages errors thrown by the AnimatLabModel class.
    Right now, this class does nothing other than print an error message.
    Last updated:   December 28, 2015
    Modified by:    Bryce Chung
    """
    def __init__(self, value):
        """
        __init__(value)
        Set the value of the error message.
        """
        self.value = value

    def __str__(self):
        """
        __str__()
        Returns the error message.
        """
        return repr(self.value)


def changeMeshPathInFile(complete_name, meshPathTxt):

    def changeDir(oldDir, meshPathTxt, meshDir):
        newPath = meshPathTxt[:meshPathTxt.find(meshDir)] + \
                 oldDir[oldDir.find(meshDir):]
        return newPath

    def findmesh(branch, sp, change_meshpath):
        for elt in branch:
            print(sp + "elt", elt)
            try:
                meshpath = elt.find("MeshFile").text
                print(sp + meshpath)
                new = changeDir(meshpath, meshPathTxt, "MaleSkeleton")
                elt.find("MeshFile").text = new
                print(sp + new)
                if meshpath != new:
                    change_meshpath = True
                    print("\t\t\t==========> Mesh path modified!!")
            except Exception as e:
                if (verbose > 1):
                    print(e)
                pass
            try:
                cb = list(elt.find("ChildBodies"))
                print(sp + "childbodies found")
                sp = sp + "\t"
                change_meshpath = findmesh(cb, sp, change_meshpath)
            except Exception as e:
                if (verbose > 1):
                    print(e)
                pass
                pass
        return change_meshpath

    sp = ""
    ProjectPath = complete_name
    projectPathTxt = convertPath2Text(ProjectPath)
    change_meshpath = False
    # -----------  finds and modifies all MeshFile instances --------------
    if complete_name[-4:] == "asim":
        filetree = elementTree.parse(complete_name)
        root = filetree.getroot()
        path = "Environment/Organisms"
        organisms = list(root.find(path))

    elif complete_name[-5:] =="aproj":
        aprojName = os.path.splitext(os.path.split(complete_name)[-1])[0]
        asimName = aprojName + ".asim"
        filetree = elementTree.parse(complete_name)
        root = filetree.getroot()
        path = "Simulation/Environment/Organisms"
        organisms = list(root.find(path))
    for organism in organisms:
        print(organism.find("Name").text)
        change_meshpath = findmesh(organism, sp, change_meshpath)
    """
    # -------  finds and modifies all aproj/asim name/path instances ------
    if complete_name[-5:] =="aproj":
        # -------  finds and modifies all aproj/asim name/path instances ------
        if root.find("ProjectName").text != complete_name:
            change_meshpath = True
            print("aprojName acutalized ->", aprojName)
            root.find("ProjectName").text = aprojName
        if root.find("SimulationFile").text != asimName:
            change_meshpath = True
            print("asimName acutalized ->", asimName)
            root.find("SimulationFile").text = asimName
        if root.find("Simulation/ProjectPath").text != projectPathTxt:
            change_meshpath = True
            print("ProjectPath acutalized ->", projectPathTxt)
            root.find("Simulation/ProjectPath").text = projectPathTxt
    """
    return [complete_name, filetree, change_meshpath]


class mesh_change(QtWidgets.QWidget):
    def __init__(self):
        super(mesh_change, self).__init__()
        
        self.to_init()
        self.show()

    def to_init(self):
        self.select_aproj_btn = QtWidgets.QPushButton(
            'Select aproj/asim folder')
        self.select_mesh_folder_btn = QtWidgets.QPushButton(
            'Select mesh folder')
        self.change_meshpath_btn = QtWidgets.QPushButton(
            'change mesh path')
        self.modify_aproj_btn = QtWidgets.QPushButton(
            'actualize apoj files')
        self.modify_asim_btn = QtWidgets.QPushButton(
            'actualize asim files')
        self.btn_quit = QtWidgets.QPushButton('QUIT')
        buttonLayout1 = QtWidgets.QVBoxLayout()
        buttonLayout1.addWidget(self.select_aproj_btn)
        buttonLayout1.addWidget(self.select_mesh_folder_btn)
        buttonLayout1.addWidget(self.change_meshpath_btn)
        buttonLayout1.addWidget(self.modify_aproj_btn)
        buttonLayout1.addWidget(self.modify_asim_btn)
        buttonLayout1.addWidget(self.btn_quit)
        self.select_aproj_btn.clicked.connect(self.choose_folder)
        self.select_mesh_folder_btn.clicked.connect(self.choose_mesh_path)
        self.change_meshpath_btn.clicked.connect(self.change_mesh_path)
        self.modify_aproj_btn.clicked.connect(self.modify_aproj_files)
        self.modify_asim_btn.clicked.connect(self.modify_asim_files)
        self.btn_quit.clicked.connect(self.closeIt)
        self.setLayout(buttonLayout1)
        self.setWindowTitle("Mesh Path Actualization")
        

    def screen_loc(self, xshift=0, yshift=0):
        ag = QtWidgets.QDesktopWidget().availableGeometry()
        # sg = QtWidgets.QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = ag.width() - widget.width() - xshift
        y = ag.height() - widget.height() - yshift
        self.move(x, y)

    def choose_folder(self):
        # ===== Get the folder in which aproj or asim files will be modified ==
        self.previousanimatsimdir = readAnimatLabDir()
        self.dirname = QtWidgets.QFileDialog.\
            getExistingDirectory(self, "Pick a folder",
                                 self.previousanimatsimdir)
        if self.dirname:  # if user didn't pick a directory don't continue
            print("You chose: %s" % self.dirname)
            
            folder = self.dirname
            if folder == '':
                projectFolder = os.getcwd()
            else:
                projectFolder = folder
            try:
                # # Check for AnimatLab project file
                self.aprojFilePathList = glob.glob(os.path.join(projectFolder,
                                                                '*.aproj'))
                self.asimFilePathList = glob.glob(os.path.join(projectFolder,
                                                               '*.asim'))
                self.aprojFilePathList.sort()
                self.asimFilePathList.sort()
                if len(self.aprojFilePathList) == 0:
                    msg = "No AnimatLab project file exists with extension "\
                            "*.aproj in folder:  %s" 
                    print(msg)
                else:
                    msg = "{} AnimatLab aproj files exist with extension" \
                            " *.aproj in folder: %s"
                    print(msg.format(len(self.aprojFilePathList)))
                    
                if len(self.asimFilePathList) == 0:
                    msg = "No AnimatLab asim file exists with extension "\
                            "*.asim in folder:  %s"
                    print(msg)
                else:
                    msg = "{} AnimatLab aproj files exist with extension" \
                            " *.asim in folder: %s"
                    print(msg.format(len(self.asimFilePathList)))
            except GUI_AnimatLabError as e:
                print("Problem in chosen folder:\n\n %s" % e.value)
                raise
        return self.aprojFilePathList, self.asimFilePathList

    def choose_mesh_path(self):
        # ===== Get the new mesh folder path  ===============
        self.newMeshPath = QtWidgets.QFileDialog.\
            getExistingDirectory(self, "Mesh files Path",
                                 self.dirname)
        if self.newMeshPath:
            print("mesh directory: %s" % self.newMeshPath)
            self.meshPathTxt = convertPath2Text(self.newMeshPath)
        return self.meshPathTxt
    
    def change_mesh_path(self):
        def findmesh(branch, sp, change_meshpath):
            for elt in branch:
                print(sp + "elt", elt)
                try:
                    meshpath = elt.find("MeshFile").text
                    print(sp + meshpath)
                    self.lst_mesh.append(meshpath)
                    #new = changeDir(meshpath, meshPathTxt, "MaleSkeleton")
                    #elt.find("MeshFile").text = new
                    #print(sp + new)
                    #if meshpath != new:
                    #    change_meshpath = True
                    #    print("\t\t\t==========> Mesh path modified!!")
                except Exception as e:
                    if (verbose > 1):
                        print(e)
                    pass
                try:
                    cb = list(elt.find("ChildBodies"))
                    print(sp + "childbodies found")
                    sp = sp + "\t"
                    change_meshpath = findmesh(cb, sp, change_meshpath)
                except Exception as e:
                    if (verbose > 1):
                        print(e)
                    pass
                    pass
            return change_meshpath

        sp=''
        self.lst_mesh = []
        change_meshpath = False
        complete_aprojname = self.aprojFilePathList[0]
        aprojName = os.path.splitext(os.path.split(complete_aprojname)[-1])[0]
        asimName = aprojName + ".asim"
        filetree = elementTree.parse(complete_aprojname)
        root = filetree.getroot()
        path = "Simulation/Environment/Organisms"
        organisms = list(root.find(path))
        for organism in organisms:
            print(organism.find("Name").text)
            change_meshpath = findmesh(organism, sp, change_meshpath)
        print("List of mesh_path found:")
        for idx, mesh in enumerate(self.lst_mesh):
            print(self.lst_mesh[idx])
        maleSkeleton_path = mesh[:mesh.find("MaleSkeleton")] + "MaleSkeleton"
        #maleSkeleton_path = convertPath2Text(maleSkeleton_path)
        print("present MaleSkeleton path:")
        print(maleSkeleton_path)
        self.oldMaleSkeleton_path = maleSkeleton_path
        self.newMaleSkeleton_path = EditMeshPath(self.oldMaleSkeleton_path)
        self.meshPathTxt = convertPath2Text(self.newMaleSkeleton_path)

    def modify_aproj_files(self):
        for aprojname in self.aprojFilePathList:
            res = changeMeshPathInFile(aprojname, self.meshPathTxt)
            aprojFilePath = res[0]
            aprojtree = res[1]
            changeAproj = res[2]
            if changeAproj:
                aprojFileName = os.path.split(aprojFilePath)[-1]
                OriginalaprojSaveDir = os.path.join(self.dirname,
                                                    "AprojFilesOriginal")
                if not os.path.exists(OriginalaprojSaveDir):
                    os.makedirs(OriginalaprojSaveDir)
                ficName = os.path.splitext(aprojFileName)[0] + '*.aproj'
                ix = len(glob.glob(os.path.join(OriginalaprojSaveDir,
                                                ficName)))
                newname = os.path.splitext(aprojFileName)[0] +\
                    '-{0:d}.aproj'.format(ix)
                sourcefile = aprojFilePath
                destfile = os.path.join(OriginalaprojSaveDir, newname)
                shutil.copy(sourcefile, destfile)

                print('saving file: {}'.format(destfile))
                print('Actualizing file: {}'.format(aprojFilePath))
                aprojtree.write(aprojFilePath)

    def modify_asim_files(self):
        for asimname in self.asimFilePathList:
            res = changeMeshPathInFile(asimname, self.meshPathTxt)
            asimFilePath = res[0]
            asimtree = res[1]
            changeAsim = res[2]
            if changeAsim:
                asimFileName = os.path.split(asimFilePath)[-1]
                OriginalasimSaveDir = os.path.join(self.dirname,
                                                    "AsimFilesOriginal")
                if not os.path.exists(OriginalasimSaveDir):
                    os.makedirs(OriginalasimSaveDir)
                ficName = os.path.splitext(asimFileName)[0] + '*.asim'
                ix = len(glob.glob(os.path.join(OriginalasimSaveDir,
                                                ficName)))
                newname = os.path.splitext(asimFileName)[0] +\
                    '-{0:d}.asim'.format(ix)
                sourcefile = asimFilePath
                destfile = os.path.join(OriginalasimSaveDir, newname)
                shutil.copy(sourcefile, destfile)

                print('saving file: {}'.format(destfile))
                print('Actualizing file: {}'.format(asimFilePath))
                asimtree.write(asimFilePath)

    def closeIt(self):
        """
        doc string
        """
        self.close()

# ==========================================================================
#                                   MAIN
# ==========================================================================
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create("Windows"))
    ag = QtWidgets.QDesktopWidget().availableGeometry()
    sg = QtWidgets.QDesktopWidget().screenGeometry()
    win = mesh_change()
    win_height = win.geometry().height()
    win_width = win.geometry().width()
    win.screen_loc(xshift=10, yshift=sg.height()-win_height)

    win.GEP_GUI_win = None  # win.GEP_GUI_win is used when makeGEPMetrics
    #                           is called from GEP_GUI to hold the object name

    win.show()   # Show the form
    app.exec_()     # and execute the app