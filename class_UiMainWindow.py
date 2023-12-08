# -*- coding: utf-8 -*-
"""
Created on Fri Mar 06 10:35:16 2020
Defines the graphic window elements used in GEP_GUI.py
Translated in Python 3.8 Jan 2023 (D. Cattaert)
Modified February 20, 2023 (D. Cattaert):
    Color of command buttons are now blue (inactive) or red (actve)
    Modifications made also in GEP_GUI, accordingly
Modified February 23, 2023 (D. Cattaert):
    pg.graphicWindow replaced by pg.GraphicsLayoutWidget
"""
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from pyqtgraph.Qt import QtWidgets


class Ui_MainWindow(QtWidgets.QMainWindow):
    """
    Class Ui_MainWindow
        extends object
        This class aims to setup every graphical component used in the class
        MaFenetre
    """
    def setupUi(self):
        """
        Method setupUi
            In : self
                MainWindow : an instance of the class MaFenetre
            This method setup every graphical component of the class MaFenetre
        """
        self.setObjectName("MainWindow")
        self.resize(600, 900)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        # =============  sets Param Graph  ==================
        self.pw_param = pg.GraphicsLayoutWidget(title="Parameters")
        self.parplt_itm = self.pw_param.addPlot()
        self.curve = self.parplt_itm.plot(pen='g')
        self.curve_slope = self.parplt_itm.plot(pen=pg.mkPen('b', width=5))
        self.symbol = self.parplt_itm.plot(pen='b', symbol='o')
        self.parplt_itm.setObjectName("pw_param")
        self.parplt_itm.setXRange(0, 1)
        self.parplt_itm.setYRange(0, 1)
        self.parplt_itm.addLegend()
        self.parplt_itm.setLabel('left', 'param0', units='')
        self.parplt_itm.setLabel('bottom', 'param1', units='')
        self.parplt_itm.showGrid(x=True, y=True)
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.parplt_itm.addItem(self.vLine, ignoreBounds=True)
        self.parplt_itm.addItem(self.hLine, ignoreBounds=True)
        """
        roi = pg.ROI([-8, 14], [6, 5])
        roi.addScaleHandle([0.5, 1], [0.5, 0.5])
        roi.addScaleHandle([0, 0.5], [0.5, 0.5])
        self.parplt_itm.addItem(roi)
        roi.setZValue(10)  # make sure ROI is drawn above image
        """
        # ===================================================
        self.gridLayout.addWidget(self.pw_param, 0, 0, 2, 1)

        # =============  sets Mse/Coact Graph  ==============
        self.pw_mse_coact = pg.GraphicsLayoutWidget(title="Mse/Coact")
        self.mseplt_itm = self.pw_mse_coact.addPlot()
        self.curve = self.mseplt_itm.plot(pen='y')
        self.curve_slope = self.mseplt_itm.plot(pen=pg.mkPen('b', width=5))
        self.symbol = self.mseplt_itm.plot(pen='b', symbol='o')
        self.mseplt_itm.setXRange(0, 2000)
        self.mseplt_itm.setYRange(0, 2000)
        self.mseplt_itm.addLegend()
        self.mseplt_itm.setLabel('left', 'coactpenality', units='',
                                 color='black', size='12pt')
        self.mseplt_itm.setLabel('bottom', 'mse', units='',
                                 color='black', size='12pt')
        self.mseplt_itm.showGrid(x=True, y=True)
        # ================================================
        self.gridLayout.addWidget(self.pw_mse_coact, 2, 0, 2, 1)



        """ ============ Left Last lines buttons============  """
        # ================================================ 
        buttonLayout0 = QtWidgets.QVBoxLayout()
        # ================================================
        spacerItem = QtWidgets.QSpacerItem(90, 2,
                                       QtWidgets.QSizePolicy.Expanding,
                                       QtWidgets.QSizePolicy.Minimum)

        """ Pre first line """
        buttonLayout00 = QtWidgets.QHBoxLayout()
        # ------------------------------------------------
        buttonLayout00.addItem(spacerItem)    # allows line expansion
        # ------------------------------------------------
        valueLabelExplain = QtWidgets.QLabel("Launch btns")
        valueLabelExplain.setFixedWidth(105)
        buttonLayout00.addWidget(valueLabelExplain)
        buttonLayout0.addLayout(buttonLayout00)

        """ first line """
        buttonLayout1 = QtWidgets.QHBoxLayout()
        self.check1 = QtWidgets.QCheckBox("Checkbox1")
        # check1.setText("Checkbox 1")
        self.check1.setChecked(True)
        self.check2 = QtWidgets.QCheckBox("Checkbox2")
        # check1.setText("Checkbox 2")
        self.bg = QtWidgets.QButtonGroup()
        self.bg.addButton(self.check1, 1)
        self.bg.addButton(self.check2, 2)

        buttonLayout1.addWidget(self.check1)
        buttonLayout1.addWidget(self.check2)
        # ------------------------------------------------
        buttonLayout1.addItem(spacerItem)    # allows line expansion
        # ------------------------------------------------
        valueLabel0b = QtWidgets.QLabel("runs Nb:")
        valueLabel0b.setFixedWidth(40)
        self.valueLine0b = QtWidgets.QLineEdit("200")
        self.valueLine0b.setFixedWidth(40)
        buttonLayout1.addWidget(valueLabel0b)
        buttonLayout1.addWidget(self.valueLine0b)
        self.btn_systParam = QtWidgets.QPushButton(self.centralwidget)
        self.btn_systParam.setObjectName("btn_systParam")
        self.btn_systParam.setFixedWidth(65)
        self.btn_systParam.setStyleSheet('QPushButton {background-color: #A3C1DA;\
                                                       color: blue;}')
        buttonLayout1.addWidget(self.btn_systParam)
        # ------------------------------------------------
        buttonLayout0.addLayout(buttonLayout1)
        # ================================================

        """ second line """
        buttonLayout2 = QtWidgets.QHBoxLayout()
        self.chk_MSE = QtWidgets.QCheckBox("chk_MSE")
        self.chk_MSE.setChecked(True)
        buttonLayout2.addWidget(self.chk_MSE)
        self.chk_varmse = QtWidgets.QCheckBox("chk_varmse")
        self.chk_varmse.setChecked(False)
        buttonLayout2.addWidget(self.chk_varmse)

        # self.bg2 = QtWidgets.QButtonGroup()
        # self.bg2.addButton(self.chk_MSE, 1)
        # self.bg2.addButton(self.chk_varmse, 2)
        # ------------------------------------------------
        buttonLayout2.addItem(spacerItem)    # allows line expansion
        # ------------------------------------------------
        valueLabel1a = QtWidgets.QLabel("Runs/Pack:")
        valueLabel1a.setFixedWidth(50)
        self.valueLine1a = QtWidgets.QLineEdit("10")
        self.valueLine1a.setFixedWidth(40)
        buttonLayout2.addWidget(valueLabel1a)
        buttonLayout2.addWidget(self.valueLine1a)
        valueLabel1b = QtWidgets.QLabel(" runs Nb:")
        valueLabel1b.setFixedWidth(40)
        self.valueLine1b = QtWidgets.QLineEdit("10")
        self.valueLine1b.setFixedWidth(40)
        buttonLayout2.addWidget(valueLabel1b)
        buttonLayout2.addWidget(self.valueLine1b)
        self.btn_randParam = QtWidgets.QPushButton(self.centralwidget)
        self.btn_randParam.setObjectName("btn_randParam")
        self.btn_randParam.setFixedWidth(65)
        self.btn_randParam.setStyleSheet('QPushButton {background-color: #A3C1DA;\
                                                       color: blue;}')
        buttonLayout2.addWidget(self.btn_randParam)
        # ------------------------------------------------
        buttonLayout0.addLayout(buttonLayout2)
        # ================================================
        """ third line """
        buttonLayout3 = QtWidgets.QHBoxLayout()
        self.chkBx_autoGEP = QtWidgets.QCheckBox("chkBx_autoGEP")
        self.chkBx_autoGEP.setChecked(True)
        buttonLayout3.addWidget(self.chkBx_autoGEP)
        aimBhvLabel = QtWidgets.QLabel(" Aim Bhv:")
        aimBhvLabel.setFixedWidth(42)
        self.aimBhvValueX = QtWidgets.QLineEdit("80")
        self.aimBhvValueX.setFixedWidth(30)
        self.aimBhvValueY = QtWidgets.QLineEdit("80")
        self.aimBhvValueY.setFixedWidth(30)
        self.aimBhvValueX.setStyleSheet("color: gray;")
        self.aimBhvValueY.setStyleSheet("color: gray;")
        buttonLayout3.addWidget(aimBhvLabel)
        buttonLayout3.addWidget(self.aimBhvValueX)
        buttonLayout3.addWidget(self.aimBhvValueY)
        # ------------------------------------------------
        buttonLayout3.addItem(spacerItem)    # allows line expansion
        # ------------------------------------------------
        valueLabel2a = QtWidgets.QLabel("neighbrs:")
        valueLabel2a.setFixedWidth(42)
        self.valueLine2a = QtWidgets.QLineEdit("1")
        self.valueLine2a.setFixedWidth(20)
        buttonLayout3.addWidget(valueLabel2a)
        buttonLayout3.addWidget(self.valueLine2a)
        label_nbExt = QtWidgets.QLabel(" Nb ext:")
        label_nbExt.setFixedWidth(35)
        self.value_nbExt = QtWidgets.QLineEdit("100")
        self.value_nbExt.setFixedWidth(25)
        buttonLayout3.addWidget(label_nbExt)
        buttonLayout3.addWidget(self.value_nbExt)
        label_nbFill = QtWidgets.QLabel(" Nb fill:")
        label_nbFill.setFixedWidth(30)
        self.value_nbFill = QtWidgets.QLineEdit("50")
        self.value_nbFill.setFixedWidth(25)
        buttonLayout3.addWidget(label_nbFill)
        buttonLayout3.addWidget(self.value_nbFill)
        # valueLabel2b = QtWidgets.QLabel(" sigmaGEP:")
        # valueLabel2b.setFixedWidth(50)
        # self.valueLine2b = QtWidgets.QLineEdit("0.1")
        # self.valueLine2b.setFixedWidth(40)
        # buttonLayout3.addWidget(valueLabel2b)
        # buttonLayout3.addWidget(self.valueLine2b)
        self.btn_GEPrand = QtWidgets.QPushButton(self.centralwidget)
        self.btn_GEPrand.setObjectName("btn_GEPrand")
        self.btn_GEPrand.setFixedWidth(65)
        self.btn_GEPrand.setStyleSheet('QPushButton {background-color: #A3C1DA;\
                                                     color: blue;}')
        buttonLayout3.addWidget(self.btn_GEPrand)
        # ------------------------------------------------
        buttonLayout0.addLayout(buttonLayout3)
        # ================================================
        """ fourth line """
        buttonLayout4 = QtWidgets.QHBoxLayout()
        # ------------------------------------------------
        buttonLayout4.addItem(spacerItem)    # allows line expansion
        # ------------------------------------------------
        valueLabel4b = QtWidgets.QLabel("save threshold:")
        valueLabel4b.setFixedWidth(72)
        self.valueLine4b = QtWidgets.QLineEdit("Var")
        self.valueLine4b.setFixedWidth(30)
        buttonLayout4.addWidget(valueLabel4b)
        buttonLayout4.addWidget(self.valueLine4b)
        valueLabel5 = QtWidgets.QLabel(" sigmaCMAes:")
        valueLabel5.setFixedWidth(65)
        self.valueLine5 = QtWidgets.QLineEdit("0.01")
        self.valueLine5.setFixedWidth(50)
        buttonLayout4.addWidget(valueLabel5)
        buttonLayout4.addWidget(self.valueLine5)
        valueLabel3 = QtWidgets.QLabel(" runs Nb:")
        valueLabel3.setFixedWidth(40)
        self.valueLine3 = QtWidgets.QLineEdit("100")
        self.valueLine3.setFixedWidth(40)
        buttonLayout4.addWidget(valueLabel3)
        buttonLayout4.addWidget(self.valueLine3)
        self.btn_CMAes = QtWidgets.QPushButton(self.centralwidget)
        self.btn_CMAes.setObjectName("btn_CMAes")
        self.btn_CMAes.setFixedWidth(65)
        self.btn_CMAes.setStyleSheet('QPushButton {background-color: #A3C1DA;\
                                                   color: blue;}')
        buttonLayout4.addWidget(self.btn_CMAes)
        # self.btn_command4 = QPushButton(self.centralwidget)
        # self.btn_command4.setObjectName("btn_command4")
        # self.btn_command4.setFixedWidth(100)
        # buttonLayout4.addWidget(self.btn_command4)
        buttonLayout0.addLayout(buttonLayout4)
        # ================================================
        """ fifth line """
        layoutLine5 = QtWidgets.QHBoxLayout()
        # ------------------------------------------------
        layoutLine5.addItem(spacerItem)    # allows line expansion
        # ------------------------------------------------
        deltacoeffLabel = QtWidgets.QLabel("  deltacoeff:")
        deltacoeffLabel.setFixedWidth(60)
        self.deltacoeffValue = QtWidgets.QLineEdit("0.01")
        self.deltacoeffValue.setFixedWidth(30)
        layoutLine5.addWidget(deltacoeffLabel)
        layoutLine5.addWidget(self.deltacoeffValue)
        buttonLayout0.addLayout(layoutLine5)
        """
        nbsyntrialsLabel = QtWidgets.QLabel(" nbsyntrials:")
        nbsyntrialsLabel.setFixedWidth(60)
        self.nbsyntrialsValue = QtWidgets.QLineEdit("1")
        self.nbsyntrialsValue.setFixedWidth(30)
        layoutLine5.addWidget(nbsyntrialsLabel)
        layoutLine5.addWidget(self.nbsyntrialsValue)
        """
        nbstepsLabel = QtWidgets.QLabel(" nbsteps:")
        nbstepsLabel.setFixedWidth(42)
        self.nbstepsValue = QtWidgets.QLineEdit("3")
        self.nbstepsValue.setFixedWidth(30)
        layoutLine5.addWidget(nbstepsLabel)
        layoutLine5.addWidget(self.nbstepsValue)
        nbepochLabel = QtWidgets.QLabel(" nbepoch:")
        nbepochLabel.setFixedWidth(45)
        self.nbepochValueLine = QtWidgets.QLineEdit("1")
        self.nbepochValueLine.setFixedWidth(30)
        layoutLine5.addWidget(nbepochLabel)
        layoutLine5.addWidget(self.nbepochValueLine)
        self.btn_VSCD = QtWidgets.QPushButton(self.centralwidget)
        self.btn_VSCD.setObjectName("btn_VSCD")
        self.btn_VSCD.setFixedWidth(65)
        self.btn_VSCD.setStyleSheet('QPushButton {background-color: #A3C1DA;\
                                                  color: blue;}')
        layoutLine5.addWidget(self.btn_VSCD)
        buttonLayout0.addLayout(layoutLine5)
        # ================================================
        vertical_space = QtWidgets.QHBoxLayout()
        space_label = QtWidgets.QLabel("   ")
        vertical_space.addWidget(space_label)
        buttonLayout0.addLayout(vertical_space)
        # ================================================

        """ sixth line """
        layoutLine6 = QtWidgets.QHBoxLayout()
        self.chkBx_saveAllMvts = QtWidgets.QCheckBox("chkBx_saveAllMvts")
        self.chkBx_saveAllMvts.setChecked(False)
        layoutLine6.addWidget(self.chkBx_saveAllMvts)
        # valueLabel4 = QtWidgets.QLabel(" Use Global span:")
        # valueLabel4.setFixedWidth(60)
        # ------------------------------------------------
        # layoutLine6.addItem(spacerItem)    # allows line expansion
        # ------------------------------------------------
        self.chkBx_glob_span = QtWidgets.QCheckBox("Use global span(%) :")
        self.chkBx_glob_span.setChecked(False)
        # layoutLine6.addWidget(valueLabel4)
        layoutLine6.addWidget(self.chkBx_glob_span)
        self.glob_span_val = QtWidgets.QLineEdit("100")
        self.glob_span_val.setFixedWidth(30)
        self.glob_span_val.setStyleSheet("color: gray;")
        layoutLine6.addWidget(self.glob_span_val)
        # ------------------------------------------------
        layoutLine6.addItem(spacerItem)    # allows line expansion
        # ------------------------------------------------
        self.chkBox_const = QtWidgets.QCheckBox("Set const params")
        self.chkBox_const.setChecked(False)
        # self.btn_fixParam = QtWidgets.QPushButton(self.centralwidget)
        # self.btn_fixParam.setObjectName("btn_fixParam")
        # self.btn_fixParam.setFixedWidth(150)
        layoutLine6.addWidget(self.chkBox_const)
        # layoutLine6.addWidget(self.btn_fixParam)
        buttonLayout0.addLayout(layoutLine6)
        # ================================================
        """ seventh line """
        layoutLine7 = QtWidgets.QHBoxLayout()
        label_bhv_ordinate = QtWidgets.QLabel("CHOOSE BEHAVIOR ORDINATE!!!:")
        label_bhv_ordinate.setFixedWidth(160)
        layoutLine7.addWidget(label_bhv_ordinate)
        # ------------------------------------------------
        layoutLine7.addItem(spacerItem)    # allows line expansion
        # ------------------------------------------------
        self.chkBx_bhv_duration = QtWidgets.QCheckBox("bhv_ordinate_duration")
        self.chkBx_bhv_duration.setChecked(False)
        layoutLine7.addWidget(self.chkBx_bhv_duration)
        # ------------------------------------------------
        # layoutLine7.addItem(spacerItem)    # allows line expansion
        # ------------------------------------------------
        self.chkBx_bhv_maxSpeed = QtWidgets.QCheckBox("bhv_ordinate_maxSpeed")
        self.chkBx_bhv_maxSpeed.setChecked(True)
        layoutLine7.addWidget(self.chkBx_bhv_maxSpeed)

        self.b_bhv = QtWidgets.QButtonGroup()
        self.b_bhv.addButton(self.chkBx_bhv_duration, 1)
        self.b_bhv.addButton(self.chkBx_bhv_maxSpeed, 2)
        buttonLayout0.addLayout(layoutLine7)
        # ================================================
        """ eigth line """
        layoutLine8 = QtWidgets.QHBoxLayout()
        # self.chkBx_cost_OK = QtWidgets.QCheckBox("chkBx_cost_OK")
        # self.chkBx_cost_OK.setChecked(False)
        # layoutLine8.addWidget(self.chkBx_cost_OK)
        labelGravity = QtWidgets.QLabel("Gravity:")
        labelGravity.setFixedWidth(40)
        self.editValueGravity = QtWidgets.QLineEdit("-9.81")
        self.editValueGravity.setFixedWidth(40)
        layoutLine8.addWidget(labelGravity)
        layoutLine8.addWidget(self.editValueGravity)
        # ------------------------------------------------
        layoutLine8.addItem(spacerItem)    # allows line expansion
        # ------------------------------------------------
        labelCoactPen1 = QtWidgets.QLabel("  Coactpenality1:")
        labelCoactPen1.setFixedWidth(80)
        self.valueCoactPen1 = QtWidgets.QLineEdit("500")
        self.valueCoactPen1.setFixedWidth(30)
        layoutLine8.addWidget(labelCoactPen1)
        layoutLine8.addWidget(self.valueCoactPen1)
        # ------------------------------------------------
        layoutLine8.addItem(spacerItem)    # allows line expansion
        # ------------------------------------------------
        labelCoactPen2 = QtWidgets.QLabel("  Coactpenality2:")
        labelCoactPen2.setFixedWidth(80)
        self.valueCoactPen2 = QtWidgets.QLineEdit("500")
        self.valueCoactPen2.setFixedWidth(30)
        layoutLine8.addWidget(labelCoactPen2)
        layoutLine8.addWidget(self.valueCoactPen2)

        buttonLayout0.addLayout(layoutLine8)
        # ================================================

        # ================================================
        self.gridLayout.addLayout(buttonLayout0, 4, 0, 1, 1)
        # ================================================

        # =========== Right 1st Case buttons==============
        buttonLayoutR1 = QtWidgets.QVBoxLayout()
        buttonLayoutR1.setGeometry(QtCore.QRect(360, 50, 141, 80))
        self.btn_clear_pw_param = QtWidgets.QPushButton(self.centralwidget)
        self.btn_clear_pw_param.setObjectName("btn_clear_pw_param")
        buttonLayoutR1.addWidget(self.btn_clear_pw_param)
        self.btn_scaleTot_pw_param = QtWidgets.QPushButton(self.centralwidget)
        self.btn_scaleTot_pw_param.setObjectName("btn_scaleTot_pw_param")
        buttonLayoutR1.addWidget(self.btn_scaleTot_pw_param)
        self.btn_choose_pw_param = QtWidgets.QPushButton(self.centralwidget)
        self.btn_choose_pw_param.setObjectName("btn_choose_pw_param")
        buttonLayoutR1.addWidget(self.btn_choose_pw_param)
        """
        buttonLayout00 = QtWidgets.QHBoxLayout()
        self.btn_next_parpair = QtWidgets.QPushButton(self.centralwidget)
        self.btn_next_parpair.setObjectName("btn_next_params")
        self.btn_prev_parpair = QtWidgets.QPushButton(self.centralwidget)
        self.btn_prev_parpair.setObjectName("btn_prev_params")
        buttonLayout00.addWidget(self.btn_prev_parpair)
        buttonLayout00.addWidget(self.btn_next_parpair)
        buttonLayoutR1.addLayout(buttonLayout00)
        """
        self.btn_show_allgraphs = QtWidgets.QPushButton(self.centralwidget)
        self.btn_show_allgraphs.setObjectName("btn_showAll_params")
        buttonLayoutR1.addWidget(self.btn_show_allgraphs)
        # self.btn_addROI = QtWidgets.QPushButton(self.centralwidget)
        # self.btn_addROI.setObjectName('add ROI')
        # buttonLayoutR1.addWidget(self.btn_addROI)
        self.gridLayout.addLayout(buttonLayoutR1, 0, 2, 1, 1)
        # ================================================

        # =========== Right 2nd Case buttons==============
        buttonLayoutR2 = QtWidgets.QVBoxLayout()
        buttonLayoutR2.setGeometry(QtCore.QRect(360, 50, 141, 80))
        self.btn_clear_pw_behav = QtWidgets.QPushButton(self.centralwidget)
        self.btn_clear_pw_behav.setObjectName("btn_clear_pw_behav")
        self.btn_getinfo_chart = QtWidgets.QPushButton(self.centralwidget)
        self.btn_getinfo_chart.setObjectName("btn_getinfo_chart")
        buttonLayoutR2.addWidget(self.btn_clear_pw_behav)
        buttonLayoutR2.addWidget(self.btn_getinfo_chart)
        self.gridLayout.addLayout(buttonLayoutR2, 2, 2, 1, 1)
        # ================================================

        # ==========Right bottom Case buttons=============
        buttonLayoutR3 = QtWidgets.QVBoxLayout()
        buttonLayoutR3_1 = QtWidgets.QHBoxLayout()
        self.btn_getfile = QtWidgets.QPushButton(self.centralwidget)
        self.btn_getfile.setObjectName("btn_getfile")
        buttonLayoutR3_1.addWidget(self.btn_getfile)

        buttonLayoutR3_2 = QtWidgets.QHBoxLayout()
        self.btn_getseeds = QtWidgets.QPushButton(self.centralwidget)
        self.btn_getseeds.setObjectName("btn_getSeeds")
        buttonLayoutR3_2.addWidget(self.btn_getseeds)

        buttonLayoutR3_3 = QtWidgets.QHBoxLayout()
        self.btn_addcharts = QtWidgets.QPushButton(self.centralwidget)
        self.btn_addcharts.setObjectName("btn_addcharts")
        buttonLayoutR3_3.addWidget(self.btn_addcharts)
        
        """
        buttonLayoutR3_4 = QtWidgets.QHBoxLayout()
        self.btn_mkpdf = QtWidgets.QPushButton(self.centralwidget)
        self.btn_mkpdf.setToolTip("")
        self.btn_mkpdf.setObjectName("btn_mkpdf")
        buttonLayoutR3_4.addWidget(self.btn_mkpdf)
        """

        buttonLayoutR3_4 = QtWidgets.QHBoxLayout()
        self.btn_Reset = QtWidgets.QPushButton(self.centralwidget)
        self.btn_Reset.setObjectName("btn_Reset")
        buttonLayoutR3_4.addWidget(self.btn_Reset)
        self.btn_quit = QtWidgets.QPushButton(self.centralwidget)
        self.btn_quit.setToolTip("")
        self.btn_quit.setObjectName("btn_quit")
        buttonLayoutR3_4.addWidget(self.btn_quit)

        buttonLayoutR3.addLayout(buttonLayoutR3_1)
        buttonLayoutR3.addLayout(buttonLayoutR3_2)
        buttonLayoutR3.addLayout(buttonLayoutR3_3)
        # buttonLayoutR3.addLayout(buttonLayout9)
        buttonLayoutR3.addLayout(buttonLayoutR3_4)

        self.gridLayout.addLayout(buttonLayoutR3, 4, 2, 1, 1)
        # ================================================

        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 898, 38))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi()
        # self.btn_quit.clicked.connect(self.MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))

        # ===================================================================
        #                     parameter graph buttons
        # ===================================================================
        f_b_cl_pargraph = "<html><head/><body><p>" +\
            "Clears Param plot but keeps data in memory</p></body></html>"
        self.btn_clear_pw_param.setToolTip(_translate("MainWindow",
                                                      f_b_cl_pargraph))
        self.btn_clear_pw_param.setStatusTip(_translate("MainWindow",
                                                        "Clear Param Graph"))
        self.btn_clear_pw_param.setText(_translate("MainWindow",
                                                   "Clear parameter graph"))

        f_b_cl_scTot_param = "<html><head/><body><p>" +\
            "Plot all param graphs with scale range [0, 1] </p></body></html>"
        self.btn_scaleTot_pw_param.setToolTip(_translate("MainWindow",
                                                         f_b_cl_scTot_param))
        self.btn_scaleTot_pw_param.setStatusTip(_translate("MainWindow",
                                                "plot param whole scale"))
        self.btn_scaleTot_pw_param.setText(_translate("MainWindow",
                                           "plot param whole scale"))

        f_b_cl_choose_graph = "<html><head/><body><p>" +\
            "Chooses which pair of parameters to plot</p></body></html>"
        self.btn_choose_pw_param.setToolTip(_translate("MainWindow",
                                                       f_b_cl_choose_graph))
        self.btn_choose_pw_param.setStatusTip(_translate("MainWindow",
                                                         "Choose Param Plot"))
        self.btn_choose_pw_param.setText(_translate("MainWindow",
                                                    "Choose params to plot"))

        """
        f_b_cl_prev_parpair = "<html><head/><body><p>" +\
            "Plots the previous pair of parameters</p></body></html>"
        self.btn_prev_parpair.setToolTip(_translate("MainWindow",
                                                    f_b_cl_prev_parpair))
        self.btn_prev_parpair.setStatusTip(_translate("MainWindow",
                                                      "plots prev params"))
        self.btn_prev_parpair.setText(_translate("MainWindow",
                                                 "Previous"))

        f_b_cl_next_parpair = "<html><head/><body><p>" +\
            "Plots the next pair of parameters</p></body></html>"
        self.btn_next_parpair.setToolTip(_translate("MainWindow",
                                                    f_b_cl_next_parpair))
        self.btn_next_parpair.setStatusTip(_translate("MainWindow",
                                                      "plots next params"))
        self.btn_next_parpair.setText(_translate("MainWindow",
                                                 "Next"))
        """

        f_b_cl_show_allgraphs = "<html><head/><body><p>" +\
            "Plots all parameter graphs</p></body></html>"
        self.btn_show_allgraphs.setToolTip(_translate("MainWindow",
                                           f_b_cl_show_allgraphs))
        self.btn_show_allgraphs.setStatusTip(_translate("MainWindow",
                                             "plots all param graph"))
        self.btn_show_allgraphs.setText(_translate("MainWindow",
                                        "All param Graphs ON"))
        """
        f_b_cl_addROI = "<html><head/><body><p>" +\
            "Adds a R.O.I to select params</p></body></html>"
        self.btn_addROI.setToolTip(_translate("MainWindow",
                                              f_b_cl_addROI))
        self.btn_addROI.setStatusTip(_translate("MainWindow",
                                                "adds a ROI in param graph"))
        self.btn_addROI.setText(_translate("MainWindow",
                                           "Add ROI in param Graph"))
        """
        f_b_cl_behavgr = "<html><head/><body><p>" +\
            "clears Behav plot but keeps data in memory</p></body></html>"
        self.btn_clear_pw_behav.setToolTip(_translate("MainWindow",
                                                      f_b_cl_behavgr))
        self.btn_clear_pw_behav.setStatusTip(_translate("MainWindow",
                                                        "Clear Behav Graph"))
        self.btn_clear_pw_behav.setText(_translate("MainWindow",
                                                   "Clear behaviour graph"))

        f_b_getinfo_chart = "<html><head/><body><p>" +\
            "opens a chart file to calculate mse, varmse...</p></body></html>"
        self.btn_getinfo_chart.setToolTip(_translate("MainWindow",
                                                     f_b_getinfo_chart))
        self.btn_getinfo_chart.setStatusTip(_translate("MainWindow",
                                                       "Get info/chartFile"))
        self.btn_getinfo_chart.setText(_translate("MainWindow",
                                                  "Get info/chartFile"))

        # ===================================================================
        #                     File read / save  buttons
        # ===================================================================
        f_b_getfile = "<html><head/><body><p>" +\
            "Opens a file of param-behav for plotting or going on" +\
            "</p></body></html>"
        self.btn_getfile.setToolTip(_translate("MainWindow", f_b_getfile))
        self.btn_getfile.setStatusTip(_translate("MainWindow",
                                                 "Choose a data file to plot"))
        self.btn_getfile.setText(_translate("MainWindow", "Open a file"))

        f_b_getseeds = "<html><head/><body><p>" +\
            "Prepres a new folder with GEPData containing seeds for GEPn" +\
            "</p></body></html>"
        self.btn_getseeds.setToolTip(_translate("MainWindow", f_b_getseeds))
        self.btn_getseeds.setStatusTip(_translate("MainWindow",
                                                  "Prepare Folder with seeds"))
        self.btn_getseeds.setText(_translate("MainWindow", "Get seeds"))
        
        f_b_getcharts = "<html><head/><body><p>" +\
            "Prepres a new folder with added charts from valid params" +\
            "</p></body></html>"
        self.btn_addcharts.setToolTip(_translate("MainWindow", f_b_getcharts))
        self.btn_addcharts.setStatusTip(_translate("MainWindow",
                                                  "Builds a new trial" +\
                                                  "subdir with newcharts"))
        self.btn_addcharts.setText(_translate("MainWindow", "Add charts"))
        
        """
        f_btn_mkpdf = "<html><head/><body><p>makes graph pdf</p></body></html>"
        self.btn_mkpdf.setToolTip(_translate("MainWindow", f_btn_mkpdf))
        self.btn_mkpdf.setStatusTip(_translate("MainWindow",
                                               "makes/saves data Graphs/pdf"))
        self.btn_mkpdf.setText(_translate("MainWindow", "Graphs & pdf"))
        """

        """
        f_b_setspan = "<html><body><p>" +\
            "Set the different span of exploration" +\
            "</p></body></html>"
        self.btn_set_span.setToolTip(_translate("MainWindow", f_b_setspan))
        self.btn_set_span.setStatusTip(_translate("MainWindow",
                                                    "Sets the span values"))
        self.btn_set_span.setText(_translate("MainWindow", "Set span"))
        """

        # ===================================================================
        #                     run control buttons
        # ===================================================================
        f_b_Check1 = "<html><head/><body><p>syst & randParam</p></body></html>"
        self.check1.setToolTip(_translate("MainWindow", f_b_Check1))
        self.check1.setStatusTip(_translate("MainWindow",
                                            "syst + randparam for each set"))
        self.check1.setText(_translate("MainWindow", "syst/randParam"))

        f_b_Check2 = "<html><head/><body><p>syst & CMAES</p></body></html>"
        self.check2.setToolTip(_translate("MainWindow", f_b_Check2))
        self.check2.setStatusTip(_translate("MainWindow",
                                            "syst + CMAES for each set"))
        self.check2.setText(_translate("MainWindow", "syst/CMAES"))

        f_b_systParam = "<html><head/><body><p>SystExplor</p></body></html>"
        self.btn_systParam.setToolTip(_translate("MainWindow", f_b_systParam))
        txt = "systematic exploration of parameters"
        self.btn_systParam.setStatusTip(_translate("MainWindow", txt))
        self.btn_systParam.setText(_translate("MainWindow", "SystPar"))

        f_b_randParam = "<html><head/><body><p>Run RandParam</p></body></html>"
        self.btn_randParam.setToolTip(_translate("MainWindow", f_b_randParam))
        self.btn_randParam.setStatusTip(_translate("MainWindow",
                                                   "param Random exploration"))
        self.btn_randParam.setText(_translate("MainWindow", "RandPar"))

        f_b_GEPrand = "<html><head/><body><p>Run RandBehav</p></body></html>"
        self.btn_GEPrand.setToolTip(_translate("MainWindow", f_b_GEPrand))
        self.btn_GEPrand.setStatusTip(_translate("MainWindow",
                                                 "Run params from behavs"))
        self.btn_GEPrand.setText(_translate("MainWindow", "GEPrand"))

        f_b_chkBx_auto = "<html><head/><body><p>select GEP with " +\
            "automatic aim search</p></body></html>"
        self.chkBx_autoGEP.setToolTip(_translate("MainWindow", f_b_chkBx_auto))
        self.chkBx_autoGEP.setStatusTip(_translate("MainWindow",
                                        "select mode with automatic aim GEP"))
        self.chkBx_autoGEP.setText(_translate("MainWindow", "Auto aim"))

        f_b_chkBx_MSE = "<html><head/><body><p>select Random progress by " +\
            "best MSE search</p></body></html>"
        self.chk_MSE.setToolTip(_translate("MainWindow", f_b_chkBx_MSE))
        self.chk_MSE.setStatusTip(_translate("MainWindow",
                                  "select oriented random by MSE"))
        self.chk_MSE.setText(_translate("MainWindow", "/MSE"))

        f_b_chkBx_varmse = "<html><head/><body><p>select Random progress by" +\
            " best varmse search (for GEP)</p></body></html>"
        self.chk_varmse.setToolTip(_translate("MainWindow", f_b_chkBx_varmse))
        self.chk_varmse.setStatusTip(_translate("MainWindow",
                                     "select oriented random by varmse"))
        self.chk_varmse.setText(_translate("MainWindow", "/varmse"))

        f_b_CMAes = "<html><head/><body><p>runs CMAES</p></body></html>"
        self.btn_CMAes.setToolTip(_translate("MainWindow", f_b_CMAes))
        self.btn_CMAes.setStatusTip(_translate("MainWindow", "run CMAES"))
        self.btn_CMAes.setText(_translate("MainWindow", "CMAES"))

        f_b_VSCD = "<html><head/><body><p>runs VSCD</p></body></html>"
        self.btn_VSCD.setToolTip(_translate("MainWindow", f_b_VSCD))
        self.btn_VSCD.setStatusTip(_translate("MainWindow",
            "run Variable Step Coordinate Descent optimization"))
        self.btn_VSCD.setText(_translate("MainWindow", "VSCD"))

        f_b_chkBx_cst = "<html><head/><body><p>select constant " +\
            "Parameters</p></body></html>"
        self.chkBox_const.setToolTip(_translate("MainWindow", f_b_chkBx_cst))
        self.chkBox_const.setStatusTip(_translate("MainWindow",
                                       "select constant parameters"))
        self.chkBox_const.setText(_translate("MainWindow", "Set Const Param"))

        f_b_chkBx_saveAllMvts = "<html><head/><body><p>save all mvts" +\
            "with acceptable varmse</p></body></html>"
        self.chkBx_saveAllMvts.setToolTip(_translate("MainWindow",
                                                     f_b_chkBx_saveAllMvts))
        self.chkBx_saveAllMvts.setStatusTip(_translate("MainWindow",
                                            "save all mvts wit varmse OK"))
        self.chkBx_saveAllMvts.setText(_translate("MainWindow", "SaveAllMvts"))

        """
        f_b_fixPar = "<html><head/><body><p>fix params</p></body></html>"
        self.btn_fixParam.setToolTip(_translate("MainWindow", f_b_fixPar))
        self.btn_fixParam.setStatusTip(_translate("MainWindow",
                                       "Set constant vals for chosen params"))
        self.btn_fixParam.setText(_translate("MainWindow",
                                             "Sets constant params values"))
        """

        f_b_reset = "<html><head/><body><p>" +\
            "Erases all data in memory and all datastructure info in memory" +\
            "</p></body></html>"
        self.btn_Reset.setToolTip(_translate("MainWindow", f_b_reset))
        self.btn_Reset.setStatusTip(_translate("MainWindow", "Reset all"))
        self.btn_Reset.setText(_translate("MainWindow", "Reset"))

        self.btn_quit.setStatusTip(_translate("MainWindow", "Exit GUI"))
        self.btn_quit.setText(_translate("MainWindow", "Quit"))
