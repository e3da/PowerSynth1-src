# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Edit_Library.ui'
#
# Created: Fri Aug  2 01:59:18 2019
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MDKWindow(object):
    def setupUi(self, MDKWindow):
        MDKWindow.setObjectName("MDKWindow")
        MDKWindow.resize(911, 580)
        self.centralwidget = QtGui.QWidget(MDKWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.save_button = QtGui.QPushButton(self.centralwidget)
        self.save_button.setGeometry(QtCore.QRect(560, 500, 75, 23))
        self.save_button.setMouseTracking(True)
        self.save_button.setObjectName("save_button")
        self.cancel_button = QtGui.QPushButton(self.centralwidget)
        self.cancel_button.setGeometry(QtCore.QRect(640, 500, 75, 23))
        self.cancel_button.setMouseTracking(True)
        self.cancel_button.setObjectName("cancel_button")
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 741, 491))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")
        self.tableWidget = QtGui.QTableWidget(self.tab)
        self.tableWidget.setGeometry(QtCore.QRect(10, 10, 711, 411))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(15)
        self.tableWidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(6, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(7, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(8, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(9, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(10, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(11, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(12, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(13, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(14, item)
        self.remove_all_button = QtGui.QPushButton(self.tab)
        self.remove_all_button.setGeometry(QtCore.QRect(480, 430, 75, 23))
        self.remove_all_button.setMouseTracking(True)
        self.remove_all_button.setObjectName("remove_all_button")
        self.add_all_button = QtGui.QPushButton(self.tab)
        self.add_all_button.setGeometry(QtCore.QRect(120, 430, 75, 23))
        self.add_all_button.setMouseTracking(True)
        self.add_all_button.setObjectName("add_all_button")
        self.edit_all_button = QtGui.QPushButton(self.tab)
        self.edit_all_button.setGeometry(QtCore.QRect(360, 430, 75, 23))
        self.edit_all_button.setMouseTracking(True)
        self.edit_all_button.setObjectName("edit_all_button")
        self.clone_all_button = QtGui.QPushButton(self.tab)
        self.clone_all_button.setGeometry(QtCore.QRect(240, 430, 75, 23))
        self.clone_all_button.setObjectName("clone_all_button")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tableWidget_2 = QtGui.QTableWidget(self.tab_2)
        self.tableWidget_2.setGeometry(QtCore.QRect(10, 10, 711, 411))
        self.tableWidget_2.setObjectName("tableWidget_2")
        self.tableWidget_2.setColumnCount(11)
        self.tableWidget_2.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(6, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(7, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(8, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(9, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(10, item)
        self.remove_pcm_button = QtGui.QPushButton(self.tab_2)
        self.remove_pcm_button.setGeometry(QtCore.QRect(480, 430, 75, 23))
        self.remove_pcm_button.setMouseTracking(True)
        self.remove_pcm_button.setObjectName("remove_pcm_button")
        self.add_pcm_button = QtGui.QPushButton(self.tab_2)
        self.add_pcm_button.setGeometry(QtCore.QRect(120, 430, 75, 23))
        self.add_pcm_button.setMouseTracking(True)
        self.add_pcm_button.setObjectName("add_pcm_button")
        self.edit_pcm_button = QtGui.QPushButton(self.tab_2)
        self.edit_pcm_button.setGeometry(QtCore.QRect(360, 430, 75, 23))
        self.edit_pcm_button.setMouseTracking(True)
        self.edit_pcm_button.setObjectName("edit_pcm_button")
        self.clone_pcm_button = QtGui.QPushButton(self.tab_2)
        self.clone_pcm_button.setGeometry(QtCore.QRect(240, 430, 75, 23))
        self.clone_pcm_button.setMouseTracking(True)
        self.clone_pcm_button.setObjectName("clone_pcm_button")
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tableWidget_3 = QtGui.QTableWidget(self.tab_3)
        self.tableWidget_3.setGeometry(QtCore.QRect(10, 10, 711, 411))
        self.tableWidget_3.setAutoScroll(True)
        self.tableWidget_3.setObjectName("tableWidget_3")
        self.tableWidget_3.setColumnCount(10)
        self.tableWidget_3.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(6, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(7, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(8, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(9, item)
        self.add_con_button = QtGui.QPushButton(self.tab_3)
        self.add_con_button.setGeometry(QtCore.QRect(120, 430, 75, 23))
        self.add_con_button.setMouseTracking(True)
        self.add_con_button.setObjectName("add_con_button")
        self.clone_con_button = QtGui.QPushButton(self.tab_3)
        self.clone_con_button.setGeometry(QtCore.QRect(240, 430, 75, 23))
        self.clone_con_button.setMouseTracking(True)
        self.clone_con_button.setObjectName("clone_con_button")
        self.edit_con_button = QtGui.QPushButton(self.tab_3)
        self.edit_con_button.setGeometry(QtCore.QRect(360, 430, 75, 23))
        self.edit_con_button.setMouseTracking(True)
        self.edit_con_button.setObjectName("edit_con_button")
        self.remove_con_button = QtGui.QPushButton(self.tab_3)
        self.remove_con_button.setGeometry(QtCore.QRect(480, 430, 75, 23))
        self.remove_con_button.setMouseTracking(True)
        self.remove_con_button.setObjectName("remove_con_button")
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QtGui.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.tableWidget_4 = QtGui.QTableWidget(self.tab_4)
        self.tableWidget_4.setGeometry(QtCore.QRect(10, 10, 711, 411))
        self.tableWidget_4.setObjectName("tableWidget_4")
        self.tableWidget_4.setColumnCount(10)
        self.tableWidget_4.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(6, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(7, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(8, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(9, item)
        self.remove_ins_button = QtGui.QPushButton(self.tab_4)
        self.remove_ins_button.setGeometry(QtCore.QRect(480, 430, 75, 23))
        self.remove_ins_button.setMouseTracking(True)
        self.remove_ins_button.setObjectName("remove_ins_button")
        self.add_ins_button = QtGui.QPushButton(self.tab_4)
        self.add_ins_button.setGeometry(QtCore.QRect(120, 430, 75, 23))
        self.add_ins_button.setMouseTracking(True)
        self.add_ins_button.setObjectName("add_ins_button")
        self.edit_ins_button = QtGui.QPushButton(self.tab_4)
        self.edit_ins_button.setGeometry(QtCore.QRect(360, 430, 75, 23))
        self.edit_ins_button.setMouseTracking(True)
        self.edit_ins_button.setObjectName("edit_ins_button")
        self.clone_ins_button = QtGui.QPushButton(self.tab_4)
        self.clone_ins_button.setGeometry(QtCore.QRect(240, 430, 75, 23))
        self.clone_ins_button.setMouseTracking(True)
        self.clone_ins_button.setObjectName("clone_ins_button")
        self.tabWidget.addTab(self.tab_4, "")
        self.tab_5 = QtGui.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.tableWidget_5 = QtGui.QTableWidget(self.tab_5)
        self.tableWidget_5.setGeometry(QtCore.QRect(10, 10, 711, 411))
        self.tableWidget_5.setObjectName("tableWidget_5")
        self.tableWidget_5.setColumnCount(10)
        self.tableWidget_5.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_5.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_5.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_5.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_5.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_5.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_5.setHorizontalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_5.setHorizontalHeaderItem(6, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_5.setHorizontalHeaderItem(7, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_5.setHorizontalHeaderItem(8, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_5.setHorizontalHeaderItem(9, item)
        self.remove_sem_button = QtGui.QPushButton(self.tab_5)
        self.remove_sem_button.setGeometry(QtCore.QRect(480, 430, 75, 23))
        self.remove_sem_button.setMouseTracking(True)
        self.remove_sem_button.setObjectName("remove_sem_button")
        self.add_sem_button = QtGui.QPushButton(self.tab_5)
        self.add_sem_button.setGeometry(QtCore.QRect(120, 430, 75, 23))
        self.add_sem_button.setMouseTracking(True)
        self.add_sem_button.setObjectName("add_sem_button")
        self.edit_sem_button = QtGui.QPushButton(self.tab_5)
        self.edit_sem_button.setGeometry(QtCore.QRect(360, 430, 75, 23))
        self.edit_sem_button.setMouseTracking(True)
        self.edit_sem_button.setObjectName("edit_sem_button")
        self.clone_sem_button = QtGui.QPushButton(self.tab_5)
        self.clone_sem_button.setGeometry(QtCore.QRect(240, 430, 75, 23))
        self.clone_sem_button.setMouseTracking(True)
        self.clone_sem_button.setObjectName("clone_sem_button")
        self.tabWidget.addTab(self.tab_5, "")
        self.load_button = QtGui.QPushButton(self.centralwidget)
        self.load_button.setGeometry(QtCore.QRect(480, 500, 75, 23))
        self.load_button.setMouseTracking(True)
        self.load_button.setObjectName("load_button")
        self.select_button = QtGui.QPushButton(self.centralwidget)
        self.select_button.setGeometry(QtCore.QRect(390, 500, 75, 23))
        self.select_button.setMouseTracking(True)
        self.select_button.setObjectName("select_button")
        MDKWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MDKWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 911, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MDKWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MDKWindow)
        self.statusbar.setObjectName("statusbar")
        MDKWindow.setStatusBar(self.statusbar)
        self.dockWidget_2 = QtGui.QDockWidget(MDKWindow)
        self.dockWidget_2.setMinimumSize(QtCore.QSize(170, 135))
        self.dockWidget_2.setMaximumSize(QtCore.QSize(170, 500))
        self.dockWidget_2.setObjectName("dockWidget_2")
        self.dockWidgetContents_2 = QtGui.QWidget()
        self.dockWidgetContents_2.setObjectName("dockWidgetContents_2")
        self.gridLayout = QtGui.QGridLayout(self.dockWidgetContents_2)
        self.gridLayout.setObjectName("gridLayout")
        self.toolBox = QtGui.QToolBox(self.dockWidgetContents_2)
        self.toolBox.setObjectName("toolBox")
        self.page_2 = QtGui.QWidget()
        self.page_2.setGeometry(QtCore.QRect(0, 0, 152, 434))
        self.page_2.setObjectName("page_2")
        self.comboBox = QtGui.QComboBox(self.page_2)
        self.comboBox.setGeometry(QtCore.QRect(10, 0, 131, 22))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.SearchItem = QtGui.QLineEdit(self.page_2)
        self.SearchItem.setGeometry(QtCore.QRect(10, 30, 113, 20))
        self.SearchItem.setObjectName("SearchItem")
        self.search_button = QtGui.QPushButton(self.page_2)
        self.search_button.setGeometry(QtCore.QRect(20, 60, 75, 23))
        self.search_button.setMouseTracking(True)
        self.search_button.setObjectName("search_button")
        self.sort_button = QtGui.QPushButton(self.page_2)
        self.sort_button.setGeometry(QtCore.QRect(20, 90, 75, 23))
        self.sort_button.setMouseTracking(True)
        self.sort_button.setObjectName("sort_button")
        self.toolBox.addItem(self.page_2, "")
        self.gridLayout.addWidget(self.toolBox, 0, 0, 1, 1)
        self.dockWidget_2.setWidget(self.dockWidgetContents_2)
        MDKWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockWidget_2)
        self.actionImport = QtGui.QAction(MDKWindow)
        self.actionImport.setObjectName("actionImport")
        self.actionSave = QtGui.QAction(MDKWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionImport_file = QtGui.QAction(MDKWindow)
        self.actionImport_file.setObjectName("actionImport_file")
        self.actionType_Material = QtGui.QAction(MDKWindow)
        self.actionType_Material.setObjectName("actionType_Material")
        self.actionImport_2 = QtGui.QAction(MDKWindow)
        self.actionImport_2.setObjectName("actionImport_2")
        self.actionOpen_explanation = QtGui.QAction(MDKWindow)
        self.actionOpen_explanation.setObjectName("actionOpen_explanation")
        self.menuFile.addAction(self.actionImport_2)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addSeparator()
        self.menuHelp.addAction(self.actionOpen_explanation)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MDKWindow)
        self.tabWidget.setCurrentIndex(0)
        self.toolBox.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MDKWindow)

    def retranslateUi(self, MDKWindow):
        MDKWindow.setWindowTitle(QtGui.QApplication.translate("MDKWindow", "PowerSynth MDK Window", None, QtGui.QApplication.UnicodeUTF8))
        self.save_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Save tables\' materials to MDK file", None, QtGui.QApplication.UnicodeUTF8))
        self.save_button.setText(QtGui.QApplication.translate("MDKWindow", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Close this window", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_button.setText(QtGui.QApplication.translate("MDKWindow", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("MDKWindow", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("MDKWindow", "Type", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(2).setText(QtGui.QApplication.translate("MDKWindow", "Young Modulus", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(3).setText(QtGui.QApplication.translate("MDKWindow", "Poisson\'s Ratio", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(4).setText(QtGui.QApplication.translate("MDKWindow", "Melting Temperature", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(5).setText(QtGui.QApplication.translate("MDKWindow", "Density(Solid)", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(6).setText(QtGui.QApplication.translate("MDKWindow", "Density(Liquid)", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(7).setText(QtGui.QApplication.translate("MDKWindow", "Thermal Conductivity(Solid)", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(8).setText(QtGui.QApplication.translate("MDKWindow", "Thermal Conductivity(Liquid)", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(9).setText(QtGui.QApplication.translate("MDKWindow", "Specific Heat Capacity (Solid)", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(10).setText(QtGui.QApplication.translate("MDKWindow", "Specific Heat Capacity (Liquid)", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(11).setText(QtGui.QApplication.translate("MDKWindow", "Electrical Resistivity", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(12).setText(QtGui.QApplication.translate("MDKWindow", "Relative permittivity", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(13).setText(QtGui.QApplication.translate("MDKWindow", "Relative Permeability", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(14).setText(QtGui.QApplication.translate("MDKWindow", "CTE", None, QtGui.QApplication.UnicodeUTF8))
        self.remove_all_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Chosen material is removed from the table", None, QtGui.QApplication.UnicodeUTF8))
        self.remove_all_button.setText(QtGui.QApplication.translate("MDKWindow", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.add_all_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Add blank line to below of the table", None, QtGui.QApplication.UnicodeUTF8))
        self.add_all_button.setText(QtGui.QApplication.translate("MDKWindow", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.edit_all_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Changed values are updated", None, QtGui.QApplication.UnicodeUTF8))
        self.edit_all_button.setText(QtGui.QApplication.translate("MDKWindow", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.clone_all_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Make clone material and show it top of the table", None, QtGui.QApplication.UnicodeUTF8))
        self.clone_all_button.setText(QtGui.QApplication.translate("MDKWindow", "Clone", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("MDKWindow", "ALL", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_2.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("MDKWindow", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_2.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("MDKWindow", "Young Modulus", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_2.horizontalHeaderItem(2).setText(QtGui.QApplication.translate("MDKWindow", "Poisson\'s Ratio", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_2.horizontalHeaderItem(3).setText(QtGui.QApplication.translate("MDKWindow", "CTE", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_2.horizontalHeaderItem(4).setText(QtGui.QApplication.translate("MDKWindow", "Melting Temperature", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_2.horizontalHeaderItem(5).setText(QtGui.QApplication.translate("MDKWindow", "Density(Solid)", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_2.horizontalHeaderItem(6).setText(QtGui.QApplication.translate("MDKWindow", "Density(Liquid)", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_2.horizontalHeaderItem(7).setText(QtGui.QApplication.translate("MDKWindow", "Thermal Conductivity (Solid)", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_2.horizontalHeaderItem(8).setText(QtGui.QApplication.translate("MDKWindow", "Thermal Conductivity (Liquid)", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_2.horizontalHeaderItem(9).setText(QtGui.QApplication.translate("MDKWindow", "Specific Heat Capacity (Solid)", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_2.horizontalHeaderItem(10).setText(QtGui.QApplication.translate("MDKWindow", "Specific Heat Capacity (Liquid)", None, QtGui.QApplication.UnicodeUTF8))
        self.remove_pcm_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Chosen material is removed from the table", None, QtGui.QApplication.UnicodeUTF8))
        self.remove_pcm_button.setText(QtGui.QApplication.translate("MDKWindow", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.add_pcm_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Add blank line to below of the table", None, QtGui.QApplication.UnicodeUTF8))
        self.add_pcm_button.setText(QtGui.QApplication.translate("MDKWindow", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.edit_pcm_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Changed values are updated", None, QtGui.QApplication.UnicodeUTF8))
        self.edit_pcm_button.setText(QtGui.QApplication.translate("MDKWindow", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.clone_pcm_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Make clone material and show it top of the table", None, QtGui.QApplication.UnicodeUTF8))
        self.clone_pcm_button.setText(QtGui.QApplication.translate("MDKWindow", "Clone", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("MDKWindow", "PCM", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_3.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("MDKWindow", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_3.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("MDKWindow", "Young Modulus", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_3.horizontalHeaderItem(2).setText(QtGui.QApplication.translate("MDKWindow", "Poisson\'s Ratio", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_3.horizontalHeaderItem(3).setText(QtGui.QApplication.translate("MDKWindow", "Density", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_3.horizontalHeaderItem(4).setText(QtGui.QApplication.translate("MDKWindow", "Thermal Conductivity", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_3.horizontalHeaderItem(5).setText(QtGui.QApplication.translate("MDKWindow", "Specific Heat Capacity", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_3.horizontalHeaderItem(6).setText(QtGui.QApplication.translate("MDKWindow", "Electrical Resistivity", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_3.horizontalHeaderItem(7).setText(QtGui.QApplication.translate("MDKWindow", "Relative Permittivity", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_3.horizontalHeaderItem(8).setText(QtGui.QApplication.translate("MDKWindow", "Relative permeability", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_3.horizontalHeaderItem(9).setText(QtGui.QApplication.translate("MDKWindow", "CTE", None, QtGui.QApplication.UnicodeUTF8))
        self.add_con_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Add blank line to below of the table", None, QtGui.QApplication.UnicodeUTF8))
        self.add_con_button.setText(QtGui.QApplication.translate("MDKWindow", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.clone_con_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Make clone material and show it top of the table", None, QtGui.QApplication.UnicodeUTF8))
        self.clone_con_button.setText(QtGui.QApplication.translate("MDKWindow", "Clone", None, QtGui.QApplication.UnicodeUTF8))
        self.edit_con_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Changed values are updated", None, QtGui.QApplication.UnicodeUTF8))
        self.edit_con_button.setText(QtGui.QApplication.translate("MDKWindow", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.remove_con_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Chosen material is removed from the table", None, QtGui.QApplication.UnicodeUTF8))
        self.remove_con_button.setText(QtGui.QApplication.translate("MDKWindow", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QtGui.QApplication.translate("MDKWindow", "Conductor", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_4.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("MDKWindow", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_4.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("MDKWindow", "Young Modulus", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_4.horizontalHeaderItem(2).setText(QtGui.QApplication.translate("MDKWindow", "Poisson\'s Ratio", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_4.horizontalHeaderItem(3).setText(QtGui.QApplication.translate("MDKWindow", "Density", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_4.horizontalHeaderItem(4).setText(QtGui.QApplication.translate("MDKWindow", "Thermal Conductivity", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_4.horizontalHeaderItem(5).setText(QtGui.QApplication.translate("MDKWindow", "Specific Heat Capacity", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_4.horizontalHeaderItem(6).setText(QtGui.QApplication.translate("MDKWindow", "Electrical Resistivity", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_4.horizontalHeaderItem(7).setText(QtGui.QApplication.translate("MDKWindow", "Relative Permittivity", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_4.horizontalHeaderItem(8).setText(QtGui.QApplication.translate("MDKWindow", "Relative Permeability", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_4.horizontalHeaderItem(9).setText(QtGui.QApplication.translate("MDKWindow", "CTE", None, QtGui.QApplication.UnicodeUTF8))
        self.remove_ins_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Chosen material is removed from the table", None, QtGui.QApplication.UnicodeUTF8))
        self.remove_ins_button.setText(QtGui.QApplication.translate("MDKWindow", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.add_ins_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Add blank line to below of the table", None, QtGui.QApplication.UnicodeUTF8))
        self.add_ins_button.setText(QtGui.QApplication.translate("MDKWindow", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.edit_ins_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Changed values are updated", None, QtGui.QApplication.UnicodeUTF8))
        self.edit_ins_button.setText(QtGui.QApplication.translate("MDKWindow", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.clone_ins_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Make clone material and show it top of the table", None, QtGui.QApplication.UnicodeUTF8))
        self.clone_ins_button.setText(QtGui.QApplication.translate("MDKWindow", "Clone", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QtGui.QApplication.translate("MDKWindow", "Insulator", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_5.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("MDKWindow", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_5.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("MDKWindow", "Young Modulus", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_5.horizontalHeaderItem(2).setText(QtGui.QApplication.translate("MDKWindow", "Poisson\'s Ratio", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_5.horizontalHeaderItem(3).setText(QtGui.QApplication.translate("MDKWindow", "Density", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_5.horizontalHeaderItem(4).setText(QtGui.QApplication.translate("MDKWindow", "Thermal Conductivity", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_5.horizontalHeaderItem(5).setText(QtGui.QApplication.translate("MDKWindow", "Specific Heat Capacity", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_5.horizontalHeaderItem(6).setText(QtGui.QApplication.translate("MDKWindow", "Electrical Resistivity", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_5.horizontalHeaderItem(7).setText(QtGui.QApplication.translate("MDKWindow", "Relative Permittivity", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_5.horizontalHeaderItem(8).setText(QtGui.QApplication.translate("MDKWindow", "Relative Permeability", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_5.horizontalHeaderItem(9).setText(QtGui.QApplication.translate("MDKWindow", "CTE", None, QtGui.QApplication.UnicodeUTF8))
        self.remove_sem_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Chosen material is removed from the table", None, QtGui.QApplication.UnicodeUTF8))
        self.remove_sem_button.setText(QtGui.QApplication.translate("MDKWindow", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.add_sem_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Add blank line to below of the table", None, QtGui.QApplication.UnicodeUTF8))
        self.add_sem_button.setText(QtGui.QApplication.translate("MDKWindow", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.edit_sem_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Changed values are updated", None, QtGui.QApplication.UnicodeUTF8))
        self.edit_sem_button.setText(QtGui.QApplication.translate("MDKWindow", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.clone_sem_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Make clone material and show it top of the table", None, QtGui.QApplication.UnicodeUTF8))
        self.clone_sem_button.setText(QtGui.QApplication.translate("MDKWindow", "Clone", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), QtGui.QApplication.translate("MDKWindow", "Semiconductor", None, QtGui.QApplication.UnicodeUTF8))
        self.load_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Open MDK file and upload it to the table", None, QtGui.QApplication.UnicodeUTF8))
        self.load_button.setText(QtGui.QApplication.translate("MDKWindow", "Load", None, QtGui.QApplication.UnicodeUTF8))
        self.select_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Choose material you want to use", None, QtGui.QApplication.UnicodeUTF8))
        self.select_button.setText(QtGui.QApplication.translate("MDKWindow", "Select", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("MDKWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHelp.setTitle(QtGui.QApplication.translate("MDKWindow", "Help", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(0, QtGui.QApplication.translate("MDKWindow", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(1, QtGui.QApplication.translate("MDKWindow", "Young Modulus", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(2, QtGui.QApplication.translate("MDKWindow", "Poisson\'s Ratio", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(3, QtGui.QApplication.translate("MDKWindow", "Melting Temperature", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(4, QtGui.QApplication.translate("MDKWindow", "Electrical Resistivity", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(5, QtGui.QApplication.translate("MDKWindow", "Density", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(6, QtGui.QApplication.translate("MDKWindow", "Density(Solid)", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(7, QtGui.QApplication.translate("MDKWindow", "Density(Liquid)", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(8, QtGui.QApplication.translate("MDKWindow", "Specific Heat Capacity", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(9, QtGui.QApplication.translate("MDKWindow", "Specific Heat Capacity (Solid)", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(10, QtGui.QApplication.translate("MDKWindow", "Specific Heat Capacity (Liquid)", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(11, QtGui.QApplication.translate("MDKWindow", "Thermal Conductivity", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(12, QtGui.QApplication.translate("MDKWindow", "Thermal Conductivity (Solid)", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(13, QtGui.QApplication.translate("MDKWindow", "Thermal Conductivity (Liquid)", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(14, QtGui.QApplication.translate("MDKWindow", "Relative Permittivity", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(15, QtGui.QApplication.translate("MDKWindow", "Relative Permeability", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(16, QtGui.QApplication.translate("MDKWindow", "CTE", None, QtGui.QApplication.UnicodeUTF8))
        self.search_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Search specific material, and it show the top of the table", None, QtGui.QApplication.UnicodeUTF8))
        self.search_button.setText(QtGui.QApplication.translate("MDKWindow", "Search", None, QtGui.QApplication.UnicodeUTF8))
        self.sort_button.setToolTip(QtGui.QApplication.translate("MDKWindow", "Sort materials based on the field", None, QtGui.QApplication.UnicodeUTF8))
        self.sort_button.setText(QtGui.QApplication.translate("MDKWindow", "Sort", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_2), QtGui.QApplication.translate("MDKWindow", "Search Material", None, QtGui.QApplication.UnicodeUTF8))
        self.actionImport.setText(QtGui.QApplication.translate("MDKWindow", "Import", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave.setText(QtGui.QApplication.translate("MDKWindow", "Export", None, QtGui.QApplication.UnicodeUTF8))
        self.actionImport_file.setText(QtGui.QApplication.translate("MDKWindow", "Import File", None, QtGui.QApplication.UnicodeUTF8))
        self.actionType_Material.setText(QtGui.QApplication.translate("MDKWindow", "Type Material", None, QtGui.QApplication.UnicodeUTF8))
        self.actionImport_2.setText(QtGui.QApplication.translate("MDKWindow", "Import", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen_explanation.setText(QtGui.QApplication.translate("MDKWindow", "Open explanation", None, QtGui.QApplication.UnicodeUTF8))

