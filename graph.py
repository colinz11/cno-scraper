from database.Repository import Repository
from database.Database import session
from visualizer.Grapher import Grapher


# Example usage
if __name__ == "__main__":
    # Initialize the Repository
    repo = Repository(session)

    # Initialize the Grapher
    grapher = Grapher(repo)

    # Example market
    market = repo.get_market_by_id(54)

    # Plot book odds for the market
    if market:
        grapher.plot_book_odds(market)
    else:

        print("Market not found.")
