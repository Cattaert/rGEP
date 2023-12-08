# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 10:48:12 2020
Contain the class used to build the graphic window used for parameter plots
@authors: D. Cattaert and N. Rault
Translated in Python 3.8 Jan 2023 (D. Cattaert)
Modified February 22, 2023 (D. Cattaert):
    all pg.Qt.QtGui replaced by pg.Qt.QtWidgets
Modified April 06, 2023 (D. Cattaert):
    pg.graphicWindow replaced by pg.GraphicsLayoutWidget
"""
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from pyqtgraph.Qt import QtWidgets


class UI_ParamWin(QtWidgets.QMainWindow):
    def setupUi(self):
        self.setObjectName("PlotWindow")
        self.resize(400, 400)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        # =============  sets one Graph  ===============
        self.pw_param = pg.GraphicsLayoutWidget(title="Behavior")
        self.plot_item = self.pw_param.addPlot()
        self.curve = self.plot_item.plot(pen='y')
        self.curve_slope = self.plot_item.plot(pen=pg.mkPen('b', width=5))
        self.symbol = self.plot_item.plot(pen='b', symbol='o')
        self.plot_item.setObjectName("pw_param")
        self.plot_item.setXRange(0, 1)
        self.plot_item.setYRange(0, 1)
        self.plot_item.addLegend()
        self.plot_item.setLabel('left', 'param_y', units='unit_y',
                                color='black', size='12pt')
        self.plot_item.setLabel('bottom', 'param_x', units='unit_x',
                                color='black', size='12pt')
        self.plot_item.showGrid(x=True, y=True)
        # ==============================================

        # Add QHBoxlayout to place the buttons
        self.buttonHLayout1 = QtWidgets.QHBoxLayout()
        self.buttonHLayout1.setObjectName("ButtonHLayout")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        # Add widgets to the layout in their proper positions
        self.verticalLayout.addWidget(self.pw_param)
        self.verticalLayout.addLayout(self.buttonHLayout1)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 898, 38))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.plot_item.addItem(self.vLine, ignoreBounds=True)
        self.plot_item.addItem(self.hLine, ignoreBounds=True)
        self.retranslatePltUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslatePltUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("PlotWindow", "ParamWindow"))


class ParamWin(UI_ParamWin):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi()      # le 2eme self est pour l'argument PlotWindow
        #                       qui est la fenetre elle-meme -> donc self
        self.to_init()
        self.show()

    def screen_loc(self, xshift=0, yshift=0):
        ag = QtWidgets.QDesktopWidget().availableGeometry()
        # sg = QtWidgets.QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = ag.width() - widget.width() - xshift
        # y = 2 * ag.height() - sg.height() - widget.height()
        y = ag.height() - widget.height() - yshift
        self.move(x, y)

    def to_init(self):
        None
        # self.btn_rangetot.clicked.connect(self.totalRange)

    def totalRange(self):
        None

    def clearParam(self):
        None
