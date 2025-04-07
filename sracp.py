import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gspread
from google.oauth2.service_account import Credentials

# Define the URLs and their corresponding fund IDs
url_yield = "https://debank.com/profile/0x4380927070ccb0dd069d6412371a72e972239e06"
fundid_yield = 3  # Assign fund ID 2 to yield

url_assets = "https://debank.com/profile/0x0a152c957fd7bcc1212eab27233da0433b7c8ea4"
fundid_assets = 2  # Assign fund ID 3 to assets

# Create a list of tuples (url, fundid)
url_fundid_list = [
    (url_yield, fundid_yield),
    (url_assets, fundid_assets)
]

def scrape_balance(url):
    # Set up Chrome options for headless browsing
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")  # Useful in some environments

    # Initialize the Chrome driver (ensure you have the matching chromedriver installed)
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to the URL
        driver.get(url)
        
        # Wait for the element containing the total balance to be present.
        wait = WebDriverWait(driver, 30)
        time.sleep(10)  # Optional static delay; adjust or remove if explicit wait is sufficient
        
        total_balance_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".HeaderInfo_totalAssetInner__HyrdC"))
        )
        
        # Extract the text from the element and parse the balance
        total_balance = total_balance_element.text.strip()
        scraped_balance = total_balance.split()[0]
        
        # Capture current date and time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"URL: {url}\nTotal Balance: {scraped_balance}\nTimestamp: {timestamp}\n")
        return scraped_balance, timestamp
    except Exception as e:
        print(f"Error occurred for URL {url}: {e}")
        return None, None
    finally:
        driver.quit()

def update_google_sheet(data):
    # Set up Google Sheets API credentials and client
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file('blck-456015-02d4cfc790b7.json', scopes=scope)
    client = gspread.authorize(creds)

    # Open the spreadsheet and access the specific sheet by its title
    spreadsheet = client.open("BLCK_CAP")
    sheet = spreadsheet.worksheet("RAW")

    # Append each fund ID, its scraped balance, and the timestamp as a new row
    for fundid, balance, timestamp in data:
        if balance is not None and timestamp is not None:
            sheet.append_row([fundid, balance, timestamp])
    print("Data inserted into Google Spreadsheet successfully.")

if __name__ == "__main__":
    results = []
    for url, fundid in url_fundid_list:
        balance, timestamp = scrape_balance(url)
        results.append((fundid, balance, timestamp))
    
    # Update the Google Sheet with the scraped data including time and date
    update_google_sheet(results)
