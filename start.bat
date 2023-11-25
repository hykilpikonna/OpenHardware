%1 mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/c %~s0 ::","","runas",1)(window.close)&&exit
cd /d "%~dp0"
cd Code\CardReader
:Start
python receiver.py
echo Press Ctrl-C if you don't want to restart automatically
ping -n 1 localhost

goto Start