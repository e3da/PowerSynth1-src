# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'device_states.ui'
#
# Created: Thu Jun 07 23:41:25 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_dev_state_dialog(object):
    def setupUi(self, dev_state_dialog):
        dev_state_dialog.setObjectName("dev_state_dialog")
        dev_state_dialog.resize(530, 312)
        self.gridLayout = QtGui.QGridLayout(dev_state_dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.frame = QtGui.QFrame(dev_state_dialog)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_2 = QtGui.QGridLayout(self.frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        spacerItem = QtGui.QSpacerItem(406, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 1, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btn_ok = QtGui.QPushButton(self.frame)
        self.btn_ok.setObjectName("btn_ok")
        self.horizontalLayout.addWidget(self.btn_ok)
        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 1, 1, 1)
        self.tbl_states = QtGui.QTableWidget(self.frame)
        self.tbl_states.setObjectName("tbl_states")
        self.tbl_states.setColumnCount(4)
        self.tbl_states.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tbl_states.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_states.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_states.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tbl_states.setHorizontalHeaderItem(3, item)
        self.gridLayout_2.addWidget(self.tbl_states, 0, 0, 1, 2)
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)

        self.retranslateUi(dev_state_dialog)
        QtCore.QMetaObject.connectSlotsByName(dev_state_dialog)

    def retranslateUi(self, dev_state_dialog):
        dev_state_dialog.setWindowTitle(QtGui.QApplication.translate("dev_state_dialog", "Device State", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_ok.setText(QtGui.QApplication.translate("dev_state_dialog", "Ok", None, QtGui.QApplication.UnicodeUTF8))
        self.tbl_states.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("dev_state_dialog", "Device ID", None, QtGui.QApplication.UnicodeUTF8))
        self.tbl_states.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("dev_state_dialog", "Connection 1", None, QtGui.QApplication.UnicodeUTF8))
        self.tbl_states.horizontalHeaderItem(2).setText(QtGui.QApplication.translate("dev_state_dialog", "Connection 2", None, QtGui.QApplication.UnicodeUTF8))
        self.tbl_states.horizontalHeaderItem(3).setText(QtGui.QApplication.translate("dev_state_dialog", "Connection 3", None, QtGui.QApplication.UnicodeUTF8))

