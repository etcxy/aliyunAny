@echo off


%1 mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/c %~s0 ::","","runas",1)(window.close)&&exit
echo start

set CURRENT_PATH=/d %~dp0

cd %CURRENT_PATH%

python -B console.py

pause