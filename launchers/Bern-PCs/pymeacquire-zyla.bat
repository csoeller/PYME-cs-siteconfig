@echo off
setlocal

set INITPATH=C:\python-support-files\PYME-cs-siteconfig\init_scripts

rem ONLY modify the path if needed
set PATH=c:\ProgramData\Miniconda3\condabin;C:\Program Files\Andor SDK3;C:\python-support-files\PYME-cs-siteconfig\launchers\bin;%PATH%

call conda-activate-chosen-env.bat

pymeacquire -i %INITPATH%\generic\init_Zyla_n.py

call conda deactivate

cmd /k
