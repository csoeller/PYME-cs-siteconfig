@echo off
setlocal

set INITPATH=C:\python-support-files\PYME-cs-siteconfig\init_scripts

rem ONLY modify the path if needed
set PATH=c:\ProgramData\Miniconda3\condabin;C:\python-support-files\PYME-cs-siteconfig\launchers\bin;%PATH%
rem set PATH=c:\ProgramData\Miniconda3\condabin;C:\Program Files\IDS\uEye\develop\bin;%PATH%

call conda-activate-chosen-env.bat

cd \python-support-files\pymelogs\driftTracking
pymeacquire -i %INITPATH%\tracking\init_drift_tracking_cs.py

call conda deactivate

cmd /k
