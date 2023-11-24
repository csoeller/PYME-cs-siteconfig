@echo off
setlocal

rem

set PATH=c:\ProgramData\Miniconda3\condabin;C:\python-support-files\PYME-cs-siteconfig\launchers\bin;%PATH%

call conda-activate-chosen-env.bat

PYMEVis %1

call conda deactivate
