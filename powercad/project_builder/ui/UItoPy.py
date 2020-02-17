# ONLY WORKS FOR PYTHON 2

import os
import shutil

def convert_and_move(file):
    file_name = file[0:-3]
    file_name += "_ui.py"
    command = "pyside-uic -o " + file_name + " " + file
    try:
        os.system(command)
        print(command)
    except:
        print("Please add pyside-uic to your system variable, you can find this in $PythonInstallDir/Scripts")
    destination = "../UI_py/" + file_name
    shutil.move(file_name, destination)


cwd = os.getcwd()  # current directory



print("This code performs UI to Py conversion. Double check with the team for the pyside current version, " \
      "high resolution monitor is recommended")
print("Type [-all] to convert all ui files to py or a ui file name [*.ui] to convert single file")
mode = input()

if mode == "-all":
    for file in os.listdir(cwd):  # Get all files in current dir
        if file.endswith(".ui"):
            convert_and_move(file)
else:
    name = mode
    if os.path.isfile(name):
        convert_and_move(name)
    else:
        print("the selected file is not existed")

