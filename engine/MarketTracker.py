import logging
from database.Database import Market
from scraper.WebScraper import WebScraper
from database.Repository import Repository

class MarketTracker:
    def __init__(self, scraper : WebScraper, repo : Repository):
        self.scraper : WebScraper = scraper
        self.repo : Repository = repo
        self.markets_to_track = []

    def track_market(self, market: Market):
        if market not in self.markets_to_track:
            self.markets_to_track.append(market)
            logging.info(f"Added market to track: {market}")
        else:
            logging.info(f"Market already being tracked: {market}")

    def remove_market(self, market: Market):
        if market in self.markets_to_track:
            self.markets_to_track.remove(market)
            logging.info(f"Removed market from tracking: {market}")
        else:
            logging.info(f"Market not found in tracking list: {market}")

    def check_market_updates(self):
        for market in self.markets_to_track:
            logging.info(f"Checking updates for market: {market}")
            response = self.scraper.scrape_market(market)
            if response == 'Invalid Market':
                self.remove_market(market)
            else:
                for book_odd in response:
                    print(book_odd)
                    
