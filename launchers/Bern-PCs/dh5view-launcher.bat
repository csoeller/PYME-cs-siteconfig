@echo off
setlocal

rem
set PATH=c:\ProgramData\Miniconda3\condabin;C:\python-support-files\PYME-cs-siteconfig\launchers\bin;%PATH%

call conda-activate-chosen-env.bat

dh5view %1

call conda deactivate

cmd /k
