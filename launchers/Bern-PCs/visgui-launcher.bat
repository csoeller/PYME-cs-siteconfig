@echo off
setlocal

rem

set PATH=c:\ProgramData\Miniconda3\condabin;%PATH%
if not defined PYMEENV ( set PYMEENV="pyme-shared" )
call conda.bat activate %PYMEENV%

PYMEVis %1

call conda deactivate
