"""
collab_recommender.py - Collaborative Filtering Movie Recommendation.
Uses Truncated SVD on a sampled user-item rating matrix.
RAM-safe: samples 7M ratings to keep peak memory ~3-4 GB.
"""
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.decomposition import TruncatedSVD


def sample_ratings(ratings_df, n=7_000_000, random_state=42):
    """Sample ratings while preserving user diversity.

    Uses stratified-like sampling: ensures we keep at least some ratings
    from as many users as possible.

    Args:
        ratings_df: full ratings DataFrame
        n: number of ratings to sample
        random_state: random seed for reproducibility

    Returns:
        DataFrame: sampled ratings
    """
    if len(ratings_df) <= n:
        print(f"  Dataset has {len(ratings_df)} ratings, no sampling needed.")
        return ratings_df

    print(f"  Sampling {n:,} from {len(ratings_df):,} ratings...")

    # Group by user and sample proportionally
    sampled = ratings_df.groupby('userId', group_keys=False).apply(
        lambda x: x.sample(
            n=max(1, int(len(x) * n / len(ratings_df))),
            random_state=random_state
        )
    )

    # If we're still short/over, adjust
    if len(sampled) > n:
        sampled = sampled.sample(n=n, random_state=random_state)

    print(f"  Sampled {len(sampled):,} ratings from "
          f"{sampled['userId'].nunique():,} users covering "
          f"{sampled['movieId'].nunique():,} movies")
    return sampled.reset_index(drop=True)


def build_user_item_matrix(ratings_df):
    """Build a sparse user-item rating matrix.

    Returns:
        tuple: (sparse_matrix, user_id_to_idx, idx_to_user_id,
                movie_id_to_idx, idx_to_movie_id)
    """
    print("  Building sparse user-item matrix...")

    # Create mappings from IDs to matrix indices
    user_ids = ratings_df['userId'].unique()
    movie_ids = ratings_df['movieId'].unique()

    user_id_to_idx = {uid: i for i, uid in enumerate(user_ids)}
    movie_id_to_idx = {mid: i for i, mid in enumerate(movie_ids)}
    idx_to_user_id = {i: uid for uid, i in user_id_to_idx.items()}
    idx_to_movie_id = {i: mid for mid, i in movie_id_to_idx.items()}

    # Build sparse matrix
    row_indices = ratings_df['userId'].map(user_id_to_idx).values
    col_indices = ratings_df['movieId'].map(movie_id_to_idx).values
    values = ratings_df['rating'].values

    matrix = csr_matrix(
        (values, (row_indices, col_indices)),
        shape=(len(user_ids), len(movie_ids))
    )

    print(f"  Matrix shape: {matrix.shape}, "
          f"non-zero: {matrix.nnz:,} ({matrix.nnz / (matrix.shape[0] * matrix.shape[1]) * 100:.4f}% dense)")

    return matrix, user_id_to_idx, idx_to_user_id, movie_id_to_idx, idx_to_movie_id


def train_svd_model(user_item_matrix, n_components=50, random_state=42):
    """Train a Truncated SVD model for dimensionality reduction.

    Args:
        user_item_matrix: sparse user-item matrix
        n_components: number of latent factors (50 for RAM safety)
        random_state: random seed

    Returns:
        TruncatedSVD: fitted model
    """
    print(f"  Training SVD with {n_components} components...")
    svd = TruncatedSVD(n_components=n_components, random_state=random_state)
    svd.fit(user_item_matrix)

    explained = svd.explained_variance_ratio_.sum() * 100
    print(f"  Explained variance: {explained:.1f}%")
    return svd


def predict_ratings_for_user(user_id, svd_model, user_item_matrix,
                              user_id_to_idx, idx_to_movie_id):
    """Predict ratings for all movies for a given user.

    Returns:
        dict: {movieId: predicted_rating}
    """
    if user_id not in user_id_to_idx:
        return {}

    user_idx = user_id_to_idx[user_id]

    # Get the user's row and project into latent space
    user_vector = user_item_matrix[user_idx]
    user_latent = svd_model.transform(user_vector)

    # Reconstruct: predicted ratings = user_latent @ components
    predicted = user_latent @ svd_model.components_

    # Map back to movie IDs
    predictions = {}
    for col_idx in range(predicted.shape[1]):
        movie_id = idx_to_movie_id[col_idx]
        predictions[movie_id] = predicted[0, col_idx]

    return predictions


def recommend_for_user(user_id, svd_model, user_item_matrix,
                       user_id_to_idx, idx_to_user_id,
                       movie_id_to_idx, idx_to_movie_id,
                       movies_df, n=10):
    """Get top-N movie recommendations for a user.

    Only recommends movies the user has NOT already rated.

    Returns:
        DataFrame with movieId, title, genres, predicted_rating
    """
    if user_id not in user_id_to_idx:
        print(f"User {user_id} not found in the sampled data.")
        return pd.DataFrame()

    # Get predictions
    predictions = predict_ratings_for_user(
        user_id, svd_model, user_item_matrix,
        user_id_to_idx, idx_to_movie_id
    )

    # Find movies the user already rated
    user_idx = user_id_to_idx[user_id]
    rated_cols = user_item_matrix[user_idx].nonzero()[1]
    rated_movie_ids = {idx_to_movie_id[c] for c in rated_cols}

    # Filter out already-rated movies
    unrated_predictions = {
        mid: score for mid, score in predictions.items()
        if mid not in rated_movie_ids
    }

    # Sort and pick top N
    top_movie_ids = sorted(unrated_predictions, key=unrated_predictions.get, reverse=True)[:n]

    results = pd.DataFrame({
        'movieId': top_movie_ids,
        'predicted_rating': [unrated_predictions[mid] for mid in top_movie_ids]
    })
    results = results.merge(movies_df[['movieId', 'title', 'genres']], on='movieId', how='left')

    return results[['movieId', 'title', 'genres', 'predicted_rating']]


if __name__ == "__main__":
    from src.data_loader import load_all_dataframes

    print("Loading data...")
    movies_df, ratings_df, tags_df = load_all_dataframes()

    print("\nSampling ratings...")
    sampled = sample_ratings(ratings_df, n=7_000_000)

    # Free memory from full ratings
    del ratings_df

    print("\nBuilding user-item matrix...")
    matrix, u2i, i2u, m2i, i2m = build_user_item_matrix(sampled)

    print("\nTraining SVD model...")
    model = train_svd_model(matrix, n_components=50)

    # Example: recommend for user 1
    print("\nTop 10 recommendations for user 1:")
    recs = recommend_for_user(1, model, matrix, u2i, i2u, m2i, i2m, movies_df, n=10)
    print(recs.to_string(index=False))
