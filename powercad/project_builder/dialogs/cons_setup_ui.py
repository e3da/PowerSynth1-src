# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cons_setup.ui'
#
# Created: Mon Sep 10 22:54:13 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Constraint_setup(object):
    def setupUi(self, Constraint_setup):
        Constraint_setup.setObjectName("Constraint_setup")
        Constraint_setup.resize(959, 876)
        self.gridLayout_2 = QtGui.QGridLayout(Constraint_setup)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.frame = QtGui.QFrame(Constraint_setup)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout = QtGui.QGridLayout(self.frame)
        self.gridLayout.setObjectName("gridLayout")
        self.tbl_cons_gaps = QtGui.QTableWidget(self.frame)
        self.tbl_cons_gaps.setObjectName("tbl_cons_gaps")
        self.tbl_cons_gaps.setColumnCount(0)
        self.tbl_cons_gaps.setRowCount(0)
        self.gridLayout.addWidget(self.tbl_cons_gaps, 3, 0, 1, 1)
        self.label_3 = QtGui.QLabel(self.frame)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btn_apply = QtGui.QPushButton(self.frame)
        self.btn_apply.setObjectName("btn_apply")
        self.horizontalLayout.addWidget(self.btn_apply)
        self.btn_load = QtGui.QPushButton(self.frame)
        self.btn_load.setObjectName("btn_load")
        self.horizontalLayout.addWidget(self.btn_load)
        self.btn_save = QtGui.QPushButton(self.frame)
        self.btn_save.setObjectName("btn_save")
        self.horizontalLayout.addWidget(self.btn_save)
        self.gridLayout.addLayout(self.horizontalLayout, 6, 0, 1, 1)
        self.tbl_cons_dims = QtGui.QTableWidget(self.frame)
        self.tbl_cons_dims.setObjectName("tbl_cons_dims")
        self.tbl_cons_dims.setColumnCount(0)
        self.tbl_cons_dims.setRowCount(0)
        self.gridLayout.addWidget(self.tbl_cons_dims, 1, 0, 1, 1)
        self.tbl_cons_encl = QtGui.QTableWidget(self.frame)
        self.tbl_cons_encl.setObjectName("tbl_cons_encl")
        self.tbl_cons_encl.setColumnCount(0)
        self.tbl_cons_encl.setRowCount(0)
        self.gridLayout.addWidget(self.tbl_cons_encl, 5, 0, 1, 1)
        self.label_4 = QtGui.QLabel(self.frame)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.frame)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.frame, 0, 0, 1, 1)

        self.retranslateUi(Constraint_setup)
        QtCore.QMetaObject.connectSlotsByName(Constraint_setup)

    def retranslateUi(self, Constraint_setup):
        Constraint_setup.setWindowTitle(QtGui.QApplication.translate("Constraint_setup", "Constraints setup", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Constraint_setup", "Spacing Constraints", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_apply.setText(QtGui.QApplication.translate("Constraint_setup", "Apply to layout", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_load.setText(QtGui.QApplication.translate("Constraint_setup", "Load DRC", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_save.setText(QtGui.QApplication.translate("Constraint_setup", "Save DRC", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Constraint_setup", "Enclosure Constraints", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Constraint_setup", "Dimensions Constraints", None, QtGui.QApplication.UnicodeUTF8))

