# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Env_setup.ui'
#
# Created: Thu May 31 11:36:33 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_EnvSetup(object):
    def setupUi(self, EnvSetup):
        EnvSetup.setObjectName("EnvSetup")
        EnvSetup.resize(550, 206)
        self.gridLayout = QtGui.QGridLayout(EnvSetup)
        self.gridLayout.setObjectName("gridLayout")
        self.txt_dir = QtGui.QLineEdit(EnvSetup)
        self.txt_dir.setObjectName("txt_dir")
        self.gridLayout.addWidget(self.txt_dir, 1, 2, 1, 1)
        self.btn_update = QtGui.QPushButton(EnvSetup)
        self.btn_update.setObjectName("btn_update")
        self.gridLayout.addWidget(self.btn_update, 2, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(368, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 2, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(71, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 2, 0, 1, 1)
        self.cmb_env = QtGui.QComboBox(EnvSetup)
        self.cmb_env.setObjectName("cmb_env")
        self.cmb_env.addItem("")
        self.cmb_env.addItem("")
        self.cmb_env.addItem("")
        self.cmb_env.addItem("")
        self.gridLayout.addWidget(self.cmb_env, 1, 1, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(18, 59, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 0, 1, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(18, 59, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem3, 3, 1, 1, 1)
        self.btn_selectdir = QtGui.QPushButton(EnvSetup)
        self.btn_selectdir.setObjectName("btn_selectdir")
        self.gridLayout.addWidget(self.btn_selectdir, 1, 3, 1, 1)
        self.label = QtGui.QLabel(EnvSetup)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)

        self.retranslateUi(EnvSetup)
        QtCore.QMetaObject.connectSlotsByName(EnvSetup)

    def retranslateUi(self, EnvSetup):
        EnvSetup.setWindowTitle(QtGui.QApplication.translate("EnvSetup", "Environment Setup", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_update.setText(QtGui.QApplication.translate("EnvSetup", "Update", None, QtGui.QApplication.UnicodeUTF8))
        self.cmb_env.setItemText(0, QtGui.QApplication.translate("EnvSetup", "Gmsh", None, QtGui.QApplication.UnicodeUTF8))
        self.cmb_env.setItemText(1, QtGui.QApplication.translate("EnvSetup", "Elmer", None, QtGui.QApplication.UnicodeUTF8))
        self.cmb_env.setItemText(2, QtGui.QApplication.translate("EnvSetup", "Ansys Q3D (IPY 64)", None, QtGui.QApplication.UnicodeUTF8))
        self.cmb_env.setItemText(3, QtGui.QApplication.translate("EnvSetup", "FastHenry", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_selectdir.setText(QtGui.QApplication.translate("EnvSetup", "Select", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("EnvSetup", "Env list :", None, QtGui.QApplication.UnicodeUTF8))

