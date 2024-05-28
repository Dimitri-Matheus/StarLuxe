@echo off
    powershell -Command "Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted"
    powershell -Command "Start-Process -FilePath Injector.exe -ArgumentList 'StarRail.exe' -Verb RunAs"
    powershell -Command "Start-Process -FilePath 'C:\Games\Star Rail\Games\StarRail.exe' -Verb RunAs"
    powershell -Command "Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Restricted"
    exit
    