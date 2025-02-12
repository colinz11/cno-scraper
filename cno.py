from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time


# Set up Selenium with Homebrew's ChromeDriver
options = Options()
options.add_argument("--headless")  # Run headless (no browser window)
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

# Use ChromeDriver from Homebrew
service = Service()

# Start WebDriver
driver = webdriver.Chrome(service=service, options=options)
# Load cookies from a file
cookies_file = "cookies.pkl"  # The file where cookies are saved



# URL of the page
url = "https://crazyninjaodds.com/site/tools/positive-ev.aspx"
driver.get(url)

# Load cookies from the text file
cookies_file = "cookies.txt"  # The file where cookies are saved

# Parse the cookies file
def load_cookies(file_path):
    cookies = []
    with open(file_path, 'r') as f:
        cookie_lines = f.readlines()
        
        for line in cookie_lines:
            cookie_parts = line.strip().split(" ")
            if len(cookie_parts) >= 2:
                cookie = {
                    'name': cookie_parts[0],
                    'value': cookie_parts[1],
                    'domain': 'crazyninjaodds.com',  # Set your domain if it's consistent
                    'path': '/',  # Set your cookie path (adjust if needed)
                    'secure': False  # Set to True if the cookie is secure
                }
                cookies.append(cookie)
    return cookies
# Load and add cookies
cookies = load_cookies(cookies_file)
for cookie in cookies:
    driver.add_cookie(cookie)

print("Cookies loaded successfully.")

driver.refresh()

time.sleep(3)
# Wait until the table is loaded
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolderMain_ContentPlaceHolderRight_GridView1")))

# Get the page source after JS has loaded the content
soup = BeautifulSoup(driver.page_source, "html.parser")

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
        # Check for link elements (<a>) and extract both text and link (href attribute)
        link = cell.find("a")
        if link:
            row.append(f"{link.text.strip()} ({link['href']})")  # Extract text and link
        # Check for bold text (<b>) and extract the bold text
        elif cell.find("b"):
            row.append(cell.find("b").text.strip())  # Extract bold text
        # Check for input elements (buttons, text inputs, etc.)
        elif cell.find("input"):
            # For buttons, you could extract the button text or attribute
            input_type = cell.find("input").get("type", "Unknown")
            row.append(f"Button ({input_type})")  # Handle input buttons (could be extended to text inputs too)
        # Handle datetime or other text that isn't a link or input
        else:
            row.append(cell.text.strip())  # Extract normal text
    rows.append(row)

# Convert to Pandas DataFrame
df = pd.DataFrame(rows, columns=headers)

# Save to CSV
df.to_csv("positive_ev_odds.csv", index=False)
time.sleep(10  )
print(df)
# Close the browser
driver.quit()
