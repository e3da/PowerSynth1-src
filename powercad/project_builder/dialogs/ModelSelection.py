# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ModelSelection.ui'
#
# Created: Mon Jun 04 11:22:16 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ModelSelection(object):
    def setupUi(self, ModelSelection):
        ModelSelection.setObjectName("ModelSelection")
        ModelSelection.resize(255, 480)
        self.gridLayout = QtGui.QGridLayout(ModelSelection)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(ModelSelection)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.list_mdl_choices = QtGui.QListView(ModelSelection)
        self.list_mdl_choices.setObjectName("list_mdl_choices")
        self.gridLayout.addWidget(self.list_mdl_choices, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ModelSelection)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.retranslateUi(ModelSelection)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), ModelSelection.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), ModelSelection.reject)
        QtCore.QMetaObject.connectSlotsByName(ModelSelection)

    def retranslateUi(self, ModelSelection):
        ModelSelection.setWindowTitle(QtGui.QApplication.translate("ModelSelection", "Model Selection", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ModelSelection", "Model Library", None, QtGui.QApplication.UnicodeUTF8))

