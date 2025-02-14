import logging

class MarketTracker:
    def __init__(self):
        self.markets_to_track = []

    def add_market_to_track(self, market_url: str):
        if market_url not in self.markets_to_track:
            self.markets_to_track.append(market_url)
            logging.info(f"Added market to track: {market_url}")
        else:
            logging.info(f"Market already being tracked: {market_url}")

    def remove_market_to_track(self, market_url: str):
        if market_url in self.markets_to_track:
            self.markets_to_track.remove(market_url)
            logging.info(f"Removed market from tracking: {market_url}")
        else:
            logging.info(f"Market not found in tracking list: {market_url}")

