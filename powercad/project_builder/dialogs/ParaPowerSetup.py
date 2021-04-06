""""
ParaPowerSetup.py

Author:
Tristan Evans @tmevans

Description:
A simple dialog window to initialize ParaPower Settings.

"""
from Tkinter import *
import ttk
import json
import os

SETTINGS_FILE = './settings.json'


class ParaPowerSettingsDialog(ttk.Frame, object):
    def __init__(self, parent, temperature=25.0, convection=100.0, process_temperature=230.0,
                 settings_file='./settings.json'):
        super(ParaPowerSettingsDialog, self).__init__(parent)
        self.root = parent
        self.grid(column=0, row=0, sticky=(N, W, E, S))
        self.temperature = temperature
        self.convection = convection
        self.process_temperature = process_temperature
        self.settings_file = settings_file
        self.params = {}
        self.external_conditions = {}
        self.settings = {}

        # Boundary heat transfer coefficients
        self.h_left = StringVar()
        self.h_right = StringVar()
        self.h_front = StringVar()
        self.h_back = StringVar()
        self.h_bottom = StringVar()
        self.h_top = StringVar()

        # Boundary temperature conditions
        self.ta_left = StringVar()
        self.ta_right = StringVar()
        self.ta_front = StringVar()
        self.ta_back = StringVar()
        self.ta_bottom = StringVar()
        self.ta_top = StringVar()

        # Solver settings
        self.time_steps = StringVar()
        self.time_delta = StringVar()
        self.temperature_init = StringVar()
        self.temperature_proc = StringVar()

        # UI Settings
        self.column_width = 11

        # UI ELEMENTS
        # Boundary Conditions
        ttk.Label(self, text='Boundary \nConditions', font='Helvetica 16 bold').grid(column=1, row=1, sticky=N)
        ttk.Label(self, text='Face', font='Helvetica 10 bold').grid(column=1, row=2, sticky=W)
        ttk.Label(self, text='Heat Transfer \nCoeff. \n(W/m^2/K)', font='Helvetica 10 bold').grid(column=2, row=2,
                                                                                                       sticky=E)
        ttk.Label(self, text='Ambient \nTemperature\n(deg C)', font='Helvetica 10 bold').grid(column=3, row=2,
                                                                                                   sticky=W)

        # Left
        ttk.Label(self, text='Left').grid(column=1, row=3, sticky=W)

        self.h_left_entry = ttk.Entry(self, width=self.column_width, textvariable=self.h_left)
        self.h_left_entry.grid(column=2, row=3, sticky=W)

        self.ta_left_entry = ttk.Entry(self, width=self.column_width, textvariable=self.ta_left)
        self.ta_left_entry.grid(column=3, row=3, sticky=W)

        # Right
        ttk.Label(self, text='Right').grid(column=1, row=4, sticky=W)

        self.h_right_entry = ttk.Entry(self, width=self.column_width, textvariable=self.h_right)
        self.h_right_entry.grid(column=2, row=4, sticky=W)

        self.ta_right_entry = ttk.Entry(self, width=self.column_width, textvariable=self.ta_right)
        self.ta_right_entry.grid(column=3, row=4, sticky=W)

        # Front
        ttk.Label(self, text='Front').grid(column=1, row=5, sticky=W)

        self.h_front_entry = ttk.Entry(self, width=self.column_width, textvariable=self.h_front)
        self.h_front_entry.grid(column=2, row=5, sticky=W)

        self.ta_front_entry = ttk.Entry(self, width=self.column_width, textvariable=self.ta_front)
        self.ta_front_entry.grid(column=3, row=5, sticky=W)

        # Back
        ttk.Label(self, text='Back').grid(column=1, row=6, sticky=W)

        self.h_back_entry = ttk.Entry(self, width=self.column_width, textvariable=self.h_back)
        self.h_back_entry.grid(column=2, row=6, sticky=W)

        self.ta_back_entry = ttk.Entry(self, width=self.column_width, textvariable=self.ta_back)
        self.ta_back_entry.grid(column=3, row=6, sticky=W)

        # Top
        ttk.Label(self, text='Top').grid(column=1, row=8, sticky=W)

        self.h_top_entry = ttk.Entry(self, width=self.column_width, textvariable=self.h_top)
        self.h_top_entry.grid(column=2, row=8, sticky=W)

        self.ta_top_entry = ttk.Entry(self, width=self.column_width, textvariable=self.ta_top)
        self.ta_top_entry.grid(column=3, row=8, sticky=W)

        # Bottom
        ttk.Label(self, text='Bottom').grid(column=1, row=9, sticky=W)

        self.h_bottom_entry = ttk.Entry(self, width=self.column_width, textvariable=self.h_bottom)
        self.h_bottom_entry.grid(column=2, row=9, sticky=W)

        self.ta_bottom_entry = ttk.Entry(self, width=self.column_width, textvariable=self.ta_bottom)
        self.ta_bottom_entry.grid(column=3, row=9, sticky=W)

        # Solver Settings
        ttk.Label(self, text='Solver\nSettings', font='Helvetica 16 bold').grid(column=1, row=10, sticky=W)

        # Disabling Time Steps and Time Delta for now since this release is only running ParaPower with static settings
        ttk.Label(self, text='Time Steps').grid(column=1, row=11, sticky=W)
        self.time_steps_entry = ttk.Entry(self, width=self.column_width, textvariable=self.time_steps, state='disabled')
        self.time_steps_entry.grid(column=2, row=11, sticky=W)

        ttk.Label(self, text='Time Delta').grid(column=1, row=12, sticky=W)
        self.time_delta_entry = ttk.Entry(self, width=self.column_width, textvariable=self.time_delta, state='disabled')
        self.time_delta_entry.grid(column=2, row=12, sticky=W)

        ttk.Label(self, text='Initial Temperature').grid(column=1, row=13, sticky=W)
        self.temperature_init_entry = ttk.Entry(self, width=self.column_width, textvariable=self.temperature_init)
        self.temperature_init_entry.grid(column=2, row=13, sticky=W)

        ttk.Label(self, text='Process Temperature').grid(column=1, row=14, sticky=W)
        self.temperature_proc_entry = ttk.Entry(self, width=self.column_width, textvariable=self.temperature_proc)
        self.temperature_proc_entry.grid(column=2, row=14, sticky=W)

        # Buttons
        ttk.Button(self, text="Default", command=self.set_defaults).grid(column=2, row=15, sticky=W)
        ttk.Button(self, text="Write Settings \n& Close", command=self.write_settings).grid(column=3, row=15, sticky=W)
        ttk.Button(self, text="Reload", command=self.read_settings).grid(column=1, row=15, sticky=W)

        # Set default values once during launch
        self.set_defaults()

    def set_defaults(self, *args):
        try:
            self.h_left.set(0.0)
            self.h_right.set(0.0)
            self.h_front.set(0.0)
            self.h_back.set(0.0)
            self.h_top.set(0.0)
            self.h_bottom.set(self.convection)

            self.ta_left.set(self.temperature)
            self.ta_right.set(self.temperature)
            self.ta_front.set(self.temperature)
            self.ta_back.set(self.temperature)
            self.ta_top.set(self.temperature)
            self.ta_bottom.set(self.temperature)

            self.time_steps.set('[]')
            self.time_delta.set(1)
            self.temperature_init.set(self.temperature)
            self.temperature_proc.set(self.process_temperature)
        except ValueError:
            pass

    def write_settings(self, *args):
        try:
            self.external_conditions = {
                'h_Left': self.h_left.get(),
                'h_Right': self.h_right.get(),
                'h_Front': self.h_front.get(),
                'h_Back': self.h_back.get(),
                'h_Top': self.h_top.get(),
                'h_Bottom': self.h_bottom.get(),
                'Ta_Left': self.ta_left.get(),
                'Ta_Right': self.ta_right.get(),
                'Ta_Front': self.ta_front.get(),
                'Ta_Back': self.ta_back.get(),
                'Ta_Top': self.ta_top.get(),
                'Ta_Bottom': self.ta_bottom.get(),
                'Tproc': self.temperature_proc.get()
            }

            self.params = {
                'Tsteps': self.time_steps.get(),
                'DeltaT': self.time_delta.get(),
                'Tinit': self.temperature_init.get()
            }

            self.settings = {
                'ExternalConditions': self.external_conditions,
                'Params': self.params
            }

            # Save output as JSON file
            output = json.dumps(self.settings, indent=4)
            with open(self.settings_file, 'w') as fp:
                fp.write(output)
            # Close the ParaPower settings window
            self.root.destroy()

        except ValueError:
            pass

    def read_settings(self, *args):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'rb') as data:
                jsondata = json.load(data)
            try:
                extcond = jsondata['ExternalConditions']
                params = jsondata['Params']

                self.h_left.set(float(extcond['h_Left']))
                self.h_right.set(float(extcond['h_Right']))
                self.h_front.set(float(extcond['h_Front']))
                self.h_back.set(float(extcond['h_Back']))
                self.h_top.set(float(extcond['h_Top']))
                self.h_bottom.set(float(extcond['h_Bottom']))
                self.ta_left.set(float(extcond['Ta_Left']))
                self.ta_right.set(float(extcond['Ta_Right']))
                self.ta_front.set(float(extcond['Ta_Front']))
                self.ta_back.set(float(extcond['Ta_Back']))
                self.ta_top.set(float(extcond['Ta_Top']))
                self.ta_bottom.set(float(extcond['Ta_Bottom']))
                self.temperature_proc.set(float(extcond['Tproc']))

                self.time_steps.set(params['Tsteps'])
                self.time_delta.set(int(params['DeltaT']))
                self.temperature_init.set(float(params['Tinit']))

            except ValueError:
                pass
        else:
            print "No settings file found, creating new file with defaults."
            self.write_settings()


def launch_parapower_settings(temperature=25.0, convection=100.0, process_temperature=230.0,
                              settings_file='./settings.json'):
    root = Tk()
    root.title('ParaPower Settings')
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    app = ParaPowerSettingsDialog(root, temperature, convection, process_temperature, settings_file=settings_file)
    root.mainloop()


if __name__ == '__main__':
    launch_parapower_settings(25.0, 100.0, 230.0, settings_file='./settings_test.json')
