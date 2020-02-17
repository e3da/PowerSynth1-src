'''
Created on Oct 7, 2013

@author: bxs003
'''
import csv
import os
import traceback

from PySide import QtGui
from PySide.QtGui import QFileDialog

from powercad.design.project_structures import ProcessDesignRules
from powercad.general.settings.save_and_load import load_file
from powercad.project_builder.UI_py.process_design_rules_editor_ui import Ui_design_rule_dialog


class ProcessDesignRulesEditor(QtGui.QDialog):
    """Process Design Rules Dialog Editor"""
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, None)
        self.ui = Ui_design_rule_dialog()
        self.ui.setupUi(self)
        self.parent = parent # parent is ProjectBuilder object
        
        self.ui.btn_import_design_rules.pressed.connect(self.import_design_rules)
        self.ui.dialog_button_box.accepted.connect(self.set_new_rules)
        self.ui.dialog_button_box.rejected.connect(self.reject)
        
        self.fields = [self.ui.min_trace_trace_width, self.ui.min_trace_width,
                       self.ui.min_die_die_dist, self.ui.min_die_trace_dist,
                       self.ui.power_wire_trace_dist, self.ui.signal_wire_trace_dist,
                       self.ui.power_wire_comp_dist, self.ui.signal_wire_comp_dist]
        
        self.field_dict = {self.ui.min_trace_trace_width:'min_trace_trace_width', 
                           self.ui.min_trace_width:'min_trace_width',
                           self.ui.min_die_die_dist:'min_die_die_dist',
                           self.ui.min_die_trace_dist:'min_die_trace_dist',
                           self.ui.power_wire_trace_dist:'power_wire_trace_dist', 
                           self.ui.signal_wire_trace_dist:'signal_wire_trace_dist',
                           self.ui.power_wire_comp_dist:'power_wire_component_dist',
                           self.ui.signal_wire_comp_dist:'signal_wire_component_dist'}
        
        self.load_design_rules()

    def load_design_rules(self):
        if self.parent.project.module_data.design_rules is None:
            # create some default design rules
            self.parent.project.module_data.design_rules = ProcessDesignRules(1.2, 1.2, 0.2, 0.1, 1.0, 0.2, 0.2, 0.2)
            
        for key, value in self.field_dict.items():
            rule_val = getattr(self.parent.project.module_data.design_rules, value)
            key.setText(str(rule_val))
            
    def import_design_rules(self):
        prev_folder = 'C://'
        # Open and parse a design rules CSV file
        design_rules_csv_file = QFileDialog.getOpenFileName(self, "Select Design Rules File", prev_folder, "CSV Files (*.csv)")
        csv_infile = open(os.path.abspath(design_rules_csv_file[0]))
        design_rules_list = self.get_design_rules_from_csv(csv_infile)
        csv_infile.close()
        
        # Fill UI fields
        for key, value in self.field_dict.items():
            for rule in design_rules_list:
                rule_name = rule[0]
                rule_val = rule[1]
                if rule_name == value:
                    key.setText(str(rule_val))
                    
        
    def get_design_rules_from_csv(self, csv_file):
        rules_list = []
        # Read from the CSV file and append rules to rules_list
        # Each rule added to rules_list as ['rule_name', 'value']
        rule_reader = csv.reader(csv_file)
        for row in rule_reader:
            if row[0] == 'R':
                rules_list.append([row[1], row[3]])
        
        return rules_list

        
    def set_new_rules(self):
        # Sets new process design rules and closes process design rules editor window on finish
        fields_pass, field_input = self.check_fields()
        if fields_pass:
            # set data into the process design rules object
            for i in range(len(self.fields)):
                field_obj = self.fields[i]
                field_val = field_input[i]
                field_name = self.field_dict[field_obj]
                setattr(self.parent.project.module_data.design_rules, field_name, field_val)
            
            # close the window
            self.accept()
        
    def check_fields(self):
        fields_pass = True
        field_input = []
        for field in self.fields:
            try:
                field_input.append(float(field.text()))
                field.setStyleSheet("background-color:white")
            except:
                fields_pass = False
                field.setStyleSheet("background-color:pink")
                traceback.print_exc()
                
        if not fields_pass:
            QtGui.QMessageBox.warning(None, "Input Error", "Fields detected which do not represent numbers!")
        
            
        return fields_pass, field_input
        