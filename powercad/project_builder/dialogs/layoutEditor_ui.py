# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'layoutEditor.ui'
#
# Created: Tue Nov 01 09:23:31 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_layouteditorDialog(object):
    def setupUi(self, layouteditorDialog):
        layouteditorDialog.setObjectName("layouteditorDialog")
        layouteditorDialog.resize(561, 603)
        self.gridLayout = QtGui.QGridLayout(layouteditorDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtGui.QGroupBox(layouteditorDialog)
        self.groupBox.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_9 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.label_42 = QtGui.QLabel(self.groupBox)
        self.label_42.setWordWrap(True)
        self.label_42.setObjectName("label_42")
        self.gridLayout_9.addWidget(self.label_42, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 2)
        self.text_layout_script = QtGui.QTextEdit(layouteditorDialog)
        self.text_layout_script.setObjectName("text_layout_script")
        self.gridLayout.addWidget(self.text_layout_script, 1, 0, 1, 2)
        self.btn_change_dir = QtGui.QPushButton(layouteditorDialog)
        self.btn_change_dir.setObjectName("btn_change_dir")
        self.gridLayout.addWidget(self.btn_change_dir, 2, 0, 1, 1)
        self.btn_reload = QtGui.QPushButton(layouteditorDialog)
        self.btn_reload.setObjectName("btn_reload")
        self.gridLayout.addWidget(self.btn_reload, 2, 1, 1, 1)

        self.retranslateUi(layouteditorDialog)
        QtCore.QMetaObject.connectSlotsByName(layouteditorDialog)

    def retranslateUi(self, layouteditorDialog):
        layouteditorDialog.setWindowTitle(QtGui.QApplication.translate("layouteditorDialog", "Layout Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("layouteditorDialog", "Instructions", None, QtGui.QApplication.UnicodeUTF8))
        self.label_42.setText(QtGui.QApplication.translate("layouteditorDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:600; font-style:normal;\">\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Below, the SymLayout text is loaded. Each row of this script defines an object on the SymLayout. Each row begins with a unique element ID, then a Line is defined by letter \'l\' or a Point \'p\'. Finally follows by the coordinate of lines and points on the UI.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_change_dir.setText(QtGui.QApplication.translate("layouteditorDialog", "Change Directory", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_reload.setText(QtGui.QApplication.translate("layouteditorDialog", "Reload SymLayout", None, QtGui.QApplication.UnicodeUTF8))

