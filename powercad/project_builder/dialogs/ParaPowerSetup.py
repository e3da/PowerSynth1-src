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

        self.parent = parent
        self.matlab_dir = None

        # GUI Elements
        # self.lbl_matlab_dir = None
        self.le_Tsteps = QtGui.QLineEdit()
        self.le_DeltaT = QtGui.QLineEdit()
        self.le_Tinit = QtGui.QLineEdit()
        self.le_Tproc = QtGui.QLineEdit()

        # ParaPower setup variables
        self.parapower_settings = {
            'Tsteps': self.le_Tsteps,
            'DeltaT': self.le_DeltaT,
            'Tinit': self.le_Tinit,
            'Tproc': self.le_Tproc
        }
        self.initUI()

    def initUI(self):
        # MATLAB Workspace Layout Elements
        lbl_workspace = QtGui.QLabel('MATLAB Workspace Directory')
        btn_matlab_dir = QtGui.QPushButton('Open')
        lbl_matlab_dir = QtGui.QLabel()
        btn_matlab_dir.clicked.connect(partial(self.get_matlab_directory, lbl_matlab_dir))
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
        form_params.addRow('Time Steps', self.le_Tsteps)
        form_params.addRow('Time Step Size', self.le_DeltaT)
        form_params.addRow('Initial Temperature', self.le_Tinit)
        form_params.addRow('Process Temperature', self.le_Tproc)

        self.le_Tsteps.textChanged.connect(self.le_Tsteps.setText)
        self.le_DeltaT.textChanged.connect(self.le_DeltaT.setText)
        self.le_Tinit.textChanged.connect(self.le_Tinit.setText)
        self.le_Tproc.textChanged.connect(self.le_Tproc.setText)

        layout_params_hbox = QtGui.QHBoxLayout()
        layout_params_hbox.addLayout(form_params)
        layout_params_hbox.addStretch(1)
        layout_params = QtGui.QVBoxLayout()
        # layout_params.addStretch(1)
        layout_params.addWidget(lbl_params)
        # layout_params.addStretch(1)
        layout_params.addLayout(layout_params_hbox)

        btn_save = QtGui.QPushButton('Save')
        btn_save.clicked.connect(self.save)

        layout_main = QtGui.QVBoxLayout()
        layout_main.addLayout(layout_workspace)
        layout_main.addStretch(1)
        layout_main.addLayout(layout_params)
        layout_main.addStretch(1)
        layout_main.addWidget(btn_save)

        self.setLayout(layout_main)


        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('ParaPower Setup')
        self.show()

    def get_matlab_directory(self, label):
        self.matlab_dir = QtGui.QFileDialog.getExistingDirectory()
        self.update_label(label, self.matlab_dir)

    def update_label(self, label, text):
        label.setText(text)
        label.adjustSize()

    def save(self):
        for key, value in self.parapower_settings.iteritems():
            print key, value.text()


def main():

    app = QtGui.QApplication(sys.argv)
    pps = ParaPowerSetupDialog()
    pps.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
