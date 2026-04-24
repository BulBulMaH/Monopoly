@echo off
setlocal EnableExtensions EnableDelayedExpansion

:: Check if python is available in PATH
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found in system PATH.
    set /p python_path="Enter full path to python.exe (e.g., C:\Python312\python.exe): "

    :: Remove surrounding quotes if the user typed them
    set python_path=!python_path:"=!

    :: Check that the file exists
    if not exist "!python_path!" (
        echo ERROR: File "!python_path!" not found.
        pause
        exit /b 1
    )

    :: Verify that the provided path actually is a working Python interpreter
    "!python_path!" --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: "!python_path!" is not a valid Python interpreter.
        pause
        exit /b 1
    )

    set "PYTHON_EXE=!python_path!"
) else (
    set "PYTHON_EXE=python"
)

echo Using Python: %PYTHON_EXE%

:: Create virtual environment
"%PYTHON_EXE%" -m venv .venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment ".venv".
    pause
    exit /b 1
)

:: Activate the environment and upgrade pip
call .venv\Scripts\activate.bat
"%PYTHON_EXE%" -m pip install --upgrade pip

:: Install dependencies if requirements.txt exists
if exist requirements.txt (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies from requirements.txt.
        pause
        exit /b 1
    )
) else (
    echo requirements.txt not found, skipping dependency installation.
)

echo Setup completed successfully.
pause
endlocal