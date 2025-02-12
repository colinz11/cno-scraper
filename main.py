import time
import logging
from datetime import datetime
from WebScraper import WebScraper
from AlertService import AlertService
from dotenv import load_dotenv
import os

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
    scraper = WebScraper(URL, COOKIES_FILE_PATH)
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
                current_top3 = df.head(3)
                if previous_data is None or not current_top3.equals(previous_data):
                    logging.info("Data has changed. Sending an alert.")
                    alert_service.analyze_data(current_top3)
                    previous_data = current_top3
                else:
                    logging.info("Data has not changed.")
            else:
                logging.warning("Failed to scrape the website.")
        logging.info("Sleeping for 30 seconds.")
        time.sleep(30)

if __name__ == "__main__":
    main()