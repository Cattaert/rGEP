# -*- coding: utf-8 -*-
"""
Created on Fri Jun 29 11:29:39 2018
Modified October 09, 2019 (D. Cattaert):
    Allows now to use up to three columns of check boxes for the same list of
    items
@author: cattaert
Translated in Python 3.8 Jan 2023 (D. Cattaert)

Modified January 23, 2023 (D. Cattaert):
    New procedure: set_values_in_list() allows to change the values of a list
    of variables in a graphic window
Modified February 14, 2023 (D. Cattaert):
    new method added in Form: choose_param00() to test the procedure 
    choose_elements_in_list()
"""
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from pyqtgraph.Qt import QtGui
from pyqtgraph.Qt import QtWidgets
from PyQt5.QtWidgets import QInputDialog, QLineEdit

import sys  # We need sys so that we can pass argv to QApplication

global verbose
verbose = 1


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


class Enter_Values(QtWidgets.QDialog):   # top-level widget to hold everything)
    def __init__(self, GUI_Gr_obj, list_entry_name, list_entry_value,
                 list_val_max, window_name, parent=None):
        super(Enter_Values, self).__init__(parent)
        self.GUI_Gr_obj = GUI_Gr_obj
        self.list_entry_name = list_entry_name
        self.list_entry_value = list_entry_value
        self.list_val_max = list_val_max
        self.resize(200, 100 * (len(list_entry_name) + 1))
        self.valueLabel = []
        self.valueLine = []
        button_HLayout = []
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        button_VLayout = QtWidgets.QVBoxLayout()
        # Create some widgets to be placed inside
        for entry, entry_name in enumerate(self.list_entry_name):
            self.valueLabel.append(QtWidgets.QLabel(list_entry_name[entry]))
            self.valueLabel[entry].setFixedWidth(150)
            self.valueLine.append(QtWidgets.QLineEdit(list_entry_value[entry]))
            self.valueLine[entry].setFixedWidth(100)
            button_HLayout.append(QtWidgets.QHBoxLayout())
            # Add widgets to the layout in their proper positions
            button_HLayout[entry].addWidget(self.valueLabel[entry])
            button_HLayout[entry].addWidget(self.valueLine[entry])
            button_VLayout.addLayout(button_HLayout[entry])
        layout.addLayout(button_VLayout, 0, 0, 1, 1)

        self.OK_btn = QtWidgets.QPushButton('OK')
        layout.addWidget(self.OK_btn, entry+2, 0, 1, 1)
        # layout.addWidget(self.plot, 0, 1, 3, 1)  # plot goes on right side,
        #                                          # spanning 3 rows
        self.setWindowTitle(window_name)
        self.to_init()
        self.OK_btn.clicked.connect(self.accept)

    def screen_loc(self, xshift=0, yshift=0):
        ag = QtWidgets.QDesktopWidget().availableGeometry()
        # sg = QtWidgets.QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = ag.width() - widget.width() - xshift
        # y = 2 * ag.height() - sg.height() - widget.height()
        y = ag.height() - widget.height() - yshift
        self.move(x, y)

    def to_init(self):
        """
        doc string
        """
        # self.show()

    def accept(self):
        """
        doc string
        """
        for entry, entry_name in enumerate(self.list_entry_name):
            if float(self.valueLine[entry].text()) > self.list_val_max[entry]:
                self.valueLine[entry].setText(str(self.list_val_max[entry]))
            print("{}:\t{}".format(entry_name, self.valueLine[entry].text()))
        self.list_value = []
        for entry, entry_name in enumerate(self.list_entry_name):
            self.list_value.append(self.valueLine[entry].text())
        self.GUI_Gr_obj.list_value = self.list_value
        self.close()


class MyMessageBox(QtWidgets.QMessageBox):
    def __init__(self):
        QtWidgets.QMessageBox.__init__(self)
        self.setSizeGripEnabled(True)

    def event(self, e):
        result = QtWidgets.QMessageBox.event(self, e)

        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)
        self.setMinimumWidth(0)
        self.setMaximumWidth(16777215)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)
        textEdit = self.findChild(QtWidgets.QTextEdit)
        if textEdit != None :
            textEdit.setMinimumHeight(0)
            textEdit.setMaximumHeight(16777215)
            textEdit.setMinimumWidth(0)
            textEdit.setMaximumWidth(16777215)
            textEdit.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        return result


def InfoWindow(title, info, message=""):  
    mb = MyMessageBox()     # This a resizeable QMessageBox
    mb.setText(title)
    mb.setInformativeText(info)
    mb.setDetailedText(message)
    mb.exec_()


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


def dialogWindow(titre, info, details=""):
    rep = showdialog(titre, info, details)
    # print(rep)
    if rep == 1024:
        OK = True
    else:
        OK = False
    return OK


def set_values_in_list(dicValues, selected, typ, text):
    """
    Open a wndow with a list of element names and values and ask to modify
    their values.
    in: list_elem = list of names
    out: the single selected name
    """
    list_elem = list(dicValues.keys())
    # list_values = list(dicValues.values())
    """
    dicValues = {}
    for idx, elem in enumerate(list_elem):
        dicValues[elem] = list_values[idx]
    """
    listDic_columns = [{typ: selected}]
    listChoix = list(listDic_columns[0].keys())
    titleText = text
    rep = ChooseInList.listTransmit(parent=None,
                                    graphNo=0,
                                    listChoix=listChoix,
                                    items=list_elem,
                                    listDicItems=listDic_columns,
                                    onePerCol=[0],
                                    colNames=[typ, "Value"],
                                    dicValues=dicValues,
                                    typ="val",
                                    titleText=titleText)
    # print rep
    SelectedNames = []
    listDic_columns = rep[0]
    # choice = listDic_columns[0][typ]
    # self.firstSelectedNames = []
    for i in range(len(listDic_columns[0][listChoix[0]])):
        itemName = listDic_columns[0][listChoix[0]][i]
        SelectedNames.append(itemName)
        dicValues[itemName] = float(rep[1][itemName])
        print(itemName, rep[1][itemName])
    return dicValues


def choose_elements_in_list(list_elem, typ, selected, text):
    """
    Open a wndow with a list of element names and ask to select a single one.
    in: list_elem = list of names to select one from
    out: the single selected name
    """
    listDic_columns = [{typ: selected}]
    listChoix = list(listDic_columns[0].keys())
    titleText = text
    rep = ChooseInList.listTransmit(parent=None,
                                    graphNo=0,
                                    listChoix=listChoix,
                                    items=list_elem,
                                    listDicItems=listDic_columns,
                                    onePerCol=[0],
                                    colNames=[typ],
                                    typ="chk",
                                    titleText=titleText)
    # Create a series from  dic_params_order
    listDic_columns = rep[0]
    choice = listDic_columns[0][typ]
    return choice


def choose_one_element_in_list(title, list_elem, typ):
    """
    Open a wndow with a list of element names and ask to select a single one.
    in: list_elem = list of names to select one from
    out: the single selected name
    """
    listDic_columns = [{typ: list_elem[0]}]
    listChoix = list(listDic_columns[0].keys())
    titleText = title
    rep = ChooseInList.listTransmit(parent=None,
                                    graphNo=0,
                                    listChoix=listChoix,
                                    items=list_elem,
                                    listDicItems=listDic_columns,
                                    onePerCol=[1],
                                    colNames=[typ],
                                    typ="chk",
                                    titleText=titleText)
    # Create a series from  dic_params_order
    listDic_columns = rep[0]
    choice = listDic_columns[0][typ][0]
    return choice


class GetText(QtWidgets.QWidget):
    def __init__(self, inputDialog="Enter text",
                 inputWindow_name="text Input Dialog",
                 selectDialog='Select text:',
                 selectWindow_name='Text Selection Dialog',
                 selectionList=["un", "deux", "trois"], parent=None):
        QtWidgets.QWidget.__init__(self)
        self.setGeometry(200, 100, 300, 300)

        self.inputDialog = inputDialog
        self.inputWindow_name = inputWindow_name
        self.selectDialog = selectDialog
        self.selectWindow_name = selectWindow_name
        self.selectionList = selectionList

        self.input_btn = QtWidgets.QPushButton('Input', self)
        self.input_btn.setGeometry(50, 75, 100, 25)
        self.select_btn = QtWidgets.QPushButton('Select', self)
        self.select_btn.setGeometry(50, 150, 100, 25)

        self.input_btn.clicked.connect(self.getInput)
        self.select_btn.clicked.connect(self.getSelection)

    def getInput(self):
        text = QtWidgets.QInputDialog.getText(self, self.inputWindow_name,
                                              self.inputDialog)
        if text[1]:
            username = text[0]
            print(username)
            return username

    def getSelection(self):
        sel = QtWidgets.QInputDialog.getItem(self, self.selectWindow_name,
                                             self.selectDialog,
                                             self.selectionList, current=0,
                                             editable=False)
        if sel[1]:
            username = sel[0]
            print(username)
            return username


class Form(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.rootname = ""
        self.mydir = ""
        self.allfiletypes = "All Files (*);;Text Files (*.txt, *.asc)"
        self.initialfiletypes = "Text Files (*.txt, *.asc)"
        nameLabel = QtWidgets.QLabel("Name:")
        self.nameLine = QtWidgets.QLineEdit()
        self.browse_folderButton = QtWidgets.QPushButton("&ChooseFolder")
        self.choose_fileButton = QtWidgets.QPushButton("&ChooseFile")
        self.choose_paramButton0 = QtWidgets.QPushButton("&ChooseOneInList")
        self.choose_paramButton00 = QtWidgets.QPushButton("&ChooseseveralInList")
        self.choose_paramButton1 = QtWidgets.QPushButton("&ChooseParam1")
        self.choose_paramButton2 = QtWidgets.QPushButton("&ChooseParam2")
        self.choose_paramButton3 = QtWidgets.QPushButton("&ChooseParam3")
        self.give_ListValuesButton = QtWidgets.QPushButton("&EnterValues")
        self.quitButton = QtWidgets.QPushButton("&Quit")

        buttonLayout1 = QtWidgets.QVBoxLayout()
        buttonLayout1.addWidget(nameLabel)
        buttonLayout1.addWidget(self.nameLine)
        buttonLayout1.addWidget(self.browse_folderButton)
        buttonLayout1.addWidget(self.choose_fileButton)
        buttonLayout1.addWidget(self.choose_paramButton0)
        buttonLayout1.addWidget(self.choose_paramButton00)
        buttonLayout1.addWidget(self.choose_paramButton1)
        buttonLayout1.addWidget(self.choose_paramButton2)
        buttonLayout1.addWidget(self.choose_paramButton3)
        buttonLayout1.addWidget(self.give_ListValuesButton)
        buttonLayout1.addWidget(self.quitButton)

        self.browse_folderButton.clicked.connect(self.browse_folder)
        self.choose_fileButton.clicked.connect(self.choose_file)
        self.choose_paramButton0.clicked.connect(self.choose_param0)
        self.choose_paramButton00.clicked.connect(self.choose_param00)
        self.choose_paramButton1.clicked.connect(self.choose_param1)
        self.choose_paramButton2.clicked.connect(self.choose_param2)
        self.choose_paramButton3.clicked.connect(self.choose_param3)
        self.give_ListValuesButton.clicked.connect(self.set_values)
        self.quitButton.clicked.connect(self.closeIt)

        mainLayout = QtWidgets.QGridLayout()
        # mainLayout.addWidget(nameLabel, 0, 0)
        mainLayout.addLayout(buttonLayout1, 0, 1)

        self.setLayout(mainLayout)
        self.setWindowTitle("Choose a file to process")

        self.listDicItems = []
        self.listDicItems1 = [{'constant': ['NS1_IaExt-ExtAlMn.SynAmp',
                                            'NS1_IaFlx-FlxAlMn.SynAmp']}]

        self.listDicItems2 = [{'X': ['1ExtAlpha_St1.CurrentOn'],
                               'Y': ['1FlxAlpha_St1.CurrentOn']},
                              {'X': ['1ExtGamma_St2.CurrentOn'],
                               'Y': ['1FlxGamma_St2.CurrentOn']}]

        self.listDicItems3 = [{'X': ['1ExtAlpha_St1.CurrentOn'],
                               'Y': ['1FlxAlpha_St1.CurrentOn'],
                               'Z': ['1FlxGamma_St1.CurrentOn']}]

        self.items = ['1ExtAlpha_St1.CurrentOn',
                      '1FlxGamma_St2.CurrentOn',
                      '1FlxGamma_St1.CurrentOn',
                      '1FlxAlpha_St1.CurrentOn',
                      '1ExtGamma_St2.CurrentOn',
                      '1ExtGamma_St1.CurrentOn',
                      'NS1_IaExt-ExtAlMn.SynAmp',
                      'NS1_IaFlx-FlxAlMn.SynAmp']

        self.dicValues = {'1ExtAlpha_St1.CurrentOn': 10.1,
                          '1FlxGamma_St2.CurrentOn': 12.2,
                          '1FlxGamma_St1.CurrentOn': 13.3,
                          '1FlxAlpha_St1.CurrentOn': 14.4,
                          '1ExtGamma_St2.CurrentOn': 15.5,
                          '1ExtGamma_St1.CurrentOn': 16.6,
                          'NS1_IaExt-ExtAlMn.SynAmp': 0.01,
                          'NS1_IaFlx-FlxAlMn.SynAmp': 0.1,
                          }

        self.listChoix1 = ["constant"]
        self.listChoix2 = ["X", "Y"]
        self.listChoix3 = ["X", "Y", "Z"]
        self.onePerCol1 = [0]  # several checks for column 0
        self.onePerCol2 = [1, 1]  # only one check for column 0 and column 1
        self.onePerCol3 = [1, 1, 1]
        self.titleText = "select axes for graph:"
        self.firstSelectedNames = ['1ExtAlpha_St1.CurrentOn',
                                   '1FlxAlpha_St1.CurrentOn']

    def submitContact(self):
        name = self.nameLine.text()

        if name == "":
            QtWidgets.QMessageBox.information(self, "Empty Field",
                                          "Please enter a name and address.")
            return
        else:
            QtWidgets.QMessageBox.information(self, "Success!",
                                          "Hello %s!" % name)

    def browse_folder(self):
        """
        doc string
        """
        self.mydir = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                            "Pick a folder",
                                                            self.rootname)
        print(self.mydir)

    def choose_file(self):
        """
        doc string
        """
        options = QtWidgets.QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        filename = QtWidgets.QFileDialog.\
            getOpenFileName(self,
                            "QFileDialog.getOpenFileName()",
                            self.mydir,
                            self.allfiletypes,
                            self.initialfiletypes,
                            options=options)
        print(filename)

    def closeIt(self):
        """
        doc string
        """
        self.close()

    def choose_param0(self):
        title = "choose one element"
        list_elem = self.items
        typ = "stim"
        choice = choose_one_element_in_list(title, list_elem, typ)
        print(choice)

    def choose_param00(self):
        text = "select sensory neurons to plot"
        list_elem = ['TimeSplice', 'Time', '1FlxPotAlpha','2ExtGamma',
                     '1ExtPotAlpha', '2FlxPotGam', '2FlxGamma', '2ExtPotGam',
                     '1FlxAlpha', '1ExtAlpha', 'Elbow', 'Triceps1', 'Biceps1',
                     '1FlxPN', '1ExtPN', '2ExtIa', '2FlxIa']
        selected = ['2ExtIa', '2FlxIa']
        typ = "chart_col"
        choice = choose_elements_in_list(list_elem, typ, selected, text)
        print(choice)


    def choose_param1(self):
        """
        """
        for graphNo in range(len(self.listDicItems1)):
            rep = ChooseInList.listTransmit(parent=None,
                                            graphNo=graphNo,
                                            listChoix=self.listChoix1,
                                            items=self.items,
                                            listDicItems=self.listDicItems1,
                                            onePerCol=self.onePerCol1,
                                            colNames=["constant", ""],
                                            typ="chk",
                                            titleText=self.titleText)
            print(rep)
            self.listDicItems = rep[0]
            self.firstSelectedNames = self.listDicItems[0][self.listChoix1[0]]

    def choose_param2(self):
        """
        """
        for graphNo in range(len(self.listDicItems2)):
            rep = ChooseInList.listTransmit(parent=None,
                                            graphNo=graphNo,
                                            listChoix=self.listChoix2,
                                            items=self.items,
                                            listDicItems=self.listDicItems2,
                                            onePerCol=self.onePerCol2,
                                            colNames=["X", "Y"],
                                            typ="chk",
                                            titleText=self.titleText)
            self.listDicItems2 = rep[0]
        print(rep)

    def choose_param3(self):
        """
        """
        for graphNo in range(len(self.listDicItems3)):
            rep = ChooseInList.listTransmit(parent=None,
                                            graphNo=graphNo,
                                            listChoix=self.listChoix3,
                                            items=self.items,
                                            listDicItems=self.listDicItems3,
                                            onePerCol=self.onePerCol3,
                                            colNames=["X", "Y", "Z"],
                                            typ="chk",
                                            titleText=self.titleText)
            self.listDicItems3 = rep[0]
        print(rep)

    def set_values(self):
        """
        """
        if self.firstSelectedNames != []:
            print(self.firstSelectedNames)

        rep = ChooseInList.listTransmit(parent=None,
                                        graphNo=0,
                                        listChoix=self.listChoix1,
                                        items=self.items,
                                        listDicItems=self.listDicItems1,
                                        onePerCol=[0],
                                        colNames=["constant", "Value"],
                                        dicValues=self.dicValues,
                                        typ="val",
                                        titleText=self.titleText)
        # print rep
        self.listDicItems = rep[0]
        listChoix1 = self.listChoix1
        self.firstSelectedNames = []
        for i in range(len(self.listDicItems[0][listChoix1[0]])):
            itemName = self.listDicItems[0][listChoix1[0]][i]
            self.firstSelectedNames.append(itemName)
            self.dicValues[itemName] = float(rep[1][itemName])
            print(itemName, rep[1][itemName])


class List_check(QtWidgets.QWidget):
    def __init__(self, parent=None,
                 graphNo=0,
                 listChoix=('choix1', 'choix2'),
                 items=("Spring", "Summer", "Fall", "Winter"),
                 listDicItems=[{'choix1': "Spring", 'choix2': "Fall"},
                               {'choix1': "Summer", 'choix2': "Winter"}],
                 onePerCol=[0, 0],  # several checks allowed in the two columns
                 colNames=["X", "Y"],
                 dicValues={'Spring': 0.1, 'Fall': 0.2},
                 typ="chk",
                 titleText="Choose a season"):
        self.graphNo = graphNo
        self.listChoix = listChoix
        self.items = items
        self.listDicItems = listDicItems
        self.onePerCol = onePerCol
        self.colNames = colNames
        self.dicValues = dicValues
        self.titleText = titleText
        self.typ = typ
        self.centralwidget = parent

        self.splitter_7 = QtWidgets.QSplitter(self.centralwidget)
        self.splitter = QtWidgets.QSplitter(self.splitter_7)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")

        self.tableWidget = QtWidgets.QTableWidget(self.splitter)
        self.tableWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setRowCount(len(self.items))
        if typ == "chk":
            self.tableWidget.setColumnCount(len(listChoix))
        elif typ == "val":
            self.tableWidget.setColumnCount(2)
        self.tableWidget.verticalHeader().hide()
        self.tableWidget.horizontalHeader().hide()

        self.label_1 = QtWidgets.QLabel(self.splitter)
        self.label_1.setEnabled(True)
        self.label_1.setObjectName("label_1")
        lab1tx = "{}"
        lab1 = lab1tx.format(colNames[0])
        if len(onePerCol) > 1:
            lab1tx = "{}\t\t\t\t{}"
            lab1 = lab1tx.format(colNames[0], colNames[1])
        if len(onePerCol) > 2:
            lab1tx = "{}\t\t\t\t{}\t{}"
            lab1 = lab1tx.format(colNames[0], colNames[1], colNames[2])

        self.label_1.setText(lab1)
        # print("listDicItems:", listDicItems)
        self.firstSelectedNames = listDicItems[graphNo][listChoix[0]]
        if len(onePerCol) > 1:
            self.secondSelectedNames = listDicItems[graphNo][listChoix[1]]
        self.firstListNb = []
        self.secondListNb = []
        self.thirdListNb = []
        self.checks = []
        self.col = len(onePerCol)
        # item0 = self.listDicItems[0]
        # graph = 0

    def buildTableWidget(self):
        # self.titleText += str(self.graphNo)
        for idx, elem in enumerate(self.items):
            # print(elem)
            itm1 = QtWidgets.QTableWidgetItem("{} {}".format(idx, elem))
            itm1.setFlags(itm1.flags() | QtCore.Qt.ItemIsUserCheckable)
            itm1.setCheckState(QtCore.Qt.Checked)

            dicVal = self.listDicItems[self.graphNo][self.listChoix[0]]
            if elem in dicVal:
                itm1.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(pg.intColor(self.graphNo, alpha=255))
                self.firstListNb.append(idx)
                # print(idx, elem)
            else:
                itm1.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidget.setItem(idx, 0, itm1)

            if self.col > 1:
                itm2 = QtWidgets.QTableWidgetItem("")
                itm2.setFlags(itm2.flags() | QtCore.Qt.ItemIsUserCheckable)

                dicVal = self.listDicItems[self.graphNo][self.listChoix[1]]
                if elem in dicVal:
                    itm2.setCheckState(QtCore.Qt.Checked)
                    itm1.setForeground(pg.intColor(self.graphNo, alpha=200))
                    self.secondListNb.append(idx)
                    #  print(idx, elem)
                else:
                    itm2.setCheckState(QtCore.Qt.Unchecked)
                self.tableWidget.setItem(idx, 1, itm2)

            if self.col > 2:
                # print "preparing check_boxes for column 3"
                itm3 = QtWidgets.QTableWidgetItem("")
                itm3.setFlags(itm3.flags() | QtCore.Qt.ItemIsUserCheckable)

                dicVal = self.listDicItems[self.graphNo][self.listChoix[2]]
                if elem in dicVal:
                    itm3.setCheckState(QtCore.Qt.Checked)
                    itm2.setForeground(pg.intColor(self.graphNo, alpha=150))
                    itm1.setForeground(pg.intColor(self.graphNo, alpha=150))
                    self.thirdListNb.append(idx)
                    #(print idx, elem)
                else:
                    itm3.setCheckState(QtCore.Qt.Unchecked)
                self.tableWidget.setItem(idx, 2, itm3)

            if self.typ == "val":
                val = self.dicValues[elem]
                # print(self.typ, elem, val)
                itmval = QtWidgets.QTableWidgetItem("{:4.4f}".format(val))
                itmval.setSizeHint(QtCore.QSize(100, 0))
                if elem in dicVal:
                    itmval.setForeground(pg.intColor(self.graphNo, alpha=255))
                else:
                    itmval.setForeground(QtGui.QColor('black'))
                self.tableWidget.setItem(idx, 1, itmval)

            self.tableWidget.item(idx, 0).\
                setBackground(pg.intColor(self.graphNo, alpha=10))

        if verbose > 2:
            print(self.firstListNb)
            if self.col > 1:
                print(self.secondListNb)
        self.tableWidget.resizeColumnsToContents()


class ChooseInList(QtWidgets.QDialog):
    """
    GetList creates a window with a list of QPushButtons and associatd QLabels
    The QPushButtons are defined by listChoix and the list of QLabels by items.
    A QGridLayout is used to dispose QPushButtons and QLabels.
    In the QLabel, a default element of the items list is displayed
    A dictionary is used to set the association of listChoix elements with an
    element of the items list selected by the user
    In call to the class procedure is made by the included function
    listTransmit. A list of dictionaries (listDicItems) is sent with the actual
    listChoix.
    When the user clicks on one of the QPushButton the list of items is
    presented and the user select one item.
    If the default item is OK, then closing the window confirms the default
    items for each QPushButton (presneting listChoix elements)
    A newlistDicItems is then returned.
    """
    MESSAGE = "<p>Message boxes have a caption, a text, and up to three " \
        "buttons, each with standard or custom texts.</p>" \
        "<p>Click a button to close the message box. Pressing the Esc " \
        "button will activate the detected escape button (if any).</p>"

    def __init__(self, parent=None,
                 graphNo=0,
                 listChoix=('choix1', 'choix2'),
                 items=("Spring", "Summer", "Fall", "Winter"),
                 listDicItems=[{'choix1': "Spring", 'choix2': "Fall"},
                               {'choix1': "Summer", 'choix2': "Winter"}],
                 onePerCol=[0, 0],  # several checks allowed in the two columns
                 colNames=["X", "Y"],
                 dicValues={'Spring': 0.1, 'Fall': 0.2},
                 typ="val",
                 titleText="Choose a season"):
        super(ChooseInList, self).__init__(parent)
        self.graphNo = graphNo
        self.listChoix = listChoix
        self.items = items
        self.listDicItems = listDicItems
        self.newlistDicItems = {}
        self.onePerCol = onePerCol
        self.colNames = colNames
        self.dicValues = dicValues
        self.newdicValues = {}
        self.typ = typ
        self.titleText = titleText

        self.centralwidget = QtWidgets.QWidget()
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        # ---------------------------------------------------------
        # Check list selection
        lchk = List_check(graphNo=self.graphNo,
                          parent=self.centralwidget,
                          listChoix=self.listChoix,
                          items=self.items,
                          listDicItems=self.listDicItems,
                          onePerCol=self.onePerCol,
                          colNames=self.colNames,
                          dicValues=self.dicValues,
                          typ=typ,
                          titleText=self.titleText)
        lchk.buildTableWidget()
        self.tableWidget = lchk.tableWidget
        self.label_1 = lchk.label_1

        self.gridLayout.addWidget(self.label_1, 0, 1, 1, 2)
        self.gridLayout.addWidget(self.tableWidget, 1, 1)
        # self.tableWidget.cellClicked.connect(self.list_was_clicked)
        self.col = lchk.col
        self.firstListNb = lchk.firstListNb
        self.secondListNb = lchk.secondListNb
        self.thirdListNb = lchk.thirdListNb
        self.titleText = lchk.titleText

        # self.gridLayout.addWidget(self.label_1, 0, 1, 1, 2)
        # self.gridLayout.addWidget(self.tableWidget, 1, 1)

        self.tableWidget.cellClicked.connect(self.list_was_clicked)

        self.dialogText = []
        self.itemLabel = []
        self.itemButton = []
        self.itemList = []

        buttonLayout_select = QtWidgets.QVBoxLayout()
        self.clickAllButton = QtWidgets.QPushButton("Select all")
        self.clickAllButton.clicked.connect(self.selectall)
        buttonLayout_select.addWidget(self.clickAllButton)
        self.unclickAllButton = QtWidgets.QPushButton("Deselect all")
        self.unclickAllButton.clicked.connect(self.unselectall)
        buttonLayout_select.addWidget(self.unclickAllButton)
        self.gridLayout.addLayout(buttonLayout_select, 1, 2)

        self.oKButton = QtWidgets.QPushButton("OK")
        self.oKButton.clicked.connect(self.closeIt)
        self.escButton = QtWidgets.QPushButton("Escape")
        self.escButton.clicked.connect(self.escape)
        self.gridLayout.addWidget(self.oKButton, 2, 1)
        self.gridLayout.addWidget(self.escButton, 2, 2)
        self.setLayout(self.gridLayout)
        self.setWindowTitle(self.titleText)

    def selectall(self):
        if self.onePerCol == [0]:
            column = 0
            for row in range(len(self.items)):
                item = self.tableWidget.item(row, column)
                item.setCheckState(QtCore.Qt.Checked)
                self.list_was_clicked(row, column)

    def unselectall(self):
        if self.onePerCol == [0]:
            column = 0
            for row in range(len(self.items)):
                # print(row, end=' ')
                item = self.tableWidget.item(row, column)
                item.setCheckState(QtCore.Qt.Unchecked)
                # print("item selected")
                self.list_was_clicked(row, column)

    def escape(self):
        self.close()

    def closeIt(self):
        """
        doc string
        """
        # print("self.listDicItems:", self.listDicItems)
        self.newlistDicItems = self.listDicItems
        # print("self.newlistDicItems:", self.newlistDicItems)
        # print("self.firstListNb=", self.firstListNb)
        # print("self.secondListNb=", self.secondListNb)
        # print("self.thirdListNb=", self.thirdListNb)
        dic = self.listDicItems[self.graphNo]
        dic[self.listChoix[0]] = [self.items[idx] for idx in self.firstListNb]
        if self.col > 1:
            dic[self.listChoix[1]] =\
                [self.items[idx] for idx in self.secondListNb]
        if self.col > 2:
            dic[self.listChoix[2]] =\
                [self.items[idx] for idx in self.thirdListNb]

        self.newlistDicItems[self.graphNo] = dic
        # print("parent ->  newlistDicItems:", self.newlistDicItems)

        if self.typ == "val":
            self.newdicValues = {}
            for idx, elem in enumerate(self.items):
                valstr = self.tableWidget.item(idx, 1).text()
                self.newdicValues[elem] = valstr
                # print(elem, valstr)
            # print(self.newdicValues)

        self.close()

    def list_was_clicked(self, row, column):
        """
        self.tableWidget.cellClicked implicitly sends the row and the column of
        the clicked item.
        With these informations, "cell_was_clicked" procedure will update the
        list of elements that are clicked in each of the columns.
        """
        # print("row: ", row, "column: ", column)
        oneChk = self.onePerCol
        col = len(oneChk)
        rep = self.cell_was_clicked(self.tableWidget, self.items,
                                    row, column, oneChk, col=col, typ=self.typ)
        self.firstListNb = rep[0]
        self.secondListNb = rep[1]
        self.thirdListNb = rep[2]

        # self.thirdListNb = rep[2]  # unused in this example
        # it is possible to use directy here the selected value to fill other
        # tableWidgets...

        """
        # example
        itm1 = QtWidgets.QTableWidgetItem(str(self.firstListNb))
        itm2 = QtWidgets.QTableWidgetItem(str(self.secondListNb))
        # itm2 and itm2 are list of string numbers for each checked elements
        # in column 1 and column 2 that can be used to update other widgets:
        # self.tableWidget_7.setItem(14, 1, itm1)
        # self.tableWidget_7.setItem(13, 1, itm2)
        """
        # print("self.firstListNb:", self.firstListNb)
        # if self.col > 1:
        #    print("self.secondListNb:", self.secondListNb)

    def cell_was_clicked(self, tableWidgt, listName,
                         row, column, oneChk, col, typ):
        """
        updates the list of checked elements for each column (firstChkList,
        secondChkList, ...) and returns these actualized lists
        """
        firstChkList = []
        secondChkList = []
        thirdChkList = []
        firstListNb = []
        secondListNb = []
        thirdListNb = []
        listValues = []
        # =====================================================
        # Set fills the state of each box on all columns
        # =====================================================
        for i in range(len(listName)):
            if col >= 1:
                item1 = tableWidgt.item(i, 0)
                if not oneChk[0]:
                    if item1.checkState() == 0:
                        firstChkList.append(0)
                    else:
                        firstChkList.append(1)
                else:
                    if column == 0:
                        if i != row:
                            # print("i:", i, " row:", row, item3.checkState())
                            if item1.checkState() == 2:  # previous check
                                item1.setForeground(QtGui.QColor('black'))
                                print("previous checked:", i)
                            item1.setCheckState(QtCore.Qt.Unchecked)
                            firstChkList.append(0)
                        else:
                            item1.setCheckState(QtCore.Qt.Checked)
                            firstChkList.append(1)
                    else:
                        if item1.checkState() == 0:
                            firstChkList.append(0)
                        else:
                            firstChkList.append(1)

            if col >= 2:
                item2 = tableWidgt.item(i, 1)
                if not oneChk[1]:
                    if item2.checkState() == 0:
                        secondChkList.append(0)
                    else:
                        secondChkList.append(1)
                else:
                    if column == 1:
                        if i != row:
                            # print "i:", i, " row:", row, item3.checkState()
                            if item2.checkState() == 2:  # previous check
                                item1.setForeground(QtGui.QColor('black'))
                                print("previous checked:", i)
                            item2.setCheckState(QtCore.Qt.Unchecked)
                            secondChkList.append(0)
                        else:
                            item2.setCheckState(QtCore.Qt.Checked)
                            secondChkList.append(1)
                    else:
                        if item2.checkState() == 0:
                            secondChkList.append(0)
                        else:
                            secondChkList.append(1)

            if col >= 3:
                item3 = tableWidgt.item(i, 2)
                if not oneChk[2]:  # several checked boxes in the list
                    if item3.checkState() == 0:
                        thirdChkList.append(0)
                    else:
                        thirdChkList.append(1)
                else:       # only one checked box at a time in the list
                    if column == 2:
                        if i != row:
                            # print("i:", i, " row:", row, item3.checkState())
                            if item3.checkState() == 2:  # previous check
                                item1.setForeground(QtGui.QColor('black'))
                                print("previous checked:", i)
                            item3.setCheckState(QtCore.Qt.Unchecked)
                            thirdChkList.append(0)
                        else:
                            item3.setCheckState(QtCore.Qt.Checked)
                            thirdChkList.append(1)
                            # print "new checked:", i
                    else:
                        if item3.checkState() == 0:
                            thirdChkList.append(0)
                        else:
                            thirdChkList.append(1)
            # print(tableWidgt.item(row, 2))
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
                if typ == "val":
                    itmval = tableWidgt.item(row, 1)
                    itmval.setForeground(QtGui.QColor('black'))
            else:
                firstChkList[row] = 1
                item1.setForeground(pg.intColor(self.graphNo, alpha=255))
                if typ == "val":
                    itmval = tableWidgt.item(row, 1)
                    itmval.setForeground(pg.intColor(self.graphNo, alpha=255))
                if col >= 2:
                    item2.setCheckState(QtCore.Qt.Unchecked)
                    secondChkList[row] = 0
                if col >= 3:
                    item3.setCheckState(QtCore.Qt.Unchecked)
                    thirdChkList[row] = 0
        elif column == 1:
            if typ != "val":  # column 1 may be values...
                if (item2.checkState() == 0):
                    secondChkList[row] = 0
                    item1.setForeground(QtGui.QColor('black'))
                else:
                    secondChkList[row] = 1
                    item1.setForeground(pg.intColor(self.graphNo, alpha=200))
                    item1.setCheckState(QtCore.Qt.Unchecked)
                    firstChkList[row] = 0
                    if col >= 3:
                        item3.setCheckState(QtCore.Qt.Unchecked)
                        thirdChkList[row] = 0
        elif column == 2:
            if item3.checkState() == 0:
                thirdChkList[row] = 0
                item1.setForeground(QtGui.QColor('black'))
            else:
                thirdChkList[row] = 1
                item1.setForeground(pg.intColor(self.graphNo, alpha=150))
                item1.setCheckState(QtCore.Qt.Unchecked)
                item2.setCheckState(QtCore.Qt.Unchecked)
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
            # print(thirdListNb)
        # print("col", col, thirdChkList, "oneChk", oneChk, "thirdNb", thirdNb)
        # print("thirdListNb", thirdListNb)

        return [firstListNb, secondListNb, thirdListNb, listValues]

    def listtransmit_info(self):
        """
        Function used to transmit the self.newlistDicItems to "listTransmit"
        """
        # return self.itemList
        # self.newlistDicItems.append(self.newdicValues)
        if self.typ == "val":
            return [self.newlistDicItems, self.newdicValues]
        else:
            return [self.newlistDicItems]

    @staticmethod
    def listTransmit(parent=None,
                     graphNo=0,
                     listChoix=('choix1', 'choix2'),
                     items=("Spring", "Summer", "Fall", "Winter"),
                     listDicItems={'choix1': "Spring", 'choix2': "Fall"},
                     onePerCol=0,
                     colNames=["X", "Y"],
                     dicValues={'Spring': 0.1, 'Fall': 0.2},
                     typ="chk",
                     titleText="Choose a season:"):
        """
        Entry of the GetList class application. It works as a staticmethod
        and returns newlistDicItems
        """

        dialog = ChooseInList(parent,
                              graphNo,
                              listChoix,
                              items,
                              listDicItems,
                              onePerCol,
                              colNames,
                              dicValues,
                              typ,
                              titleText)
        dialog.exec_()  # si on veut bloquant
        # item_list = dialog.listtransmit_info()
        newlistDicItems = dialog.listtransmit_info()[0]
        if newlistDicItems == {}:     # if we did not click any item...
            newlistDicItems = listDicItems
            if verbose > 2:
                print("no click.... keep default")
                print('classe enfant unchanged: {}'.format(newlistDicItems))
        if len(newlistDicItems) < len(listChoix):       # we removed one key...
            for name in listChoix:
                if name not in listChoix:
                    del newlistDicItems[name]
            # print('classe enfant changed -: {}'.format(newlistDicItems))

        # else:                                     # a new key was added
            # print('classe enfant changed +: {}'.format(newlistDicItems))
        # if newdicValues == {}:
            # newdicValues = dicValues
        if typ == "val":
            newdicValues = dialog.listtransmit_info()[1]
            return [newlistDicItems, newdicValues]
        else:
            return [newlistDicItems]


def main():
    """
    doc string
    """
    # import sys
    app = QtWidgets.QApplication(sys.argv)
    win = Form()
    win.show()   # Show the form
    app.exec_()     # and execute the app


# ==========================================================================
#                                   MAIN
# ==========================================================================
if __name__ == '__main__':
    main()
