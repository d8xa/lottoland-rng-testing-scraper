import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


class LottoScraper:
    def __init__(self, headless = True):
        # Set up Chrome options
        chrome_options = webdriver.ChromeOptions()
        if headless:
            chrome_options.add_argument('--headless')  # no window
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Initialize the driver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get("https://www.lottohelden.de/lotto/")
        
        self._accept_cookies()

        # Wait for lottery field to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "lotteryfield-container"))
        )
        
        # Initialize storage for numbers
        self.all_numbers = []


    @property
    def df(self) -> pd.DataFrame:
        return pd.DataFrame(self.all_numbers, columns=list(range(1,7)))


    def _accept_cookies(self):
        """Click the 'Okay' button in the cookie banner."""

        try:
            # Wait for the cookie banner to appear
            cookie_banner = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "cookie-banner")]'))
            )
            
            # Click the "Okay" button
            ok_button = cookie_banner.find_element(
                By.XPATH,
                './/button[@type="button" and @aria-label="Okay"]'
            )
            ok_button.click()
            print("Cookie banner accepted.")
            
        except Exception as e:
            print(f"Could not accept cookies: {e}")
    
    
    def get_quicktip(self):
        """Click the quick tip button and parse the active numbers"""

        try:
            # Find the first field container
            field_container = self.driver.find_element(
                By.XPATH, 
                '//div[contains(@class, "lotteryfield-container") and .//div[contains(text(), "Feld 1 von")]]'
            )
            
            # Click the quick tip button
            quick_tip_btn = field_container.find_element(
                By.CSS_SELECTOR, 
                'button.control-btn.btn-quicktip'
            )
            quick_tip_btn.click()
            
            # Wait for the numbers to update
            time.sleep(1)
            
            # get the marked numbers
            numbers = field_container.find_elements(By.TAG_NAME, "li")

            if numbers:
                current_pick = [
                    i+1
                    for i, x in enumerate(numbers)
                    if 'is-active' in x.get_attribute("class")
                ]
                self.all_numbers.append(current_pick)
                print(f"Collected numbers: {current_pick}")
                return current_pick
            else:
                print("Could not find the numbers")
                return None
                
        except Exception as e:
            print(f"Error occurred: {e}")
            return None
    

    def close(self):
        """Close the browser"""

        self.driver.quit()