from sqlalchemy.orm import Session
from database.Database import Market, BookOdd, Bet
from datetime import datetime

class Repository:
    def __init__(self, session: Session):
        self.session = session

    def add_market(self, market: Market):
        existing_market = self.session.query(Market).filter(
            Market.date == market.date,
            Market.sport == market.sport,
            Market.league == market.league,
            Market.event == market.event,
            Market.market == market.market,
            Market.bet_name == market.bet_name
        ).first()
        if not existing_market:
            self.session.add(market)
            self.session.commit()

    def add_book_odd(self, book_odd: BookOdd):
        existing_book_odd = self.session.query(BookOdd).filter(
            BookOdd.market_id == book_odd.market_id,
            BookOdd.book_name == book_odd.book_name,
            BookOdd.odds == book_odd.odds,
            BookOdd.timestamp == book_odd.timestamp,
            BookOdd.is_best == book_odd.is_best
        ).first()
        if not existing_book_odd:
            self.session.add(book_odd)
            self.session.commit()

    def add_bet(self, bet: Bet):
        existing_bet = self.session.query(Bet).filter(
            Bet.market_id == bet.market_id,
            Bet.bet_odds == bet.bet_odds,
            Bet.fair_odds == bet.fair_odds,
            Bet.timestamp == bet.timestamp
        ).first()
        if not existing_bet:
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

    def save_game_data(self, market: Market, game_data) -> list[BookOdd]:   
        self.add_market(market)
        # Create BookOdd instances
        book_odds = []
        for header, data in zip(list(game_data.columns), game_data.values[0]):
            if header not in ['Bet Name', 'Best', 'Fair Odds']:
                if data['text']:
                    odds = int(data['text'])
                else: 
                    odds = None
                book_odd = BookOdd(
                    market_id=market.id,
                    book_name=header,  # Use the header as the book name
                    odds=odds,  # Assuming the text contains the odds
                    timestamp=datetime.now(),
                    is_best=data['is_best']
                )
                self.add_book_odd(book_odd)
                book_odds.append(book_odd)
        return book_odds
    
    def save_market_data(self, game_data) -> list[Market]:
        markets = []
        for index, row in game_data.iterrows():
            market = Market(
                date=row['Date'],
                sport=row['Sport'],
                league=row['League'],
                event=row['Event'],
                market=row['Market'],
                bet_name=row['Bet Name']
            )
            self.add_market(market)
            markets.append(market)
        return markets