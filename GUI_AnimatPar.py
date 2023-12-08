# -*- coding: utf-8 -*-
"""
Defines the graphic window elements used in GUI_AnimatLabOptimization.py
Translated in Python 3.8 Jan 2023 (D. Cattaert)
Modified February 17, 2023 (D. Cattaert):
    This script was modified to work with PyQtgraph 5
    It replaces the two preceeding python scripts:
        GUI_AnimatLabOptimization.py and design.py
Modified February 24, 2023 (D. Cattaert):
    New procedures:
        readColIntervalFromAform(chartPathName)
        changeCollIntervalAform(chartPathName)
        readColIntervalFromAsim(asimPathName)
        changeCollIntervalAsim(asimPathName)
    These procedures are called at when browse_folder() method is called. It
    allows to acertain the collectInterval is OK (0.01) in asim and aform fles.
Modified March 02, 2023 (D. Cattaert):
    New procedure check_mesh() checks that the asim file was built frm the 
    aproj file (i.e. same meshFiles). If not it aborts the script and tells
    what to do.
"""
# Form implementation generated from reading ui file 'design7.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

# import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from pyqtgraph.Qt import QtGui
from pyqtgraph.Qt import QtWidgets

from functools import partial
import sys  # We need sys so that we can pass argv to QApplication
import os  # For listing directory methods
import pickle

from DialogChoose_in_List import ChooseInList

import class_animatLabModel as AnimatLabModel
import class_projectManager as ProjectManager
import class_animatLabSimulationRunner as AnimatLabSimRunner
from animatlabOptimSetting import OptimizeSimSettings
import shutil
import glob
import xml.etree.ElementTree as elementTree
from FoldersArm import FolderOrg

from optimization import copyFileDir
# from optimization import getInfoComputer
from optimization import showdialog

# from SaveInfoComputer import SetComputerInfo
# folders = FolderOrg()
global verbose
verbose = 1

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context,
                                            text,
                                            disambig,
                                            _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)


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


def readAnimatLabV2ProgDir():
    filename = "animatlabV2ProgDir.txt"
    try:
        fic = open(filename, 'r')
        directory = fic.readline()
        fic.close()
    except Exception as e:
        if (verbose > 1):
            print(e)
        directory = ""
    # print "First instance: Root directory will be created from GUI"
    return directory


def readAnimatLabSimDir():
    filename = "animatlabSimDir.txt"
    try:
        fic = open(filename, 'r')
        directory = fic.readline()
        fic.close()
    except Exception as e:
        if (verbose > 1):
            print(e)
        directory = ""
    # print "First instance: Root directory will be created from GUI"
    return directory


def chooseChart(optSet):
    listDicItems = [{"selectedChart": [optSet.chartName[0]]}]
    titleText = "Choose a chart"
    rep = ChooseInList.listTransmit(parent=None,
                                    graphNo=0,
                                    listChoix=["selectedChart"],
                                    items=optSet.chartName,
                                    listDicItems=listDicItems,
                                    onePerCol=[1],
                                    colNames=["chart"],
                                    typ="chk",
                                    titleText=titleText)
    """
    rep = GetList.listTransmit(parent=None,
                               listChoix=["selectedChart"],
                               items=optSet.chartName,
                               dicItems=dicItems,
                               titleText="Choose the chart for measurements")
    """
    return rep[0]


def readColIntervalFromAform(chartPathName):
    print(os.path.split(chartPathName)[-1])
    aformtree = elementTree.parse(chartPathName)
    root = aformtree.getroot()
    el0 = root.find('Form/AutoCollectInterval')
    print("AutoCollectInterval:", el0.text)

    el = root.find('Form/CollectDataInterval')
    va = el.get("Value")
    sc = el.get("Scale")
    ac = el.get("Actual")
    print("Value:", va, "\tScale:", sc, "\tActual:", ac)
    return ac


def changeCollIntervalAform(chartPathName):
    print()
    print("changes CollectDataInterval")
    print(os.path.split(chartPathName)[-1])
    aformtree = elementTree.parse(chartPathName)
    root = aformtree.getroot()
    el0 = root.find('Form/AutoCollectInterval')
    newAutocoll = "False"
    print("AutoCollectInterval:", newAutocoll)
    el0.text = newAutocoll

    el = root.find('Form/CollectDataInterval')
    newValue = "10"
    sc = el.get("Scale")
    newActual = "0.01"
    el.set("Value", str(newValue))
    el.set("Scale", sc)
    el.set("Actual", str(newActual))
    print("Value:", newValue, "\tScale:", sc, "\tActual:", newActual)
    aformtree.write(chartPathName)
    print()


def readColIntervalFromAsim(asimPathName):
    asimtree = elementTree.parse(asimPathName)
    root = asimtree.getroot()
    dataCharts = root.find('DataCharts')
    OK = True
    for chart in dataCharts :
        # print(list(chart))
        chartName = chart.find("Name").text
        collectInterval = chart.find("CollectInterval").text
        print(chartName, "->", "collectInterval:", collectInterval)
        if collectInterval != '0.01':
            OK = False
    return OK


def changeCollIntervalAsim(asimPathName):
    print()
    print("Changes CollectInterval")
    asimtree = elementTree.parse(asimPathName)
    root = asimtree.getroot()
    dataCharts = root.find('DataCharts')
    for chart in dataCharts :
        # print(list(chart))
        chartName = chart.find("Name").text
        # print(chartName, end=" ")
        chart.find("CollectInterval").text = "0.01"
        collectInterval = chart.find("CollectInterval").text
        print(chartName, "->", "collectInterval:", collectInterval)
    asimtree.write(asimPathName)
    print()


def dialogWindow(titre, info, details=""):
    rep = showdialog(titre, info, details)
    # print(rep)
    if rep == 1024:
        OK = True
    else:
        OK = False
    return OK


def check_mesh(aprojFilePath, asimFilePath):
    """
    Procedure that reads aproj File and Asim File and compare 1st mesh folder
    """

    """
    modelPath = '//mac/Home/Documents/Labo/Scripts/AnimatLabV2/Human/Daniel'
    modelPath += '/ArmNS25NG(Mac)/NS25NG_14'
    aprojFilePath = modelPath + '/ArmNS25_14.aproj'
    asimFilePath = modelPath + '/ArmNS25_14_Standalone.asim'
    """

    def findmesh(branch, sp, dic):
        for elt in branch:
            # print(sp + "elt", elt)
            try:
                meshpath = elt.find("MeshFile").text
                eltname = elt.find('Name').text
                print(sp + eltname)
                print(sp + meshpath)
                dic[eltname] = meshpath.replace("\\", "/")
            except Exception as e:
                if (verbose > 1):
                    print(e)
                pass
            try:
                cb = list(elt.find("ChildBodies"))
                print(sp + "childbodies found")
                sp = sp + "\t"
                findmesh(cb, sp, dic)
            except Exception as e:
                if (verbose > 1):
                    print(e)

    print("Analysis of aproj file")
    aprojdicmesh = {}
    sp = ""
    aprojtree = elementTree.parse(aprojFilePath)
    aprojroot = aprojtree.getroot()
    aprojpath = "Simulation/Environment/Organisms"
    aprojorganisms = list(aprojroot.find(aprojpath))
    for aprojorganism in aprojorganisms:
        print(aprojorganism.find("Name").text)
        findmesh(aprojorganism, sp, aprojdicmesh)
    print()

    print("Analysis of asim file")
    asimdicmesh = {}
    sp = ""
    asimtree = elementTree.parse(asimFilePath)
    asimroot = asimtree.getroot()
    asimpath = "Environment/Organisms"
    asimorganisms = list(asimroot.find(asimpath))
    for asimorganism in asimorganisms:
        print(asimorganism.find("Name").text)
        findmesh(asimorganism, sp, asimdicmesh)


    for name in list(aprojdicmesh.keys()):
        print(aprojdicmesh[name])
        print(asimdicmesh[name])
        if aprojdicmesh[name] != asimdicmesh[name]:
            print("PROBLEM")
            print("The asim File was not built from the aproj file")
            print("Please, run AnimatLab.exe to export standlone asim Fle")
            titre ="PROBLEM WITH ASIM FILE"
            info = "Run again AnimatLab.exe to export stanalone asim File"
            dialogWindow(titre, info, details="")
            MainWindow.close()
            sys.exit()
        print()


class GetList(QtWidgets.QDialog):
    """
    GetList creates a window with a list of QPushButtons and associatd QLabels
    The QPushButtons are defined by listChoix and the list of QLabels by items.
    A QGridLayout is used to dispose QPushButtons and QLabels.
    In the QLabel, a default element of the items list is displayed
    A dictionary is used to set the association of listChoix elements with an
    element of the items list selected by the user
    In call to the class procedure is made by the included function
    listTransmit. A dictionary (dicItems) is sent with the actual listChoix.
    WHen the user clicks on one of the QPushButton the list of items is
    presented and the user select one item.
    If the default item is OK, then closing the window confirms the default
    items for each QPushButton (presneting listChoix elements)
    A newdicItems is then returned.
    """
    MESSAGE = "<p>Message boxes have a caption, a text, and up to three " \
        "buttons, each with standard or custom texts.</p>" \
        "<p>Click a button to close the message box. Pressing the Esc " \
        "button will activate the detected escape button (if any).</p>"

    def __init__(self, parent=None, listChoix=('choix1', 'choix2'),
                 items=("Spring", "Summer", "Fall", "Winter"),
                 dicItems={'choix1': "Spring", 'choix2': "Fall"},
                 titleText="Choose a season"):
        super(GetList, self).__init__(parent)

        layout = QtWidgets.QGridLayout()
        layout.setColumnStretch(1, 1)
        layout.setColumnMinimumWidth(1, 250)

        # self.parent=parent
        self.items = items
        self.dialogText = []
        self.itemLabel = []
        self.itemButton = []
        self.itemList = []
        self.listChoix = listChoix
        self.dicItems = dicItems
        self.newdicItems = {}
        if len(dicItems) < len(listChoix):
            print("GetList listChoix: {}    dicItems: {}".format(listChoix,
                                                                 dicItems))
            for i in (len(dicItems)+1, len(listChoix)):  # complete the dic
                self.dicItems[listChoix[i]] = i
        for itm in range(len(listChoix)):
            self.dialogText.append(str(listChoix[itm]))
        for itm in range(len(listChoix)):
            self.errorMessageDialog = QtWidgets.QErrorMessage(self)
            frameStyle = QtWidgets.QFrame.Sunken | QtWidgets.QFrame.Panel
            choix = listChoix[itm]
            self.itemLabel.append(QtWidgets.QLabel(self.dicItems[choix]))
            self.itemLabel[itm].setFrameStyle(frameStyle)
            self.itemButton.append(QtWidgets.QPushButton(self.dialogText[itm]))

            self.itemButton[itm].clicked.connect(partial(self.setItem, itm))
            layout.addWidget(self.itemButton[itm], 1+itm, 0)
            layout.addWidget(self.itemLabel[itm], 1+itm, 1)
        self.setLayout(layout)
        self.setWindowTitle(titleText)

    def setItem(self, rg):
        """
        Function called by the "clicked.connect" event when a QPushButton is
        clicked. This function calls a QInputDIalog procedure to present the
        list of items and select one. It actualizes the newdicItems dictionary
        (self.newdicItems) the the key corresponding to the QPushButton that
        was activated (presenting an element of listChoix). The row of the
        activatd QPushButton is givent in the variable rg.
        """
        print("rg: ", rg)
        diaText = self.dialogText[rg]
        item, ok = QtWidgets.QInputDialog.getItem(self,
                                              diaText,
                                              diaText,
                                              self.items,
                                              0,
                                              False)
        if ok and item:
            self.itemLabel[rg].setText(item)
            self.itemList.append(item)
        print(self.itemList)
        self.newdicItems = self.dicItems
        self.newdicItems[str(self.listChoix[rg])] = item
        print("   newdicItems:", self.newdicItems)

    def listtransmit_info(self):
        """
        Function used to transmit the self.newdicItems to "listTransmit"
        """
        # return self.itemList
        return self.newdicItems

    @staticmethod
    def listTransmit(parent=None,
                     listChoix=('choix1', 'choix2'),
                     items=("Spring", "Summer", "Fall", "Winter"),
                     dicItems={'choix1': "Spring", 'choix2': "Fall"},
                     titleText="Choose a season:"):
        """
        Entry of the GetList class application. It works as a staticmethod
        and returns newdicItems
        """

        dialog = GetList(parent,
                         listChoix,
                         items,
                         dicItems,
                         titleText)
        dialog.exec_()  # si on veut bloquant
        # item_list = dialog.listtransmit_info()
        newdicItems = dialog.listtransmit_info()

        if newdicItems == {}:     # if we did not click any item...
            newdicItems = dicItems
            print("no click.... keep default")
            # print('classe enfant unchanged: {}'.format(newdicItems))
        if len(newdicItems) < len(listChoix):       # we removed one key...
            for mnName in listChoix:
                if mnName not in listChoix:
                    del newdicItems[mnName]
            print('classe enfant changed -: {}'.format(newdicItems))

        else:                                       # a new key was added
            print('classe enfant changed +: {}'.format(newdicItems))
        # return item_list
        return newdicItems


def applyType(paramType, strTab):
    """
    doc string
    """
    tab = []
    # chain=0
    for chain in range(len(strTab)):
        # print(strTab[chain])
        if paramType[chain] is int:
            tab.append(int(strTab[chain]))
        elif paramType[chain] is float:
            tab.append(float(strTab[chain]))
        elif paramType[chain] is list:
            if strTab[chain][0] == "[":
                chaine = strTab[chain][1:-1]
                # print(chaine)
                if chaine == '':
                    tab.append([])
                else:
                    listStr = chaine.split(",")
                    try:
                        listVal = []
                        for rang in range(len(listStr)):
                            val = int(listStr[rang])
                            listVal.append(val)
                        tab.append(listVal)
                    except Exception as e:
                        if (verbose > 1):
                            print(e)
                        listVal = []
                        for rang in range(len(listStr)):
                            # print(listStr[rang])
                            if listStr[rang][0] == " ":
                                listStr[rang] = listStr[rang][1:]
                                # print(listStr[rang])
                            par = listStr[rang]
                            if par[0] == "'":
                                par2 = par[1:-1]
                                # print(par2)
                                # print()
                                listVal.append(par2)
                        tab.append(listVal)
        # print(tab)
        # chain +=1
        
    return tab


def saveParams(paramFicName, optSet):
    """
    doc string
    """
    with open(paramFicName, 'wb') as output:
        pickle.dump(optSet.paramVSCDName, output)
        pickle.dump(optSet.paramVSCDValue, output)
        pickle.dump(optSet.paramVSCDType, output)
        pickle.dump(optSet.paramVSCDCoul, output)
        pickle.dump(optSet.paramMarquezName, output)
        pickle.dump(optSet.paramMarquezValue, output)
        pickle.dump(optSet.paramMarquezType, output)
        pickle.dump(optSet.paramMarquezCoul, output)
    print("&&&&&& File saved :", paramFicName, "  &&&&&&")


def saveAnimatLabSimDir(directory):
    """
    doc string
    """
    filename = "animatlabSimDir.txt"
    fic = open(filename, 'w')
    fic.write(directory)
    fic.close()


def saveAnimatLabV2ProgDir(directory):
    """
    doc string
    """
    filename = "animatlabV2ProgDir.txt"
    fic = open(filename, 'w')
    fic.write(directory)
    fic.close()


def saveInfoComputer(directory, nb_processors):
    """
    doc string
    """
    filename = "infos_computer.txt"
    fic = open(filename, 'w')
    fic.write(directory)
    fic.write("nb_processors=%s" % nb_processors)
    fic.close()


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


class Ui_MainWindow(QtWidgets.QMainWindow):
    def setupUi(self):
        #MainWindow.setObjectName("MainWindow")
        #MainWindow.resize(1631, 953)
        self.resize(2600, 1800)
        self.setObjectName("MainWindow")
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter_7 = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_7.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_7.setObjectName("splitter_7")
        self.splitter = QtWidgets.QSplitter(self.splitter_7)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.Titre1 = QtWidgets.QLabel(self.splitter)
        self.Titre1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.Titre1.setObjectName("Titre1")
        self.label_1 = QtWidgets.QLabel(self.splitter)
        self.label_1.setEnabled(True)
        self.label_1.setObjectName("label_1")
        self.tableWidget = QtWidgets.QTableWidget(self.splitter)
        self.tableWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.tableWidget_9 = QtWidgets.QTableWidget(self.splitter)
        self.tableWidget_9.setMinimumSize(QtCore.QSize(0, 0))
        self.tableWidget_9.setMaximumSize(QtCore.QSize(16777215, 131))
        self.tableWidget_9.setObjectName("tableWidget_9")
        self.tableWidget_9.setColumnCount(0)
        self.tableWidget_9.setRowCount(0)
        self.splitter_2 = QtWidgets.QSplitter(self.splitter_7)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setObjectName("splitter_2")
        self.Titre2 = QtWidgets.QLabel(self.splitter_2)
        self.Titre2.setMinimumSize(QtCore.QSize(0, 27))
        self.Titre2.setObjectName("Titre2")
        self.label_2 = QtWidgets.QLabel(self.splitter_2)
        self.label_2.setObjectName("label_2")
        self.tableWidget_2 = QtWidgets.QTableWidget(self.splitter_2)
        self.tableWidget_2.setMinimumSize(QtCore.QSize(0, 0))
        self.tableWidget_2.setObjectName("tableWidget_2")
        self.tableWidget_2.setColumnCount(0)
        self.tableWidget_2.setRowCount(0)
        self.Titre3 = QtWidgets.QLabel(self.splitter_2)
        self.Titre3.setObjectName("Titre3")
        self.tableWidget_3 = QtWidgets.QTableWidget(self.splitter_2)
        self.tableWidget_3.setMinimumSize(QtCore.QSize(0, 0))
        self.tableWidget_3.setObjectName("tableWidget_3")
        self.tableWidget_3.setColumnCount(0)
        self.tableWidget_3.setRowCount(0)
        self.tableWidget_10 = QtWidgets.QTableWidget(self.splitter_2)
        self.tableWidget_10.setMinimumSize(QtCore.QSize(0, 0))
        self.tableWidget_10.setMaximumSize(QtCore.QSize(16777215, 131))
        self.tableWidget_10.setObjectName("tableWidget_10")
        self.tableWidget_10.setColumnCount(0)
        self.tableWidget_10.setRowCount(0)
        self.splitter_3 = QtWidgets.QSplitter(self.splitter_7)
        self.splitter_3.setOrientation(QtCore.Qt.Vertical)
        self.splitter_3.setObjectName("splitter_3")
        self.Titre4 = QtWidgets.QLabel(self.splitter_3)
        self.Titre4.setMinimumSize(QtCore.QSize(0, 27))
        self.Titre4.setObjectName("Titre4")
        self.label_3 = QtWidgets.QLabel(self.splitter_3)
        self.label_3.setObjectName("label_3")
        self.tableWidget_4 = QtWidgets.QTableWidget(self.splitter_3)
        self.tableWidget_4.setMinimumSize(QtCore.QSize(0, 0))
        self.tableWidget_4.setObjectName("tableWidget_4")
        self.tableWidget_4.setColumnCount(0)
        self.tableWidget_4.setRowCount(0)
        self.Titre5 = QtWidgets.QLabel(self.splitter_3)
        self.Titre5.setObjectName("Titre5")
        self.tableWidget_5 = QtWidgets.QTableWidget(self.splitter_3)
        self.tableWidget_5.setMinimumSize(QtCore.QSize(0, 0))
        self.tableWidget_5.setObjectName("tableWidget_5")
        self.tableWidget_5.setColumnCount(0)
        self.tableWidget_5.setRowCount(0)
        self.tableWidget_11 = QtWidgets.QTableWidget(self.splitter_3)
        self.tableWidget_11.setMinimumSize(QtCore.QSize(0, 0))
        self.tableWidget_11.setMaximumSize(QtCore.QSize(16777215, 131))
        self.tableWidget_11.setObjectName("tableWidget_11")
        self.tableWidget_11.setColumnCount(0)
        self.tableWidget_11.setRowCount(0)
        self.splitter_4 = QtWidgets.QSplitter(self.splitter_7)
        self.splitter_4.setOrientation(QtCore.Qt.Vertical)
        self.splitter_4.setObjectName("splitter_4")
        self.Titre6 = QtWidgets.QLabel(self.splitter_4)
        self.Titre6.setObjectName("Titre6")
        self.label_4 = QtWidgets.QLabel(self.splitter_4)
        self.label_4.setObjectName("label_4")
        self.tableWidget_6 = QtWidgets.QTableWidget(self.splitter_4)
        self.tableWidget_6.setMinimumSize(QtCore.QSize(0, 0))
        self.tableWidget_6.setObjectName("tableWidget_6")
        self.tableWidget_6.setColumnCount(0)
        self.tableWidget_6.setRowCount(0)
        self.splitter_5 = QtWidgets.QSplitter(self.splitter_7)
        self.splitter_5.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.splitter_5.setOrientation(QtCore.Qt.Vertical)
        self.splitter_5.setObjectName("splitter_5")
        self.Titre7 = QtWidgets.QLabel(self.splitter_5)
        self.Titre7.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.Titre7.setObjectName("Titre7")
        self.tableWidget_7 = QtWidgets.QTableWidget(self.splitter_5)
        self.tableWidget_7.setObjectName("tableWidget_7")
        self.tableWidget_7.setColumnCount(0)
        self.tableWidget_7.setRowCount(0)
        self.splitter_6 = QtWidgets.QSplitter(self.splitter_7)
        self.splitter_6.setOrientation(QtCore.Qt.Vertical)
        self.splitter_6.setObjectName("splitter_6")
        self.Titre8 = QtWidgets.QLabel(self.splitter_6)
        self.Titre8.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.Titre8.setObjectName("Titre8")
        self.tableWidget_8 = QtWidgets.QTableWidget(self.splitter_6)
        self.tableWidget_8.setObjectName("tableWidget_8")
        self.tableWidget_8.setColumnCount(0)
        self.tableWidget_8.setRowCount(0)
        self.gridLayout.addWidget(self.splitter_7, 0, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnBrowse = QtWidgets.QPushButton(self.centralwidget)
        self.btnBrowse.setObjectName("btnBrowse")
        self.horizontalLayout.addWidget(self.btnBrowse)
        self.btnMeshPath = QtWidgets.QPushButton(self.centralwidget)
        self.btnMeshPath.setObjectName("btnMeshPath")
        self.horizontalLayout.addWidget(self.btnMeshPath)
        self.btnSaveAproj = QtWidgets.QPushButton(self.centralwidget)
        self.btnSaveAproj.setObjectName("btnSaveAproj")
        self.horizontalLayout.addWidget(self.btnSaveAproj)
        self.btnActualize = QtWidgets.QPushButton(self.centralwidget)
        self.btnActualize.setObjectName("btnActualize")
        self.horizontalLayout.addWidget(self.btnActualize)
        self.btnSave = QtWidgets.QPushButton(self.centralwidget)
        self.btnSave.setObjectName("btnSave")
        self.horizontalLayout.addWidget(self.btnSave)
        self.btnQuit = QtWidgets.QPushButton(self.centralwidget)
        self.btnQuit.setObjectName("btnQuit")
        self.horizontalLayout.addWidget(self.btnQuit)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar()
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1631, 21))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar()
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi()
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.Titre1.setText(_translate("MainWindow", "Label 1"))
        self.label_1.setText(_translate("MainWindow", "TextLabel1"))
        self.Titre2.setText(_translate("MainWindow", "Label 2"))
        self.label_2.setText(_translate("MainWindow", "TextLabel2"))
        self.Titre3.setText(_translate("MainWindow", "Label 3"))
        self.Titre4.setText(_translate("MainWindow", "Label 4"))
        self.label_3.setText(_translate("MainWindow", "TextLabel3"))
        self.Titre5.setText(_translate("MainWindow", "Label 5"))
        self.Titre6.setText(_translate("MainWindow", "Label 6"))
        self.label_4.setText(_translate("MainWindow", "TextLabel4"))
        self.Titre7.setText(_translate("MainWindow", "Label 7"))
        self.Titre8.setText(_translate("MainWindow", "Label 8"))
        self.btnBrowse.setText(_translate("MainWindow", "Pick a Folder"))
        self.btnMeshPath.setText(_translate("MainWindow", "Mesh Path for aproj"))
        self.btnSaveAproj.setText(_translate("MainWindow", "SaveNewAproj"))
        self.btnActualize.setText(_translate("MainWindow", "Actualize"))
        self.btnSave.setText(_translate("MainWindow", "Save Parameters"))
        self.btnQuit.setText(_translate("MainWindow", "Quit"))


class ReadAsimAform(Ui_MainWindow):
    """
    doc string
    """
    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(ReadAsimAform, self).__init__()
        # super(self.__class__, self).__init__()
        self.setupUi()  # This is defined in design.py file automatically
        # It sets up layout and widgets that are defined
        # Connecting pushbuttons. When one button is pressed
        # Execute corresponding function
        self.to_init()
        self.show()
        
    def to_init(self):
        self.btnBrowse.clicked.connect(self.browse_folder)
        self.btnMeshPath.clicked.connect(self.meshPath)
        self.btnSaveAproj.clicked.connect(self.saveAproj)
        self.btnActualize.clicked.connect(self.miseAjour)
        self.btnSave.clicked.connect(self.saveparamFile)
        self.btnQuit.clicked.connect(self.closeIt)

        self.exConn = []
        self.exConnFR = []
        self.exStim = []
        self.exConnName = []
        self.exConnFRName = []
        self.exStimName = []
        self.parVSCDVal = []
        self.parMarqVal = []
        self.font = QtGui.QFont()
        self.font.setBold(False)
        self.font.setPointSize(12)
        self.font.setWeight(75)
        self.Titre1.setText(_translate("MainWindow", "External Stimuli", None))
        self.Titre1.setFont(self.font)
        self.Titre2.setText(_translate("MainWindow", "Connexions", None))
        self.Titre2.setFont(self.font)
        self.Titre3.setText(_translate("MainWindow", "ConnexionsFR", None))
        self.Titre3.setFont(self.font)
        self.Titre4.setText(_translate("MainWindow", "Neurons", None))
        self.Titre4.setFont(self.font)
        self.Titre5.setText(_translate("MainWindow", "NeuronsFR", None))
        self.Titre5.setFont(self.font)
        self.Titre6.setText(_translate("MainWindow", "ChartNames", None))
        self.Titre6.setFont(self.font)
        self.Titre7.setText(_translate("MainWindow", "VSCD Parameters", None))
        self.Titre7.setFont(self.font)
        self.Titre8.setText(_translate("MainWindow",
                                       "Marquez Parameters", None))
        self.Titre8.setFont(self.font)

        self.btnBrowse.setText(_translate("MainWindow", "Pick a Folder", None))
        self.btnBrowse.setFont(self.font)
        self.btnMeshPath.setText(_translate("MainWindow",
                                            "Change Mesh Path", None))
        self.btnMeshPath.setFont(self.font)
        self.btnMeshPath.setEnabled(True)
        self.btnSaveAproj.setFont(self.font)
        self.btnSaveAproj.setEnabled(False)
        self.btnActualize.setText(_translate("MainWindow", "Actualize", None))
        self.btnActualize.setFont(self.font)
        self.btnActualize.setEnabled(False)
        self.btnSave.setText(_translate("MainWindow", "Save", None))
        self.btnSave.setFont(self.font)
        self.btnSave.setEnabled(False)
        self.btnQuit.setText(_translate("MainWindow", "Quit", None))
        self.btnQuit.setFont(self.font)
        lab1 = "Don'tChange                     Disable"
        self.label_1.setText(_translate("MainWindow", lab1, None))
        lab2 = "Don'tChange                                 Disable"
        self.label_2.setText(_translate("MainWindow", lab2, None))
        lab3 = "Sensory                         MN"
        self.label_3.setText(_translate("MainWindow", lab3, None))
        lab4 = "Sensory                         MN      Mvt"
        self.label_4.setText(_translate("MainWindow", lab4, None))
        # self.list_item = []
        self.newMNtoSt = {}
        self.MNtoSt = {}
        self.folders = FolderOrg()
        self.sims = None
        self.model = None
        self.projMan = None
        self.optSet = None
        self.animatLabV2ProgDir = None
        self.rootname = None

    def loadParams(self, paramFicName, listparNameOpt):
        try:
            print("looking paramOpt file:", paramFicName)
            with open(paramFicName, 'rb') as input:
                self.optSet.paramVSCDName = pickle.load(input)
                self.optSet.paramVSCDValue = pickle.load(input)
                self.optSet.paramVSCDType = pickle.load(input)
                self.optSet.paramVSCDCoul = pickle.load(input)
                self.optSet.paramMarquezName = pickle.load(input)
                self.optSet.paramMarquezValue = pickle.load(input)
                self.optSet.paramMarquezType = pickle.load(input)
                self.optSet.paramMarquezCoul = pickle.load(input)
            print("nb loaded param :", len(self.optSet.paramVSCDName))
            print("nb actual param:", len(listparNameOpt))
            nbloadedpar = len(self.optSet.paramVSCDName)
            if nbloadedpar == 42:
                if self.optSet.paramVSCDName[16] == 'disabledSynNbs':
                    # This is the last version that includes "seriesSynNSParam"
                    print("paramOpt :")
                    self.optSet.printParams(self.optSet.paramVSCDName,
                                            self.optSet.paramVSCDValue)
                elif self.optSet.paramVSCDName[16] == 'allsyn':
                    # This is the last version that includes "seriesSynNSParam"
                    print("this version does not indicate seriesSynNSParam")
                    print("ACTUALIZING...")
                    self.optSet.update_optSetParamVSCD()
                    print("paramOpt :")
                    self.optSet.printParams(self.optSet.paramVSCDName,
                                            self.optSet.paramVSCDValue)
                print("paramMarquez :")
                self.optSet.printParams(self.optSet.paramMarquezName,
                                        self.optSet.paramMarquezValue)
                print('====  Param loaded  ====')
                response = True
            elif nbloadedpar == 41:
                print("paramOpt with only 41 params: => actualization...")
                pln = ['selectedChart'] + self.optSet.paramVSCDName
                self.optSet.paramVSCDName = pln
                plv = [0] + self.optSet.paramVSCDValue
                self.optSet.paramVSCDValue = plv
                plt = [int] + self.optSet.paramVSCDType
                self.optSet.paramVSCDType = plt
                plc = ["Magenta"] + self.optSet.paramVSCDCoul
                self.optSet.paramVSCDCoul = plc
                self.optSet.printParams(self.optSet.paramVSCDName,
                                        self.optSet.paramVSCDValue)
                print("paramMarquez :")
                self.optSet.printParams(self.optSet.paramMarquezName,
                                        self.optSet.paramMarquezValue)
                print('===================  Param loaded  ====================')
                response = True
            else:
                print("Mismatch between existing and actual parameter files")
                response = False
        except Exception as e:
            if (verbose > 1):
                print(e)
            print("No parameter file with this name in the directory")
            print("NEEDs to create a new parameter file")
            response = False
        return response

    def closeIt(self):
        """
        doc string
        """
        self.close()

    def saveAproj(self):
        """
        doc string
        """
        aprojFileName = os.path.split(self.model.aprojFile)[-1]
        aprojSaveDir = os.path.join(self.folders.animatlab_rootFolder,
                                    "AprojFiles")
        if not os.path.exists(aprojSaveDir):
            os.makedirs(aprojSaveDir)
            copyFileDir(self.animatsimdir,
                        aprojSaveDir,
                        copy_dir=0)
        self.model.saveXMLaproj(os.path.join(aprojSaveDir, aprojFileName))

    def saveparamFile(self):
        """
        doc string
        """
        self.miseAjour()
        saveParams(os.path.join(self.folders.animatlab_result_dir,
                                'paramOpt.pkl'),
                   self.optSet)

    def miseAjour(self):
        """
        doc string
        """
        # lecture de la colonne "Parametres VSCD"
        self.parVSCDVal = self.getValuesFromPannel(self.tableWidget_7,
                                                   self.optSet.paramVSCDName,
                                                   self.optSet.paramVSCDType,
                                                   "VSCD Param")
        self.optSet.paramVSCDValue = self.parVSCDVal
        self.optSet.actualizeparamVSCD()

        # lecture de la colonne "Parametres Marquez"
        self.parMarqVal = self.\
            getValuesFromPannel(self.tableWidget_8,
                                self.optSet.paramMarquezName,
                                self.optSet.paramMarquezType,
                                "Marquez Param")
        self.optSet.paramMarquezValue = self.parMarqVal
        self.optSet.actualizeparamMarquez()

    def getValuesFromPannel(self, tableWidg, paramTabName, paramTabType, txt):
        """
        doc string
        """
        # print self.paramType
        listparValStr = []
        for rg in range(len(paramTabName)):
            valstr = tableWidg.item(rg, 1).text()
            # listparValStr.append(valstr.encode('ascii', 'ignore'))
            listparValStr.append(valstr)
            # print(valstr)
        # print(listparValStr)
        print()
        print("@@ ", txt, " actualized  @@")
        paramValue = applyType(paramTabType, listparValStr)
        self.optSet.printParams(paramTabName, paramValue)
        return paramValue

    def stim_cell_was_clicked(self, row, column):
        """
        doc string
        """
        oneChk = 0
        rep = self.cell_was_clicked(self.tableWidget, self.optSet.stimName,
                                    row, column, oneChk, col=2)
        firstListNb = rep[0]
        secondListNb = rep[1]
        # print(firstListNb)
        # print(secondListNb)
        self.optSet.paramOpt['dontChangeStimNbs'] = firstListNb
        self.optSet.paramOpt['disabledStimNbs'] = secondListNb
        itm1 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramOpt['dontChangeStimNbs']))
        itm2 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramOpt['disabledStimNbs']))
        self.tableWidget_7.setItem(14, 1, itm1)
        self.tableWidget_7.setItem(13, 1, itm2)

    def connex_cell_was_clicked(self, row, column):
        """
        doc string
        """
        oneChk = 0
        rep = self.cell_was_clicked(self.tableWidget_2, self.optSet.connexName,
                                    row, column, oneChk, col=2)
        firstListNb = rep[0]
        secondListNb = rep[1]
        self.optSet.paramOpt['dontChangeSynNbs'] = firstListNb
        self.optSet.paramOpt['disabledSynNbs'] = secondListNb
        itm1 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramOpt['dontChangeSynNbs']))
        itm2 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramOpt['disabledSynNbs']))
        self.tableWidget_7.setItem(17, 1, itm1)
        self.tableWidget_7.setItem(16, 1, itm2)

    def connexFR_cell_was_clicked(self, row, column):
        """
        doc string
        """
        oneChk = 0
        rep = self.cell_was_clicked(self.tableWidget_3,
                                    self.optSet.connexFRName,
                                    row, column, oneChk, col=2)
        firstListNb = rep[0]
        secondListNb = rep[1]
        self.optSet.paramOpt['dontChangeSynFRNbs'] = firstListNb
        self.optSet.paramOpt['disabledSynFRNbs'] = secondListNb
        itm1 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramOpt['dontChangeSynFRNbs']))
        itm2 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramOpt['disabledSynFRNbs']))
        self.tableWidget_7.setItem(19, 1, itm1)
        self.tableWidget_7.setItem(18, 1, itm2)

    def neuron_cell_was_clicked(self, row, column):
        """
        doc string
        """
        oneChk = 0
        rep = self.cell_was_clicked(self.tableWidget_4,
                                    self.optSet.neuronNames,
                                    row, column, oneChk, col=2)
        firstListNb = rep[0]
        secondListNb = rep[1]
        self.optSet.paramMarquez['sensoryNeuronNbs'] = firstListNb
        self.optSet.paramMarquez['motorNeuronNbs'] = secondListNb
        itm1 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramMarquez['sensoryNeuronNbs']))
        itm2 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramMarquez['motorNeuronNbs']))
        self.tableWidget_8.setItem(5, 1, itm1)
        self.tableWidget_8.setItem(6, 1, itm2)

    def neuronFR_cell_was_clicked(self, row, column):
        """
        doc string
        """
        oneChk = 0
        rep = self.cell_was_clicked(self.tableWidget_5,
                                    self.optSet.neuronFRNames,
                                    row, column, oneChk, col=2)
        firstListNb = rep[0]
        secondListNb = rep[1]
        self.optSet.paramMarquez['sensoryNeuronFRNbs'] = firstListNb
        self.optSet.paramMarquez['motorNeuronFRNbs'] = secondListNb
        # self.optSet.actualizeparamMarquez
        itm1 = QtWidgets.QTableWidgetItem(str(firstListNb))
        itm2 = QtWidgets.QTableWidgetItem(str(secondListNb))
        self.tableWidget_8.setItem(7, 1, itm1)
        self.tableWidget_8.setItem(8, 1, itm2)

    def chart_cell_was_clicked(self, row, column):
        """
        doc string
        """
        oneChk = 1
        rep = self.cell_was_clicked(self.tableWidget_6,
                                    self.optSet.chartColNames,
                                    row, column, oneChk, col=3)
        firstListNb = rep[0]
        # print "rep[0]", rep[0]
        secondListNb = rep[1]
        # print "rep[1]", rep[1]
        thirdListNb = rep[2]
        # print "rep[2]", thirdListNb
        for i in thirdListNb:
            thirdNb = i

        self.optSet.paramMarquez['sensColChartNbs'] = firstListNb
        self.optSet.paramMarquez['mnColChartNbs'] = secondListNb
        self.optSet.paramOpt['mvtcolumn'] = thirdNb
        itm1 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramMarquez['sensColChartNbs']))
        itm2 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramMarquez['mnColChartNbs']))
        itm3 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramOpt['mvtcolumn']))
        self.tableWidget_8.setItem(9, 1, itm1)
        self.tableWidget_8.setItem(10, 1, itm2)
        self.tableWidget_7.setItem(1, 1, itm3)

        if column == 1:     # We have checked/unchecked a MN
            self.optSet.mnColChartNbs = self.optSet.\
                paramMarquez['mnColChartNbs']
            self.optSet.mnColChartNames = []
            for i in self.optSet.mnColChartNbs:
                self.optSet.mnColChartNames.\
                    append(self.optSet.chartColNames[i])
            print()
            print(self.optSet.mnColChartNames)
            # Creation of the dictionnary mnColChartNames->twitStMusclesStNames
            if self.MNtoSt == {}:  # this is the first acces to the Dict...
                i = 0
                for mn in self.optSet.mnColChartNames:
                    if self.optSet.twitStMusclesStNames == []:
                        self.MNtoSt[mn] = self.optSet.stimName[i]
                    else:
                        self.MNtoSt[mn] = self.optSet.twitStMusclesStNames[i]
                    i += 1

            # Actualization of the dictionary ChartMN -> StimMNNb
            twitMusNb = len(self.optSet.twitStMusclesStNames)
            charmnNb = len(self.optSet.mnColChartNames)
            print("charmnNb : {}    twitMusNb: {}".format(charmnNb, twitMusNb))

            if twitMusNb > charmnNb:
                print(list(self.MNtoSt.keys()))
                for mnName in list(self.MNtoSt.keys()):
                    if mnName not in self.optSet.mnColChartNames:
                        del self.MNtoSt[mnName]
            elif twitMusNb < charmnNb:
                i = 0
                for mnName in self.optSet.mnColChartNames:
                    if mnName not in list(self.MNtoSt.keys()):
                        self.MNtoSt[mnName] = self.optSet.stimName[i]
                        i += 1
            print("self.MNtoSt: ", self.MNtoSt)

# TODO:
            """
            listMNs = self.optSet.mnColChartNames
            for MN in listMNs:
                rep = ChooseInList.listTransmit(parent=None,
                                                graphNo=0,
                                                listChoix=listMNs,
                                                items=self.optSet.stimName,
                                                listDicItems=self.MNtoSt,
                                                onePerCol=[1,1],
                                                colNames=listMNs,
                                                typ="chk",
                                                titleText=MN)
            self.listDicItems2 = rep[0][0]
            """

            self.newMNtoSt = \
                GetList.listTransmit(parent=None,
                                     listChoix=self.optSet.mnColChartNames,
                                     items=(self.optSet.stimName),
                                     dicItems=self.MNtoSt,
                                     titleText="Choose Stim of this MN:")
            # print("self.newMNtoSt: ", self.newMNtoSt)
            # self.list_item = list(self.newMNtoSt.values())
            print('fen princ : {}'.format(self.newMNtoSt))
            self.MNtoSt = self.newMNtoSt
            print(list(self.MNtoSt.keys()))
            print(list(self.MNtoSt.values()))
            twitchSt_listnb = []
            self.optSet.twitStMusclesStNbs = []
            self.optSet.twitStMusclesStNames = []
            for mnNb in self.optSet.paramMarquez['mnColChartNbs']:
                mnName = self.optSet.chartColNames[mnNb]
                stName = self.MNtoSt[mnName]
                stNb = self.optSet.rank_stim[stName]
                twitchSt_listnb.append(stNb)
                self.optSet.twitStMusclesStNames.append(stName)
                self.optSet.twitStMusclesStNbs.append(stNb)
            self.optSet.paramMarquez['twitStMusclesStNbs'] = twitchSt_listnb
            itm4 = QtWidgets.QTableWidgetItem(str(twitchSt_listnb))
            self.tableWidget_8.setItem(4, 1, itm4)

    def stimPar_cell_was_clicked(self, row, column):
        """
        doc string
        """
        oneChk = 0
        rep = self.cell_was_clicked(self.tableWidget_9,
                                    self.optSet.stimParam,
                                    row, column, oneChk, col=1)
        firstListNb = rep[0]
        listParamStim = []
        for i in firstListNb:
            listParamStim.append(self.optSet.stimParam[i])
        self.optSet.paramOpt['seriesStimParam'] = listParamStim
        itm1 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramOpt['seriesStimParam']))
        self.tableWidget_7.setItem(15, 1, itm1)

    def cell_was_clicked(self, tableWidgt, listName, row, column, oneChk, col):
        """
        doc string
        """
        firstChkList = []
        secondChkList = []
        thirdChkList = []
        firstListNb = []
        secondListNb = []
        thirdListNb = []
        # =====================================================
        # Set fills the state of each box on all columns
        # =====================================================
        for i in range(len(listName)):
            if col >= 1:
                item1 = tableWidgt.item(i, 0)
                if item1.checkState() == 0:
                    firstChkList.append(0)
                else:
                    firstChkList.append(1)
            if col >= 2:
                item2 = tableWidgt.item(i, 1)
                if item2.checkState() == 0:
                    secondChkList.append(0)
                else:
                    secondChkList.append(1)
            if col >= 3:
                item3 = tableWidgt.item(i, 2)
                if not oneChk:  # severale checked boxes in the list
                    if item3.checkState() == 0:
                        thirdChkList.append(0)
                    else:
                        thirdChkList.append(1)
                else:       # only one checked box at a time in the list
                    if column == 2:
                        if i != row:
                            # print "i:", i, " row:", row, item3.checkState()
                            if item3.checkState() == 2:  # previous check
                                item1.setForeground(QtGui.QColor('black'))
                                print("previous checked:", i)
                            item3.setCheckState(QtCore.Qt.Unchecked)
                            thirdChkList.append(0)
                        else:
                            item3.setCheckState(QtCore.Qt.Checked)
                            thirdChkList.append(1)
                    else:
                        if item3.checkState() == 0:
                            thirdChkList.append(0)
                        else:
                            thirdChkList.append(1)
        # =====================================================
        # Set interactions between columns for the clicked row
        # =====================================================
        item1 = tableWidgt.item(row, 0)
        if col >= 2:
            item2 = tableWidgt.item(row, 1)
        if col >= 3:
            item3 = tableWidgt.item(row, 2)

        if column == 0:
            if item1.checkState() == 0:
                firstChkList[row] = 0
                item1.setForeground(QtGui.QColor('black'))
            else:
                firstChkList[row] = 1
                item1.setForeground(QtGui.QColor('red'))
                if col >= 2:
                    item2.setCheckState(QtCore.Qt.Unchecked)
                    secondChkList[row] = 0
        elif column == 1:
            if col >= 2:
                if item2.checkState() == 0:
                    secondChkList[row] = 0
                    item1.setForeground(QtGui.QColor('black'))
                else:
                    secondChkList[row] = 1
                    item1.setForeground(QtGui.QColor('blue'))
                    item1.setCheckState(QtCore.Qt.Unchecked)
                    firstChkList[row] = 0
        elif column == 2:
            if col == 3:
                if item3.checkState() == 0:
                    thirdChkList[row] = 0
                    item1.setForeground(QtGui.QColor('black'))
                else:
                    thirdChkList[row] = 1
                    item1.setForeground(QtGui.QColor('magenta'))
                    item1.setCheckState(QtCore.Qt.Unchecked)
                    # firstChkList[row] = 0
                    # secondChkList[row] = 0
        for i in range(len(listName)):
            if firstChkList[i]:
                firstListNb.append(i)
        # print("disabledList", secondChkList)
        # print("dontChangeList", firstListNb)
        for i in range(len(listName)):
            if col >= 2:
                if secondChkList[i]:
                    secondListNb.append(i)
        # print("dontChangeList", firstChkList)
        # print("disabledList", secondListNb)
        for i in range(len(listName)):
            if col >= 3:
                if thirdChkList[i]:
                    thirdListNb.append(i)
        # print("col", col, thirdChkList, "oneChk", oneChk, "thirdNb", thirdNb)
        # print("thirdListNb", thirdListNb)
        return [firstListNb, secondListNb, thirdListNb]

    def browse_folder(self):
        """
        doc string
        """
        # global folders, sims, model, projman
        # self.listWidget.clear()     # If there are any elements in the list

        self.animatsimdir = readAnimatLabSimDir()
        if self.animatsimdir != "":
            subdir = os.path.split(self.animatsimdir)[-1]
            rootname = os.path.dirname(self.animatsimdir)
            # rootname += "/"
        else:
            print("First instance - no previous animatlab folder selected")
            rootname = ""
        """
        # mydir = "//Mac/Home/Documents/Labo/Scripts/AnimatLabV2/Human/test/"
        # mydir = ""
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                         "Pick a folder",
                                                         rootname)
        """
        res = (QtWidgets.QFileDialog.
               getExistingDirectory(self, "Pick a folder", rootname))
        if type(res) == tuple:
            dirname, __tmp = res
        else:
            dirname = res
        print(dirname)

        dname = ""
        for ch in dirname:
            if ch == '\\':
                ch = '/'
            dname += ch
        print(dname)
        dirname = dname
        self.dirname = dirname
        # execute getExistingDirectory dialog and set the directory variable
        #  to be equal to the user selected directory

        if dirname:       # if user didn't pick a directory don't continue
            print("You chose %s" % dirname)
            subdir = os.path.split(dirname)[-1]
            print(subdir)
            rootname = os.path.dirname(dirname)
            # rootname += "/"
            
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

            aprojNames = []
            for projname in os.listdir(dirname):
                if projname.endswith("aproj"):
                    print(projname)
                    aprojNames.append(projname)
            if len(aprojNames) > 1:
                    print("PROBLEM: More than one aproj file is present")
                    sys.exit()
            elif len(aprojNames) == 0:
                    print("PROBLEM: No aproj file is present")
                    sys.exit()
            else:
                aprojFilePath =  dirname + "/" + aprojNames[0]
                asimFilePath = dirname + "/" + asimNames[0]

            check_mesh(aprojFilePath, asimFilePath)

            self.folders = FolderOrg(animatlab_root=rootname,
                                     subdir=subdir,
                                     python27_source_dir=self.
                                     animatLabV2ProgDir)
            self.folders.affectDirectories()
            saveAnimatLabSimDir(dirname)
            self.dirname = dirname
            self.rootname = rootname
            self.btnActualize.setEnabled(True)
            self.btnSave.setEnabled(True)
            # ################################################################
            #                  Creation of sims & initialisation             #
            # ################################################################
            # Initializes the AnimatLabSimRunner
            self.sims = AnimatLabSimRunner.AnimatLabSimulationRunner("Test Sims",
                    rootFolder=self.folders.animatlab_rootFolder,
                    commonFiles=self.folders.animatlab_commonFiles_dir,
                    sourceFiles=self.folders.python27_source_dir,
                    simFiles=self.folders.animatlab_simFiles_dir,
                    resultFiles=self.folders.animatlab_result_dir)
            asimdir= os.path.join(self.folders.animatlab_commonFiles_dir,
                                  '*.asim')
            if len(glob.glob(asimdir)) == 0:
                print("No .asim file exist in directory")

            self.model = AnimatLabModel.\
                AnimatLabModel(self.folders.animatlab_commonFiles_dir)
            self.projMan = ProjectManager.ProjectManager('Test Project')
            self.optSet = OptimizeSimSettings(folders=self.folders,
                                              model=self.model,
                                              projMan=self.projMan,
                                              sims=self.sims)

            # ################################################################
            #                      Default parameters                        #
            # ################################################################
            # Parameters for optimization
            listparNameOpt = ['selectedChart',
                              'mvtcolumn',
                              'startMvt1', 'endMvt1', 'endPos1', 'angle1',
                              'startMvt2', 'endMvt2', 'endPos2', 'angle2',
                              'startEQM', 'endEQM',
                              'allstim',
                              'disabledStimNbs', 'dontChangeStimNbs',
                              'seriesStimParam',
                              'disabledSynNbs', 'dontChangeSynNbs',
                              'disabledSynFRNbs', 'dontChangeSynFRNbs',
                              'seriesSynParam',
                              'seriesSynNSParam',
                              'seriesSynFRParam',
                              'nbepoch', 'nbstimtrials', 'nbsyntrials',
                              'nbsteps',
                              'deltaStimCoeff', 'maxDeltaStim',
                              'multSynCoeff', 'maxMultSyn',
                              'coactivityFactor', 'activThr', 'limQuality',
                              'maxStim', 'maxSynAmp',
                              'maxG', 'maxWeight',
                              'defaultval', 'cmaes_sigma',
                              'fourchetteStim', 'fourchetteSyn']
            listparValOpt = [0,
                             6,
                             0, 0.3, 5, 0, 5, 5.8, 10, 60,
                             3, 10,
                             1,
                             [], [],
                             ['CurrentOn', 'StartTime', 'EndTime'],
                             [], [], [], [],
                             ['G'], ['SynAmp'], ['Weight'],
                             2, 1, 1, 4,
                             1.5, 50, 1.5, 50, 1000, -0.06, 0.0001, 2e-08,
                             50, 10, 5e-07, 100000.0, 0.0035, 5, 5]
            listparTypeOpt = [int,
                              int,
                              float, float, float, float,
                              float, float, float, float,
                              float, float,
                              int,
                              list, list, list,
                              list, list, list, list,
                              list, list, list,
                              int, int, int, int,
                              float, float, float, float, float, float, float,
                              float, float, float, float, float, float,
                              float, float]
            listparCoulOpt = ['LavenderBlush',
                              'pink',
                              'lightyellow', 'lightyellow', 'lightyellow',
                              'lightyellow', 'lightyellow', 'lightyellow',
                              'lightyellow', 'lightyellow',
                              'lightyellow', 'lightyellow',
                              'lightblue',
                              'lightblue', 'lightblue', 'lightblue',
                              'lightgreen',
                              'lightgreen', 'lightgreen',
                              'lightgreen', 'lightgreen',
                              'lightgreen', 'lightgreen',
                              'pink', 'pink', 'pink', 'pink', 'pink', 'pink',
                              'pink', 'pink', 'pink', 'pink', 'pink',
                              'MistyRose', 'MistyRose',
                              'MistyRose', 'MistyRose',
                              'lightPink', 'lightgray',
                              'lightgray', 'lightgray']

            # Parameters for Marquez procedure
            listparNameMarquez = ['startTest', 'startTwitch',
                                  'endTwitch', 'endTest',
                                  'twitStMusclesStNbs',
                                  'sensoryNeuronNbs', 'motorNeuronNbs',
                                  'sensoryNeuronFRNbs', 'motorNeuronFRNbs',
                                  'sensColChartNbs', 'mnColChartNbs',
                                  'nbruns', 'timeMes', 'delay', 'eta']
            listparValMarquez = [0., 5., 5.1, 8.,
                                 [0, 1],
                                 [], [],
                                 [], [],
                                 [], [],
                                 3, 0.08, 0.02, 1000]
            listparTypeMarquez = [float, float, float, float,
                                  list, list, list, list, list, list, list,
                                  int, float, float, float]
            listparCoulMarquez = ['orange', 'orange', 'orange', 'orange',
                                  'orange', 'orange', 'orange', 'orange',
                                  'orange', 'orange', 'orange', 'orange',
                                  'orange', 'orange', 'orange']

            # ###############################################################
            #       Looks for a parameter file in the chosen directory      #
            # ###############################################################
            fileName = 'paramOpt.pkl'
            if self.loadParams(os.path.join(self.folders.animatlab_result_dir,
                                            fileName),
                               listparNameOpt):
                print("parameter file found => reading params")
                self.optSet.paramVSCDCoul = listparCoulOpt
            else:
                print("No parameter file found => default settings")
                # If no parameter file found, then uses the default parameters
                self.optSet.paramVSCDName = listparNameOpt
                self.optSet.paramVSCDValue = listparValOpt
                self.optSet.paramVSCDType = listparTypeOpt
                self.optSet.paramVSCDCoul = listparCoulOpt
                self.optSet.paramMarquezName = listparNameMarquez
                self.optSet.paramMarquezValue = listparValMarquez
                self.optSet.paramMarquezType = listparTypeMarquez
                self.optSet.paramMarquezCoul = listparCoulMarquez
            self.optSet.actualizeparamVSCD()
            self.optSet.actualizeparamMarquez()

            if len(self.optSet.chartName) > 1:      # if more than one chart...
                print(self.optSet.chartName)
                previousChart = self.optSet.paramVSCDValue[0]
                chartNumber = {}
                for idx, elem in enumerate(self.optSet.chartName):
                    chartNumber[elem] = idx
                listSelectedDic = chooseChart(self.optSet)  # then select chart
                # chooseChart returns a dictionary...
                # gets the chartName from the dictionary
                selected = listSelectedDic[0]['selectedChart'][0]
                # ... and gets its number
                self.optSet.selectedChart = chartNumber[selected]
                print("selected chart number :", self.optSet.selectedChart,
                      end=" ")
                print(selected)  # selected is the name of the chart
                self.optSet.paramVSCDValue[0] = self.optSet.selectedChart
                self.optSet.actualizeparamVSCD()
                if chartNumber[selected] != previousChart:
                    self.optSet.paramMarquezName = listparNameMarquez
                    self.optSet.paramMarquezValue = listparValMarquez
                    self.optSet.paramMarquezType = listparTypeMarquez
                    self.optSet.paramMarquezCoul = listparCoulMarquez
                    self.optSet.actualizeparamMarquez()

            self.exConn = []
            for i in range(self.optSet.nbConnexions):
                if self.optSet.tab_connexions[i][6] == "Disabled" or \
                   self.optSet.tab_connexions[i][7] == "Disabled":
                    self.exConn.append(i)
                    # print(self.optSet.tab_connexions[i][6])
                    # print(self.optSet.tab_connexions[i][7])
            for i in self.exConn:
                if i not in self.optSet.paramOpt['disabledSynNbs']:
                    self.optSet.paramOpt['disabledSynNbs'].append(i)
            # self.optSet.paramOpt['disabledSynNbs'] += self.exConn
            self.optSet.paramOpt['disabledSynNbs'] = \
                list(set(self.optSet.paramOpt['disabledSynNbs']))
            self.optSet.disabledSynNames = []
            for i in self.optSet.disabledSynNbs:
                self.optSet.disabledSynNames.append(self.optSet.connexName[i])

            self.exConnFR = []
            for i in range(self.optSet.nbSynapsesFR):
                if self.optSet.tab_connexionsFR[i][3] == "Disabled" or \
                   self.optSet.tab_connexionsFR[i][4] == "Disabled":
                    self.exConnFR.append(i)
            for i in self.exConnFR:
                if i not in self.optSet.paramOpt['disabledSynFRNbs']:
                    self.optSet.paramOpt['disabledSynFRNbs'].append(i)
            # self.optSet.paramOpt['disabledSynFRNbs'] += self.exConnFR
            self.optSet.paramOpt['disabledSynFRNbs'] = \
                list(set(self.optSet.paramOpt['disabledSynFRNbs']))
            self.optSet.disabledSynFRNames = []
            for i in self.optSet.disabledSynFRNbs:
                self.optSet.disabledSynFRNames.\
                    append(self.optSet.connexFRName[i])

            self.exStim = []
            for i in range(self.optSet.nbStims):
                name = self.optSet.model.\
                    getElementByID(self.optSet.tab_stims[i][6]).\
                    find('Name').text
                # print name
                if name == "Disabled":
                    self.exStim.append(i)
            for i in self.exStim:
                if i not in self.optSet.paramOpt['disabledStimNbs']:
                    self.optSet.paramOpt['disabledStimNbs'].append(i)
            # self.optSet.paramOpt['disabledStimNbs'] += self.exStim
            self.optSet.paramOpt['disabledStimNbs'] = \
                list(set(self.optSet.paramOpt['disabledStimNbs']))
            self.optSet.disabledStimNames = []
            for i in self.optSet.disabledStimNbs:
                self.optSet.disabledStimNames.append(self.optSet.stimName[i])

            for i in range(len(self.exStim)):
                self.exStimName.append(self.optSet.stimName[self.exStim[i]])
            for i in range(len(self.exConn)):
                self.exConnName.append(self.optSet.connexName[self.exConn[i]])
            for i in range(len(self.exConnFR)):
                self.exConnFRName.\
                    append(self.optSet.connexFRName[self.exConnFR[i]])

        # ################################################################
        #                   Select list of External Stimuli              #
        # ################################################################
        self.tableWidget.setRowCount(len(self.optSet.stimName))
        self.tableWidget.setColumnCount(2)
        self.tableWidget.verticalHeader().hide()
        self.tableWidget.horizontalHeader().hide()
        for idx, elem in enumerate(self.optSet.stimName):
            itm1 = QtWidgets.QTableWidgetItem("{0} {1}".format(idx, elem))
            itm1.setFlags(itm1.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramOpt['dontChangeStimNbs']:
                itm1.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('red'))
            else:
                itm1.setCheckState(QtCore.Qt.Unchecked)

            itm2 = QtWidgets.QTableWidgetItem("")
            itm2.setFlags(itm2.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramOpt['disabledStimNbs']:
                itm2.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('blue'))
            else:
                itm2.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidget.setItem(idx, 0, itm1)
            self.tableWidget.setItem(idx, 1, itm2)
            self.tableWidget.item(idx, 0).\
                setBackground(QtGui.QColor(self.optSet.paramVSCDCoul[12]))
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.cellClicked.connect(self.stim_cell_was_clicked)
        # ################################################################
        #                Select list of Connexions                       #
        # ################################################################
        self.tableWidget_2.setRowCount(len(self.optSet.connexName))
        self.tableWidget_2.setColumnCount(2)
        self.tableWidget_2.verticalHeader().hide()
        self.tableWidget_2.horizontalHeader().hide()
        for idx, elem in enumerate(self.optSet.connexName):
            itm1 = QtWidgets.\
                QTableWidgetItem("{0} {1}".format(idx, elem))
            itm1.setFlags(itm1.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramOpt['dontChangeSynNbs']:
                itm1.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('red'))
            else:
                itm1.setCheckState(QtCore.Qt.Unchecked)
            itm2 = QtWidgets.QTableWidgetItem("")
            itm2.setFlags(itm2.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramOpt['disabledSynNbs']:
                itm2.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('blue'))
            else:
                itm2.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidget_2.setItem(idx, 0, itm1)
            self.tableWidget_2.setItem(idx, 1, itm2)
            self.tableWidget_2.item(idx, 0).\
                setBackground(QtGui.QColor(self.optSet.paramVSCDCoul[16]))
        self.tableWidget_2.resizeColumnsToContents()
        self.tableWidget_2.cellClicked.connect(self.connex_cell_was_clicked)

        # self.tableWidget_2.setColumnWidth(0, 80)
        # self.tableWidget_2.horizontalHeader().setDefaultSectionSize(140)
        # self.tableWidget_2.verticalHeader().setStretchLastSection(True)
        # ################################################################
        #                Select list of ConnexionsFR                      #
        # ################################################################
        self.tableWidget_3.setRowCount(len(self.optSet.connexFRName))
        self.tableWidget_3.setColumnCount(2)
        self.tableWidget_3.verticalHeader().hide()
        self.tableWidget_3.horizontalHeader().hide()
        for idx, elem in enumerate(self.optSet.connexFRName):
            itm1 = QtWidgets.QTableWidgetItem("{0} {1}".format(idx, elem))
            itm1.setFlags(itm1.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramOpt['dontChangeSynFRNbs']:
                itm1.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('red'))
            else:
                itm1.setCheckState(QtCore.Qt.Unchecked)
            itm2 = QtWidgets.QTableWidgetItem("")
            itm2.setFlags(itm2.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramOpt['disabledSynFRNbs']:
                itm2.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('blue'))
            else:
                itm2.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidget_3.setItem(idx, 0, itm1)
            self.tableWidget_3.setItem(idx, 1, itm2)
            self.tableWidget_3.item(idx, 0).\
                setBackground(QtGui.QColor(self.optSet.paramVSCDCoul[16]))
        self.tableWidget_3.resizeColumnsToContents()
        self.tableWidget_3.cellClicked.connect(self.connexFR_cell_was_clicked)

        # self.tableWidget_3.setColumnWidth(0, 80)
        # self.tableWidget_3.horizontalHeader().setDefaultSectionSize(140)
        # self.tableWidget_3.horizontalHeader().setStretchLastSection(True)
        # ################################################################
        #                    Select list of Neurons                      #
        # ################################################################
        self.tableWidget_4.setRowCount(len(self.optSet.neuronNames))
        self.tableWidget_4.setColumnCount(2)
        self.tableWidget_4.verticalHeader().hide()
        self.tableWidget_4.horizontalHeader().hide()
        for idx, elem in enumerate(self.optSet.neuronNames):
            itm1 = QtWidgets.QTableWidgetItem("{0} {1}".format(idx, elem))
            itm1.setFlags(itm1.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramMarquez['sensoryNeuronNbs']:
                itm1.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('red'))
            else:
                itm1.setCheckState(QtCore.Qt.Unchecked)
            itm2 = QtWidgets.QTableWidgetItem("")
            itm2.setFlags(itm2.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramMarquez['motorNeuronNbs']:
                itm2.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('blue'))
            else:
                itm2.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidget_4.setItem(idx, 0, itm1)
            self.tableWidget_4.setItem(idx, 1, itm2)
            self.tableWidget_4.item(idx, 0).\
                setBackground(QtGui.QColor('gold'))
        self.tableWidget_4.resizeColumnsToContents()
        self.tableWidget_4.cellClicked.connect(self.neuron_cell_was_clicked)
        # ################################################################
        #                  Select list of NeuronsFR                      #
        # ################################################################
        self.tableWidget_5.setRowCount(len(self.optSet.neuronFRNames))
        self.tableWidget_5.setColumnCount(2)
        self.tableWidget_5.verticalHeader().hide()
        self.tableWidget_5.horizontalHeader().hide()
        for idx, elem in enumerate(self.optSet.neuronFRNames):
            itm1 = QtWidgets.QTableWidgetItem("{0} {1}".format(idx, elem))
            itm1.setFlags(itm1.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramMarquez['sensoryNeuronFRNbs']:
                itm1.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('red'))
            else:
                itm1.setCheckState(QtCore.Qt.Unchecked)
            itm2 = QtWidgets.QTableWidgetItem("")
            itm2.setFlags(itm2.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramMarquez['motorNeuronFRNbs']:
                itm2.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('blue'))
            else:
                itm2.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidget_5.setItem(idx, 0, itm1)
            self.tableWidget_5.setItem(idx, 1, itm2)
            self.tableWidget_5.item(idx, 0).\
                setBackground(QtGui.QColor('gold'))
        self.tableWidget_5.resizeColumnsToContents()
        self.tableWidget_5.cellClicked.connect(self.neuronFR_cell_was_clicked)
        # ################################################################
        #                  Select list of Chart Names                    #
        # ################################################################
        self.tableWidget_6.setRowCount(len(self.optSet.chartColNames))
        self.tableWidget_6.setColumnCount(3)
        self.tableWidget_6.verticalHeader().hide()
        self.tableWidget_6.horizontalHeader().hide()
        for idx, elem in enumerate(self.optSet.chartColNames):
            itm1 = QtWidgets.QTableWidgetItem("{0} {1}".format(idx, elem))
            itm1.setFlags(itm1.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramMarquez['sensColChartNbs']:
                itm1.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('red'))
            else:
                itm1.setCheckState(QtCore.Qt.Unchecked)

            itm2 = QtWidgets.QTableWidgetItem("")
            itm2.setFlags(itm2.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramMarquez['mnColChartNbs']:
                itm2.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('blue'))
            else:
                itm2.setCheckState(QtCore.Qt.Unchecked)

            itm3 = QtWidgets.QTableWidgetItem("")
            itm3.setFlags(itm3.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx == self.optSet.paramOpt['mvtcolumn']:
                itm3.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('magenta'))
            else:
                itm3.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidget_6.setItem(idx, 0, itm1)
            self.tableWidget_6.setItem(idx, 1, itm2)
            self.tableWidget_6.setItem(idx, 2, itm3)
            self.tableWidget_6.item(idx, 0).\
                setBackground(QtGui.QColor('LavenderBlush'))
        self.tableWidget_6.resizeColumnsToContents()
        self.tableWidget_6.cellClicked.connect(self.chart_cell_was_clicked)
        # ################################################################
        #              Parameters for VSCD Optimization                  #
        # ################################################################
        self.tableWidget_7.setRowCount(len(self.optSet.paramVSCDName))
        self.tableWidget_7.setColumnCount(2)
        self.tableWidget_7.verticalHeader().hide()
        self.tableWidget_7.horizontalHeader().hide()
        for idx, elem in enumerate(self.optSet.paramVSCDName):
            item1 = QtWidgets.QTableWidgetItem("{0} {1}".format(idx, elem))
            # item1.setTextAlignment(QtCore.Qt.AlignLeft)
            txt = self.optSet.paramVSCDValue[idx]
            item2 = QtWidgets.QTableWidgetItem("{0}".format(txt))
            item2.setSizeHint(QtCore.QSize(500, 0))
            self.tableWidget_7.setItem(idx, 0, item1)
            self.tableWidget_7.setItem(idx, 1, item2)
            self.tableWidget_7.item(idx, 0).\
                setBackground(QtGui.QColor(self.optSet.paramVSCDCoul[idx]))
        self.tableWidget_7.resizeColumnsToContents()
        # ################################################################
        #              Parameters for Marquez Optimization               #
        # ################################################################
        self.tableWidget_8.setRowCount(len(self.optSet.paramMarquezName))
        self.tableWidget_8.setColumnCount(2)
        self.tableWidget_8.verticalHeader().hide()
        self.tableWidget_8.horizontalHeader().hide()
        for idx, elem in enumerate(self.optSet.paramMarquezName):
            item1 = QtWidgets.QTableWidgetItem("{0} {1}".format(idx, elem))
            txt = self.optSet.paramMarquezValue[idx]
            item2 = QtWidgets.QTableWidgetItem("{0}".format(txt))
            item2.setSizeHint(QtCore.QSize(500, 0))
            self.tableWidget_8.setItem(idx, 0, item1)
            self.tableWidget_8.setItem(idx, 1, item2)
            self.tableWidget_8.item(idx, 0).\
                setBackground(QtGui.QColor(self.optSet.paramMarquezCoul[idx]))
        self.tableWidget_8.resizeColumnsToContents()

        # ################################################################
        #                  Select External Stimuli parameters            #
        # ################################################################
        self.tableWidget_9.setRowCount(len(self.optSet.stimParam))
        self.tableWidget_9.setColumnCount(1)
        self.tableWidget_9.verticalHeader().hide()
        self.tableWidget_9.horizontalHeader().hide()
        for idx, elem in enumerate(self.optSet.stimParam):
            itm1 = QtWidgets.QTableWidgetItem(str(elem))
            itm1.setFlags(itm1.flags() | QtCore.Qt.ItemIsUserCheckable)
            txt = self.optSet.stimParam[idx]
            if txt in self.optSet.paramOpt['seriesStimParam']:
                itm1.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('red'))
            else:
                itm1.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidget_9.setItem(idx, 0, itm1)
            self.tableWidget_9.item(idx, 0).\
                setBackground(QtGui.QColor('lightCyan'))
        self.tableWidget_9.resizeColumnsToContents()
        self.tableWidget_9.cellClicked.connect(self.stimPar_cell_was_clicked)

    def meshPath(self):
        # newMeshPath = ""
        # nameLabel = QLabel(newMeshPath)
        # screen = MeshPathForm()
        # screen.show()
        self.animatsimdir = readAnimatLabSimDir()
        if self.animatsimdir != "":
            # subdir = os.path.split(self.animatsimdir)[-1]
            rootname = os.path.dirname(self.animatsimdir)
        else:
            print("First instance - no previous animatlab folder selected")
            rootname = ""
        aprojdirname = QtWidgets.QFileDialog.\
            getExistingDirectory(self, "Pick a folder", rootname)
        # execute getExistingDirectory dialog and set the directory variable
        #  to be equal to the user selected directory

        if aprojdirname:       # if user didn't pick a directory don't continue
            print("You chose: %s" % aprojdirname)
            rootname = os.path.dirname(aprojdirname)
            """
            subdir = os.path.split(aprojdirname)[-1]
            print subdir
            self.folders = FolderOrg(animatlab_root=rootname,
                                     subdir=subdir,
                                     python27_source_dir=self.
                                     animatLabV2ProgDir)
            # self.folders.affectDirectories()
            """
            self.newMeshPath = QtWidgets.QFileDialog.\
                getExistingDirectory(self, "Mesh files Path",
                                     self.rootname)
            if self.newMeshPath:
                print("mesh direvtory: %s" % self.newMeshPath)
                meshPathTxt = convertPath2Text(self.newMeshPath)
                res = changeMeshPath(aprojdirname, meshPathTxt)
                aprojFilePath = res[0]
                aprojtree = res[1]
                changeAproj = res[2]
                # self.btnSaveAproj.setEnabled(True)

                if changeAproj:
                    aprojFileName = os.path.split(aprojFilePath)[-1]
                    OriginalaprojSaveDir = os.path.join(aprojdirname,
                                                        "AprojFilesOriginal")
                    if not os.path.exists(OriginalaprojSaveDir):
                        os.makedirs(OriginalaprojSaveDir)
                        # copyFileDir(self.animatsimdir,
                        #             OriginalaprojSaveDir,
                        #             copy_dir=0)

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
                    print()
                    print("##############################################")
                    print("PLEASE RECREATE THE ASSIM FILE FROM ANIMATLAB")
                    print("##############################################")

        else:
            print("process aborted...")

        # self.model.saveXMLaproj(aprojSaveDir + aprojFileName)
# ==========================================================================
if __name__ == "__main__":
    #import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = ReadAsimAform()
    #ui = Ui_MainWindow()
    #ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
