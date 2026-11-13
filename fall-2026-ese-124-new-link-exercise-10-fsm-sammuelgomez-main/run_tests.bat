@echo off
REM ESE 124 Exercise 10 - double-click me, or type:  run_tests.bat q2
cd /d "%~dp0"
where py >nul 2>nul && (py tests\run_all_tests.py %*) || (python tests\run_all_tests.py %*)
echo.
echo Full report: tests\last_report.txt
pause
