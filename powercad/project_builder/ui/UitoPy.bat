@cd /d "%~dp0"
@echo off
setlocal enabledelayedexpansion
for /r %%i in (*.ui) do (
set name=%%~ni
set newext=.py
set oldext=.ui
set "newname=!name!!newext!"
echo. !newname!
set "oldname=!name!!oldext!"
echo. !oldname!
pyside-uic -o !newname! !oldname!

)
move *.py .\UI_py\