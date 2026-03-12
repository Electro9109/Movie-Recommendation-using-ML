"""
eda.py - Exploratory Data Analysis for the movie recommendation system.
Run directly: python -m src.eda
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from src.data_loader import load_all_dataframes


def plot_popularity_distribution(ratings_df, output_dir='outputs'):
    """Plot histogram of how many ratings each movie has."""
    movie_popularity = ratings_df.groupby('movieId')['rating'].count()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Raw distribution
    axes[0].hist(movie_popularity.values, bins=50, color='steelblue', edgecolor='black')
    axes[0].set_xlabel('Number of Ratings')
    axes[0].set_ylabel('Number of Movies')
    axes[0].set_title('Movie Popularity Distribution')

    # Log scale for better visibility
    axes[1].hist(movie_popularity.values, bins=50, color='coral', edgecolor='black', log=True)
    axes[1].set_xlabel('Number of Ratings')
    axes[1].set_ylabel('Number of Movies (log scale)')
    axes[1].set_title('Movie Popularity Distribution (Log Scale)')

    plt.tight_layout()
    output_path = os.path.join(output_dir, 'popularity_distribution.png')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.show()
    print(f"Saved: {output_path}")


def plot_rating_distribution(ratings_df, output_dir='outputs'):
    """Plot bar chart of rating values (0.5 to 5.0)."""
    rating_counts = ratings_df['rating'].value_counts().sort_index()

    plt.figure(figsize=(10, 5))
    bars = plt.bar(rating_counts.index.astype(str), rating_counts.values,
                   color='mediumpurple', edgecolor='black')
    plt.xlabel('Rating')
    plt.ylabel('Count')
    plt.title('Rating Value Distribution')

    # Add count labels on bars
    for bar, count in zip(bars, rating_counts.values):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                 f'{count:,}', ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    output_path = os.path.join(output_dir, 'rating_distribution.png')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.show()
    print(f"Saved: {output_path}")


def plot_user_activity(ratings_df, output_dir='outputs'):
    """Plot distribution of ratings per user."""
    user_activity = ratings_df.groupby('userId')['rating'].count()

    print("\n--- User Activity Statistics ---")
    print(user_activity.describe())

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].hist(user_activity.values, bins=50, color='seagreen', edgecolor='black')
    axes[0].set_xlabel('Number of Ratings per User')
    axes[0].set_ylabel('Number of Users')
    axes[0].set_title('User Activity Distribution')

    # Log scale
    axes[1].hist(user_activity.values, bins=50, color='tomato', edgecolor='black', log=True)
    axes[1].set_xlabel('Number of Ratings per User')
    axes[1].set_ylabel('Number of Users (log scale)')
    axes[1].set_title('User Activity Distribution (Log Scale)')

    plt.tight_layout()
    output_path = os.path.join(output_dir, 'user_activity_distribution.png')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.show()
    print(f"Saved: {output_path}")


def print_dataset_summary(movies_df, ratings_df, tags_df):
    """Print basic dataset info: shapes, dtypes, missing values."""
    print("=" * 60)
    print("DATASET SUMMARY")
    print("=" * 60)

    for name, df in [("Movies", movies_df), ("Ratings", ratings_df), ("Tags", tags_df)]:
        print(f"\n--- {name} ---")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Dtypes:\n{df.dtypes.to_string()}")
        missing = df.isnull().sum()
        if missing.any():
            print(f"  Missing values:\n{missing[missing > 0].to_string()}")
        else:
            print("  Missing values: None")
        print()


def print_genre_stats(movies_df):
    """Print genre frequency and co-occurrence info."""
    # Split genres and count
    all_genres = movies_df['genres'].str.split('|').explode()
    genre_counts = all_genres.value_counts()

    print("\n--- Genre Statistics ---")
    print(f"Total unique genres: {genre_counts.shape[0]}")
    print(f"\nGenre frequency:")
    for genre, count in genre_counts.items():
        pct = count / len(movies_df) * 100
        print(f"  {genre:<25} {count:>6} ({pct:.1f}%)")

    # Average genres per movie
    genres_per_movie = movies_df['genres'].str.split('|').apply(len)
    print(f"\nGenres per movie: mean={genres_per_movie.mean():.1f}, "
          f"median={genres_per_movie.median():.0f}, "
          f"max={genres_per_movie.max()}")


def print_hidden_gems_preview(movies_df, ratings_df):
    """Quick preview of potential hidden gems."""
    movie_stats = ratings_df.groupby('movieId').agg(
        rating_count=('rating', 'count'),
        avg_rating=('rating', 'mean')
    ).reset_index()

    hidden_gems = movie_stats[
        (movie_stats['rating_count'] < 1000) &
        (movie_stats['avg_rating'] >= 4.0)
    ]

    print(f"\n--- Hidden Gems Preview ---")
    print(f"Total movies: {len(movie_stats)}")
    print(f"Hidden gems (< 1000 ratings, avg >= 4.0): "
          f"{len(hidden_gems)} ({len(hidden_gems)/len(movie_stats)*100:.1f}%)")

    # Show top 10 hidden gems
    top_gems = hidden_gems.nlargest(10, 'avg_rating')
    top_gems = top_gems.merge(movies_df[['movieId', 'title']], on='movieId')
    print(f"\nTop 10 Hidden Gems:")
    for _, row in top_gems.iterrows():
        print(f"  {row['title']:<50} avg={row['avg_rating']:.2f}  "
              f"count={row['rating_count']}")


def run_eda(output_dir='outputs'):
    """Run the full EDA pipeline."""
    print("Loading data...")
    movies_df, ratings_df, tags_df = load_all_dataframes()

    print_dataset_summary(movies_df, ratings_df, tags_df)
    print_genre_stats(movies_df)
    print_hidden_gems_preview(movies_df, ratings_df)

    print("\nGenerating plots...")
    plot_popularity_distribution(ratings_df, output_dir=output_dir)
    plot_rating_distribution(ratings_df, output_dir=output_dir)
    plot_user_activity(ratings_df, output_dir=output_dir)

    print("\n✓ EDA complete!")


if __name__ == "__main__":
    run_eda()
