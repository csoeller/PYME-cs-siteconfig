@echo off
setlocal

rem
set PATH=c:\ProgramData\Miniconda3\condabin;%PATH%

call conda.bat activate pyme-shared

PYMEClusterofone

call conda deactivate

cmd /k
