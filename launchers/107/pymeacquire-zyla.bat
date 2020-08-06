@echo off
setlocal
set PATH=c:\ProgramData\Miniconda2;c:\ProgramData\Miniconda2\Scripts;c:\ProgramData\Miniconda2\Library\bin;%PATH%

call conda.bat activate pyme-default-plain

pymeacquire -i c:\python-default\pyme-exeter-siteconfig\init_scripts\generic\init_Zyla_n.py

call conda deactivate
