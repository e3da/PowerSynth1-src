# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ModelSelection.ui'
#
# Created: Wed May 24 17:20:14 2017
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog_model_select(object):
    def setupUi(self, Dialog_model_select):
        Dialog_model_select.setObjectName("Dialog_model_select")
        Dialog_model_select.resize(632, 480)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog_model_select)
        self.buttonBox.setGeometry(QtCore.QRect(430, 440, 181, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.textEdit = QtGui.QTextEdit(Dialog_model_select)
        self.textEdit.setGeometry(QtCore.QRect(200, 80, 411, 341))
        self.textEdit.setObjectName("textEdit")
        self.listView = QtGui.QListView(Dialog_model_select)
        self.listView.setGeometry(QtCore.QRect(10, 80, 161, 341))
        self.listView.setObjectName("listView")
        self.label = QtGui.QLabel(Dialog_model_select)
        self.label.setGeometry(QtCore.QRect(10, 60, 46, 13))
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel(Dialog_model_select)
        self.label_2.setGeometry(QtCore.QRect(200, 60, 131, 16))
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")

        self.retranslateUi(Dialog_model_select)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog_model_select.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog_model_select.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog_model_select)

    def retranslateUi(self, Dialog_model_select):
        Dialog_model_select.setWindowTitle(QtGui.QApplication.translate("Dialog_model_select", "Model Selection", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog_model_select", "Model:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog_model_select", "Model Info:", None, QtGui.QApplication.UnicodeUTF8))

