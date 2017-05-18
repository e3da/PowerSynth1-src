# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'process_design_rules_editor.ui'
#
# Created: Tue Apr 18 14:24:35 2017
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_design_rule_dialog(object):
    def setupUi(self, design_rule_dialog):
        design_rule_dialog.setObjectName("design_rule_dialog")
        design_rule_dialog.resize(604, 275)
        self.formLayout = QtGui.QFormLayout(design_rule_dialog)
        self.formLayout.setObjectName("formLayout")
        self.label = QtGui.QLabel(design_rule_dialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.min_trace_trace_width = QtGui.QLineEdit(design_rule_dialog)
        self.min_trace_trace_width.setObjectName("min_trace_trace_width")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.min_trace_trace_width)
        self.label_2 = QtGui.QLabel(design_rule_dialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.min_trace_width = QtGui.QLineEdit(design_rule_dialog)
        self.min_trace_width.setObjectName("min_trace_width")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.min_trace_width)
        self.label_3 = QtGui.QLabel(design_rule_dialog)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.min_die_die_dist = QtGui.QLineEdit(design_rule_dialog)
        self.min_die_die_dist.setObjectName("min_die_die_dist")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.min_die_die_dist)
        self.label_4 = QtGui.QLabel(design_rule_dialog)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_4)
        self.min_die_trace_dist = QtGui.QLineEdit(design_rule_dialog)
        self.min_die_trace_dist.setObjectName("min_die_trace_dist")
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.min_die_trace_dist)
        self.label_5 = QtGui.QLabel(design_rule_dialog)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.label_5)
        self.power_wire_trace_dist = QtGui.QLineEdit(design_rule_dialog)
        self.power_wire_trace_dist.setObjectName("power_wire_trace_dist")
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.power_wire_trace_dist)
        self.label_6 = QtGui.QLabel(design_rule_dialog)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(5, QtGui.QFormLayout.LabelRole, self.label_6)
        self.signal_wire_trace_dist = QtGui.QLineEdit(design_rule_dialog)
        self.signal_wire_trace_dist.setObjectName("signal_wire_trace_dist")
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.signal_wire_trace_dist)
        self.label_7 = QtGui.QLabel(design_rule_dialog)
        self.label_7.setObjectName("label_7")
        self.formLayout.setWidget(6, QtGui.QFormLayout.LabelRole, self.label_7)
        self.power_wire_comp_dist = QtGui.QLineEdit(design_rule_dialog)
        self.power_wire_comp_dist.setObjectName("power_wire_comp_dist")
        self.formLayout.setWidget(6, QtGui.QFormLayout.FieldRole, self.power_wire_comp_dist)
        self.label_8 = QtGui.QLabel(design_rule_dialog)
        self.label_8.setObjectName("label_8")
        self.formLayout.setWidget(7, QtGui.QFormLayout.LabelRole, self.label_8)
        self.signal_wire_comp_dist = QtGui.QLineEdit(design_rule_dialog)
        self.signal_wire_comp_dist.setObjectName("signal_wire_comp_dist")
        self.formLayout.setWidget(7, QtGui.QFormLayout.FieldRole, self.signal_wire_comp_dist)
        self.dialog_button_box = QtGui.QDialogButtonBox(design_rule_dialog)
        self.dialog_button_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.dialog_button_box.setObjectName("dialog_button_box")
        self.formLayout.setWidget(8, QtGui.QFormLayout.FieldRole, self.dialog_button_box)
        self.btn_import_design_rules = QtGui.QPushButton(design_rule_dialog)
        self.btn_import_design_rules.setObjectName("btn_import_design_rules")
        self.formLayout.setWidget(8, QtGui.QFormLayout.LabelRole, self.btn_import_design_rules)

        self.retranslateUi(design_rule_dialog)
        QtCore.QMetaObject.connectSlotsByName(design_rule_dialog)

    def retranslateUi(self, design_rule_dialog):
        design_rule_dialog.setWindowTitle(QtGui.QApplication.translate("design_rule_dialog", "Process Design Rules", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("design_rule_dialog", "Min. trace to trace distance", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("design_rule_dialog", "Min. trace width", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("design_rule_dialog", "Min. die to die distance", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("design_rule_dialog", "Min. die to trace distance", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("design_rule_dialog", "Power bondwire to trace distance", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("design_rule_dialog", "Signal bondwire to trace distance", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("design_rule_dialog", "Power bondwire to component distance", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("design_rule_dialog", "Signal bondwire to component distance", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_import_design_rules.setText(QtGui.QApplication.translate("design_rule_dialog", "Import from CSV File", None, QtGui.QApplication.UnicodeUTF8))

