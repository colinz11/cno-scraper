import matplotlib.pyplot as plt
from datetime import datetime
from database.Repository import Repository
from database.Database import Market, BookOdd, session
import re
import logging
import mplcursors

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Grapher:
    def __init__(self, repository: Repository):
        self.repository = repository

    def plot_book_odds(self, market: Market):
        # Query the book odds for the given market
        book_odds = self.repository.session.query(BookOdd).filter(BookOdd.market_id == market.id).all()

        if not book_odds:
            logging.info(f"No book odds found for market: {market}")
            return

        # Prepare data for plotting
        book_names = set([book_odd.book_name for book_odd in book_odds])
        book_odds_by_book = {book_name: [] for book_name in book_names}
        timestamps = []

        for book_odd in book_odds:
            book_odds_by_book[book_odd.book_name].append((book_odd.timestamp, book_odd.odds))
            if book_odd.timestamp not in timestamps:
                timestamps.append(book_odd.timestamp)

        # Sort timestamps
        timestamps.sort()

        # Remove content within parentheses from the event string
        event_cleaned = re.sub(r'\([^)]*\)', '', market.event).strip()

        # Plot data as line plot with different colors
        plt.figure(figsize=(10, 6))
        lines = []
        for book_name, odds in book_odds_by_book.items():
            odds.sort(key=lambda x: x[0])  # Sort by timestamp
            times = [o[0] for o in odds]
            values = [o[1] for o in odds]
            line, = plt.plot(times, values, label=book_name)
            lines.append(line)

        plt.xlabel('Time')
        plt.ylabel('Odds')
        plt.title(f'Book Odds for Market: {event_cleaned} - Bet: {market.bet_name}')
        plt.legend()
        plt.grid(True)

        # Add interactive hover functionality
        
        cursor = mplcursors.cursor(lines, hover=True)
        cursor.connect(
            "add", lambda sel: sel.annotation.set_text(f"{sel.artist.get_label()}: {sel.target[1]:.2f}")
        )

        plt.show()

    def close_all_windows(self):
        plt.close('all')

