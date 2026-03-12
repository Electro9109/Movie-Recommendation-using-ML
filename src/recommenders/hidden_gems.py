"""
hidden_gems.py - Hidden Gems Movie Discovery Engine.
Finds high-quality movies that are under-appreciated / under-watched.
Uses Bayesian average + popularity penalty to score movies.
"""
import numpy as np
import pandas as pd


def compute_bayesian_average(ratings_df, min_votes=50):
    """Compute Bayesian (shrinkage) average rating for each movie.

    This smooths out movies with very few ratings by pulling them
    toward the global mean, preventing noise from dominating.

    Formula: bayesian_avg = (count * avg + min_votes * global_mean) / (count + min_votes)

    Args:
        ratings_df: ratings DataFrame
        min_votes: minimum number of votes for the prior (shrinkage strength)

    Returns:
        DataFrame with movieId, rating_count, raw_avg_rating, bayesian_avg_rating
    """
    global_mean = ratings_df['rating'].mean()

    movie_stats = ratings_df.groupby('movieId').agg(
        rating_count=('rating', 'count'),
        raw_avg_rating=('rating', 'mean')
    ).reset_index()

    movie_stats['bayesian_avg_rating'] = (
        (movie_stats['rating_count'] * movie_stats['raw_avg_rating'] +
         min_votes * global_mean) /
        (movie_stats['rating_count'] + min_votes)
    )

    return movie_stats


def compute_gem_scores(movie_stats_df):
    """Score movies to identify hidden gems.

    Formula: gem_score = bayesian_avg * log_penalty(max_count / count)

    Higher scores = better hidden gems (high quality + low popularity).

    Args:
        movie_stats_df: DataFrame from compute_bayesian_average

    Returns:
        DataFrame with added gem_score column
    """
    df = movie_stats_df.copy()

    max_count = df['rating_count'].max()

    # Log penalty: boosts lesser-known movies
    # log(max_count / count) is large for unpopular movies, small for popular ones
    df['popularity_penalty'] = np.log1p(max_count / (df['rating_count'] + 1))

    # Normalize penalty to 0-1 range
    max_penalty = df['popularity_penalty'].max()
    df['popularity_penalty_norm'] = df['popularity_penalty'] / max_penalty

    # Gem score: quality * obscurity
    df['gem_score'] = df['bayesian_avg_rating'] * (1 + df['popularity_penalty_norm'])

    return df


def get_hidden_gems(movies_df, ratings_df, n=20, genre=None,
                    min_votes=50, max_popularity=5000):
    """Get the top-N hidden gems.

    Args:
        movies_df: movies DataFrame
        ratings_df: ratings DataFrame
        n: number of gems to return
        genre: optional genre filter (e.g., "Sci-Fi")
        min_votes: minimum ratings for Bayesian average
        max_popularity: maximum number of ratings (above this = too popular to be a gem)

    Returns:
        DataFrame with movie info and gem scores
    """
    # Compute scores
    movie_stats = compute_bayesian_average(ratings_df, min_votes=min_votes)
    scored = compute_gem_scores(movie_stats)

    # Filter: must have enough votes but not be super popular
    gems = scored[
        (scored['rating_count'] >= min_votes) &
        (scored['rating_count'] <= max_popularity)
    ]

    # Merge with movie info
    gems = gems.merge(movies_df[['movieId', 'title', 'genres']], on='movieId')

    # Optional genre filter
    if genre:
        gems = gems[gems['genres'].str.contains(genre, case=False, na=False)]

    # Sort by gem score and return top N
    gems = gems.nlargest(n, 'gem_score')

    return gems[['movieId', 'title', 'genres', 'bayesian_avg_rating',
                  'rating_count', 'gem_score']].reset_index(drop=True)


def get_personalized_hidden_gems(user_id, predictions, movies_df, ratings_df,
                                  n=10, min_votes=50, max_popularity=5000):
    """Get hidden gems personalized for a specific user.

    Combines the gem score with the user's predicted collaborative rating
    to find gems that match the user's taste.

    Args:
        user_id: target user ID
        predictions: dict of {movieId: predicted_rating} from collab model
        movies_df: movies DataFrame
        ratings_df: ratings DataFrame
        n: number of gems to return
        min_votes: minimum ratings for Bayesian average
        max_popularity: max popularity threshold

    Returns:
        DataFrame with personalized gem recommendations
    """
    # Get base gem scores
    movie_stats = compute_bayesian_average(ratings_df, min_votes=min_votes)
    scored = compute_gem_scores(movie_stats)

    gems = scored[
        (scored['rating_count'] >= min_votes) &
        (scored['rating_count'] <= max_popularity)
    ].copy()

    # Add predicted ratings from collaborative filtering
    gems['predicted_rating'] = gems['movieId'].map(predictions).fillna(0)

    # Filter out movies with no prediction (not in user's collab model)
    gems = gems[gems['predicted_rating'] > 0]

    # Normalize both scores to 0-1 for combination
    if len(gems) == 0:
        return pd.DataFrame()

    gem_min, gem_max = gems['gem_score'].min(), gems['gem_score'].max()
    pred_min, pred_max = gems['predicted_rating'].min(), gems['predicted_rating'].max()

    if gem_max > gem_min:
        gems['gem_score_norm'] = (gems['gem_score'] - gem_min) / (gem_max - gem_min)
    else:
        gems['gem_score_norm'] = 0.5

    if pred_max > pred_min:
        gems['pred_score_norm'] = (gems['predicted_rating'] - pred_min) / (pred_max - pred_min)
    else:
        gems['pred_score_norm'] = 0.5

    # Combined score: 60% gem quality, 40% user preference
    gems['personalized_gem_score'] = 0.6 * gems['gem_score_norm'] + 0.4 * gems['pred_score_norm']

    # Merge with movie info
    gems = gems.merge(movies_df[['movieId', 'title', 'genres']], on='movieId')

    gems = gems.nlargest(n, 'personalized_gem_score')

    return gems[['movieId', 'title', 'genres', 'bayesian_avg_rating',
                  'rating_count', 'predicted_rating',
                  'personalized_gem_score']].reset_index(drop=True)


if __name__ == "__main__":
    from src.data_loader import load_all_dataframes

    print("Loading data...")
    movies_df, ratings_df, tags_df = load_all_dataframes()

    print("\nTop 20 Hidden Gems (all genres):")
    gems = get_hidden_gems(movies_df, ratings_df, n=20)
    print(gems.to_string(index=False))

    print("\nTop 10 Sci-Fi Hidden Gems:")
    scifi_gems = get_hidden_gems(movies_df, ratings_df, n=10, genre='Sci-Fi')
    print(scifi_gems.to_string(index=False))
