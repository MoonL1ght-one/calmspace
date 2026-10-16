@echo off
rem =====================================================
rem  CalmSpace launcher  (double-click this file)
rem  Opens a borderless fullscreen calm space.
rem  To leave the space, type the leave word in the box.
rem =====================================================
setlocal enabledelayedexpansion
cd /d "%~dp0"

if not exist "index.html" (
  echo.
  echo   index.html not found in this folder.
  echo.
  pause
  exit /b 1
)

set "PYCMD="
set "PYARGS="

rem 1) Python launcher, windowed
where pyw.exe >nul 2>nul
if !errorlevel!==0 (
  set "PYCMD=pyw.exe"
  set "PYARGS=-3"
)

rem 2) Python launcher, console
if not defined PYCMD (
  where py.exe >nul 2>nul
  if !errorlevel!==0 (
    set "PYCMD=py.exe"
    set "PYARGS=-3"
  )
)

rem 3) common per-user installs
if not defined PYCMD (
  for %%V in (313 312 311 310) do (
    if not defined PYCMD if exist "%LOCALAPPDATA%\Programs\Python\Python%%V\pythonw.exe" set "PYCMD=%LOCALAPPDATA%\Programs\Python\Python%%V\pythonw.exe"
  )
)

rem 4) common machine-wide installs
if not defined PYCMD (
  for %%V in (313 312 311 310) do (
    if not defined PYCMD if exist "%ProgramFiles%\Python%%V\pythonw.exe" set "PYCMD=%ProgramFiles%\Python%%V\pythonw.exe"
  )
)

rem 5) PATH fallback (skips the Microsoft Store stub)
if not defined PYCMD (
  for %%C in (pythonw.exe python.exe) do (
    if not defined PYCMD (
      for /f "delims=" %%W in ('where %%C 2^>nul') do (
        if not defined PYCMD (
          echo %%W | find /i "WindowsApps" >nul
          if !errorlevel! neq 0 set "PYCMD=%%W"
        )
      )
    )
  )
)

if not defined PYCMD (
  echo.
  echo   Python 3 was not found on this computer.
  echo   Install it from https://www.python.org/downloads/ and try again.
  echo.
  pause
  exit /b 1
)

start "" "%PYCMD%" %PYARGS% "launcher.py"
exit /b 0
