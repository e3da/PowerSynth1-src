# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\bxs003\Dropbox\PMLST\code\workspace\PowerCAD\src\powercad\project_builder\ui\edit_tech_lib_dir.ui'
#
# Created: Thu Mar 20 14:38:41 2014
#      by: pyside-uic 0.2.14 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_EditTechLibDirDialog(object):
    def setupUi(self, EditTechLibDirDialog):
        EditTechLibDirDialog.setObjectName("EditTechLibDirDialog")
        EditTechLibDirDialog.resize(513, 128)
        self.gridLayout = QtGui.QGridLayout(EditTechLibDirDialog)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtGui.QSpacerItem(399, 8, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 0, 0, 1, 1)
        self.label = QtGui.QLabel(EditTechLibDirDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 2)
        self.select_dir = QtGui.QToolButton(EditTechLibDirDialog)
        self.select_dir.setObjectName("select_dir")
        self.gridLayout.addWidget(self.select_dir, 5, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(399, 17, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 6, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(EditTechLibDirDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 7, 0, 1, 2)
        self.txt_library_path = QtGui.QLineEdit(EditTechLibDirDialog)
        self.txt_library_path.setEnabled(True)
        self.txt_library_path.setMinimumSize(QtCore.QSize(400, 0))
        self.txt_library_path.setReadOnly(False)
        self.txt_library_path.setObjectName("txt_library_path")
        self.gridLayout.addWidget(self.txt_library_path, 5, 0, 1, 1)

        self.retranslateUi(EditTechLibDirDialog)
        QtCore.QMetaObject.connectSlotsByName(EditTechLibDirDialog)

    def retranslateUi(self, EditTechLibDirDialog):
        EditTechLibDirDialog.setWindowTitle(QtGui.QApplication.translate("EditTechLibDirDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("EditTechLibDirDialog", "Select technology library directory:", None, QtGui.QApplication.UnicodeUTF8))
        self.select_dir.setText(QtGui.QApplication.translate("EditTechLibDirDialog", "Select Directory", None, QtGui.QApplication.UnicodeUTF8))

