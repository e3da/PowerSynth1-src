'''
Created on Oct 7, 2013

@author: bxs003
'''
import traceback

from PySide import QtCore, QtGui

from powercad.design.project_structures import ProcessDesignRules
from powercad.project_builder.dialogs.process_design_rules_editor_ui import Ui_design_rule_dialog

class ProcessDesignRulesEditor(QtGui.QDialog):
    """Process Design Rules Dialog Editor"""
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, None)
        self.ui = Ui_design_rule_dialog()
        self.ui.setupUi(self)
        self.parent = parent # parent is ProjectBuilder object
        
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
            
        for key, value in self.field_dict.iteritems():
            rule_val = getattr(self.parent.project.module_data.design_rules, value)
            key.setText(str(rule_val))
        
    def set_new_rules(self):
        fields_pass, field_input = self.check_fields()
        if fields_pass:
            # set data into the process design rules object
            for i in xrange(len(self.fields)):
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
        