# Project Structure Guide

## New File Organization

```
movie_review/
├── main.py                    # Entry point - run from root directory
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
│
├── src/                       # Source code package
│   ├── __init__.py
│   ├── data_loader.py         # Database connection & data loading
│   ├── eda.py                 # Exploratory Data Analysis
│   │
│   └── recommenders/          # Recommendation engines
│       ├── __init__.py
│       ├── collab_recommender.py      # Collaborative filtering (SVD)
│       ├── content_recommender.py     # Content-based (genre + tags)
│       ├── hidden_gems.py             # Hidden gems discovery
│       └── hybrid_recommender.py      # Hybrid system & CLI
│
├── data/                      # Data directory (for Kaggle upload)
│   └── movie_review.db        # SQLite database - MOVE HERE
│
└── outputs/                   # Analysis outputs
    ├── popularity_distribution.png
    ├── rating_distribution.png
    └── user_activity_distribution.png
```

## Key Changes

### ✅ What You Can Upload to Kaggle
- **Database: `data/movie_review.db`** ← Upload this separately as your dataset
- The database file is now isolated in the `data/` directory for easy Kaggle upload
- Kaggle users can download just the database once you publish it

### ✅ Source Code Organization
- **`src/`**: Contains all Python modules organized logically
- **`src/recommenders/`**: Separate subpackage for all recommendation engines
- **`src/data_loader.py`**: Updated to automatically look for the database in `data/`
- Cleaner imports using the package structure

### ✅ Output Organization
- **`outputs/`**: All visualization outputs are saved here (created automatically)
- Keeps the root directory clean and organized

## How to Use

### Running from the root directory:
```bash
# Install dependencies
pip install -r requirements.txt

# Run EDA
python main.py eda

# Launch interactive recommender
python main.py recommend

# Show hidden gems
python main.py hidden-gems
python main.py hidden-gems "Sci-Fi"
```

### Database Location
The `data_loader.py` automatically looks for `movie_review.db` in:
1. `data/movie_review.db` (new location - recommended)
2. Falls back to root directory for backward compatibility

## To Complete Setup

### 1. **Move the database file:**
   - Move `movie_review.db` from root to `data/` folder
   - Or simply copy it there - the loader will use the new location

### 2. **Create .gitignore** (optional but recommended):
   ```
   __pycache__/
   *.pyc
   *.db
   outputs/
   .DS_Store
   ```

### 3. **Update Git (if using version control):**
   ```bash
   git add .
   git commit -m "Reorganize project structure for Kaggle"
   ```

## For Kaggle Upload

### Option A: Upload Just the Database
1. Create a Kaggle dataset with just `data/movie_review.db`
2. Users can train their own recommender systems

### Option B: Upload Complete Code + Data
1. Create a Kaggle dataset with:
   - `data/movie_review.db`
   - `src/` folder (all Python modules)
   - `main.py`
   - `requirements.txt`
2. Users can run the full system immediately

### Option C: Kaggle Notebook + Your Database
1. Upload your database as a dataset
2. Create Kaggle notebooks that import and use your code
3. Link to your uploaded database

## Benefits of This Structure

✅ **Scalable**: Easy to add new recommenders to `src/recommenders/`
✅ **Clean**: Separation of code, data, and outputs
✅ **Professional**: Follows Python packaging conventions
✅ **Kaggle-Ready**: Database easily separable for upload
✅ **Maintainable**: Clear organization makes collaboration easier
✅ **Backward Compatible**: Old database location still works
