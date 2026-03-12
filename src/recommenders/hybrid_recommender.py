"""
hybrid_recommender.py - Hybrid Recommendation Engine & CLI.
Combines content-based, collaborative filtering, and hidden gems.
"""
import numpy as np
import pandas as pd
from src.data_loader import load_all_dataframes, get_movie_id, get_movie_title
from src.recommenders.content_recommender import build_content_features, get_similar_movies
from src.recommenders.collab_recommender import (
    sample_ratings, build_user_item_matrix,
    train_svd_model, predict_ratings_for_user, recommend_for_user
)
from src.recommenders.hidden_gems import get_hidden_gems, get_personalized_hidden_gems


class HybridRecommender:
    """Hybrid movie recommendation system combining multiple strategies."""

    def __init__(self, sample_size=7_000_000, svd_components=50):
        self.sample_size = sample_size
        self.svd_components = svd_components
        self.is_loaded = False

    def load_data(self):
        """Load all data and build models."""
        print("=" * 60)
        print("LOADING MOVIE RECOMMENDATION SYSTEM")
        print("=" * 60)

        # Step 1: Load data
        print("\n[1/4] Loading data from database...")
        self.movies_df, self.ratings_df, self.tags_df = load_all_dataframes()
        print(f"  Movies: {len(self.movies_df):,}")
        print(f"  Ratings: {len(self.ratings_df):,}")
        print(f"  Tags: {len(self.tags_df):,}")

        # Step 2: Build content features
        print("\n[2/4] Building content-based features...")
        self.content_features, self.content_movie_ids = build_content_features(
            self.movies_df, self.tags_df
        )

        # Step 3: Build collaborative model
        print("\n[3/4] Building collaborative filtering model...")
        sampled = sample_ratings(self.ratings_df, n=self.sample_size)
        self.user_item_matrix, self.u2i, self.i2u, self.m2i, self.i2m = \
            build_user_item_matrix(sampled)
        del sampled  # free memory

        print("\n[4/4] Training SVD model...")
        self.svd_model = train_svd_model(
            self.user_item_matrix, n_components=self.svd_components
        )

        self.is_loaded = True
        print("\n✓ System ready!")
        print("=" * 60)

    def similar_movies(self, movie_id, n=10):
        """Find movies similar to a given movie (content-based)."""
        return get_similar_movies(
            movie_id, self.content_features, self.movies_df, n=n
        )

    def user_recommendations(self, user_id, n=10):
        """Get personalized recommendations for a user (collaborative)."""
        return recommend_for_user(
            user_id, self.svd_model, self.user_item_matrix,
            self.u2i, self.i2u, self.m2i, self.i2m,
            self.movies_df, n=n
        )

    def hidden_gems(self, n=20, genre=None):
        """Get top hidden gem movies."""
        return get_hidden_gems(
            self.movies_df, self.ratings_df, n=n, genre=genre
        )

    def personalized_gems(self, user_id, n=10):
        """Get hidden gems tailored to a specific user's taste."""
        predictions = predict_ratings_for_user(
            user_id, self.svd_model, self.user_item_matrix,
            self.u2i, self.i2m
        )
        return get_personalized_hidden_gems(
            user_id, predictions, self.movies_df, self.ratings_df, n=n
        )

    def hybrid_recommend(self, user_id, n=10, alpha=0.3):
        """Hybrid recommendations blending content + collaborative scores.

        Args:
            user_id: target user ID
            n: number of recommendations
            alpha: weight for content score (1 - alpha = collab weight)

        Returns:
            DataFrame with blended recommendations
        """
        # Get collaborative predictions
        predictions = predict_ratings_for_user(
            user_id, self.svd_model, self.user_item_matrix,
            self.u2i, self.i2m
        )

        if not predictions:
            print(f"User {user_id} not found. Falling back to hidden gems.")
            return self.hidden_gems(n=n)

        # Get user's top-rated movies for content-based expansion
        user_idx = self.u2i[user_id]
        rated_cols = self.user_item_matrix[user_idx].nonzero()[1]
        rated_data = self.user_item_matrix[user_idx].data

        if len(rated_cols) == 0:
            return self.hidden_gems(n=n)

        # Find user's highest-rated movies
        top_rated_idx = rated_data.argsort()[::-1][:5]
        top_movie_ids = [self.i2m[rated_cols[i]] for i in top_rated_idx]

        # Get content-similar movies to user's favorites
        content_scores = {}
        for mid in top_movie_ids:
            similar = get_similar_movies(
                mid, self.content_features, self.movies_df, n=50
            )
            for _, row in similar.iterrows():
                m = row['movieId']
                if m not in content_scores or row['similarity_score'] > content_scores[m]:
                    content_scores[m] = row['similarity_score']

        # Combine scores
        all_movie_ids = set(predictions.keys()) | set(content_scores.keys())
        rated_movie_ids = {self.i2m[c] for c in rated_cols}
        all_movie_ids -= rated_movie_ids  # exclude already rated

        results = []
        for mid in all_movie_ids:
            collab_score = predictions.get(mid, 0)
            content_score = content_scores.get(mid, 0)
            hybrid_score = alpha * content_score + (1 - alpha) * collab_score
            results.append({'movieId': mid, 'hybrid_score': hybrid_score})

        results_df = pd.DataFrame(results)
        results_df = results_df.nlargest(n, 'hybrid_score')
        results_df = results_df.merge(
            self.movies_df[['movieId', 'title', 'genres']], on='movieId', how='left'
        )

        return results_df[['movieId', 'title', 'genres', 'hybrid_score']].reset_index(drop=True)

    def search_movie(self, title):
        """Search for a movie by title."""
        return get_movie_id(title, self.movies_df)


def run_cli():
    """Run the interactive CLI for the recommendation system."""
    recommender = HybridRecommender()
    recommender.load_data()

    while True:
        print("\n" + "=" * 60)
        print("MOVIE RECOMMENDATION SYSTEM")
        print("=" * 60)
        print("1. Find similar movies        (content-based)")
        print("2. Recommendations for user   (collaborative)")
        print("3. Hybrid recommendations     (content + collab)")
        print("4. Hidden gems                (all genres)")
        print("5. Hidden gems by genre")
        print("6. Personalized hidden gems   (for a user)")
        print("7. Search for a movie")
        print("0. Exit")
        print("-" * 60)

        choice = input("Choose an option: ").strip()

        if choice == '0':
            print("Goodbye!")
            break

        elif choice == '1':
            query = input("Enter movie title (or ID): ").strip()
            movie_id = _resolve_movie(query, recommender)
            if movie_id:
                n = _get_n("How many similar movies? (default 10): ", 10)
                title = get_movie_title(movie_id, recommender.movies_df)
                print(f"\nMovies similar to: {title}")
                print("-" * 60)
                result = recommender.similar_movies(movie_id, n=n)
                _print_results(result)

        elif choice == '2':
            user_id = _get_int("Enter user ID: ")
            if user_id:
                n = _get_n("How many recommendations? (default 10): ", 10)
                print(f"\nRecommendations for user {user_id}:")
                print("-" * 60)
                result = recommender.user_recommendations(user_id, n=n)
                _print_results(result)

        elif choice == '3':
            user_id = _get_int("Enter user ID: ")
            if user_id:
                n = _get_n("How many recommendations? (default 10): ", 10)
                print(f"\nHybrid recommendations for user {user_id}:")
                print("-" * 60)
                result = recommender.hybrid_recommend(user_id, n=n)
                _print_results(result)

        elif choice == '4':
            n = _get_n("How many hidden gems? (default 20): ", 20)
            print(f"\nTop {n} Hidden Gems:")
            print("-" * 60)
            result = recommender.hidden_gems(n=n)
            _print_results(result)

        elif choice == '5':
            genre = input("Enter genre (e.g., Sci-Fi, Comedy, Drama): ").strip()
            n = _get_n("How many hidden gems? (default 10): ", 10)
            print(f"\nTop {n} {genre} Hidden Gems:")
            print("-" * 60)
            result = recommender.hidden_gems(n=n, genre=genre)
            _print_results(result)

        elif choice == '6':
            user_id = _get_int("Enter user ID: ")
            if user_id:
                n = _get_n("How many personalized gems? (default 10): ", 10)
                print(f"\nPersonalized hidden gems for user {user_id}:")
                print("-" * 60)
                result = recommender.personalized_gems(user_id, n=n)
                _print_results(result)

        elif choice == '7':
            query = input("Search for movie: ").strip()
            results = recommender.search_movie(query)
            if len(results) == 0:
                print("No movies found.")
            else:
                print(f"\nFound {len(results)} matches:")
                print(results.head(20).to_string(index=False))

        else:
            print("Invalid option. Try again.")


def _resolve_movie(query, recommender):
    """Resolve a movie title or ID to a movieId."""
    try:
        return int(query)
    except ValueError:
        matches = recommender.search_movie(query)
        if len(matches) == 0:
            print("No movies found.")
            return None
        elif len(matches) == 1:
            return matches.iloc[0]['movieId']
        else:
            print(f"\nFound {len(matches)} matches:")
            print(matches.head(15).to_string(index=False))
            movie_id = _get_int("\nEnter the movie ID: ")
            return movie_id


def _get_int(prompt):
    """Get an integer from user input."""
    try:
        return int(input(prompt).strip())
    except ValueError:
        print("Invalid number.")
        return None


def _get_n(prompt, default):
    """Get a count from user input with a default."""
    val = input(prompt).strip()
    if not val:
        return default
    try:
        return int(val)
    except ValueError:
        return default


def _print_results(df):
    """Pretty-print a results DataFrame."""
    if df is None or len(df) == 0:
        print("No results found.")
    else:
        print(df.to_string(index=False))


if __name__ == "__main__":
    run_cli()
