# -*- coding: utf-8 -*-
"""
Created on Tue Dec  4 16:36:20 2018
@author: cattaert
Creates a txt file with informations on the number of available processors
and the path of AnimatLab program
Translated in Python 3.8 Jan 2023 (D. Cattaert)
"""
import os

from pyqtgraph.Qt import QtCore
from pyqtgraph.Qt import QtGui
from PyQt5 import QtWidgets


class Ui_SetCompInfo(object):
    def setupUi(self, SetComputerInfo):
        self.SetComputerInfo = SetComputerInfo
        self.SetComputerInfo.setObjectName("SetComputerInfo")
        self.SetComputerInfo.resize(300, 150)
        self.centralwidget = QtWidgets.QWidget(self.SetComputerInfo)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        # Create a series of button widgets to be placed inside
        text = "         NO ANIMATLAB V2 CHOSEN!!! PLEASE CHOOSE ONE"
        self.animatLabV2ProgDir = text
        self.valueLabel1 = QtWidgets.QLabel(self.animatLabV2ProgDir)
        self.valueLabel1.setFixedWidth(300)
        self.SetAnimatLabDir = QtWidgets.QPushButton("&Choose AnimatLab Prog Dir")

        buttonLayout2 = QtWidgets.QHBoxLayout()
        valueLabel2 = QtWidgets.QLabel("Nb processors:")
        valueLabel2.setFixedWidth(70)
        self.valueLine2 = QtWidgets.QLineEdit("1")
        self.valueLine2.setFixedWidth(20)
        buttonLayout2.addWidget(valueLabel2)
        buttonLayout2.addWidget(self.valueLine2)

        self.quit_Button = QtWidgets.QPushButton("&OK")

        # Add QHBoxlayout to place the buttons
        buttonLayout1 = QtWidgets.QVBoxLayout()

        # Add widgets to the layout in their proper positions
        buttonLayout1.addWidget(self.valueLabel1)
        buttonLayout1.addWidget(self.SetAnimatLabDir)
        buttonLayout1.addLayout(buttonLayout2)
        buttonLayout1.addWidget(self.quit_Button)

        self.gridLayout.addLayout(buttonLayout1, 0, 1)
        # self.gridLayout.addLayout(buttonLayout2)

        self.SetComputerInfo.setCentralWidget(self.centralwidget)
        self.setLayout(self.gridLayout)
        self.setWindowTitle("Give Computer information")
        QtCore.QMetaObject.connectSlotsByName(self.SetComputerInfo)


class SetComputerInfo(QtWidgets.QMainWindow, Ui_SetCompInfo):
    def __init__(self, dialogue):
        super(SetComputerInfo, self).__init__()
        self.setupUi(self)      # le 2eme self est pour l'argument PlotWindow
        #                       qui est la fenetre elle-meme -> donc self
        self.dialogue = dialogue
        self.to_init()
        self.show()

    def to_init(self):
        self.rootname = ""
        self.animatLabV2ProgDir = ""

        self.SetAnimatLabDir.clicked.connect(self.browse_folder)
        # self.choose_file_Button.clicked.connect(self.choose_file)
        self.text = self.valueLine2
        self.quit_Button.clicked.connect(self.closeIt)

        self.allfiletypes = "All Files (*);;Text Files (*.txt, *.asc, *.par)"
        self.initialfiletypes = "Text Files ('*.txt', '*.asc', '*.par')"
        # nameLabel = QtWidgets.QLabel("Name:")
        # self.nameLine = QtWidgets.QLineEdit()
        self.show

    def browse_folder(self):
        """
        doc string
        """
        self.animatLabV2ProgDir = QtWidgets.QFileDialog.\
            getExistingDirectory(self,
                                 self.dialogue,
                                 self.rootname)
        print(self.animatLabV2ProgDir)
        self.valueLabel1.setText(self.animatLabV2ProgDir)

    def closeIt(self):
        """
        doc string
        """
        self.nb_processors = self.valueLine2.text()
        print("nb_processors:", self.nb_processors)
        with open("infos_computer.txt", 'w') as fich:
            fich.write(self.animatLabV2ProgDir + "\n")
            fich.write("nb_processors=%s\n" % str(self.nb_processors))
            fich.close()
        self.close()


def main():
    """
    doc string
    """
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MyWin = SetComputerInfo("Choose AnimatLabV2 Prog")
    MyWin.show()   # Show the form
    app.exec_()     # and execute the app


# ==========================================================================
#                                   MAIN
# ==========================================================================
if __name__ == '__main__':
    main()
