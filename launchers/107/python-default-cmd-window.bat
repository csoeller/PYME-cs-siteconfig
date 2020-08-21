@echo off
setlocal
set PATH=c:\ProgramData\Miniconda2;c:\ProgramData\Miniconda2\Scripts;c:\ProgramData\Miniconda2\Library\bin;%PATH%

call conda.bat activate pyme-default-plain

D:

cd D:\data

cmd /k
