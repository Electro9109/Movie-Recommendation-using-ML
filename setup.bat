@echo off
REM Movie Recommendation System - Windows Setup Script
REM This script sets up the environment and downloads the dataset

echo ============================================================
echo MOVIE RECOMMENDATION SYSTEM - WINDOWS SETUP
echo ============================================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python first.
    pause
    exit /b 1
)
echo OK - Python found
echo.

REM Check pip
echo Checking pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip not found
    pause
    exit /b 1
)
echo OK - pip found
echo.

REM Install/upgrade kaggle
echo Installing Kaggle API...
pip install --upgrade kaggle
if errorlevel 1 (
    echo ERROR: Failed to install kaggle
    pause
    exit /b 1
)
echo OK - Kaggle API installed
echo.

REM Check Kaggle credentials
echo Checking Kaggle credentials...
if not exist "%USERPROFILE%\.kaggle\kaggle.json" (
    echo WARNING: kaggle.json not found
    echo.
    echo To set up Kaggle API:
    echo   1. Go to https://www.kaggle.com/settings/account
    echo   2. Click "Create New API Token"
    echo   3. Move the downloaded kaggle.json to: %USERPROFILE%\.kaggle\
    echo.
    echo After setting up credentials, run this script again.
    pause
    exit /b 1
)
echo OK - Kaggle credentials found
echo.

REM Download data
echo Downloading dataset...
python download_data.py
if errorlevel 1 (
    echo ERROR: Download failed
    pause
    exit /b 1
)
echo.

echo ============================================================
echo SETUP COMPLETE!
echo ============================================================
echo.
echo To test the installation, run:
echo   python main.py eda
echo   python main.py recommend
echo.
pause
