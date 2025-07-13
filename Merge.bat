@echo off
cd /d %~dp0
call "C:\Users\User\anaconda3\condabin\conda.bat" activate AccessibilityTool
REM Ensure the environment is activated
echo "Activated environment: %CONDA_DEFAULT_ENV%"
python main.py
pause