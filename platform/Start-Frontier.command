#!/bin/bash
# Double-click to open the Frontier app (Mac; also works on Linux with: bash Start-Frontier.command).
# First run: makes a private Python environment and installs the packages (needs internet, about 2 minutes).
# Later runs: opens the app straight away. Replay mode works with Wi-Fi off.
cd "$(dirname "$0")" || exit 1
VENV=".venv-app"
PY=$(command -v python3 || command -v python)
if [ -z "$PY" ]; then
  echo "Python 3 is not installed. Get it from https://www.python.org/downloads/ and try again."
  read -r -p "Press Enter to close." _; exit 1
fi
if [ ! -x "$VENV/bin/python" ] || [ requirements.txt -nt "$VENV/.installed" ]; then
  echo "First run: setting up (about 2 minutes)..."
  "$PY" -m venv "$VENV" || { read -r -p "Could not create the environment. Press Enter to close." _; exit 1; }
  "$VENV/bin/python" -m pip install --quiet --upgrade pip
  if ! "$VENV/bin/python" -m pip install --quiet -r requirements.txt; then
    read -r -p "Installing packages failed (is the internet on?). Press Enter to close." _; exit 1
  fi
  touch "$VENV/.installed"
fi
echo "Opening the Frontier app in your browser. Keep this window open; close it to stop the app."
URL="http://localhost:8501"
( sleep 4; if command -v open >/dev/null; then open "$URL"; elif command -v xdg-open >/dev/null; then xdg-open "$URL"; fi ) &
exec "$VENV/bin/python" -m streamlit run Frontier.py --server.headless true --server.port 8501
