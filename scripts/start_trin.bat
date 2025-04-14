@echo off
taskkill /F /IM pythonw.exe /FI "WINDOWTITLE eq Trin Assistant" 2>nul
timeout /t 1
start "" pythonw trin_gui.py
timeout /t 5
pause 