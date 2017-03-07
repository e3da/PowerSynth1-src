'''
Created on Oct 5, 2012

@author: anizam
'''

import os
import sys
import pickle

from PySide import QtGui
from PySide.QtGui import QMessageBox

from powercad.tech_lib.tech_lib_wiz_ui import Ui_Wizard
from powercad.design.library_structures import *
from powercad.tech_lib.test_techlib import make_sub_dir
from powercad.tech_lib.device import DevicePage
from powercad.tech_lib.die_attach import DieAttachPage
from powercad.tech_lib.lead import LeadPage
from powercad.tech_lib.bondwire import BondwirePage
from powercad.tech_lib.substrate import SubstratePage
from powercad.tech_lib.substrate_attach import SubAttachPage
from powercad.tech_lib.baseplate import BaseplatePage
import powercad.settings as settings

class TechLibWizDialog(QtGui.QWizard):
    
    #Page IDs
    DEVICE_PAGE = 1
    DIE_ATTACH_PAGE = 2
    LEAD_PAGE = 3
    BONDWIRE_PAGE = 4
    SUBSTRATE_PAGE = 5
    SUB_ATTACH_PAGE = 6
    BASEPLATE_PAGE = 7
    
    #This section activates the Technology Library Wizard pages. It goes through the wizard,
    #collects the user input, validates the data entered, raises error message if the data
    #are invalid or stores the data if it's valid.
    
    def __init__(self, parent=None, tech_lib_dir=settings.DEFAULT_TECH_LIB_DIR):
        QtGui.QWizard.__init__(self, parent)
        
        # Load Qt wizard
        self.ui = Ui_Wizard()
        self.ui.setupUi(self)
        
        # Store tech. lib. directory
        self.tech_lib_dir = tech_lib_dir
        
        # Connect signal representing Wizard page change
        self.currentIdChanged.connect(self.page_changed)
        
        # Call all pages
        self.device_page = DevicePage(self)
        self.die_attach_page = DieAttachPage(self)
        self.lead_page = LeadPage(self)
        self.bondwire_page = BondwirePage(self)
        self.substrate_page = SubstratePage(self)
        self.sub_attach_page = SubAttachPage(self)
        self.baseplate_page = BaseplatePage(self)
        
    def page_changed(self, page_id):
        if page_id == self.DEVICE_PAGE:
            self.device_page.load_page()
        elif page_id == self.DIE_ATTACH_PAGE:
            self.die_attach_page.load_page() 
        elif page_id == self.LEAD_PAGE:
            self.lead_page.load_page()
        elif page_id == self.BONDWIRE_PAGE:
            self.bondwire_page.load_page()
        elif page_id == self.SUBSTRATE_PAGE:
            self.substrate_page.load_page()
        elif page_id == self.SUB_ATTACH_PAGE:
            self.sub_attach_page.load_page()
        elif page_id == self.BASEPLATE_PAGE:
            self.baseplate_page.load_page()
      
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    techlib = TechLibWizDialog()
    techlib.show()
    sys.exit(app.exec_())
    