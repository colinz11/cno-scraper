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
from urllib.parse import urlparse, parse_qs

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WebScraper:
    def __init__(self, url, cookies_file):
        self.url = url
        self.cookies_file = cookies_file
        self.options = Options()
        self.options.add_argument("--headless")  # Run headless (no browser window)
        self.options.add_argument("--disable-gpu")
        self.service = Service()
        self.driver = webdriver.Chrome(service=self.service, options=self.options)

    def connect_and_scrape(self):
        logging.info(f"Connecting to {self.url}")
        with webdriver.Chrome(service=self.service, options=self.options) as driver:
            self.driver = driver
            try:
                self.driver.get(self.url)
                logging.info("Page loaded.")
                self.load_cookies()
                self.driver.refresh()
                logging.info("Page refreshed after loading cookies.")
                time.sleep(3)
                wait = WebDriverWait(self.driver, 10)
                wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolderMain_ContentPlaceHolderRight_GridView1")))
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                logging.info("Scraping completed successfully.")
                return soup
            except Exception as e:
                logging.error(f"An error occurred during scraping: {e}")
                return None

    def load_cookies(self):
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
            self.driver.add_cookie(cookie)

    def extract_data(self, soup):
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
            rows.append(row)
        # Convert to Pandas DataFrame
        df = pd.DataFrame(rows, columns=headers)
        
        return df
    
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
            data.append(text)
        df = pd.DataFrame([data], columns=headers)
        return df
    
    def navigate_and_scrape_links(self, row):
        logging.info("Navigating and scraping links.")
        # Iterate through the DataFrame
        
        if row['Event'] is not None:
            
            # Extract the URL from the cell
            url = "https://crazyninjaodds.com" + row['Event'].split('(')[-1].strip(')')
            logging.info("Navigating to URL: %s", url)
            # Navigate to the new page
            self.driver = webdriver.Chrome(service=self.service, options=self.options)
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "ContentPlaceHolderMain_ContentPlaceHolderRight_GridView1"))
            )
            # Extract the row ID from the URL
            row_id = self.extract_row_id(url)
            logging.info("Extracting data for row ID: %s", row_id)
            # Scrape data from the new page
            new_soup = BeautifulSoup(self.driver.page_source, "html.parser")
            game_data = self.extract_game_data(new_soup, row_id)
            return game_data
                
                    