# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\shook\Documents\DropBox_madshook\Dropbox\PMLST\code\workspace\PowerCAD\src\powercad\sol_browser\ui\objective_widget.ui'
#
# Created: Sun Feb 23 15:41:32 2014
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ObjectiveWidget(object):
    def setupUi(self, ObjectiveWidget):
        ObjectiveWidget.setObjectName("ObjectiveWidget")
        ObjectiveWidget.resize(480, 286)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ObjectiveWidget.sizePolicy().hasHeightForWidth())
        ObjectiveWidget.setSizePolicy(sizePolicy)
        ObjectiveWidget.setMinimumSize(QtCore.QSize(334, 192))
        ObjectiveWidget.setWindowOpacity(1.0)
        ObjectiveWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        ObjectiveWidget.setFrameShape(QtGui.QFrame.NoFrame)
        ObjectiveWidget.setFrameShadow(QtGui.QFrame.Plain)
        self.grpbx_objective = QtGui.QGroupBox(ObjectiveWidget)
        self.grpbx_objective.setGeometry(QtCore.QRect(2, 0, 330, 190))
        self.grpbx_objective.setMinimumSize(QtCore.QSize(330, 190))
        self.grpbx_objective.setMaximumSize(QtCore.QSize(330, 190))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setWeight(75)
        font.setBold(True)
        self.grpbx_objective.setFont(font)
        self.grpbx_objective.setObjectName("grpbx_objective")
        self.sldr_pos = QtGui.QSlider(self.grpbx_objective)
        self.sldr_pos.setGeometry(QtCore.QRect(80, 50, 200, 19))
        self.sldr_pos.setMinimum(0)
        self.sldr_pos.setMaximum(100)
        self.sldr_pos.setProperty("value", 50)
        self.sldr_pos.setOrientation(QtCore.Qt.Horizontal)
        self.sldr_pos.setObjectName("sldr_pos")
        self.sldr_env = QtGui.QSlider(self.grpbx_objective)
        self.sldr_env.setGeometry(QtCore.QRect(80, 100, 200, 19))
        self.sldr_env.setMinimum(0)
        self.sldr_env.setMaximum(100)
        self.sldr_env.setProperty("value", 100)
        self.sldr_env.setOrientation(QtCore.Qt.Horizontal)
        self.sldr_env.setObjectName("sldr_env")
        self.txt_max = QtGui.QLineEdit(self.grpbx_objective)
        self.txt_max.setGeometry(QtCore.QRect(275, 150, 50, 20))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setWeight(50)
        font.setBold(False)
        self.txt_max.setFont(font)
        self.txt_max.setText("")
        self.txt_max.setMaxLength(6)
        self.txt_max.setAlignment(QtCore.Qt.AlignCenter)
        self.txt_max.setObjectName("txt_max")
        self.txt_min = QtGui.QLineEdit(self.grpbx_objective)
        self.txt_min.setGeometry(QtCore.QRect(5, 150, 50, 20))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setWeight(50)
        font.setBold(False)
        self.txt_min.setFont(font)
        self.txt_min.setText("")
        self.txt_min.setMaxLength(6)
        self.txt_min.setAlignment(QtCore.Qt.AlignCenter)
        self.txt_min.setObjectName("txt_min")
        self.label_4 = QtGui.QLabel(self.grpbx_objective)
        self.label_4.setGeometry(QtCore.QRect(20, 130, 21, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setWeight(75)
        font.setUnderline(True)
        font.setBold(True)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.label_5 = QtGui.QLabel(self.grpbx_objective)
        self.label_5.setGeometry(QtCore.QRect(287, 130, 31, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setWeight(75)
        font.setUnderline(True)
        font.setBold(True)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.lbl_pos = QtGui.QLabel(self.grpbx_objective)
        self.lbl_pos.setGeometry(QtCore.QRect(285, 50, 41, 20))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setWeight(50)
        font.setBold(False)
        self.lbl_pos.setFont(font)
        self.lbl_pos.setObjectName("lbl_pos")
        self.lbl_env = QtGui.QLabel(self.grpbx_objective)
        self.lbl_env.setGeometry(QtCore.QRect(285, 100, 41, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setWeight(50)
        font.setBold(False)
        self.lbl_env.setFont(font)
        self.lbl_env.setObjectName("lbl_env")
        self.line = QtGui.QFrame(self.grpbx_objective)
        self.line.setGeometry(QtCore.QRect(55, 31, 16, 91))
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.label_3 = QtGui.QLabel(self.grpbx_objective)
        self.label_3.setGeometry(QtCore.QRect(84, 32, 111, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setWeight(75)
        font.setUnderline(True)
        font.setBold(True)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_2 = QtGui.QLabel(self.grpbx_objective)
        self.label_2.setGeometry(QtCore.QRect(84, 77, 91, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setWeight(75)
        font.setUnderline(True)
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label = QtGui.QLabel(self.grpbx_objective)
        self.label.setGeometry(QtCore.QRect(19, 32, 24, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setWeight(75)
        font.setUnderline(True)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.ckbx_X = QtGui.QCheckBox(self.grpbx_objective)
        self.ckbx_X.setGeometry(QtCore.QRect(19, 51, 29, 17))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setWeight(50)
        font.setBold(False)
        self.ckbx_X.setFont(font)
        self.ckbx_X.setObjectName("ckbx_X")
        self.ckbx_Y = QtGui.QCheckBox(self.grpbx_objective)
        self.ckbx_Y.setGeometry(QtCore.QRect(19, 74, 29, 17))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setWeight(50)
        font.setBold(False)
        self.ckbx_Y.setFont(font)
        self.ckbx_Y.setObjectName("ckbx_Y")
        self.ckbx_Z = QtGui.QCheckBox(self.grpbx_objective)
        self.ckbx_Z.setGeometry(QtCore.QRect(19, 97, 29, 17))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setWeight(50)
        font.setBold(False)
        self.ckbx_Z.setFont(font)
        self.ckbx_Z.setObjectName("ckbx_Z")
        self.grfx_display = QtGui.QGraphicsView(self.grpbx_objective)
        self.grfx_display.setGeometry(QtCore.QRect(60, 150, 211, 20))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        self.grfx_display.setPalette(palette)
        self.grfx_display.setFrameShape(QtGui.QFrame.NoFrame)
        self.grfx_display.setFrameShadow(QtGui.QFrame.Plain)
        self.grfx_display.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.grfx_display.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.grfx_display.setObjectName("grfx_display")

        self.retranslateUi(ObjectiveWidget)
        QtCore.QMetaObject.connectSlotsByName(ObjectiveWidget)

    def retranslateUi(self, ObjectiveWidget):
        ObjectiveWidget.setWindowTitle(QtGui.QApplication.translate("ObjectiveWidget", "Frame", None, QtGui.QApplication.UnicodeUTF8))
        self.grpbx_objective.setTitle(QtGui.QApplication.translate("ObjectiveWidget", "GroupBox", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("ObjectiveWidget", "Min", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("ObjectiveWidget", "Max", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_pos.setText(QtGui.QApplication.translate("ObjectiveWidget", "Val", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_env.setText(QtGui.QApplication.translate("ObjectiveWidget", "Val", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("ObjectiveWidget", "Envelope Position", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ObjectiveWidget", "Envelope Size", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ObjectiveWidget", "Axis", None, QtGui.QApplication.UnicodeUTF8))
        self.ckbx_X.setText(QtGui.QApplication.translate("ObjectiveWidget", "X", None, QtGui.QApplication.UnicodeUTF8))
        self.ckbx_Y.setText(QtGui.QApplication.translate("ObjectiveWidget", "Y", None, QtGui.QApplication.UnicodeUTF8))
        self.ckbx_Z.setText(QtGui.QApplication.translate("ObjectiveWidget", "Z", None, QtGui.QApplication.UnicodeUTF8))
