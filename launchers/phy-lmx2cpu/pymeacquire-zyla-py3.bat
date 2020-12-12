@echo off
setlocal

set INITPATH=C:\python-support\PYME-exeter-siteconfig\init_scripts

rem ONLY modify the path if needed
rem set PATH=c:\ProgramData\Miniconda2;c:\ProgramData\Miniconda2\Scripts;c:\ProgramData\Miniconda2\Library\bin;%PATH%

call conda.bat activate pyme-py3

pymeacquire -i %INITPATH%\generic\init_Zyla_n.py

call conda deactivate

cmd /k
