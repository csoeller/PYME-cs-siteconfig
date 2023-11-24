if not defined PYMEENV ( set PYMEENV="pyme-shared" )

echo *****************************************
echo starting in conda environment %PYMEENV%
echo *****************************************

call conda.bat activate %PYMEENV%
