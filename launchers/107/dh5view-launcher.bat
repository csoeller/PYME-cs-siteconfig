@echo off
setlocal
set PATH=c:\ProgramData\Miniconda2;c:\ProgramData\Miniconda2\Scripts;c:\ProgramData\Miniconda2\Library\bin;%PATH%

call conda.bat activate pyme-default-plain

dh5view %1

call conda deactivate
