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
