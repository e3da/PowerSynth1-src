# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'bondwire_setup.ui'
#
# Created: Wed Jun 06 10:25:33 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Bondwire_setup(object):
    def setupUi(self, Bondwire_setup):
        Bondwire_setup.setObjectName("Bondwire_setup")
        Bondwire_setup.resize(442, 658)
        self.gridLayout_2 = QtGui.QGridLayout(Bondwire_setup)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.frame = QtGui.QFrame(Bondwire_setup)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout = QtGui.QGridLayout(self.frame)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtGui.QLabel(self.frame)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.tbl_bw_connection = QtGui.QTableWidget(self.frame)
        self.tbl_bw_connection.setObjectName("tbl_bw_connection")
        self.tbl_bw_connection.setColumnCount(4)
        self.tbl_bw_connection.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tbl_bw_connection.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_bw_connection.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_bw_connection.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_bw_connection.setHorizontalHeaderItem(3, item)
        self.gridLayout.addWidget(self.tbl_bw_connection, 1, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btn_add = QtGui.QPushButton(self.frame)
        self.btn_add.setObjectName("btn_add")
        self.horizontalLayout.addWidget(self.btn_add)
        self.btn_remove = QtGui.QPushButton(self.frame)
        self.btn_remove.setObjectName("btn_remove")
        self.horizontalLayout.addWidget(self.btn_remove)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)
        self.gridLayout_2.addWidget(self.frame, 0, 0, 1, 1)

        self.retranslateUi(Bondwire_setup)
        QtCore.QMetaObject.connectSlotsByName(Bondwire_setup)

    def retranslateUi(self, Bondwire_setup):
        Bondwire_setup.setWindowTitle(QtGui.QApplication.translate("Bondwire_setup", "BondwireSetup", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Bondwire_setup", "Bondwire Connections", None, QtGui.QApplication.UnicodeUTF8))
        self.tbl_bw_connection.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("Bondwire_setup", "Bondwire Type", None, QtGui.QApplication.UnicodeUTF8))
        self.tbl_bw_connection.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("Bondwire_setup", "Start", None, QtGui.QApplication.UnicodeUTF8))
        self.tbl_bw_connection.horizontalHeaderItem(2).setText(QtGui.QApplication.translate("Bondwire_setup", "Stop", None, QtGui.QApplication.UnicodeUTF8))
        self.tbl_bw_connection.horizontalHeaderItem(3).setText(QtGui.QApplication.translate("Bondwire_setup", "Model", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_add.setText(QtGui.QApplication.translate("Bondwire_setup", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_remove.setText(QtGui.QApplication.translate("Bondwire_setup", "Remove", None, QtGui.QApplication.UnicodeUTF8))

