@echo off
setlocal

rem
set PATH=c:\ProgramData\Miniconda3\condabin;%PATH%

call conda.bat activate pyme-shared

dh5view %1

call conda deactivate
