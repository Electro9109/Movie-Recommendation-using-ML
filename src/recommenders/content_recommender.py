"""
content_recommender.py - Content-Based Movie Recommendation.
Recommends movies similar to a given movie using genre + tag features.
"""
import numpy as np
import pandas as pd
from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer


def build_genre_features(movies_df):
    """One-hot encode the pipe-separated genres.

    Returns:
        sparse matrix: shape (n_movies, n_genres)
    """
    genre_lists = movies_df['genres'].str.split('|')
    mlb = MultiLabelBinarizer()
    genre_matrix = mlb.fit_transform(genre_lists)
    return csr_matrix(genre_matrix), mlb.classes_


def build_tag_features(tags_df, movies_df, max_features=500):
    """Aggregate all tags per movie and apply TF-IDF.

    Args:
        tags_df: tags DataFrame
        movies_df: movies DataFrame (to ensure alignment)
        max_features: limit TF-IDF vocabulary size to save memory

    Returns:
        sparse matrix: shape (n_movies, max_features)
    """
    # Aggregate all tags for each movie into a single string
    tag_agg = tags_df.groupby('movieId')['tag'].apply(
        lambda x: ' '.join(x.astype(str).str.lower())
    ).reset_index()
    tag_agg.columns = ['movieId', 'tags_combined']

    # Merge with movies to ensure every movie has an entry
    movies_tags = movies_df[['movieId']].merge(tag_agg, on='movieId', how='left')
    movies_tags['tags_combined'] = movies_tags['tags_combined'].fillna('')

    # TF-IDF on the combined tags
    tfidf = TfidfVectorizer(max_features=max_features, stop_words='english')
    tag_matrix = tfidf.fit_transform(movies_tags['tags_combined'])

    return tag_matrix, tfidf.get_feature_names_out()


def build_content_features(movies_df, tags_df, tag_weight=0.5):
    """Build combined genre + tag feature matrix.

    Args:
        movies_df: movies DataFrame
        tags_df: tags DataFrame
        tag_weight: weight for tag features relative to genres (0-1)

    Returns:
        tuple: (feature_matrix, movie_ids array)
    """
    print("  Building genre features...")
    genre_matrix, genre_names = build_genre_features(movies_df)

    print("  Building tag features...")
    tag_matrix, tag_names = build_tag_features(tags_df, movies_df)

    # Combine: genres (weight 1) + tags (weight tag_weight)
    combined = hstack([genre_matrix, tag_matrix * tag_weight])

    movie_ids = movies_df['movieId'].values
    print(f"  Content feature matrix: {combined.shape}")
    return combined, movie_ids


def get_similar_movies(movie_id, feature_matrix, movies_df, n=10):
    """Find the top-N most similar movies to a given movie.

    Args:
        movie_id: the target movie's ID
        feature_matrix: sparse feature matrix from build_content_features
        movies_df: movies DataFrame
        n: number of similar movies to return

    Returns:
        DataFrame with movieId, title, genres, similarity_score
    """
    movie_ids = movies_df['movieId'].values

    # Find the index of the target movie
    idx_array = np.where(movie_ids == movie_id)[0]
    if len(idx_array) == 0:
        print(f"Movie ID {movie_id} not found.")
        return pd.DataFrame()

    idx = idx_array[0]

    # Compute cosine similarity between this movie and all others
    movie_vector = feature_matrix[idx]
    similarities = cosine_similarity(movie_vector, feature_matrix).flatten()

    # Get top N+1 (excluding itself)
    top_indices = similarities.argsort()[::-1][1:n + 1]

    results = pd.DataFrame({
        'movieId': movie_ids[top_indices],
        'similarity_score': similarities[top_indices]
    })
    results = results.merge(movies_df[['movieId', 'title', 'genres']], on='movieId')

    return results[['movieId', 'title', 'genres', 'similarity_score']]


if __name__ == "__main__":
    from src.data_loader import load_all_dataframes

    print("Loading data...")
    movies_df, ratings_df, tags_df = load_all_dataframes()

    print("Building content features...")
    features, movie_ids = build_content_features(movies_df, tags_df)

    # Example: find movies similar to Toy Story (movieId=1)
    print("\nMovies similar to Toy Story (1995):")
    similar = get_similar_movies(1, features, movies_df, n=10)
    print(similar.to_string(index=False))
