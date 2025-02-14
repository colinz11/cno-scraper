from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
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

    book_odds = relationship("BookOdd", back_populates="market")
    bets = relationship("Bet", back_populates="market")

    def __repr__(self) -> str:
        return f"Market(id={self.id}, date={self.date}, sport={self.sport}, league={self.league}, event={self.event}, market={self.market}, bet_name={self.bet_name})"

class BookOdd(Base):
    __tablename__ = 'book_odds'
    id = Column(Integer, primary_key=True, autoincrement=True)
    market_id = Column(Integer, ForeignKey('markets.id'), nullable=False)
    book_name = Column(String, nullable=False)
    odds = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_best = Column(Boolean, nullable=False)

    market = relationship("Market", back_populates="book_odds")

    def __repr__(self) -> str:
        return f"BookOdd(id={self.id}, market_id={self.market_id}, book_name={self.book_name}, odds={self.odds}, timestamp={self.timestamp}, is_best={self.is_best})"

class Bet(Base):
    __tablename__ = 'bets'
    id = Column(Integer, primary_key=True, autoincrement=True)
    market_id = Column(Integer, ForeignKey('markets.id'), nullable=False)
    bet_odds = Column(Integer, nullable=False)
    fair_odds = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    market = relationship("Market", back_populates="bets")

    def __repr__(self) -> str:
        return f"Bet(id={self.id}, market_id={self.market_id}, bet_odds={self.bet_odds}, fair_odds={self.fair_odds}, timestamp={self.timestamp})"

# Database setup
DATABASE_URL = "sqlite:///cno_scraper.db"  # Use SQLite for simplicity

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()