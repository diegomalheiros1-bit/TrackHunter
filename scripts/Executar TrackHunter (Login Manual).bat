@echo off
setlocal
cd /d "%~dp0\.."
python -m trackhunter.cli --tracklist ".\tracklist.txt" --downloads ".\downloads" --logs ".\logs" --history ".\state\track_history.json" --manual-login
set "EXIT_CODE=%ERRORLEVEL%"
echo.
echo Execucao finalizada com codigo %EXIT_CODE%.
pause
exit /b %EXIT_CODE%
