"""
data_loader.py - Data loading utilities for the movie recommendation system.
Handles SQLite database connections and DataFrame loading.
"""
import pandas as pd
import sqlite3
import os


def create_connection(db_name='movie_review.db'):
    """Create and return a SQLite database connection.
    
    Looks for the database in the 'data' directory.
    """
    # Get the path relative to the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, 'data', db_name)
    
    # Check if database exists at the new location
    if not os.path.exists(db_path):
        # Fallback to current directory for backward compatibility
        if os.path.exists(db_name):
            db_path = db_name
    
    conn = sqlite3.connect(db_path)
    return conn


def load_movies_dataframe(conn):
    """Load the movies table into a DataFrame."""
    query = "SELECT * FROM movies"
    df = pd.read_sql_query(query, conn)
    return df


def load_ratings_dataframe(conn):
    """Load the ratings table into a DataFrame."""
    query = "SELECT * FROM ratings"
    df = pd.read_sql_query(query, conn)
    return df


def load_tags_dataframe(conn):
    """Load the tags table into a DataFrame."""
    query = "SELECT * FROM tags"
    df = pd.read_sql_query(query, conn)
    return df


def load_all_dataframes(db_name='movie_review.db'):
    """Load all tables and return as DataFrames.

    Returns:
        tuple: (movies_df, ratings_df, tags_df)
    """
    conn = create_connection(db_name)
    try:
        movies_df = load_movies_dataframe(conn)
        ratings_df = load_ratings_dataframe(conn)
        tags_df = load_tags_dataframe(conn)
        return movies_df, ratings_df, tags_df
    finally:
        conn.close()


def get_movie_title(movie_id, movies_df):
    """Get movie title by movieId."""
    match = movies_df[movies_df['movieId'] == movie_id]
    if len(match) == 0:
        return None
    return match.iloc[0]['title']


def get_movie_id(title, movies_df):
    """Search for a movie by title (case-insensitive partial match).

    Returns:
        DataFrame: matching movies with movieId and title
    """
    mask = movies_df['title'].str.contains(title, case=False, na=False)
    return movies_df[mask][['movieId', 'title', 'genres']]


def get_movie_genres(movie_id, movies_df):
    """Get the list of genres for a movie."""
    match = movies_df[movies_df['movieId'] == movie_id]
    if len(match) == 0:
        return []
    return match.iloc[0]['genres'].split('|')


def get_top_rated_movies(conn, limit=10):
    """Get top rated movies by average rating."""
    query = """
    SELECT m.movieId, m.title, ROUND(AVG(r.rating), 2) as avg_rating, 
           COUNT(r.ratingId) as num_ratings
    FROM movies m
    JOIN ratings r ON m.movieId = r.movieId
    GROUP BY m.movieId
    HAVING num_ratings >= 10
    ORDER BY avg_rating DESC, num_ratings DESC
    LIMIT ?
    """
    return pd.read_sql_query(query, conn, params=(limit,))


def get_most_rated_movies(conn, limit=10):
    """Get movies with the most ratings."""
    query = """
    SELECT m.movieId, m.title, ROUND(AVG(r.rating), 2) as avg_rating,
           COUNT(r.ratingId) as num_ratings
    FROM movies m
    JOIN ratings r ON m.movieId = r.movieId
    GROUP BY m.movieId
    ORDER BY num_ratings DESC
    LIMIT ?
    """
    return pd.read_sql_query(query, conn, params=(limit,))


def get_movie_ratings_stats(conn, movie_id):
    """Get rating statistics for a specific movie."""
    query = """
    SELECT m.movieId, m.title,
           COUNT(r.ratingId) as total_ratings,
           ROUND(AVG(r.rating), 2) as avg_rating,
           ROUND(MIN(r.rating), 1) as min_rating,
           ROUND(MAX(r.rating), 1) as max_rating,
           ROUND(CAST(SUM((r.rating - (SELECT AVG(rating) FROM ratings WHERE movieId = ?)
                           * (r.rating - (SELECT AVG(rating) FROM ratings WHERE movieId = ?))
                    ) AS FLOAT) / COUNT(r.ratingId), 2) as std_dev
    FROM movies m
    JOIN ratings r ON m.movieId = r.movieId
    WHERE m.movieId = ?
    """
    return pd.read_sql_query(query, conn, params=(movie_id, movie_id, movie_id))


def get_movies_by_genre(conn, genre, limit=20):
    """Get movies by genre."""
    query = """
    SELECT DISTINCT m.movieId, m.title, m.genres
    FROM movies m
    WHERE m.genres LIKE ?
    LIMIT ?
    """
    return pd.read_sql_query(query, conn, params=(f'%{genre}%', limit))


def get_similar_movies_by_tags(conn, movie_id, limit=10):
    """Get movies similar to the given movie based on genome tags."""
    query = """
    SELECT DISTINCT m2.movieId, m2.title,
           COUNT(DISTINCT gs1.tagId) as common_tags,
           ROUND(AVG(gs2.relevance), 3) as avg_similarity
    FROM genome_scores gs1
    JOIN movies m1 ON gs1.movieId = m1.movieId
    JOIN genome_scores gs2 ON gs1.tagId = gs2.tagId AND gs2.movieId != gs1.movieId
    JOIN movies m2 ON gs2.movieId = m2.movieId
    WHERE m1.movieId = ?
    GROUP BY m2.movieId
    ORDER BY common_tags DESC, avg_similarity DESC
    LIMIT ?
    """
    return pd.read_sql_query(query, conn, params=(movie_id, limit))


def get_user_ratings_summary(conn, user_id):
    """Get rating summary for a user."""
    query = """
    SELECT ? as userId,
           COUNT(ratingId) as total_ratings,
           ROUND(AVG(rating), 2) as avg_rating,
           ROUND(MIN(rating), 1) as min_rating,
           ROUND(MAX(rating), 1) as max_rating
    FROM ratings
    WHERE userId = ?
    """
    return pd.read_sql_query(query, conn, params=(user_id, user_id))


def get_user_rated_movies(conn, user_id, limit=50):
    """Get movies rated by a user."""
    query = """
    SELECT m.movieId, m.title, m.genres, r.rating,
           datetime(r.timestamp, 'unixepoch') as rating_date
    FROM ratings r
    JOIN movies m ON r.movieId = m.movieId
    WHERE r.userId = ?
    ORDER BY r.timestamp DESC
    LIMIT ?
    """
    return pd.read_sql_query(query, conn, params=(user_id, limit))


def get_genome_tags_for_movie(conn, movie_id, limit=20):
    """Get genome tags and relevance scores for a movie."""
    query = """
    SELECT gt.tagId, gt.tag, ROUND(gs.relevance, 4) as relevance
    FROM genome_scores gs
    JOIN genome_tags gt ON gs.tagId = gt.tagId
    WHERE gs.movieId = ?
    ORDER BY gs.relevance DESC
    LIMIT ?
    """
    return pd.read_sql_query(query, conn, params=(movie_id, limit))


def search_movies(conn, search_term, limit=20):
    """Search for movies by title (case-insensitive)."""
    query = """
    SELECT m.movieId, m.title, m.genres,
           ROUND(AVG(r.rating), 2) as avg_rating,
           COUNT(r.ratingId) as num_ratings
    FROM movies m
    LEFT JOIN ratings r ON m.movieId = r.movieId
    WHERE LOWER(m.title) LIKE LOWER(?)
    GROUP BY m.movieId
    ORDER BY num_ratings DESC
    LIMIT ?
    """
    return pd.read_sql_query(query, conn, params=(f'%{search_term}%', limit))
