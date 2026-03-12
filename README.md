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

## Installation & Setup

### 1. Clone and Install Dependencies

```bash
git clone <your-repo-url>
cd movie_review
pip install -r requirements.txt
```

### 2. Download Dataset from Kaggle

The dataset is hosted at: **https://www.kaggle.com/datasets/aravind100k/20m-combined-db**

#### Option A: Automated Setup (Recommended)

**Windows (PowerShell):**
```powershell
.\setup.ps1
```

**Windows (Command Prompt):**
```cmd
setup.bat
```

**Mac/Linux:**
```bash
python download_data.py
```

#### Option B: Manual Download Script

```bash
# Install Kaggle API first
pip install kaggle

# Set up Kaggle credentials:
# 1. Go to https://www.kaggle.com/settings/account
# 2. Click "Create New API Token"
# 3. Move kaggle.json to ~/.kaggle/kaggle.json
# 4. On Mac/Linux: chmod 600 ~/.kaggle/kaggle.json

# Download the dataset
python download_data.py
```

#### Option C: Manual Download from Website

1. Visit: https://www.kaggle.com/datasets/aravind100k/20m-combined-db
2. Click **Download** button
3. Extract the zip file
4. Place the `.db` file in the `data/` folder

For detailed setup instructions, see [DOWNLOAD.md](DOWNLOAD.md)

---

## Usage

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

---

## Project Structure

```
movie_review/
├── main.py                      # CLI entry point
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── STRUCTURE.md                 # Detailed project structure guide
├── SETUP.md                     # Setup and next steps
├── DOWNLOAD.md                  # Data download guide
│
├── download_data.py             # Download dataset from Kaggle
├── setup.ps1                    # Windows PowerShell setup script
├── setup.bat                    # Windows batch setup script
│
├── src/                         # Source code package
│   ├── __init__.py
│   ├── data_loader.py           # SQLite data loading & movie lookup
│   ├── eda.py                   # Exploratory data analysis with plots
│   │
│   └── recommenders/            # Recommendation engines subpackage
│       ├── __init__.py
│       ├── collab_recommender.py        # Truncated SVD collaborative filtering
│       ├── content_recommender.py       # Genre + tag TF-IDF cosine similarity
│       ├── hidden_gems.py               # Bayesian average + popularity penalty
│       └── hybrid_recommender.py        # Combined engine & interactive CLI
│
├── data/                        # Data directory
│   └── movie_review.db          # SQLite database (download via setup script)
│
└── outputs/                     # Analysis outputs
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

| Table | Rows | Columns |
|---|---|---|
| `movies` | 27,278 | `movieId`, `title`, `genres` |
| `ratings` | 20,000,263 | `userId`, `movieId`, `rating`, `timestamp` |
| `tags` | 465,548 | `userId`, `movieId`, `tag`, `timestamp` |

---

## Performance Notes

| Operation | Time | RAM |
|---|---|---|
| Data loading (all 20M ratings) | ~4 min | ~2 GB |
| Content feature building | ~6 sec | ~200 MB |
| Collaborative model training (7M sample) | ~3 min | ~3-4 GB peak |
| Hidden gems scoring | ~1 sec | minimal |
| Individual query (after models loaded) | instant | — |

---

## Tech Stack

- **pandas** — data manipulation
- **scikit-learn** — TF-IDF, SVD, cosine similarity
- **scipy** — sparse matrices
- **numpy** — numerical operations
- **matplotlib** — EDA visualizations
- **sqlite3** — database access

---

## License

This project uses the [MovieLens 20M dataset](https://grouplens.org/datasets/movielens/20m/) by GroupLens Research, distributed under their [terms of use](https://files.grouplens.org/datasets/movielens/ml-20m-README.html).

---

## Troubleshooting

### "Kaggle credits not found" error

**Solution:**
1. Install Kaggle API: `pip install kaggle`
2. Go to https://www.kaggle.com/settings/account
3. Create a new API token (downloads `kaggle.json`)
4. Move to: `~/.kaggle/kaggle.json`
5. On Mac/Linux: `chmod 600 ~/.kaggle/kaggle.json`

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
