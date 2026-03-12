# Data Download Setup Guide

This guide explains how to download the movie database from Kaggle.

## Overview

The dataset is hosted at: https://www.kaggle.com/datasets/aravind100k/20m-combined-db

Three download methods are provided:
1. **PowerShell script** (Windows) - Easiest ✅
2. **Batch script** (Windows) - Simple
3. **Python script** (Cross-platform) - Manual control

---

## ⚡ Quick Start (Recommended)

### On Windows (PowerShell):

```powershell
# From the project root directory
.\setup.ps1
```

### On Windows (Command Prompt):

```cmd
setup.bat
```

### On Mac/Linux:

```bash
python download_data.py
```

---

## Prerequisites

### 1. Install Kaggle API

```bash
pip install kaggle
```

### 2. Set Up Kaggle Credentials

This is **required** to download from Kaggle.

**Steps:**

1. Go to: https://www.kaggle.com/settings/account
2. Scroll down and click **"Create New API Token"**
3. This downloads a file called `kaggle.json`
4. Move it to the correct location:
   - **Windows**: `C:\Users\YOUR_USERNAME\.kaggle\kaggle.json`
   - **Mac**: `~/.kaggle/kaggle.json`
   - **Linux**: `~/.kaggle/kaggle.json`

**On Mac/Linux**, also run:
```bash
chmod 600 ~/.kaggle/kaggle.json
```

---

## Method 1: PowerShell Script (Windows - Recommended)

This is the easiest method for Windows users.

```powershell
# Open PowerShell in the project directory
# Right-click folder → Open PowerShell here

.\setup.ps1
```

The script will:
- ✓ Check Python installation
- ✓ Verify Kaggle credentials
- ✓ Install/upgrade Kaggle API
- ✓ Download the dataset
- ✓ Verify the download

**Features:**
- Colorized output for easy reading
- Opens Kaggle settings if credentials are missing
- Automatic error handling

---

## Method 2: Batch Script (Windows)

Simple batch file for Windows Command Prompt.

```cmd
# In Command Prompt, navigate to project folder
setup.bat
```

**Note:** This method won't open Kaggle settings automatically. Set up credentials first using Method 1 or the manual instructions above.

---

## Method 3: Python Script (All Platforms)

Manual control - works on Windows, Mac, and Linux.

```bash
python download_data.py
```

**Features:**
- Detailed error messages
- Verification of downloaded files
- Checks all prerequisites
- Cross-platform compatible

---

## Troubleshooting

### Error: "Kaggle credentials not found"

**Solution:**
1. Go to https://www.kaggle.com/settings/account
2. Create a new API token (downloads `kaggle.json`)
3. Move to `~/.kaggle/kaggle.json` (use `~` = home directory)
4. On Mac/Linux: `chmod 600 ~/.kaggle/kaggle.json`
5. Try again

### Error: "Dataset not found"

**Solution:**
- The dataset URL might have changed
- Try downloading manually from: https://www.kaggle.com/datasets/aravind100k/20m-combined-db
- Save to `data/` folder with filename `movie_review.db`

### Error: "Permission denied"

**Solution (Mac/Linux):**
```bash
chmod 600 ~/.kaggle/kaggle.json
```

**Solution (Windows):**
- Run PowerShell as Administrator
- Or manually set folder permissions on `C:\Users\YOUR_USERNAME\.kaggle\`

### Download is very slow

**Solution:**
- Kaggle datasets can be large
- Check your internet connection
- The database is ~900 MB - this may take several minutes
- Be patient!

---

## Manual Download (If Scripts Fail)

If the automated scripts don't work:

1. Go to: https://www.kaggle.com/datasets/aravind100k/20m-combined-db
2. Click **Download** button
3. Extract the zip file
4. Find the `.db` file (should be named something like `movie_review.db`)
5. Place it in the `data/` folder of this project

Then verify by running:
```bash
python main.py eda
```

---

## Verify Installation

After downloading, verify everything works:

```bash
# Run exploratory data analysis
python main.py eda

# Or launch the interactive recommender
python main.py recommend

# Or show hidden gems
python main.py hidden-gems
```

If these commands run without errors, you're all set! ✓

---

## File Locations

After successful download, you should have:

```
data/
└── movie_review.db    ← Downloaded here
```

The `data_loader.py` automatically looks for the database at:
- `data/movie_review.db` (preferred)
- Falls back to root `movie_review.db`

---

## Support

If you encounter issues:

1. **Check prerequisites:** `python --version`, `pip --version`
2. **Verify Kaggle setup:** Check that `~/.kaggle/kaggle.json` exists
3. **Try the Python script directly:** `python download_data.py`
4. **Check Kaggle website:** Make sure dataset still exists at https://www.kaggle.com/datasets/aravind100k/20m-combined-db
5. **Manual download:** Download dataset directly from Kaggle and place in `data/` folder

---

## Next Steps

After downloading:

1. ✓ Database is in `data/` folder
2. Test with: `python main.py eda`
3. Ready to use recommender system!
4. Ready to push to Kaggle or GitHub
