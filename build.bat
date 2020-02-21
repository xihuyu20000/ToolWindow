@echo off
@rem C:\Users\Administrator\.virtualenvs\ToolWindow\Scripts\python.exe  cx_setup.py build
C:/Users/Administrator/.virtualenvs/ToolWindow/Scripts/pyinstaller.exe  -i icon.ico -D -w SpiderTool_win10_64.py  --hidden-import PyQt5.QtWebKit