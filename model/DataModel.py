from typing import Any

class Market:
    def __init__(self, date: str, sport: str, league: str, event: str, market: str, bet_name: str,) -> None:
        self.date: str = date
        self.sport: str = sport
        self.league: str = league
        self.event: str = event
        self.market: str = market
        self.bet_name: str = bet_name

    def __eq__(self, value):
        if not isinstance(value, Market):
            return False
        return self.date == value.date and self.sport == value.sport and self.league == value.league and self.event == value.event and self.market == value.market

    def __repr__(self) -> str:
        return f"Market(date={self.date}, sport={self.sport}, league={self.league}, event={self.event}, market={self.market})"

class BookOdd:
    def __init__(self, market: Market, book_name: str, odds: int) -> None:
        self.market: Market = market
        self.book_name: str = book_name
        self.odds: int = odds  

    def __repr__(self) -> str:
        return f"BookOdds(market={self.market}, book_name={self.book_name}, odds={self.odds})"
    
class Bet:
    def __init__(self, market: Market, book_odds: list[BookOdd], fair_odds: int) -> None:
        self.market: Market = market
        self.book_odds: list[BookOdd] = book_odds
        self.fair_odds: int = fair_odds
    
    def calculate_fair_odds():
        pass