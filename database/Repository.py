from sqlalchemy.orm import Session
from database.Database import Market, BookOdd, Bet

class Repository:
    def __init__(self, session: Session):
        self.session = session

    def add_market(self, market: Market):
        self.session.add(market)
        self.session.commit()

    def add_book_odd(self, book_odd: BookOdd):
        self.session.add(book_odd)
        self.session.commit()

    def add_bet(self, bet: Bet):
        self.session.add(bet)
        self.session.commit()

    def get_market_by_id(self, market_id: int) -> Market:
        return self.session.query(Market).filter(Market.id == market_id).first()

    def get_all_markets(self) -> list:
        return self.session.query(Market).all()

    def get_book_odd_by_id(self, book_odd_id: int) -> BookOdd:
        return self.session.query(BookOdd).filter(BookOdd.id == book_odd_id).first()

    def get_all_book_odds(self) -> list:
        return self.session.query(BookOdd).all()

    def get_bet_by_id(self, bet_id: int) -> Bet:
        return self.session.query(Bet).filter(Bet.id == bet_id).first()

    def get_all_bets(self) -> list:
        return self.session.query(Bet).all()

    def update_market(self, market: Market):
        self.session.merge(market)
        self.session.commit()

    def update_book_odd(self, book_odd: BookOdd):
        self.session.merge(book_odd)
        self.session.commit()

    def update_bet(self, bet: Bet):
        self.session.merge(bet)
        self.session.commit()

    def delete_market(self, market: Market):
        self.session.delete(market)
        self.session.commit()

    def delete_book_odd(self, book_odd: BookOdd):
        self.session.delete(book_odd)
        self.session.commit()

    def delete_bet(self, bet: Bet):
        self.session.delete(bet)
        self.session.commit()