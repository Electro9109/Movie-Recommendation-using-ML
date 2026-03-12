# Movie Recommendation System - PowerShell Setup Script
# Run from project root: .\setup.ps1

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "MOVIE RECOMMENDATION SYSTEM - WINDOWS SETUP (PowerShell)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "✗ ERROR: Python not found. Please install Python first." -ForegroundColor Red
    Write-Host "  Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Check pip
Write-Host "Checking pip..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✓ pip found: $pipVersion" -ForegroundColor Green
}
catch {
    Write-Host "✗ ERROR: pip not found" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Install kaggle
Write-Host "Installing Kaggle API..." -ForegroundColor Yellow
pip install --upgrade kaggle 2>&1 | ForEach-Object {
    if ($_ -like "*Successfully installed*" -or $_ -like "*Requirement already satisfied*") {
        Write-Host "✓ $_" -ForegroundColor Green
    }
}
Write-Host ""

# Check Kaggle credentials
Write-Host "Checking Kaggle credentials..." -ForegroundColor Yellow
$kaggleDir = "$($env:USERPROFILE)\.kaggle"
$credentialsFile = "$kaggleDir\kaggle.json"

if (Test-Path $credentialsFile) {
    Write-Host "✓ Kaggle credentials found" -ForegroundColor Green
}
else {
    Write-Host "✗ WARNING: kaggle.json not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "To set up Kaggle API:" -ForegroundColor Yellow
    Write-Host "  1. Go to https://www.kaggle.com/settings/account"
    Write-Host "  2. Click 'Create New API Token'"
    Write-Host "  3. This downloads kaggle.json"
    Write-Host "  4. Move it to: $credentialsFile"
    Write-Host ""
    Write-Host "After setting up credentials, run this script again." -ForegroundColor Cyan
    Read-Host "Press Enter to open Kaggle settings"
    Start-Process "https://www.kaggle.com/settings/account"
    exit 1
}
Write-Host ""

# Download data
Write-Host "Downloading dataset from Kaggle..." -ForegroundColor Yellow
python download_data.py
$downloadExitCode = $LASTEXITCODE

if ($downloadExitCode -ne 0) {
    Write-Host "✗ ERROR: Download failed" -ForegroundColor Red
    exit $downloadExitCode
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "✓ SETUP COMPLETE!" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To test the installation, run one of these commands:" -ForegroundColor Green
Write-Host "  python main.py eda"
Write-Host "  python main.py recommend"
Write-Host "  python main.py hidden-gems"
Write-Host ""
