import time
import logging
from datetime import datetime
from dotenv import load_dotenv
import os
from database.Database import session, Market, BookOdd, Bet
from database.Repository import Repository
from scraper.WebScraper import WebScraper
from AlertService import AlertService

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

URL = "https://crazyninjaodds.com/site/tools/positive-ev.aspx"
COOKIES_FILE_PATH = "cookies.txt"
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")
TO_EMAIL = os.getenv("TO_EMAIL")


def main():
    logging.info("Starting the web scraper and alert service.") 
    repo = Repository(session)
    scraper = WebScraper(URL, COOKIES_FILE_PATH, repo)
    alert_service = AlertService(SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL, TO_EMAIL)
   
    previous_data = None

    while True:
        current_time = datetime.now().time()
        if current_time.hour >= 0 and current_time.hour < 8:
            logging.info("Skipping alerts between midnight and 8 AM")
        else:
            logging.info("Scraping the website for data.")
            soup = scraper.connect_and_scrape()
            if soup:
                df = scraper.extract_data(soup)
                if df.empty:
                    logging.info("No data found on the page.")
                    time.sleep(30)
                    continue
                df.to_csv("output.csv", index=False)
                for index, row in df.iterrows():
                    scraper.navigate_and_scrape_links(row)
          
                current_top3 = df.head(3)
                
                # Save data to the database
                for index, row in df.iterrows():
                    if 'Book' not in row.keys():
                        continue
                    market = Market(
                        date=row['Date'],
                        sport=row['Sport'],
                        league=row['League'],
                        event=row['Event'],
                        market=row['Market'],
                        bet_name=row['Bet Name']
                    )
                    repo.add_market(market)
                    
                    book_odd = BookOdd(
                        market_id=market.id,
                        book_name=row['Book'],
                        odds=int(row['Odds']),
                        timestamp=datetime.now()
                    )
                    repo.add_book_odd(book_odd)
                    
                    bet = Bet(
                        market_id=market.id,
                        fair_odds=int(row['Fair Odds']),
                        timestamp=datetime.now()
                    )
                    bet.book_odds.append(book_odd)
                    repo.add_bet(bet)
                
                if previous_data is None or not current_top3.equals(previous_data):
                    logging.info("Data has changed. Sending an alert.")
                    #alert_service.analyze_data(current_top3)
                    previous_data = current_top3
                else:
                    logging.info("Data has not changed.")
            else:
                logging.warning("Failed to scrape the website.")
        logging.info("Sleeping for 30 seconds.")
        time.sleep(30)

if __name__ == "__main__":
    main()