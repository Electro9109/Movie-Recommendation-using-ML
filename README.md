# 🎬 Movie Recommendation System

A movie recommendation engine built on the [MovieLens 20M dataset](https://www.kaggle.com/datasets/grouplens/movielens-20m-dataset) that combines **content-based filtering**, **collaborative filtering (SVD)**, and a **hidden gems discovery engine** to suggest movies based on user preferences — including under-appreciated films most people haven't seen.

---

## Features

| Strategy | Description |
|---|---|
| **Content-Based** | Finds similar movies using genre encoding + user-tag TF-IDF with cosine similarity |
| **Collaborative Filtering** | Predicts ratings via Truncated SVD on a sparse user-item matrix (7M sampled ratings) |
| **Hidden Gems** | Surfaces high-quality, low-popularity movies using Bayesian average + log popularity penalty |
| **Hybrid** | Blends content and collaborative scores for best-of-both-worlds recommendations |
| **Personalized Gems** | Hidden gems tailored to a specific user's predicted taste |

---

## Quick Start

### Prerequisites

- Python 3.10+
- ~8 GB RAM (collaborative filtering is memory-optimized with sampling + sparse matrices)
- Database: `data/movie_review.db` (2.9 GB, **already initialized**)

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Database is Ready!

The SQLite database (`data/movie_review.db`) is **already initialized** with 41.8 million clean records:
- 62,423 movies
- 25 million user ratings
- 1.1 million user tags
- 15.5 million genome scores (tag relevance)
- IMDB/TMDB links

**No download needed!** The data is cleaned, deduplicated, and validated.

---

## Usage

### Data Access (Programmatic)

```python
from src.data_loader import create_connection, get_top_rated_movies, search_movies

conn = create_connection()

# Get top rated movies
top_movies = get_top_rated_movies(conn, limit=10)

# Search for movies
results = search_movies(conn, "inception")

# Get user ratings
from src.data_loader import get_user_rated_movies
user_movies = get_user_rated_movies(conn, user_id=1, limit=20)

# Get similar movies
from src.data_loader import get_similar_movies_by_tags
similar = get_similar_movies_by_tags(conn, movie_id=603, limit=10)
```

See [DATABASE_QUICKSTART.md](DATABASE_QUICKSTART.md) for more examples.

### Interactive Recommendation CLI

```bash
python main.py recommend
```

This launches a menu-driven interface with 7 options:

```
1. Find similar movies        (content-based)
2. Recommendations for user   (collaborative)
3. Hybrid recommendations     (content + collab)
4. Hidden gems                (all genres)
5. Hidden gems by genre
6. Personalized hidden gems   (for a user)
7. Search for a movie
0. Exit
```

### Exploratory Data Analysis

```bash
python main.py eda
```

Generates dataset summaries, genre statistics, and distribution plots (saved as PNGs):
- `popularity_distribution.png`
- `rating_distribution.png`
- `user_activity_distribution.png`

### Hidden Gems (Quick Access)

```bash
python main.py hidden-gems            # Top 20 across all genres
python main.py hidden-gems Sci-Fi     # Filtered by genre
python main.py hidden-gems Comedy     # Any genre works
```

### Verify Database

```bash
python verify_database.py   # Check data integrity & statistics
python test_database.py     # Test all query functions
```

---

## Project Structure

```
movie_review/
├── main.py                           # CLI entry point
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
├── SETUP_COMPLETE.md                 # Database initialization summary
├── DATABASE_REPORT.md                # Detailed data report
├── DATABASE_QUICKSTART.md            # Query examples & patterns
│
├── load_data.py                      # Reload database from CSVs (if needed)
├── verify_database.py                # Check database integrity
├── test_database.py                  # Test query functions
│
├── src/                              # Source code package
│   ├── __init__.py
│   ├── data_loader.py                # SQLite queries & 10+ helper functions
│   ├── eda.py                        # Exploratory data analysis with plots
│   │
│   └── recommenders/                 # Recommendation engines subpackage
│       ├── __init__.py
│       ├── collab_recommender.py     # Truncated SVD collaborative filtering
│       ├── content_recommender.py    # Genre + tag TF-IDF cosine similarity
│       ├── hidden_gems.py            # Bayesian average + popularity penalty
│       └── hybrid_recommender.py     # Combined engine & interactive CLI
│
├── data/                             # Data directory
│   ├── movie_review.db               # SQLite database (2.9 GB, ready to use)
│   └── *.csv                         # Source CSVs (for reference/reload only)
│
└── outputs/                          # Analysis outputs
    ├── popularity_distribution.png
    ├── rating_distribution.png
    └── user_activity_distribution.png
```

---

## How It Works

### Content-Based Filtering

Each movie is represented as a feature vector combining:
- **One-hot encoded genres** (20 genres)
- **TF-IDF of user tags** (top 500 terms)

Similarity between movies is measured using **cosine similarity** on these vectors.

### Collaborative Filtering

1. **Sample** 7M ratings (stratified by user) from the full 20M to stay within RAM limits
2. Build a **sparse user-item matrix** (scipy CSR)
3. Apply **Truncated SVD** (50 latent factors) for dimensionality reduction
4. Predict ratings for unrated movies by reconstructing the matrix from latent factors

### Hidden Gems Engine

Movies are scored using:

```
gem_score = bayesian_avg_rating × (1 + normalized_log_penalty)
```

- **Bayesian average** smooths ratings toward the global mean (prior of 50 votes), preventing noisy scores from movies with very few ratings
- **Log popularity penalty** boosts lesser-known movies: `log(max_count / count)`
- Movies must have ≥ 50 ratings and ≤ 5,000 ratings to qualify as a "gem"

### Hybrid Recommender

Blends content-based and collaborative scores:

```
hybrid_score = α × content_score + (1 − α) × collab_score
```

Default α = 0.3 (favors collaborative since the dataset has 20M ratings).

---

## Dataset

| Table | Records | Status |
|---|---|---|
| `movies` | 62,423 | ✓ All unique, clean |
| `ratings` | 25,000,095 | ✓ Deduplicated by user+movie |
| `user_tags` | 1,093,344 | ✓ Nulls removed |
| `links` | 62,423 | ✓ IMDB/TMDB IDs |
| `genome_tags` | 1,128 | ✓ Reference tags |
| `genome_scores` | 15,584,448 | ✓ Tag relevance scores |
| **TOTAL** | **41.8M** | ✓ Clean & validated |

**Database**: `data/movie_review.db` (2.9 GB, SQLite)  
**Status**: Ready to use — no further setup needed

---

## Performance Notes

| Operation | Time | Notes |
|---|---|---|
| Data loading | instant | Already in SQLite database |
| Query indexed columns | <100ms | Fast with indexes on userId, movieId |
| Query genome_scores (full) | 5-30s | 15.5M record full scans are expected |
| Content feature building | ~6 sec | One-time, on-demand |
| Collaborative model training | ~3 min | First run, cached afterward |
| Hidden gems scoring | ~1 sec | Real-time queries |
| Individual recommendation | instant | After models are cached |

---

## Tech Stack

- **pandas** — data manipulation
- **scikit-learn** — TF-IDF, SVD, cosine similarity
- **scipy** — sparse matrices
- **numpy** — numerical operations
- **matplotlib** — EDA visualizations
- **sqlite3** — database access (built-in)

---

## Database Status

✅ **Fully Initialized & Validated**

- All CSV data loaded and deduplicated
- Foreign key constraints verified
- 0 orphaned records
- Performance indexes created
- See [SETUP_COMPLETE.md](SETUP_COMPLETE.md) for details

---

## License

This project uses the [MovieLens 20M dataset](https://grouplens.org/datasets/movielens/20m/) by GroupLens Research, distributed under their [terms of use](https://files.grouplens.org/datasets/movielens/ml-20m-README.html).

---

## Troubleshooting

### "No module named 'src'" error

**Solution**: Run from the project root directory:
```bash
cd path/to/movie_review
python main.py recommend
```

### "Database file not found"

**Solution**: The database file should be at `data/movie_review.db`. If missing, reload it:
```bash
python load_data.py  # Requires CSV files in data/ folder
```

### Import errors for pandas, numpy, etc.

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

See [DOWNLOAD.md](DOWNLOAD.md) for detailed troubleshooting.

### Memory issues during training

If you run out of RAM:
- Reduce `sample_size` in `hybrid_recommender.py` (default: 7M)
- Reduce `svd_components` in `hybrid_recommender.py` (default: 50)
- Close other applications

### Database file not found

Ensure the database is in `data/movie_review.db`:
```bash
# From project root
python -c "from src.data_loader import load_all_dataframes; load_all_dataframes()"
```

---

## Documentation

- **[STRUCTURE.md](STRUCTURE.md)** — Detailed project organization
- **[SETUP.md](SETUP.md)** — Initial setup and next steps
- **[DOWNLOAD.md](DOWNLOAD.md)** — Data download with troubleshooting

---

## References

**Papers & Articles:**
- _Factorization Machines_ (Rendle, 2010) - basis for collaborative filtering
- _A Bayesian approach to relevance in e-commerce search_ (Browne et al., 2013)
- _Item-based Collaborative Filtering Recommendation Algorithms_ (Sarwar et al., 2001)

**Datasets:**
- GroupLens MovieLens 20M: https://grouplens.org/datasets/movielens/20m/
- Aravind's 20M Combined DB: https://www.kaggle.com/datasets/aravind100k/20m-combined-db

---

## Author Notes

Built as a demonstration of combining multiple recommendation approaches:
- ✨ **Content-based**: Understands movie features
- 🤝 **Collaborative**: Learns from user behavior patterns
- 💎 **Hidden Gems**: Discovers underrated movies
- 🔀 **Hybrid**: Best of all worlds

Perfect for learning recommendation systems or as a standalone movie discovery tool!
