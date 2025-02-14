from typing import List
from datetime import datetime

class Market:
    def __init__(self, date: str, sport: str, league: str, event: str, market: str, bet_name: str) -> None:
        self.date: str = date
        self.sport: str = sport
        self.league: str = league
        self.event: str = event
        self.market: str = market
        self.bet_name: str = bet_name

    def __eq__(self, value) -> bool:
        if not isinstance(value, Market):
            return False
        return self.date == value.date and self.sport == value.sport and self.league == value.league and self.event == value.event and self.market == value.market

    def __repr__(self) -> str:
        return f"Market(date={self.date}, sport={self.sport}, league={self.league}, event={self.event}, market={self.market}, bet_name={self.bet_name})"

class BookOdd:
    def __init__(self, market: Market, book_name: str, odds: int, timestamp: datetime) -> None:
        self.market: Market = market
        self.book_name: str = book_name
        self.odds: int = odds
        self.timestamp: datetime = timestamp

    def __repr__(self) -> str:
        return f"BookOdd(market={self.market}, book_name={self.book_name}, odds={self.odds}, timestamp={self.timestamp})"

class Bet:
    def __init__(self, market: Market, book_odds: List[BookOdd], timestamp: datetime) -> None:
        self.market: Market = market
        self.book_odds: List[BookOdd] = book_odds
        self.fair_odds: int = self.calculate_fair_odds()
        self.timestamp: datetime = timestamp

    # TODO - Implement more accurate fair odds calculation 
    def calculate_fair_odds(self) -> int:
        # Placeholder implementation
        return sum(book_odd.odds for book_odd in self.book_odds) // len(self.book_odds)

    def __repr__(self) -> str:
        return f"Bet(market={self.market}, book_odds={self.book_odds}, fair_odds={self.fair_odds}, timestamp={self.timestamp})"