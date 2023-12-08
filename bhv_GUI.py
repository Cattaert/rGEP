# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 10:44:59 2020 (form D.Cattaert script)
@author: nrault
Translated in Python 3.8 Jan 2023 (D. Cattaert)
Modified May 16, 2023 (D. Cattaert):
    Scale of Bhv plot changed to (0, 500) for ordinate
"""
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from pyqtgraph.Qt import QtWidgets


class Ui_BhvWindow(QtWidgets.QMainWindow):
    def setupUi(self):
        self.setObjectName("BhvWindow")
        self.resize(400, 400)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        # =============  sets one Graph  ==============
        # self.pw_bhv = pg.GraphicsWindow(title="Behavior")
        self.pw_bhv = pg.GraphicsLayoutWidget()
        # self.plot_item = self.pw_bhv.addPlot(title='Behavior')
        self.plot_item = self.pw_bhv.addPlot()

        self.curve = self.plot_item.plot(pen='y')
        self.curve_slope = self.plot_item.plot(pen=pg.mkPen('b', width=5))
        self.symbol = self.plot_item.plot(pen='b', symbol='o')
        self.plot_item.setObjectName("pw_bhv")
        self.plot_item.setXRange(0, 120)
        self.plot_item.setYRange(0, 500)
        self.plot_item.addLegend()
        self.plot_item.setLabel('left', 'duration', units='s',
                                color='black', size='12pt')
        self.plot_item.setLabel('bottom', 'angle', units='degrees',
                                color='black', size='12pt')
        self.plot_item.showGrid(x=True, y=True)
        # =============================================

        # Create a series of button widgets to be placed inside
        self.btn_erase = QtWidgets.QPushButton('ERASE')
        self.btn_mse_filter = QtWidgets.QPushButton('Filter/mse')
        self.btn_coactP_filt = QtWidgets.QPushButton('Filter/coactP')
        self.btn_cst_filter = QtWidgets.QPushButton('flter/cont')
        self.btn_showAll = QtWidgets.QPushButton('Show All')

        # Add QHBoxlayout to place the buttons
        self.buttonHLayout1 = QtWidgets.QHBoxLayout()
        self.buttonHLayout1.setObjectName("ButtonHLayout")
        # Add widgets to the H1 layout in their proper positions
        self.buttonHLayout1.addWidget(self.btn_erase)
        self.buttonHLayout1.addWidget(self.btn_mse_filter)
        self.buttonHLayout1.addWidget(self.btn_coactP_filt)
        self.buttonHLayout1.addWidget(self.btn_cst_filter)

        self.buttonHLayout1.addWidget(self.btn_showAll)

        self.check_select_curs = QtWidgets.QCheckBox("Activate curs_region")
        self.check_select_curs.setChecked(False)
        self.btn_selctRegion = QtWidgets.QPushButton('Select in curs_region')
        self.btn_unselect = QtWidgets.QPushButton('Unselect dots')

        # Add QHBoxlayout to place the check buttons
        self.buttonHLayout2 = QtWidgets.QHBoxLayout()
        self.buttonHLayout2.setObjectName("Check&ButtonHLayout")
        # Add widgets to the H2 layout in their proper positions
        self.buttonHLayout2.addWidget(self.check_select_curs)
        self.buttonHLayout2.addWidget(self.btn_selctRegion)
        self.buttonHLayout2.addStretch()
        self.buttonHLayout2.addWidget(self.btn_unselect)

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        # Add widgets to the layout in their proper positions
        self.verticalLayout.addWidget(self.pw_bhv)
        self.verticalLayout.addLayout(self.buttonHLayout1)
        self.verticalLayout.addLayout(self.buttonHLayout2)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 898, 38))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.codeCoul_df = None
        self.retranslateBhvUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateBhvUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("BhvWindow", "BhvWindow"))

        self.btn_erase.setStatusTip(_translate("BhvWindow", "Erase curves"))
        self.btn_erase.setText(_translate("BhvWindow", "Erase"))

        self.btn_mse_filter.setStatusTip(_translate("BhvWindow",
                                                    "Select data with mseThr"))
        self.btn_mse_filter.setText(_translate("BhvWindow", "Filter/mse"))

        self.btn_cst_filter.setStatusTip(_translate("BhvWindow",
                                                    "Select data with const"))
        self.btn_cst_filter.setText(_translate("BhvWindow", "filter/const"))

        self.btn_selctRegion.setStatusTip(_translate("BhvWindow",
                                          "Select bhv between cursors"))
        self.btn_selctRegion.setText(_translate("BhvWindow", "select/curs"))

        self.btn_unselect.setStatusTip(_translate("BhvWindow",
                                       "Unselect points selected/mouse click"))
        self.btn_unselect.setText(_translate("BhvWindow", "UnselectDots"))

        self.btn_showAll.setStatusTip(_translate("BhvWindow",
                                                 "Show all behav data"))
        self.btn_showAll.setText(_translate("BhvWindow", "Show All Sets"))


class BhvWin(Ui_BhvWindow):
    # class BhvWin(pg.PlotWidget, Ui_BhvWindow):
    def __init__(self, win):
        super(self.__class__, self).__init__()
        self.setupUi()      # le 2eme self est pour l'argument PlotWindow
        #                       qui est la fenetre elle-meme -> donc self
        self.to_init()
        self.targetwin = None
        self.df_parremain = None
        self.win = win
        self.show()

    def location_on_the_screen(self, xshift=0, yshift=0):
        ag = QtWidgets.QDesktopWidget().availableGeometry()
        # sg = QtWidgets.QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = ag.width() - widget.width() - xshift
        y = ag.height() - widget.height() - yshift
        self.move(x, y)

    def to_init(self):
        self.btn_erase.clicked.connect(self.clearbvt)
        self.btn_cst_filter.clicked.connect(self.bhv_filterWithCst)
        self.btn_coactP_filt.clicked.connect(self.bhv_filterWithCoactP)
        self.btn_mse_filter.clicked.connect(self.bhv_filterWithMse)
        self.btn_selctRegion.clicked.connect(self.bhv_show_between_curs)
        self.btn_showAll.clicked.connect(self.showAllBhvs)

    def set_region(self):
        self.region = pg.LinearRegionItem()
        self.region.setRegion([40, 45])
        self.region.setZValue(10)
        self.plot_item.addItem(self.region, ignoreBounds=True)

        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.plot_item.addItem(self.vLine, ignoreBounds=True)
        self.plot_item.addItem(self.hLine, ignoreBounds=True)
        self.vb = self.plot_item.vb
        self.proxy = pg.SignalProxy(self.pw_bhv.scene().sigMouseMoved,
                                    rateLimit=60, slot=self.mouseMoved)
        self.region.sigRegionChanged.connect(self.update)

    def clear_region(self):
        self.plot_item.removeItem(self.region)
        self.plot_item.removeItem(self.vLine)
        self.plot_item.removeItem(self.hLine)

    def showAllBhvs(self):
        None

    def bhv_filterWithCst(self):
        None

    def bhv_filterWithCoactP(self):
        None

    def bhv_filterWithMse(self):
        None

    def bhv_show_between_curs(self):
        None

    def clearbvt(self):
        None

    def update(self):
        self.region.setZValue(10)
        self.minX, self.maxX = self.region.getRegion()
        # print minX, maxX

    def closest(self, df, point):
        xaim = point[0]
        yaim = point[1]
        behav_X = self.win.bhv_names[self.win.behav_col[0]]
        behav_Y = self.win.bhv_names[self.win.behav_col[1]]
        # poss_ypos = df.dur_mvt2 == (yaim + min(abs(df.dur_mvt2 - yaim)))
        poss_ypos = df[behav_Y] == (yaim + min(abs(df[behav_Y] - yaim)))
        list_booly = list(poss_ypos)
        if True not in list_booly:
            # poss_ypos = df.dur_mvt2 == (yaim - min(abs(df.dur_mvt2 - yaim)))
            poss_ypos = df[behav_Y] == (yaim - min(abs(df[behav_Y] - yaim)))
        choix_df = df[poss_ypos]
        if len(choix_df) > 1:
            poss_xpos = choix_df[behav_X] == (xaim +
                                              min(abs(choix_df.endangle
                                                      - xaim)))
            list_boolx = list(poss_xpos)
            if True not in list_boolx:
                poss_xpos = choix_df[behav_X] == (xaim -
                                                  min(abs(choix_df[behav_X] -
                                                          xaim)))
            choix_df = choix_df[poss_xpos]
        ypos = float(choix_df.iloc[0][behav_Y])
        xpos = float(choix_df.iloc[0][behav_X])
        rg = int(choix_df.iloc[0]["rgserie"])
        return xpos, ypos, rg

    def mouseMoved(self, evt):
        pos = evt[0]  # using signal proxy turns original arguments into a
        #               tuple
        if self.plot_item.sceneBoundingRect().contains(pos):
            self.mousePoint = self.vb.mapSceneToView(pos)
            index = int(self.mousePoint.x())

            if index > 0 and index < 100:
                None
                # print index,


# TODO : to continue GEP procedures

            """
            self=win
            xpos = self.bhvPlot.mousePoint.x()
            ypos = self.bhvPlot.mousePoint.y()
            point = [xpos, ypos]
            df = self.bhvPlot.codeCoul_df
            self.df_parremain = self.bhvPlot.df_parremain
            self.targetwin = self.bhvPlot.targetwin
            """

            xpos = self.mousePoint.x()
            ypos = self.mousePoint.y()
            self.ypos = ypos
            if self.codeCoul_df is not None:
                df = self.codeCoul_df
                # draws the hline and vline on selected point and gets its rg
                self.xpos, self.ypos, rg = self.closest(df, [xpos, ypos])
                self.vLine.setPos(self.xpos)
                self.hLine.setPos(self.ypos)

                # draws hlines and vlines on all paramWindpws
                df_par = self.df_parremain
                namex = self.win.listDicGraphs[0]["abscissa"]
                namey = self.win.listDicGraphs[0]["ordinate"]
                x = float(df_par.loc[rg][namex])
                y = float(df_par.loc[rg][namey])
                # if self.win (MaFenetre) was not called from "GUI_Graph"
                if self.win.main_mode is True:
                    self.win.vLine.setPos(x)
                    self.win.hLine.setPos(y)
                else:
                    pargr = self.win.nbactivepargraphs
                    self.win.screen[pargr].vLine.setPos(x)
                    self.win.screen[pargr].hLine.setPos(y)
                if self.targetwin is not None:
                    for pargr in range(self.win.nbactivepargraphs):
                        namex = self.win.listDicGraphs[pargr+1]["abscissa"]
                        namey = self.win.listDicGraphs[pargr+1]["ordinate"]
                        x = float(df_par.loc[rg][namex])
                        y = float(df_par.loc[rg][namey])
                        self.win.screen[pargr].vLine.setPos(x)
                        self.win.screen[pargr].hLine.setPos(y)
