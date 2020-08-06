@echo off
setlocal
set PATH=c:\ProgramData\Miniconda2;c:\ProgramData\Miniconda2\Scripts;c:\ProgramData\Miniconda2\Library\bin;%PATH%

cd C:\python-default\log

CALL conda.bat activate pyme-default-plain
rem echo %path%
launchworkers
CALL conda.bat deactivate
