@echo off

echo Creating venv ...
python -m venv .venv

REM 만약 파이썬이 설치되어있지 않다면
if not errorlevel 0 goto FAIL

copy automatic_exe.py .venv
copy interpreter.py .venv
copy logManager.py .venv
copy reportWriter.py .venv
copy run.py .venv
copy sshConnector.py .venv
cd .venv

REM venv 안에 모듈을 설치

echo Installing styleframe ...
Scripts\pip.exe install styleframe
if not errorlevel 0 goto FAIL

echo Installing paramiko ...
Scripts\pip.exe install paramiko
if not errorlevel 0 goto FAIL

echo Installing pyinstaller ...
Scripts\pip.exe install pyinstaller
if not errorlevel 0 goto FAIL

echo Installing pandas ...
Scripts\pip.exe install pandas
if not errorlevel 0 goto FAIL

REM EXE를 추출함
echo creating checker.exe ...
Scripts\pyinstaller.exe --onefile run.py -n checker.exe

REM 산출물 디렉토리 생성 및 산출물 이동
mkdir ..\output
move dist\checker.exe ..\output\checker.exe
cd ..
copy customInterpreter.py output
copy customReportWriter.py output
goto SUCCESS

REM 분기목록
:FAIL
echo Python is not installed on your computer. Please install Python.
goto QUIT

:SUCCESS

echo SUCCESS! Files have been created in the output folder.
goto QUIT

:QUIT
pause
exit