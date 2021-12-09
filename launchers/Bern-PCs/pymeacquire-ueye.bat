@echo off
setlocal

set INITPATH=C:\python-support-files\PYME-exeter-siteconfig\init_scripts

rem ONLY modify the path if needed
set PATH=c:\ProgramData\Miniconda3\condabin;C:\Program Files\IDS\uEye\develop\bin;%PATH%

call conda.bat activate pyme-shared

pymeacquire -i %INITPATH%\generic\init_ui306x_n.py

call conda deactivate

cmd /k
