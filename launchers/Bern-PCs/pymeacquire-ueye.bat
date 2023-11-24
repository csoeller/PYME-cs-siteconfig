@echo off
setlocal

set INITPATH=C:\python-support-files\PYME-cs-siteconfig\init_scripts

rem ONLY modify the path if needed
set PATH=c:\ProgramData\Miniconda3\condabin;C:\Program Files\IDS\uEye\develop\bin;C:\python-support-files\PYME-cs-siteconfig\launchers\bin;%PATH%

call conda-activate-chosen-env.bat

cd \python-support-files\pymelogs\ueye
pymeacquire -i %INITPATH%\generic\init_ui306x_n.py

call conda deactivate

cmd /k
