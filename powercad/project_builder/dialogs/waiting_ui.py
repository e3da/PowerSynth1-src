# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'waiting_ui.ui'
#
# Created: Wed Sep 26 10:33:43 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_waiting_dialog(object):
    def setupUi(self, waiting_dialog):
        waiting_dialog.setObjectName("waiting_dialog")
        waiting_dialog.resize(436, 78)
        self.gridLayout = QtGui.QGridLayout(waiting_dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.txt_wait_msg = QtGui.QLabel(waiting_dialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.txt_wait_msg.setFont(font)
        self.txt_wait_msg.setObjectName("txt_wait_msg")
        self.gridLayout.addWidget(self.txt_wait_msg, 0, 0, 1, 1)

        self.retranslateUi(waiting_dialog)
        QtCore.QMetaObject.connectSlotsByName(waiting_dialog)

    def retranslateUi(self, waiting_dialog):
        waiting_dialog.setWindowTitle(QtGui.QApplication.translate("waiting_dialog", "please wait !!", None, QtGui.QApplication.UnicodeUTF8))
        self.txt_wait_msg.setText(QtGui.QApplication.translate("waiting_dialog", "Running thermal characterization, please wait ... ", None, QtGui.QApplication.UnicodeUTF8))

