# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\bxs003\Dropbox\PMLST\code\workspace\PowerCAD\src\powercad\project_builder\ui\openProjectDialog.ui'
#
# Created: Thu Mar 20 14:38:32 2014
#      by: pyside-uic 0.2.14 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_openProjectDialog(object):
    def setupUi(self, openProjectDialog):
        openProjectDialog.setObjectName("openProjectDialog")
        openProjectDialog.resize(487, 157)
        self.gridLayout = QtGui.QGridLayout(openProjectDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.txt_projectLocation = QtGui.QLineEdit(openProjectDialog)
        self.txt_projectLocation.setEnabled(True)
        self.txt_projectLocation.setMinimumSize(QtCore.QSize(400, 0))
        self.txt_projectLocation.setReadOnly(False)
        self.txt_projectLocation.setObjectName("txt_projectLocation")
        self.gridLayout.addWidget(self.txt_projectLocation, 2, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(openProjectDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 0, 0, 1, 1)
        self.label = QtGui.QLabel(openProjectDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 2)
        self.btn_selectFile = QtGui.QToolButton(openProjectDialog)
        self.btn_selectFile.setObjectName("btn_selectFile")
        self.gridLayout.addWidget(self.btn_selectFile, 2, 1, 1, 1)

        self.retranslateUi(openProjectDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), openProjectDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), openProjectDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(openProjectDialog)

    def retranslateUi(self, openProjectDialog):
        openProjectDialog.setWindowTitle(QtGui.QApplication.translate("openProjectDialog", "Open Project", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("openProjectDialog", "Select a project file:", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_selectFile.setText(QtGui.QApplication.translate("openProjectDialog", "Select File", None, QtGui.QApplication.UnicodeUTF8))

