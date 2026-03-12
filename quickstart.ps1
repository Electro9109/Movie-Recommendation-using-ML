#!/usr/bin/env powershell
# Quick start guide for Movie Recommendation System (Windows)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "MOVIE RECOMMENDATION SYSTEM - QUICK START" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Install dependencies
Write-Host "[1/3] Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install requirements" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Step 2: Download dataset
Write-Host "[2/3] Setting up dataset..." -ForegroundColor Yellow
Write-Host ""
Write-Host "To download the dataset from Kaggle, run:" -ForegroundColor Cyan
Write-Host "  .\setup.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Or manually:" -ForegroundColor Cyan
Write-Host "  python download_data.py" -ForegroundColor White
Write-Host ""
Write-Host "See DOWNLOAD.md for detailed instructions." -ForegroundColor Yellow
Write-Host ""

# Step 3: Test installation
Write-Host "[3/3] Testing installation..." -ForegroundColor Yellow
Write-Host ""
python -c "from src.data_loader import load_all_dataframes; print('✓ Code structure verified')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Could not verify code (database may not be downloaded yet)" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "✓ SETUP COMPLETE!" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Green
Write-Host "  1. Download dataset: .\setup.ps1"
Write-Host "  2. Run EDA: python main.py eda"
Write-Host "  3. Try recommender: python main.py recommend"
Write-Host ""
Write-Host "For help, see:" -ForegroundColor Cyan
Write-Host "  - README.md      (Project overview)"
Write-Host "  - DOWNLOAD.md    (Dataset download guide)"
Write-Host "  - STRUCTURE.md   (Project organization)"
Write-Host "  - SETUP.md       (Initial setup guide)"
Write-Host ""
