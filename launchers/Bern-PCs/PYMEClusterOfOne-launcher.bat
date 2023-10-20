@echo off
setlocal

rem
set PATH=c:\ProgramData\Miniconda3\condabin;%PATH%

if not defined PYMEENV ( set PYMEENV="pyme-shared" )

echo *****************************************
echo starting in conda environment %PYMEENV%
echo *****************************************

call conda.bat activate %PYMEENV%

PYMEClusterofone

call conda deactivate

cmd /k
