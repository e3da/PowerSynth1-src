# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ModelSelection.ui'
#
# Created: Thu May 25 09:13:19 2017
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ModelSelection(object):
    def setupUi(self, ModelSelection):
        ModelSelection.setObjectName("ModelSelection")
        ModelSelection.resize(632, 480)
        self.buttonBox = QtGui.QDialogButtonBox(ModelSelection)
        self.buttonBox.setGeometry(QtCore.QRect(430, 440, 181, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.textEdit = QtGui.QTextEdit(ModelSelection)
        self.textEdit.setGeometry(QtCore.QRect(200, 80, 411, 341))
        self.textEdit.setObjectName("textEdit")
        self.list_mdl_choices = QtGui.QListView(ModelSelection)
        self.list_mdl_choices.setGeometry(QtCore.QRect(10, 80, 161, 341))
        self.list_mdl_choices.setObjectName("list_mdl_choices")
        self.label = QtGui.QLabel(ModelSelection)
        self.label.setGeometry(QtCore.QRect(10, 60, 46, 13))
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel(ModelSelection)
        self.label_2.setGeometry(QtCore.QRect(200, 60, 131, 16))
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")

        self.retranslateUi(ModelSelection)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), ModelSelection.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), ModelSelection.reject)
        QtCore.QMetaObject.connectSlotsByName(ModelSelection)

    def retranslateUi(self, ModelSelection):
        ModelSelection.setWindowTitle(QtGui.QApplication.translate("ModelSelection", "Model Selection", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ModelSelection", "Model:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ModelSelection", "Model Info:", None, QtGui.QApplication.UnicodeUTF8))

