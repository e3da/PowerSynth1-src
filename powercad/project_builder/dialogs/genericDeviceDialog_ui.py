# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'genericDeviceDialog.ui'
#
# Created: Sun Sep 25 22:46:50 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_generic_device_builder(object):
    def setupUi(self, generic_device_builder):
        generic_device_builder.setObjectName("generic_device_builder")
        generic_device_builder.setWindowModality(QtCore.Qt.ApplicationModal)
        generic_device_builder.resize(732, 464)
        generic_device_builder.setAccessibleName("")
        generic_device_builder.setAccessibleDescription("")
        generic_device_builder.setWindowFilePath("")
        self.frame = QtGui.QFrame(generic_device_builder)
        self.frame.setGeometry(QtCore.QRect(10, 90, 294, 291))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.widget = QtGui.QWidget(self.frame)
        self.widget.setGeometry(QtCore.QRect(3, 38, 291, 251))
        self.widget.setObjectName("widget")
        self.lst_device = QtGui.QListView(self.widget)
        self.lst_device.setGeometry(QtCore.QRect(10, 20, 256, 192))
        self.lst_device.setObjectName("lst_device")
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(10, 10, 256, 13))
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.frame_2 = QtGui.QFrame(generic_device_builder)
        self.frame_2.setGeometry(QtCore.QRect(9, 9, 294, 101))
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.label_3 = QtGui.QLabel(self.frame_2)
        self.label_3.setGeometry(QtCore.QRect(10, 10, 72, 16))
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.cmb_device_choice = QtGui.QComboBox(self.frame_2)
        self.cmb_device_choice.setGeometry(QtCore.QRect(10, 40, 281, 18))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmb_device_choice.sizePolicy().hasHeightForWidth())
        self.cmb_device_choice.setSizePolicy(sizePolicy)
        self.cmb_device_choice.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.cmb_device_choice.setEditable(True)
        self.cmb_device_choice.setObjectName("cmb_device_choice")
        self.cmb_device_choice.addItem("")
        self.cmb_device_choice.addItem("")
        self.btn_buildgenericmdl = QtGui.QPushButton(generic_device_builder)
        self.btn_buildgenericmdl.setGeometry(QtCore.QRect(30, 410, 261, 23))
        self.btn_buildgenericmdl.setObjectName("btn_buildgenericmdl")
        self.groupBox_8 = QtGui.QGroupBox(generic_device_builder)
        self.groupBox_8.setGeometry(QtCore.QRect(310, 20, 411, 161))
        self.groupBox_8.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.groupBox_8.setFont(font)
        self.groupBox_8.setObjectName("groupBox_8")
        self.gridLayout_7 = QtGui.QGridLayout(self.groupBox_8)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.label_44 = QtGui.QLabel(self.groupBox_8)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_44.setFont(font)
        self.label_44.setWordWrap(True)
        self.label_44.setObjectName("label_44")
        self.gridLayout_7.addWidget(self.label_44, 0, 0, 1, 1)
        self.stackedWidget = QtGui.QStackedWidget(generic_device_builder)
        self.stackedWidget.setEnabled(True)
        self.stackedWidget.setGeometry(QtCore.QRect(310, 190, 221, 261))
        self.stackedWidget.setObjectName("stackedWidget")
        self.page_3 = QtGui.QWidget()
        self.page_3.setObjectName("page_3")
        self.widget_5 = QtGui.QWidget(self.page_3)
        self.widget_5.setEnabled(True)
        self.widget_5.setGeometry(QtCore.QRect(10, 20, 192, 50))
        self.widget_5.setAutoFillBackground(True)
        self.widget_5.setObjectName("widget_5")
        self.gridLayout_6 = QtGui.QGridLayout(self.widget_5)
        self.gridLayout_6.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.label_15 = QtGui.QLabel(self.widget_5)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_15.setFont(font)
        self.label_15.setObjectName("label_15")
        self.gridLayout_6.addWidget(self.label_15, 0, 0, 1, 1)
        self.label_16 = QtGui.QLabel(self.widget_5)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_16.setFont(font)
        self.label_16.setObjectName("label_16")
        self.gridLayout_6.addWidget(self.label_16, 1, 0, 1, 1)
        self.stackedWidget.addWidget(self.page_3)
        self.page_4 = QtGui.QWidget()
        self.page_4.setObjectName("page_4")
        self.widget_6 = QtGui.QWidget(self.page_4)
        self.widget_6.setEnabled(True)
        self.widget_6.setGeometry(QtCore.QRect(2, 15, 211, 221))
        self.widget_6.setAutoFillBackground(True)
        self.widget_6.setObjectName("widget_6")
        self.gridLayout_5 = QtGui.QGridLayout(self.widget_6)
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_17 = QtGui.QLabel(self.widget_6)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_17.setFont(font)
        self.label_17.setObjectName("label_17")
        self.gridLayout_5.addWidget(self.label_17, 0, 0, 1, 2)
        self.label_18 = QtGui.QLabel(self.widget_6)
        self.label_18.setObjectName("label_18")
        self.gridLayout_5.addWidget(self.label_18, 1, 0, 1, 1)
        self.ln_edit_qrr = QtGui.QLineEdit(self.widget_6)
        self.ln_edit_qrr.setObjectName("ln_edit_qrr")
        self.gridLayout_5.addWidget(self.ln_edit_qrr, 1, 1, 1, 1)
        self.label_19 = QtGui.QLabel(self.widget_6)
        self.label_19.setObjectName("label_19")
        self.gridLayout_5.addWidget(self.label_19, 2, 0, 1, 1)
        self.ln_edit_ciss = QtGui.QLineEdit(self.widget_6)
        self.ln_edit_ciss.setObjectName("ln_edit_ciss")
        self.gridLayout_5.addWidget(self.ln_edit_ciss, 2, 1, 1, 1)
        self.label_21 = QtGui.QLabel(self.widget_6)
        self.label_21.setObjectName("label_21")
        self.gridLayout_5.addWidget(self.label_21, 4, 0, 1, 1)
        self.ln_edit_vpl = QtGui.QLineEdit(self.widget_6)
        self.ln_edit_vpl.setObjectName("ln_edit_vpl")
        self.gridLayout_5.addWidget(self.ln_edit_vpl, 4, 1, 1, 1)
        self.label_22 = QtGui.QLabel(self.widget_6)
        self.label_22.setObjectName("label_22")
        self.gridLayout_5.addWidget(self.label_22, 5, 0, 1, 1)
        self.btn_vth_vs_tj = QtGui.QPushButton(self.widget_6)
        self.btn_vth_vs_tj.setObjectName("btn_vth_vs_tj")
        self.gridLayout_5.addWidget(self.btn_vth_vs_tj, 5, 1, 1, 1)
        self.label_23 = QtGui.QLabel(self.widget_6)
        self.label_23.setObjectName("label_23")
        self.gridLayout_5.addWidget(self.label_23, 6, 0, 1, 1)
        self.btn_crss_vs_vds = QtGui.QPushButton(self.widget_6)
        self.btn_crss_vs_vds.setObjectName("btn_crss_vs_vds")
        self.gridLayout_5.addWidget(self.btn_crss_vs_vds, 6, 1, 1, 1)
        self.label_24 = QtGui.QLabel(self.widget_6)
        self.label_24.setObjectName("label_24")
        self.gridLayout_5.addWidget(self.label_24, 7, 0, 1, 1)
        self.btn_rds_vs_tj = QtGui.QPushButton(self.widget_6)
        self.btn_rds_vs_tj.setObjectName("btn_rds_vs_tj")
        self.gridLayout_5.addWidget(self.btn_rds_vs_tj, 7, 1, 1, 1)
        self.stackedWidget.addWidget(self.page_4)
        self.graphicsView = QtGui.QGraphicsView(generic_device_builder)
        self.graphicsView.setGeometry(QtCore.QRect(530, 190, 181, 241))
        self.graphicsView.setObjectName("graphicsView")

        self.retranslateUi(generic_device_builder)
        self.stackedWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(generic_device_builder)

    def retranslateUi(self, generic_device_builder):
        generic_device_builder.setWindowTitle(QtGui.QApplication.translate("generic_device_builder", "Generic model", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("generic_device_builder", "Device List:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("generic_device_builder", "Device Type:", None, QtGui.QApplication.UnicodeUTF8))
        self.cmb_device_choice.setItemText(0, QtGui.QApplication.translate("generic_device_builder", "Transistor", None, QtGui.QApplication.UnicodeUTF8))
        self.cmb_device_choice.setItemText(1, QtGui.QApplication.translate("generic_device_builder", "Diode", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_buildgenericmdl.setText(QtGui.QApplication.translate("generic_device_builder", "Build Generic Model", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_8.setTitle(QtGui.QApplication.translate("generic_device_builder", "Instructions", None, QtGui.QApplication.UnicodeUTF8))
        self.label_44.setText(QtGui.QApplication.translate("generic_device_builder", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:10pt; font-weight:600; font-style:normal;\">\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Select a Device from the device list on the left and input Datasheet information on the right to create the power dissipation model for each device</span></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Vth vs Tj csv file:  Left collumn name: \' Tj\'. Right collumn name: \'Vth\'</span></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Crss vs Vds csv file:  Left collumn name: \' Vds\'. Right collumn name: \'Cap\'</span></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Rds vs Tj CVS file:  Left collumn name: \' Tj\'. Right collumn name: \'Rds\'</span><span style=\" font-size:8pt;\"> </span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_15.setText(QtGui.QApplication.translate("generic_device_builder", "Datasheet Information Diode:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_16.setText(QtGui.QApplication.translate("generic_device_builder", "This feature will be added soon", None, QtGui.QApplication.UnicodeUTF8))
        self.label_17.setText(QtGui.QApplication.translate("generic_device_builder", "Datasheet Information Transitor:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_18.setText(QtGui.QApplication.translate("generic_device_builder", "Qrr", None, QtGui.QApplication.UnicodeUTF8))
        self.label_19.setText(QtGui.QApplication.translate("generic_device_builder", "Ciss", None, QtGui.QApplication.UnicodeUTF8))
        self.label_21.setText(QtGui.QApplication.translate("generic_device_builder", "Vpl", None, QtGui.QApplication.UnicodeUTF8))
        self.label_22.setText(QtGui.QApplication.translate("generic_device_builder", "Vth vs Tj", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_vth_vs_tj.setText(QtGui.QApplication.translate("generic_device_builder", "Load CSV data", None, QtGui.QApplication.UnicodeUTF8))
        self.label_23.setText(QtGui.QApplication.translate("generic_device_builder", "Crss vs Vds", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_crss_vs_vds.setText(QtGui.QApplication.translate("generic_device_builder", "Load CSV data", None, QtGui.QApplication.UnicodeUTF8))
        self.label_24.setText(QtGui.QApplication.translate("generic_device_builder", "Rds vs Tj", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_rds_vs_tj.setText(QtGui.QApplication.translate("generic_device_builder", "Load CSV data", None, QtGui.QApplication.UnicodeUTF8))
