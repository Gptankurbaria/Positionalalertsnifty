@echo off
title StratEdge GitHub Updater
echo Preparing Institutional Update...
git add .
set /p msg="Enter Update Summary (default: 'Auto Update'): "
if "%msg%"=="" set msg=Dashboard Auto Update
git commit -m "%msg%"
echo Pushing Intelligence to GitHub Cloud...
git push origin main
echo.
echo Update Complete!
pause
