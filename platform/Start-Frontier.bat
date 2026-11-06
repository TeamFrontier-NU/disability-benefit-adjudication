@echo off
REM Double-click to open the Frontier app (Windows).
REM First run: makes a private Python environment and installs the packages (needs internet, about 2 minutes).
REM Later runs: opens the app straight away. Replay mode works with Wi-Fi off.
cd /d "%~dp0"
set VENV=.venv-app
if exist "%VENV%\Scripts\python.exe" if exist "%VENV%\.installed" goto run
echo First run: setting up (about 2 minutes)...
py -3 -m venv "%VENV%" 2>nul || python -m venv "%VENV%"
if not exist "%VENV%\Scripts\python.exe" (
  echo Python 3 is not installed. Get it from https://www.python.org/downloads/ and tick "Add python.exe to PATH".
  pause
  exit /b 1
)
"%VENV%\Scripts\python.exe" -m pip install --quiet --upgrade pip
"%VENV%\Scripts\python.exe" -m pip install --quiet -r requirements.txt
if errorlevel 1 (
  echo Installing packages failed. Is the internet on?
  pause
  exit /b 1
)
echo done> "%VENV%\.installed"
:run
echo Opening the Frontier app in your browser. Keep this window open; close it to stop the app.
start "" cmd /c "timeout /t 4 /nobreak >nul & start http://localhost:8501"
"%VENV%\Scripts\python.exe" -m streamlit run Frontier.py --server.headless true --server.port 8501
pause
