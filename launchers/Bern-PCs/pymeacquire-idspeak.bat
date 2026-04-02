@echo off
setlocal

set INITPATH=C:\python-support-files\PYME-cs-siteconfig\init_scripts

rem ONLY modify the path if needed
rem set PATH=c:\ProgramData\miniforge3\condabin;%PATH%
rem set PATH=c:\ProgramData\miniforge3\condabin;C:\Program Files\IDS\uEye\develop\bin;%PATH%

call conda.bat activate test-pyme-3.11-mamba_1

pymeacquire -i %INITPATH%\generic\ids-coolLED.py

call conda deactivate

cmd /k
