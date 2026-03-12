"""
main.py - Entry point for the Movie Recommendation System.
Usage:
    python main.py eda            Run exploratory data analysis
    python main.py recommend      Launch interactive recommendation CLI
    python main.py hidden-gems    Show top hidden gems
    python main.py                Show help
"""
import sys


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1].lower()

    if command == 'eda':
        from src.eda import run_eda
        run_eda()

    elif command == 'recommend':
        from src.recommenders.hybrid_recommender import run_cli
        run_cli()

    elif command == 'hidden-gems':
        from src.recommenders.hidden_gems import get_hidden_gems
        from src.data_loader import load_all_dataframes

        print("Loading data...")
        movies_df, ratings_df, _ = load_all_dataframes()

        genre = None
        if len(sys.argv) > 2:
            genre = sys.argv[2]
            print(f"\nTop 20 {genre} Hidden Gems:")
        else:
            print("\nTop 20 Hidden Gems:")

        gems = get_hidden_gems(movies_df, ratings_df, n=20, genre=genre)
        print(gems.to_string(index=False))

    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()