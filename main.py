import time
import logging
import signal
import sys
from dotenv import load_dotenv
import os
from scraper.WebScraper import WebScraper
from engine.AlertService import AlertService

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

def get_market_key(market):
    """Generate a unique key for a market to track if it's been alerted."""
    return (market.date, market.sport, market.league, market.event, market.market, market.bet_name)

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    logging.info("Shutdown signal received. Cleaning up...")
    if 'scraper' in globals():
        scraper.cleanup()
    sys.exit(0)

def main():
    global scraper
    logging.info("Starting the web scraper and alert service (no database operations).") 
    scraper = WebScraper(URL, COOKIES_FILE_PATH)
    alert_service = AlertService(SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL, TO_EMAIL)
    alerted_markets = set()  # Track markets that have already been alerted

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        while True:
            logging.info("Scraping the website for positive EV markets.")
            soup = scraper.connect_and_scrape()
            if soup:
                markets = scraper.extract_positve_markets(soup)
                if len(markets) == 0:
                    logging.info("No positive EV markets found on the page.")
                    logging.info("Sleeping for 10 seconds.")
                    time.sleep(10)
                    continue                 
                
                # Send alerts only for new positive EV markets
                for market in markets:
                    market_key = get_market_key(market)
                    if market_key not in alerted_markets:
                        logging.info(f"Sending alert for new market: {market.bet_name}")
                        alert_service.send_market_alert(market)
                        alerted_markets.add(market_key)
                    else:
                        logging.info(f"Skipping already alerted market: {market.bet_name}")
                
            else:
                logging.warning("Failed to scrape the website.")
        
            logging.info("Sleeping for 10 seconds.")
            time.sleep(10)
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received. Cleaning up...")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()