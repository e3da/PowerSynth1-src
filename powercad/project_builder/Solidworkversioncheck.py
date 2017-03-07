# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Solidworkversioncheck.ui'
#
# Created: Thu Mar 24 11:56:31 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_checkversion_dialog(object):
    def setupUi(self, checkversion_dialog):
        checkversion_dialog.setObjectName("checkversion_dialog")
        checkversion_dialog.resize(576, 301)
        self.buttonBox = QtGui.QDialogButtonBox(checkversion_dialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.SolidworkVersion = QtGui.QLineEdit(checkversion_dialog)
        self.SolidworkVersion.setGeometry(QtCore.QRect(150, 170, 201, 20))
        self.SolidworkVersion.setObjectName("SolidworkVersion")
        self.solidworkversion = QtGui.QLabel(checkversion_dialog)
        self.solidworkversion.setGeometry(QtCore.QRect(30, 170, 101, 16))
        self.solidworkversion.setObjectName("solidworkversion")
        self.To_User = QtGui.QLabel(checkversion_dialog)
        self.To_User.setGeometry(QtCore.QRect(10, 10, 561, 111))
        self.To_User.setObjectName("To_User")

        self.retranslateUi(checkversion_dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), checkversion_dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), checkversion_dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(checkversion_dialog)

    def retranslateUi(self, checkversion_dialog):
        checkversion_dialog.setWindowTitle(QtGui.QApplication.translate("checkversion_dialog", "Solidwork version checker", None, QtGui.QApplication.UnicodeUTF8))
        self.solidworkversion.setText(QtGui.QApplication.translate("checkversion_dialog", "<html><head/><body><p><span style=\" font-weight:600;\">Solidwork version</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.To_User.setText(QtGui.QApplication.translate("checkversion_dialog", "<html><head/><body><p><span style=\" font-weight:600;\">Depends on the Solidwork version on your computer the .swp macro file will be written differently.</span></p><p><span style=\" font-weight:600;\">To ensure this macro file works on your system, please input your Solidwork version</span></p><p><span style=\" font-weight:600;\">Input version number below (e.g 2012, 2014...)</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

