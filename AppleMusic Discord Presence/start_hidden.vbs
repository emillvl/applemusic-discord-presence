' Launches the watcher with pythonw.exe (no console window) so it can
' sit in the Windows Startup folder and run invisibly in the background.
'
' SETUP: edit the two paths below to match where you put this folder,
' then copy and paste this .vbs file into your Windows Startup folder
' (press Win+R, type:  shell:startup  and press Enter, then drop the
' shortcut there).
 
Set objShell = CreateObject("WScript.Shell")
pythonwPath =  ' replace with your pythonw.exe path if different
scriptPath =  ' replace with the path to main.py
 
objShell.Run """" & pythonwPath & """ """ & scriptPath & """", 0, False