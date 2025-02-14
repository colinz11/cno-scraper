import time
import logging
from datetime import datetime
from dotenv import load_dotenv
import os
from database.Database import session, Market, BookOdd, Bet
from database.Repository import Repository
from scraper.WebScraper import WebScraper
from engine.AlertService import AlertService
from engine.MarketTracker import MarketTracker

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
    market_tracker = MarketTracker(scraper, repo)
    previous_data = None

    while True:
        current_time = datetime.now().time()
        if current_time.hour >= 0 and current_time.hour < 8:
            logging.info("Skipping alerts between midnight and 8 AM")
        else:
            logging.info("Scraping the website for data.")
            soup = scraper.connect_and_scrape()
            if soup:
                markets = scraper.extract_positve_markets(soup)
                if len(markets) == 0:
                    logging.info("No data found on the page.")
                    time.sleep(30)
                    continue                 
                
                # Save data to the database
                for market in markets:
                    market_tracker.track_market(market)
                    market_tracker.check_market_updates()
                    
                 
                    alert_service.send_market_alert(market, None)
                
            else:
                logging.warning("Failed to scrape the website.")
        
        logging.info("Sleeping for 30 seconds.")
        time.sleep(30)

if __name__ == "__main__":
    main()