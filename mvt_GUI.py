# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 10:41:11 2020
Contains the class and procedures used to run the graphic window for movement plots
@author: nrault
Translated in Python 3.8 Jan 2023 (D. Cattaert)
Modified February 22, 2023 (D. Cattaert):
    all pg.Qt.QtGui replaced by pg.Qt.QtWidgets
"""
from pyqtgraph import PlotWidget
from pyqtgraph.Qt import QtCore
from pyqtgraph.Qt import QtWidgets

class Ui_MvtWindow(QtWidgets.QMainWindow):
    def setupUi(self):
        self.setObjectName("MvtWindow")
        self.resize(400, 400)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        # =============  sets one Graph  ===============
        self.pw_mvt = PlotWidget(self.centralwidget)
        self.pw_mvt.setObjectName("pw_mvt")
        self.pw_mvt.setXRange(0, 1)
        self.pw_mvt.setYRange(0, 1)
        self.pw_mvt.addLegend()
        self.pw_mvt.setLabel('left', 'angle', units='degrees',
                             color='black', size='12pt')
        self.pw_mvt.setLabel('bottom', 'time', units='s',
                             color='black', size='12pt')
        self.pw_mvt.showGrid(x=True, y=True)
        # ==============================================
        # Create a series of button widgets to be placed inside
        self.btn_showFirst = QtWidgets.QPushButton('Show First')
        self.btn_showPrev = QtWidgets.QPushButton('Show Prev')
        self.btn_showNext = QtWidgets.QPushButton('Show Next')
        self.btn_showAll = QtWidgets.QPushButton('Show All')
        # self.btn_erase = QtWidgets.QPushButton('ERASE')

        # Add QHBoxlayout to place the buttons
        buttonHLayout1 = QtWidgets.QHBoxLayout()

        # Add widgets to the layout in their proper positions
        # buttonHLayout1.addWidget(self.btn_erase)
        buttonHLayout1.addWidget(self.btn_showFirst)
        buttonHLayout1.addWidget(self.btn_showPrev)
        buttonHLayout1.addWidget(self.btn_showNext)
        buttonHLayout1.addWidget(self.btn_showAll)

        self.check_keepSet = QtWidgets.QCheckBox("Keep Set")
        self.check_keepSet.setChecked(True)
        self.check_bestMvt = QtWidgets.QCheckBox("OnlyBest")
        self.check_bestMvt.setChecked(False)
        self.check_perPacket = QtWidgets.QCheckBox("per Pacquet")
        self.check_perPacket.setChecked(True)
        self.serie_label = QtWidgets.QLabel("##########")
        self.serie_label.setText("mode: show all Sets")
        self.serie_label.setFixedWidth(100)

        # Add QHBoxlayout to place the check buttons
        buttonHLayout2 = QtWidgets.QHBoxLayout()

        # Add widgets to the layout in their proper positions
        buttonHLayout2.addWidget(self.check_keepSet)
        buttonHLayout2.addStretch()
        buttonHLayout2.addWidget(self.serie_label)
        buttonHLayout2.addStretch()
        buttonHLayout2.addWidget(self.check_bestMvt)
        buttonHLayout2.addStretch()
        buttonHLayout2.addWidget(self.check_perPacket)

        self.gridLayout.addWidget(self.pw_mvt, 0, 0, 2, 1)  # plot on left,
        #                                                   # spanning 2 rows
        self.gridLayout.addLayout(buttonHLayout1, 4, 0, 1, 1)
        self.gridLayout.addLayout(buttonHLayout2, 5, 0, 1, 1)

        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 898, 38))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.retranslateMvtUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateMvtUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MvtWindow", "MvtWindow"))

        # self.btn_erase.setStatusTip(_translate("MvtWindow", "Erase curves"))
        # self.btn_erase.setText(_translate("MvtWindow", "Erase"))

        self.btn_showFirst.setStatusTip(_translate("MvtWindow",
                                                   "Show First set"))
        self.btn_showFirst.setText(_translate("MvtWindow", "Show First Set"))

        self.btn_showPrev.setStatusTip(_translate("MvtWindow",
                                                  "Show previous set"))
        self.btn_showPrev.setText(_translate("MvtWindow", "Show previous Set"))

        # self.btn_keepSet.setStatusTip(_translate("MvtWindow", "Keep set"))
        # self.btn_keepSet.setText(_translate("MvtWindow", "Keep Set"))

        self.btn_showNext.setStatusTip(_translate("MvtWindow",
                                                  "Show next set"))
        self.btn_showNext.setText(_translate("MvtWindow", "Show next Set"))

        self.btn_showAll.setStatusTip(_translate("MvtWindow",
                                                 "Show all mvts"))
        self.btn_showAll.setText(_translate("MvtWindow", "Show All Sets"))

        f_b_keepSet = "<html><head/><body><p>keep Sets/graph</p></body></html>"
        self.check_keepSet.setToolTip(_translate("MainWindow", f_b_keepSet))
        self.check_keepSet.setStatusTip(_translate("MainWindow",
                                        "keep/not keep set data in graphs"))
        self.check_keepSet.setText(_translate("MainWindow",
                                              "keep set"))

        f_b_OnlyBest = "<html><head/><body><p>show only best</p></body></html>"
        self.check_bestMvt.setToolTip(_translate("MainWindow", f_b_OnlyBest))
        self.check_bestMvt.setStatusTip(_translate("MainWindow",
                                        "show only best result in each set"))
        self.check_bestMvt.setText(_translate("MainWindow",
                                              "Only best"))

        f_b_perPacqt = "<html><head/>" +\
            "<body><p>show by individual Pacquet</p></body></html>"
        self.check_perPacket.setToolTip(_translate("MainWindow", f_b_perPacqt))
        self.check_perPacket.setStatusTip(_translate("MainWindow",
                                          "show separate result for pacquets"))
        self.check_perPacket.setText(_translate("MainWindow",
                                                "Show packs cont"))


class MvtWin(Ui_MvtWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi()      # le 2eme self est pour l'argument MvtWindow
        #                       qui est la fenetre elle-meme -> donc self
        self.to_init()
        self.show()

    def location_on_the_screen(self, xshift=0, yshift=0):
        ag = QtWidgets.QDesktopWidget().availableGeometry()
        # sg = QtWidgets.QDesktopWidget().screenGeometry()

        widget = self.geometry()
        x = ag.width() - widget.width() - xshift
        # y = 2 * ag.height() - sg.height() - widget.height() - yshift
        y = ag.height() - widget.height() - yshift
        self.move(x, y)

    def to_init(self):
        # self.btn_erase.clicked.connect(self.clearmvt)
        self.btn_showNext.clicked.connect(self.showNextMvtSet)
        # self.btn_showPrev.clicked.connect(self.showPrevMvtSet)
        self.btn_showAll.clicked.connect(self.showAllMvts)

    def showAllMvts(self):
        None

    def showNextMvtSet(self):
        None

    def clearmvt(self):
        None