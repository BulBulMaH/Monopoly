@echo off
python --version >nul 2>&1
python -m venv .venv
if errorlevel 1 (
    echo venv creating error
    pause
    exit /b 1
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
if exist requirements.txt (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo requirements install error
        pause
        exit /b 1
    )
) else (
    echo requirements.txt not found
)
replace lib\init_for_magic\__init__.py .venv\Lib\site-packages\magic\
echo Setup is completed
pause