from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from datetime import datetime

Base = declarative_base()

class Market(Base):
    __tablename__ = 'markets'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, nullable=False)
    sport = Column(String, nullable=False)
    league = Column(String, nullable=False)
    event = Column(String, nullable=False)
    market = Column(String, nullable=False)
    bet_name = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f"Market(id={self.id}, date={self.date}, sport={self.sport}, league={self.league}, event={self.event}, market={self.market}, bet_name={self.bet_name})"

class BookOdd(Base):
    __tablename__ = 'book_odds'
    id = Column(Integer, primary_key=True, autoincrement=True)
    market_id = Column(Integer, ForeignKey('markets.id'), nullable=False)
    book_name = Column(String, nullable=False)
    odds = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime)

    market = relationship("Market", back_populates="book_odds")

    def __repr__(self) -> str:
        return f"BookOdd(id={self.id}, market_id={self.market_id}, book_name={self.book_name}, odds={self.odds}, timestamp={self.timestamp})"

class Bet(Base):
    __tablename__ = 'bets'
    id = Column(Integer, primary_key=True, autoincrement=True)
    market_id = Column(Integer, ForeignKey('markets.id'), nullable=False)
    fair_odds = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime)

    market = relationship("Market", back_populates="bets")
    book_odds = relationship("BookOdd", secondary="bet_book_odd_link")

    def __repr__(self) -> str:
        return f"Bet(id={self.id}, market_id={self.market_id}, fair_odds={self.fair_odds}, timestamp={self.timestamp})"

class BetBookOddLink(Base):
    __tablename__ = 'bet_book_odd_link'
    bet_id = Column(Integer, ForeignKey('bets.id'), primary_key=True)
    book_odd_id = Column(Integer, ForeignKey('book_odds.id'), primary_key=True)

Market.book_odds = relationship("BookOdd", order_by=BookOdd.id, back_populates="market")
Market.bets = relationship("Bet", order_by=Bet.id, back_populates="market")

# Database setup
DATABASE_URL = "sqlite:///cno_scraper.db"  # Use SQLite for simplicity

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()