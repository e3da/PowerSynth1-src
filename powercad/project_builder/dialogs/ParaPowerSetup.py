""""
ParaPowerSetup.py

Author:
Tristan Evans @tmevans

Description:
A simple dialog window to initialize ParaPower Settings.

"""

import sys
from PySide import QtGui, QtCore
from functools import partial

class ParaPowerSetupDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        super(ParaPowerSetupDialog, self).__init__(parent)

        # ParaPower setup variables
        self.matlab_dir = None
        self.Tsteps = None
        self.DeltaT = None
        self.Tinit = None
        self.Ta = None
        self.hbot = None
        self.Tproc = None

        # GUI Elements
        # self.lbl_matlab_dir = None
        self.le_Tsteps = None
        self.le_DeltaT = None
        self.le_Tinit = None
        self.le_Tproc = None
        self.initUI()

    def initUI(self):

        # MATLAB Workspace Layout Elements
        lbl_workspace = QtGui.QLabel('MATLAB Workspace Directory')
        btn_matlab_dir = QtGui.QPushButton('Open')
        lbl_matlab_dir = QtGui.QLabel()
        self.matlab_dir = btn_matlab_dir.clicked.connect(partial(self.get_matlab_directory, lbl_matlab_dir))
        layout_workspace_hbox = QtGui.QHBoxLayout()
        layout_workspace_hbox.addWidget(btn_matlab_dir)
        layout_workspace_hbox.addWidget(lbl_matlab_dir)
        layout_workspace_hbox.addStretch(1)
        layout_workspace = QtGui.QVBoxLayout()  # Main layout for workspace settings
        layout_workspace.addWidget(lbl_workspace)
        layout_workspace.addLayout(layout_workspace_hbox)
        # layout_workspace.addStretch(1)

        # self.setLayout(layout_workspace)

        # Solver Params Layout Elements
        lbl_params = QtGui.QLabel('Solver Parameters')
        form_params = QtGui.QFormLayout()
        form_params.addRow('Time Steps', QtGui.QLineEdit())
        form_params.addRow('Time Step Size', QtGui.QLineEdit())
        form_params.addRow('Initial Temp', QtGui.QLineEdit())
        layout_params_hbox = QtGui.QHBoxLayout()
        layout_params_hbox.addLayout(form_params)
        layout_params_hbox.addStretch(1)
        layout_params = QtGui.QVBoxLayout()
        # layout_params.addStretch(1)
        layout_params.addWidget(lbl_params)
        # layout_params.addStretch(1)
        layout_params.addLayout(layout_params_hbox)

        # External Conditions Layout Elements

        layout_main = QtGui.QVBoxLayout()
        layout_main.addLayout(layout_workspace)
        layout_main.addStretch(1)
        layout_main.addLayout(layout_params)
        layout_main.addStretch(1)

        self.setLayout(layout_main)


        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('ParaPower Setup')
        self.show()

    def get_matlab_directory(self, label):
        matlab_dir = QtGui.QFileDialog.getExistingDirectory()
        self.update_label(label, matlab_dir)
        return matlab_dir

    def update_label(self, label, text):
        label.setText(text)
        label.adjustSize()

def main():

    app = QtGui.QApplication(sys.argv)
    pps = ParaPowerSetupDialog()
    pps.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
