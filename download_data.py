#!/usr/bin/env python3
"""
Download the movie database from Kaggle.

Usage:
    python download_data.py

Prerequisites:
    1. Install Kaggle API: pip install kaggle
    2. Set up Kaggle credentials:
       - Go to https://www.kaggle.com/settings/account
       - Click "Create New API Token"
       - Place kaggle.json in ~/.kaggle/
       - On Linux/Mac: chmod 600 ~/.kaggle/kaggle.json

Dataset: https://www.kaggle.com/datasets/aravind100k/20m-combined-db
"""

import os
import sys
import zipfile
import shutil
from pathlib import Path


def check_kaggle_installed():
    """Check if kaggle package is installed."""
    try:
        import kaggle
        return True
    except ImportError:
        print("❌ Kaggle API not installed.")
        print("\nInstall it with:")
        print("  pip install kaggle")
        return False


def check_kaggle_credentials():
    """Check if Kaggle credentials are set up."""
    kaggle_dir = Path.home() / '.kaggle'
    credentials_file = kaggle_dir / 'kaggle.json'
    
    if not credentials_file.exists():
        print("❌ Kaggle credentials not found.")
        print("\nSet up credentials:")
        print("  1. Go to https://www.kaggle.com/settings/account")
        print("  2. Click 'Create New API Token'")
        print("  3. This downloads kaggle.json")
        print(f"  4. Move it to: {credentials_file}")
        print("\nOn Linux/Mac, also run:")
        print(f"  chmod 600 {credentials_file}")
        return False
    
    return True


def download_dataset(output_dir='data'):
    """Download the dataset from Kaggle."""
    import kaggle
    
    dataset_name = 'aravind100k/20m-combined-db'
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"📥 Downloading dataset: {dataset_name}")
    print(f"📂 Output directory: {output_path.absolute()}")
    print()
    
    try:
        # Download the dataset
        kaggle.api.dataset_download_files(
            dataset_name,
            path=str(output_path),
            unzip=True
        )
        print("✅ Download completed!")
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False


def verify_database(output_dir='data', db_filename='movie_review.db'):
    """Verify that the database file exists."""
    db_path = Path(output_dir) / db_filename
    
    if db_path.exists():
        size_mb = db_path.stat().st_size / (1024 * 1024)
        print(f"✅ Database verified: {db_path}")
        print(f"   Size: {size_mb:.2f} MB")
        return True
    else:
        # Check what files were downloaded
        output_path = Path(output_dir)
        files = list(output_path.glob('*'))
        
        if files:
            print(f"❌ Database file not found at {db_path}")
            print(f"\nFiles found in {output_dir}:")
            for f in files:
                if f.is_file():
                    size_mb = f.stat().st_size / (1024 * 1024)
                    print(f"  - {f.name} ({size_mb:.2f} MB)")
                else:
                    print(f"  - {f.name}/ (directory)")
            
            # Try to find .db files
            db_files = list(output_path.rglob('*.db'))
            if db_files:
                print(f"\n💡 Found .db file(s):")
                for db_file in db_files:
                    print(f"  - {db_file.relative_to(output_path)}")
                    print(f"\n💡 Rename it to '{db_filename}' or update data_loader.py")
        else:
            print(f"❌ No files found in {output_dir}")
        
        return False


def main():
    """Main download workflow."""
    print("=" * 60)
    print("MOVIE RECOMMENDATION SYSTEM - DATA DOWNLOAD")
    print("=" * 60)
    print()
    
    # Check prerequisites
    print("Checking prerequisites...")
    if not check_kaggle_installed():
        return False
    
    if not check_kaggle_credentials():
        return False
    
    print("✅ Kaggle API ready")
    print()
    
    # Download
    if not download_dataset():
        return False
    print()
    
    # Verify
    print("Verifying download...")
    if verify_database():
        print()
        print("=" * 60)
        print("✅ All done! You can now run:")
        print("   python main.py eda")
        print("   python main.py recommend")
        print("=" * 60)
        return True
    else:
        print()
        print("⚠️  Database file not found. Please check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
