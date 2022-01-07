@echo off
setlocal

set INITPATH=C:\python-support-files\PYME-cs-siteconfig\init_scripts

rem ONLY modify the path if needed
set PATH=c:\ProgramData\Miniconda3\condabin;C:\Program Files\Andor SDK3;%PATH%

call conda.bat activate pyme-shared

pymeacquire -i %INITPATH%\B1\init_B1_main_n.py

call conda deactivate

cmd /k
