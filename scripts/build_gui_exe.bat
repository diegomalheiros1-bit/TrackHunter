@echo off
setlocal
cd /d "%~dp0\.."

python -m pip install -r requirements.txt
python -m pip install pyinstaller
set PLAYWRIGHT_BROWSERS_PATH=0
python -m playwright install chromium

pyinstaller --noconfirm --clean TrackHunterApp.spec

echo.
echo Build concluido em: dist\TrackHunterApp
pause
