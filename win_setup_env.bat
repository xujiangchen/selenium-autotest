@echo off
setlocal enabledelayedexpansion

set JOB_NAME=%1

if "%JOB_NAME%" == ""(
    echo [ERROR] JOB_NAME is not provided. Please pass it as the first argument.
    exit /b 1
)

set VENV_DIR=.venv_%JOB_NAME%
set VENV_PY=%VENV_DIR%\Scripts\python
set VENV_PIP=%VENV_DIR%\Scripts\pip

echo [INFO] Using virtual environment: %VENV_DIR%

if not exit %VENV_DIR%(
    echo [INFO] virtual environment not found. Creating....
    python -m venv %VENV_DIR%
    if errorlevel 1(
        echo [ERROR] Failed to create virtual environment.
        exit /b 1
    )
)

call %VENV_PY% -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install requirements.txt.
    exit /b 1
)

for /R %%F in (*.pyc) do (
    echo %%F | findstr /I /C:%VENV_DIR% >nul
    if errorlevel 1 (
        del "%%F"
    )
)

echo [SUCCESS] virtual environment is ready: %VENV_DIR%
endlocal