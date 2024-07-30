@echo off
echo Installing Python packages...
pip install -r req.txt

echo Starting MultiRoblox.exe minimized...
start "" /min "MultiRoblox.exe"

echo Running main.py...
python main.py

pause
