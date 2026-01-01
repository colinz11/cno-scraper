import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
from database.Database import Market
from urllib.parse import urlparse, parse_qs

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class WebScraper:
    def __init__(self, url, cookies_file):
        self.url = url
        self.cookies_file = cookies_file
        self.options = Options()
        self.options.add_argument("--headless")  # Run headless (no browser window)
        self.options.add_argument("--disable-gpu")
        self.driver = None
        self.service = None
        self.cookies_loaded = False

    def _initialize_driver(self):
        """Initialize the browser driver if it doesn't exist or is invalid."""
        try:
            if self.driver is None:
                logging.info("Initializing browser driver.")
                self.service = Service()
                self.driver = webdriver.Chrome(service=self.service, options=self.options)
                self.driver.get(self.url)
                logging.info("Page loaded initially.")
                self.load_cookies(self.driver)
                self.driver.refresh()
                logging.info("Page refreshed after loading cookies.")
                self.cookies_loaded = True
            else:
                # Check if driver is still valid
                try:
                    self.driver.current_url
                except:
                    # Driver is invalid, recreate it
                    logging.warning("Browser driver became invalid, recreating...")
                    if self.driver:
                        try:
                            self.driver.quit()
                        except:
                            pass
                    self.service = Service()
                    self.driver = webdriver.Chrome(service=self.service, options=self.options)
                    self.driver.get(self.url)
                    logging.info("Page loaded after recreation.")
                    self.load_cookies(self.driver)
                    self.driver.refresh()
                    logging.info("Page refreshed after loading cookies.")
                    self.cookies_loaded = True
        except Exception as e:
            logging.error(f"Error initializing driver: {e}")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            self.driver = None
            raise

    def connect_and_scrape(self):
        logging.info(f"Refreshing page at {self.url}")
        try:
            # Initialize driver if needed
            self._initialize_driver()
            
            # Just refresh the page instead of creating a new browser
            self.driver.refresh()
            logging.info("Page refreshed.")
            time.sleep(2)
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolderMain_ContentPlaceHolderRight_GridView1")))
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            logging.info("Scraping completed successfully.")
            return soup
        except Exception as e:
            logging.error(f"An error occurred during scraping: {e}")
            # Try to recover by resetting the driver
            self.driver = None
            self.cookies_loaded = False
            return None

    def cleanup(self):
        """Clean up the browser driver."""
        if self.driver:
            try:
                self.driver.quit()
                logging.info("Browser driver closed.")
            except Exception as e:
                logging.error(f"Error closing driver: {e}")
            finally:
                self.driver = None
                self.service = None
                self.cookies_loaded = False

    def load_cookies(self, driver):
        cookies = []
        with open(self.cookies_file, 'r') as f:
            cookie_lines = f.readlines()
            for line in cookie_lines:
                cookie_parts = line.strip().split(" ")
                if len(cookie_parts) >= 2:
                    cookie = {
                        'name': cookie_parts[0],
                        'value': cookie_parts[1],
                        'domain': 'crazyninjaodds.com',
                        'path': '/',
                        'secure': False
                    }
                    cookies.append(cookie)
        for cookie in cookies:
            driver.add_cookie(cookie)

    def extract_positve_markets(self, soup) -> list[Market]:
        # Locate the table
        table = soup.find("table", {"id": "ContentPlaceHolderMain_ContentPlaceHolderRight_GridView1"})
        # Extract headers
        headers = [th.text.strip() for th in table.find_all("th")]

        # Extract table rows
        rows = []
        for tr in table.find_all("tr")[1:]:  # Skip header row
            cells = tr.find_all("td")
            row = []
            for cell in cells:
               row.append(self.extract_cell_data(cell))
            if (len(row) == len(headers)):
                rows.append(row)
        # Convert to Pandas DataFrame
        df = pd.DataFrame(rows, columns=headers)
        # Create Market objects without saving to database
        markets = []
        for index, row in df.iterrows():
            market = Market(
                date=row['Date'],
                sport=row['Sport'],
                league=row['League'],
                event=row['Event'],
                market=row['Market'],
                bet_name=row['Bet Name']
            )
            # Add fair odds and best book odds as attributes (not part of DB schema)
            if 'Fair Odds' in row:
                market.fair_odds = row['Fair Odds']
            else:
                market.fair_odds = None
                
            if 'Best' in row:
                market.best_odds = row['Best']
            else:
                market.best_odds = None
                
            markets.append(market)
        return markets
    
    def extract_cell_data(self, cell):
         # Check for link elements (<a>) and extract both text and link (href attribute)
        link = cell.find("a")
        if link:
            return f"{link.text.strip()} ({link['href']})"
        # Check for bold text (<b>) and extract the bold text
        elif cell.find("b"):
            return cell.find("b").text.strip()
        # Check for input elements (buttons, text inputs, etc.)
        elif cell.find("input"):
            # For buttons, you could extract the button text or attribute
            input_type = cell.find("input").get("type", "Unknown")
            return f"Button ({input_type})"
        # Handle datetime or other text that isn't a link or input
        else:
            return cell.text.strip()
    
    def extract_row_id(self, url):
         # Parse the URL to extract the sideid parameter
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        side_id = query_params.get('sideid', [None])[0]
        return side_id
    
    def extract_game_data(self, soup, row_id):
        table = soup.find("table", {"id": "ContentPlaceHolderMain_ContentPlaceHolderRight_GridView1"})
        headers = [th.text.strip() for th in table.find_all("th")]

        # Locate the row by its id
        row = soup.find("tr", {"id": row_id})
        if not row:
            print(f"Row with id {row_id} not found.")
            return []

        # Extract all numbers from the row
        data = []
        cells = row.find_all("td")
        for cell in cells:
            text = cell.text.strip()
            is_best = 'background-color:#AFE1AF;' in cell.get('style', '')
            data.append({'text': text, 'is_best': is_best})
        df = pd.DataFrame([data], columns=headers)
        return df
    
                
                    