import requests
import os
from datetime import datetime, date
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def is_trading_day():
    """Check if today is a trading day (Monday-Friday)"""
    today = date.today()
    return today.weekday() < 5

def download_nse_data():
    """Download NSE pre-open market data"""
    if not is_trading_day():
        print("Today is weekend. Skipping download.")
        return
    
    # Create downloads directory
    os.makedirs("downloads", exist_ok=True)
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    
    # Set download preferences
    prefs = {
        "download.default_directory": os.path.abspath("downloads"),
        "download.prompt_for_download": False,
        "directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    try:
        # Initialize driver
        driver = webdriver.Chrome(
            ChromeDriverManager().install(),
            options=chrome_options
        )
        
        # Navigate to NSE page
        url = "https://www.nseindia.com/market-data/pre-open-market-cm-and-emerge-market"
        driver.get(url)
        
        # Wait for page load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(5)
        
        # Try to find and click download button
        download_selectors = [
            "a[href*='download']",
            "button[class*='download']",
            ".download-btn",
            "[data-download]",
            "a[title*='Download']",
            ".btn-download"
        ]
        
        downloaded = False
        for selector in download_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        element.click()
                        downloaded = True
                        print(f"Download triggered with selector: {selector}")
                        break
                if downloaded:
                    break
            except:
                continue
        
        if downloaded:
            time.sleep(10)  # Wait for download
            
            # Rename file with date
            today_str = datetime.now().strftime("%Y%m%d")
            files = [f for f in os.listdir("downloads") 
                    if f.endswith(('.xlsx', '.xls', '.csv'))]
            
            if files:
                latest_file = max(files, key=lambda x: os.path.getctime(f"downloads/{x}"))
                ext = os.path.splitext(latest_file)[1]
                new_name = f"NSE_PreOpen_{today_str}{ext}"
                os.rename(f"downloads/{latest_file}", f"downloads/{new_name}")
                print(f"File saved as: {new_name}")
            
        driver.quit()
        print("Download completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    download_nse_data()
